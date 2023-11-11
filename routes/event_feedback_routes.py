from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
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
    name         = StringField('Full Name:', validators = [DataRequired()])
    email        = StringField('Email Address:', validators=[DataRequired(), Email(), CheckValidCampusConnectEmail()])
    rating       = IntegerField('Rating (scale 1 to 5):', validators=[NumberRange(min=1, max=5, message=None)])
    comments     = StringField('Comments:', validators = [DataRequired()])
    submit       = SubmitField('Submit Review')

@event_feedback.route('/leave_event_feedback/<event_id>', methods=['GET', 'POST'])
def leave_event_feedback(event_id):
    form = EventFeedbackForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            session['name']             = str(form.name.data)
            session['email']            = str(form.email.data)
            session['rating']           = str(form.rating.data)
            session['comments']         = str(form.comments.data)

            feedback_id = ObjectId()  # Create new event feedback ID
            email_query = {'email': session.get('email')}
            success_user, user = get_data_one('Users', email_query)  # Get corresponding user_id for entered CampusConnect email

            event_object = {
                'event_feedback_id': str(feedback_id),
                'user_id': str(user['_id']),
                'rating': session.get('rating'),
                'comments': session.get('comments'),
            }

            # Update Events database with corresponding event rating and comments for given event
            success_events, result_events = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'event_ratings': event_object}})

            if success_events:
                success1, event1 = get_data_one('Events', {'_id': ObjectId(event_id)})
            
                if success1 and event1:
                    event_ratings = [int(rating['rating']) for rating in event1['event_ratings']]

                    # Computer average rating of all event's ratings (including given rating just added)
                    if event_ratings:
                        avg_rating = sum(event_ratings)/len(event_ratings)
                    else:
                        avg_rating = 0

                    # Update Events database with corresponding event average rating for given event
                    success_avg_rating, result_avg_rating = update_one('Events', {'_id': ObjectId(event_id)}, {'$set': {'event_rating_avg': avg_rating}})

                    # Once form properly submitted, user redirected back to event page
                    if success_avg_rating:
                        return redirect(url_for('event_feed.view_event_user', event_id=event_id))
                    else:
                        return jsonify({'error': result_avg_rating}), 500
                else:
                    return jsonify({'error': result_events}), 500
    return render_template('event_feedback_form.html', form=form, event_id=event_id)
    
