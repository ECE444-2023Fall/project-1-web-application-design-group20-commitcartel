from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request
from database import insert_one, get_data_one
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email
from werkzeug.security import check_password_hash

user_auth = Blueprint('user_auth', __name__)

class LoginForm(FlaskForm):
    email            = StringField('Email Address:', validators=[DataRequired()])
    password         = PasswordField('Password:', validators = [DataRequired()])
    submit           = SubmitField('Login')


@user_auth.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect the user to the login page or any other page
    return redirect(url_for('user_auth.login'))

@user_auth.route('/login', methods=['GET', 'POST'])
def login():
    # Declare Form
    form = LoginForm()

    if form.validate_on_submit():
        email = str(form.email.data)
        password = str(form.password.data)

        # Check if the user exists based on email
        success, user_data = get_data_one("Users", {"email": email}, {'_id': 1, 'email': 1, 'password': 1, 'name': 1})

        if success and user_data:
            if check_password_hash(str(user_data['password']), password):
                session['is_user'] = True
                session['user_id'] = str(user_data['_id'])
                session['name'] = str(user_data['name'])
                session['search'] = None
                session['categories'] = None
                session['start_date'] = None
                session['end_date'] = None
                session['filter'] = {}
                
                return redirect(url_for('index'))

        success, club_data = get_data_one("Clubs", {"email": email}, {'_id': 1, 'email': 1, 'password': 1, 'name': 1})

        if success and club_data:
            if check_password_hash(str(club_data['password']), password):
                session['is_user'] = False
                session['club_id'] = str(club_data['_id'])
                session['name'] = str(club_data['name'])
                club_id = session['club_id']

                return redirect(url_for('club_pg.club_view', club_id = club_id))
                          
        return redirect(url_for('user_auth.login'))
    
    return render_template('login.html', form=form)
