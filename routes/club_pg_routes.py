from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from database import insert_one, get_data_one
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename
from datetime import datetime

# Create a Blueprint
club_pg = Blueprint('club_pg', __name__)


class ClubForm(FlaskForm):
    club_name        = StringField('What is the Club Name?', validators=[DataRequired()])
    email            = StringField('What is the Club Email Address?', validators=[DataRequired() , Email(message = "Please include an '@' in the email address. Email address is missing an '@' ")] )
    password         = StringField( 'Please Create a Password', validators = [DataRequired(), EqualTo('password_conf', message = 'Password and confirm password do not match') ])
    password_conf    = StringField( 'Please Confirm the Password', validators = [DataRequired()] )
    club_icon        = FileField('Please Attach Club Logo:', validators= [DataRequired()] )
    club_description = TextAreaField('Please Write a Short description About the Club:', validators=[DataRequired()])
    submit           = SubmitField('Submit') 



@club_pg.route('/clubs/<string:club_id>')
def clubs(club_id):
    event_list = []
    club_id   = ObjectId(club_id)
    success, club_find = get_data_one('Clubs', {'_id': club_id})
    if(success):
        club_name = club_find['club_name']
        club_description = club_find['club_description']
        email = club_find['email']
        events = club_find['events'] #this is a list of event ids
        for eventID in events:
            success, event_find = get_data_one('Events',{'_id': eventID})
            event_list.append(event_find['name'])     #create a list of event names from event IDs

    return render_template("clubs.html", club_name=club_name, club_description=club_description, events=event_list, email=email)


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
    # event data
    data['event_name'] = event['name']
    data['event_description'] = event['description']
    data['attendees'] = event['attendees']
    data['num_attending'] = len(event['attendees'])
    data['date'] = timestamp.strftime("%B %d, %Y")
    data['time'] = timestamp.strftime("%I:%M %p")
    data['location'] = event['location']
    # Club data
    # TODO add imgs

    if event_completed:
        data['event_rating'] = event['event_rating_avg']
        data['event_comments'] = event['event_comments']
    
    return render_template('club_event.html', data=data)

@club_pg.route('/create_club', methods=['GET', 'POST'])
def create_club():
    form = ClubForm()    
    if form.validate_on_submit():
        session['club_name']        = str(form.club_name.data)   
        session['email']            = str(form.email.data)
        session['club_description'] = str(form.club_description.data) 
        session['password']         = str(form.password.data)

        club_object = {
            'club_description': session.get('club_description'),
            'club_name': session.get('club_name'),
            'email': session.get('email'),
            'password': session.get('password'), 
            'club_rating_avg': '', 
            'events': '', 
            'followers': '', 
            'photo': ''
        }

        success, club_id = insert_one('Clubs', club_object)      

        if success == False:
            return jsonify({'error'}), 500


        if request.method == 'POST':
            #Once the create club form is sucessfully completed, user gets redirected to club page
            return redirect(url_for('club_pg.clubs', club_id=club_id)) 


        return redirect(url_for('club_pg.create_club'))

    return render_template('create_club.html', form=form, club_icon=session.get('club_icon'), club_description=session.get('club_description'), club_name=session.get('club_name'), email=session.get('email'))
