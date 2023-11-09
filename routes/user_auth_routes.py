from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request
from database import insert_one, get_data_one
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email
from werkzeug.security import generate_password_hash

user_auth = Blueprint('user_auth', __name__)

class LoginForm(FlaskForm):
    email            = StringField('Email Address:', validators=[DataRequired()])
    password         = PasswordField('Password:', validators = [DataRequired()])
    Submit           = SubmitField('Login')


@user_auth.route('/login', methods=['GET', 'POST'])
def login():
    # Declare Form
    form = LoginForm()

    if form.validate_on_submit():
        email = str(form.email.data)
        password = generate_password_hash(str(form.password.data))

        # Check if the user exists based on email
        success, user_data = get_data_one("Users", {"email": email}, {'_id': 1, 'email': 1, 'password': 1})

        if success:
            if password == user_data['password']:
                session['is_user'] = True
                session['user_id'] = user_data['_id']
                # Redirect to where needed
                return redirect('/explore')

        success, club_data = get_data_one("Clubs", {"email": email}, {'_id': 1, 'email': 1, 'password': 1})

        if success:
            if password == club_data['password']:
                session['is_user'] = False
                session['club_id'] = club_data['_id']
                club_id = str(session['club_id'])
                return redirect(f'/clubs/{club_id}')              

        return redirect('/login')
    
    return render_template('login.html', form=form)
