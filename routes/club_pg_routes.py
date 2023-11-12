from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from database import insert_one, get_data_one
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime
from werkzeug.security import generate_password_hash


# Create a Blueprint
club_pg = Blueprint('club_pg', __name__)


class ClubForm(FlaskForm):
    name             = StringField('Club Name:', validators=[DataRequired()])
    email            = StringField('Club Email Address:', validators=[DataRequired() , Email(message = "Please include an '@' in the email address. Email address is missing an '@' ")] )
    password         = PasswordField( 'Create a Password:', validators = [DataRequired(), EqualTo('password_conf', message = 'Password and confirm password do not match') ])
    password_conf    = PasswordField( 'Confirm Password:', validators = [DataRequired()] )
    description      = TextAreaField('Short description About the Club:', validators=[DataRequired()])
    club_icon        = FileField('Attach Club Logo:')
    submit           = SubmitField('Create Account') 



@club_pg.route('/clubs/<string:club_id>')
def clubs(club_id):
    event_list = []
    club_id   = ObjectId(club_id)
    success, club_find = get_data_one('Clubs', {'_id': club_id})
    if(success):
        name = club_find['name']
        description = club_find['description']
        email = club_find['email']
        events = club_find['events'] #this is a list of event ids
        for eventID in events:
            success, event_find = get_data_one('Events',{'_id': eventID})
            event_list.append(event_find['name'])     #create a list of event names from event IDs

    return render_template("clubs.html", name=name, description=description, events=event_list, email=email)


@club_pg.route('/clubs/<string:club_id>/<string:event_id>')
def club_event_view(club_id, event_id):
    
    success_1, club = get_data_one('Clubs', {'_id': ObjectId(club_id)})
    success_2, event = get_data_one('Events', {'_id': ObjectId(event_id)})

    if not success_1 or not success_2:
        return "<h1> Error </h1>"
    
    # determine if a event has already passed
    current_time = datetime.utcnow()
    timestamp = datetime.fromtimestamp(event['time'].time)
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
    
    # Club data
    # TODO add imgs
    data['club_name'] = club['name']
    data['club_id'] = str(club['_id'])

    if event_completed:
        # get all reviews of event
        reviews = []
        for review in event['event_ratings']:
            success, user_data = get_data_one('Users', {'_id': ObjectId(review['user_id'])}, {'name': 1})

            if success:
                review_obj = {
                    'name': user_data.get('name', "N/A"),
                    'rating': int(review['rating']),
                    'comment': review['comments']
                }

                reviews.append(review_obj)        
        
        # get event rating average
        data['event_rating_avg'] = int(event['event_rating_avg'])
        data['reviews'] = reviews
        
    
    return render_template('club_event.html', data=data)

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
            'avg_rating': 0, 
            'events': [], 
            'followers': [], 
            'photo': ''
        }

        success, club_id = insert_one('Clubs', club_object)      

        if not success:
            #Once the create club form is sucessfully completed, user gets redirected to club page
            return redirect(url_for('club_pg.create_club'))

        return redirect(url_for('user_auth.login', club_id=club_id))

    return render_template('create_club.html', form=form, club_icon=session.get('club_icon'), description=session.get('description'), name=session.get('name'), email=session.get('email'))
