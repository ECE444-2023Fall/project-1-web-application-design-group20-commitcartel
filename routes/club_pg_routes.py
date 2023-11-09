from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from database import insert_one, get_data_one
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

# Create a Blueprint
club_pg = Blueprint('club_pg', __name__)


class ClubForm(FlaskForm):
    club_name        = StringField('Club Name:', validators=[DataRequired()])
    email            = StringField('Club Email Address:', validators=[DataRequired() , Email(message = "Please include an '@' in the email address. Email address is missing an '@' ")] )
    password         = PasswordField( 'Create a Password:', validators = [DataRequired(), EqualTo('password_conf', message = 'Password and confirm password do not match') ])
    password_conf    = PasswordField( 'Confirm Password:', validators = [DataRequired()] )
    club_description = TextAreaField('Short description About the Club:', validators=[DataRequired()])
    club_icon        = FileField('Attach Club Logo:', validators= [DataRequired()] )
    submit           = SubmitField('Create Account') 



@club_pg.route('/clubs/<string:club_id>')
def clubs(club_id):
    event_list = []
    club_id   = ObjectId(club_id)
    club_find = get_data_one('Clubs',{'_id': club_id})
    if(len(club_find)> 0):
        club_info = club_find[1]
        club_name = club_info['club_name']
        club_description = club_info['club_description']
        email = club_info['email']
        events = club_info['events'] #this is a list of event ids
        for eventID in events:
            event_find = get_data_one('Events',{'_id': eventID})
            event_info = event_find[0]
            event_name = event_info['name']
            event_list.append(event_name)     #create a list of event names from event IDs

    return render_template("clubs.html", club_name=club_name, club_description=club_description, events=event_list, email=email)

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
