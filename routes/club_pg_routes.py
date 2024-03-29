from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField, PasswordField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from database import insert_one, get_data_one, get_data, update_one
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime
from werkzeug.security import generate_password_hash
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

cloudinary.config( 
  cloud_name = "da0xh1cht",
  api_key = "271152383133998",
  api_secret = "jeaUxjpB__T2H3yEDZg6I_mOje8"
)

# Create a Blueprint
club_pg = Blueprint('club_pg', __name__)

class ClubForm(FlaskForm):
    name             = StringField('Club Name:', validators=[DataRequired()])
    email            = StringField('Club Email Address:', validators=[DataRequired() , Email(message = "Please include an '@' in the email address. Email address is missing an '@' ")] )
    password         = PasswordField( 'Create a Password:', validators = [DataRequired(), EqualTo('password_conf', message = 'Password and confirm password do not match') ])
    password_conf    = PasswordField( 'Confirm Password:', validators = [DataRequired()] )
    category         = SelectField("Club Category:", choices=[
                        ('academic', 'Academic'),
                        ('arts_culture', 'Arts/Culture'),
                        ('community_service', 'Community Service'),
                        ('environment_sustainability', 'Environment'),
                        ('health_wellness', 'Health/Wellness'),
                        ('hobby_special_interest', 'Hobby'),
                        ('leadership', 'Leadership'),
                        ('misc', "Miscellaneous"), 
                        ('sports_athletics', 'Sports/Athletics'),
                        ('technology_innovation', 'Technology')],
                        validators=[DataRequired()])
    description      = TextAreaField('Club Description:', validators=[DataRequired()])
    club_icon        = FileField('Attach Club Logo:')
    submit           = SubmitField('Create Club') 

class FollowClub(FlaskForm):
    follow = SubmitField('Follow')

class UnfollowClub(FlaskForm):
    unfollow = SubmitField('Unfollow')


def user_follow_club(user_id, club_id):

    # Add the user to the Club's followers array
    success, result = update_one('Clubs', {'_id': ObjectId(club_id)}, {'$addToSet': {'followers': ObjectId(user_id)}})

    if not success:
        return False, result
    
    # Add the club to the user's following array
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$addToSet': {'following_clubs': ObjectId(club_id)}})
    
    if success:
        return True, result

    else:
        return False, result


def user_unfollow_club(user_id, club_id):

    # Remove the user from the Club's followers array
    success, result = update_one('Clubs', {'_id': ObjectId(club_id)}, {'$pull': {'followers': ObjectId(user_id)}})

    if not success:
        return False, result

    # Remove the club from the user's following array
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$pull': {'following_clubs': ObjectId(club_id)}})

    if success:
        return True, result
    else:
        return False, result
    

def is_user_following_club(user_id, club_id):
    # determine if user is following a given club
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'following_clubs': 1})
    if success:
        return ObjectId(club_id) in data['following_clubs']

    return False


@club_pg.route('/clubs/<string:club_id>', methods=['GET', 'POST'])
def club_view(club_id):
    follow_club = FollowClub()
    unfollow_club = UnfollowClub()

    success, club = get_data_one('Clubs', {'_id': ObjectId(club_id)})

    if not success:
        return "<h1> Error </h1>"

    # Get all events for the club
    success_events, events = get_data('Events', {'club_id': ObjectId(club_id)})

    if not success_events:
        events = []

    current_time = datetime.now()

    # Prepare data for the template
    data = {'club_name': club['name'], 'club_description': club['description'], 'club_id':club_id, 'events': [], 'club_img': club['photo']}

    for event in events:
        timestamp = event['time']
        event_completed = timestamp <= current_time

        # Get attendees for each event
        success_attendees, attendees = get_data('Users', {'_id': {'$in': event['attendees']}})
        num_attending = len(attendees) if success_attendees else 0

        # Get the number of reviews for each event (if completed)
        num_reviews = len(event.get('event_ratings', []))

        # Prepare event data
        event_data = {
            'event_id': str(event['_id']),
            'event_name': event['name'],
            'event_description': event['description'],
            'attendees': attendees,
            'num_attending': num_attending,
            'date': timestamp.strftime("%B %d, %Y"),
            'time': timestamp.strftime("%I:%M %p"),
            'location': event['location'],
            'completed': event_completed,
            'num_reviews': num_reviews,
            'event_rating_avg': int(event['event_rating_avg']) if 'event_rating_avg' in event else 0
        }

        data['events'].append(event_data)
        
    # User View
    if session['is_user']:
        is_following = is_user_following_club(session['user_id'], club_id)

        if request.method == 'POST':
            if is_following:
                success,_ = user_unfollow_club(str(session['user_id']), str(club_id))
                if success:
                    return redirect(url_for('club_pg.club_view', club_id=data['club_id']))
            else:
                success,_ = user_follow_club(str(session['user_id']), str(club_id))
                if success:
                    return redirect(url_for('club_pg.club_view', club_id=data['club_id']))
            
        if is_following:
            return render_template('club.html', data=data, is_user=session['is_user'], form=unfollow_club, name=session['name'])
        else:
            return render_template('club.html', data=data, is_user=session['is_user'], form=follow_club, name=session['name'])
    # Club View
    return render_template('club.html', data=data, is_user=session['is_user'], name=session['name'])


@club_pg.route('/clubs/<string:club_id>/<string:event_id>')
def club_event_view(club_id, event_id):
    
    success_1, club = get_data_one('Clubs', {'_id': ObjectId(club_id)})
    success_2, event = get_data_one('Events', {'_id': ObjectId(event_id)})

    if not success_1 or not success_2:
        return "<h1> Error </h1>"
    
    # determine if a event has already passed
    current_time = datetime.utcnow()
    timestamp = event['time']
    event_completed = timestamp <= current_time
    
    data = {}

    # get name of attendees
    attendees = []

    for user_id in event['attendees']:
        success, user_data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'name': 1, 'email': 1, 'year': 1, 'program': 1})

        if success:
            attendee = {
                'name': user_data.get('name', "N/A"),
                'email': user_data.get('email', "N/A"),
                'year': user_data.get('year', "N/A"),
                'program': user_data.get('program', "N/A")
            }

            attendees.append(attendee)
    # Event data
    data['event_name'] = event['name']
    data['event_description'] = event['description']
    data['attendees'] = attendees
    data['num_attending'] = len(event['attendees'])
    data['date'] = timestamp.strftime("%B %d, %Y")
    data['time'] = timestamp.strftime("%I:%M %p")
    data['location'] = event['location']
    data['completed'] = event_completed
    data['categories'] = event['categories']
    # Club data
    # TODO add imgs
    data['club_name'] = club['name']
    data['club_id'] = str(club['_id'])
    data['club_img'] = club['photo']

    if event_completed:
        # get all reviews of event
        reviews = []
        for review in event['event_ratings']:
            review_obj = {
                'name': review.get('name', "Anonymous"),
                'rating': int(review['rating']),
                'comment': review['comments']
            }
            reviews.append(review_obj)        

        # get event rating average
        data['event_rating_avg'] = int(event['event_rating_avg'])
        data['reviews'] = reviews

    return render_template('club_event.html', data=data, is_user=session['is_user'], name=session['name'])

@club_pg.route('/create_club', methods=['GET', 'POST'])
def create_club():
    form = ClubForm()    
    if form.validate_on_submit():
        session['name']        = str(form.name.data)   
        session['email']            = str(form.email.data)
        session['description'] = str(form.description.data) 
        session['password']         = generate_password_hash(str(form.password.data))

        club_object = {
            'description': session.get('description'),
            'name': session.get('name'),
            'email': session.get('email'),
            'password': session.get('password'), 
            'avg_rating': 0.0, 
            'events': [], 
            'followers': [], 
            'photo': '',
            'category': form.category.data
        }

        club_icon_file = form.club_icon.data
        if club_icon_file:
    
            allowed_extensions = {'jpg', 'jpeg', 'png'}
            filename = secure_filename(club_icon_file.filename)
            file_extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else None
            content_type = club_icon_file.content_type

            if file_extension in allowed_extensions or content_type.startswith('image/'):
                result = upload(club_icon_file)
                cloudinary_url = result['secure_url']

                # Save the Cloudinary URL to the club object
                club_object['photo'] = cloudinary_url
            else:
                # Handle the case where the uploaded file is not an image
                # You can display an error message to the user or take other appropriate action
                flash("Invalid file format. Please upload an image file.")
                return redirect(url_for('club_pg.create_club'))          

        else:
            club_object['photo'] = '/static/Utoronto_logo.png'

        success, club_id = insert_one('Clubs', club_object)      

        if not success:
            #Once the create club form is sucessfully completed, user gets redirected to club page
            return redirect(url_for('club_pg.create_club'))

        return redirect(url_for('user_auth.login', club_id=club_id))

    return render_template('create_club.html', form=form, club_icon=session.get('club_icon'), description=session.get('description'), name=session.get('name'), email=session.get('email'), is_user=session.get('is_user'))
