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
    Submit           = SubmitField('Login')


@user_auth.route('/login', methods=['GET', 'POST'])
def login():
    # Declare Form
    form = LoginForm()

    if form.validate_on_submit():
        email = str(form.email.data)
        password = str(form.password.data)

        # Check if the user exists based on email
        success, user_data = get_data_one("Users", {"email": email}, {'_id': 1, 'email': 1, 'password': 1})

        if success:
            if check_password_hash(user_data['password'], password):
                session['is_user'] = True
                session['user_id'] = str(user_data['_id'])
                # Redirect to where needed
                return redirect(url_for('/explore'))

        success, club_data = get_data_one("Clubs", {"email": email}, {'_id': 1, 'email': 1, 'password': 1})

        if success:
            if check_password_hash(club_data['password'], password):
                session['is_user'] = False
                session['club_id'] = str(club_data['_id'])
                club_id = session['club_id']
                return redirect(url_for('/clubs/{club_id}'))              

        return redirect(url_for('/login'))
    
    return render_template('login.html', form=form)
