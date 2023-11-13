from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, NumberRange, ValidationError
from database import update_one, get_data_one
from bson.objectid import ObjectId

event_feedback = Blueprint('event_feedback', __name__)

# Check to ensure email entered is valid CampusConnect user email
class CheckValidCampusConnectEmail(object):
    def __init__(self, response=None):
        if not response:
            response = 'Wrong email entered. Use email registered with CampusConnect account.'
        self.response = response

    def __call__(self, form, value):
        email_query = {'email': value.data}
        success_email, real_user = get_data_one('Users', email_query)

        if not success_email or real_user is None:
            raise ValidationError(self.response)

class EventFeedbackForm(FlaskForm):
    rating       = IntegerField('Rating (scale 1 to 5):', validators=[DataRequired(), NumberRange(min=1, max=5, message=None)])
    comments     = StringField('Comments:', validators = [DataRequired()])
    anonymous    = BooleanField('Leave Anonymous Review')
    submit       = SubmitField('Submit Review')

@event_feedback.route('/leave_event_feedback/<event_id>', methods=['GET', 'POST'])
def leave_event_feedback(event_id):
    form = EventFeedbackForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            anonymous = form.anonymous.data
            session['rating']           = str(form.rating.data)
            session['comments']         = str(form.comments.data)

            feedback_id = ObjectId()  # Create new event feedback ID
            user_id = str(session['user_id'])
            success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'name': 1, 'registered_events': 1})

            if not success:
                flash("Error reviewing event!")
                return redirect(url_for('event_feedback.leave_event_feedback', event_id=event_id))

            # Get name if not anonymous
            name = "Anonymous"
            if not anonymous:
                name = data['name']
            
            # Check if user is registered to event
            if ObjectId(event_id) not in data['registered_events']:
                # ideally they will never be able to reach this page but putting this for safe measure
                flash("You can only review events you registered for!")
                return redirect(url_for('event_feedback.leave_event_feedback', event_id=event_id))

            # Check if user already left a review
            success, data = get_data_one('Events', {'_id': ObjectId(event_id)}, {'event_ratings': 1, 'event_rating_avg': 1})

            if not success:
                flash("Error reviewing event!")
                return redirect(url_for('event_feedback.leave_event_feedback', event_id=event_id))

            for review in data['event_ratings']:
                if str(user_id) == review.get('user_id'):
                    flash("You have already left a review for this event!")
                    return redirect(url_for('event_feedback.leave_event_feedback', event_id=event_id))

            event_object = {
                'event_feedback_id': str(feedback_id),
                'user_id': user_id,
                'rating': session.get('rating'),
                'comments': session.get('comments'),
                'name': name
            }

            # Update Events database with corresponding event rating and comments for given event
            num_reviews = len(data['event_ratings'])
            old_event_avg = data['event_rating_avg']
            event_average = ((old_event_avg * num_reviews) + int(form.rating.data)) / (num_reviews + 1)
            success, result = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'event_ratings': event_object}, '$set': {'event_rating_avg': event_average}})

            if success:
                flash("Successfully left a review")
                return redirect(url_for('event_feed.view_event_user', event_id=event_id))

            flash("Error leaving event review!")
            return redirect(url_for('event_feedback.leave_event_feedback', event_id=event_id))

    return render_template('event_feedback_form.html', form=form, event_id=event_id, is_user=session['is_user'], name=session['name'])
    
