from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, NumberRange
from database import insert_one, get_data_one
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash

# Create a Blueprint
user_account = Blueprint('user_account', __name__)

class UofTEmail(object):
    def __init__(self, message=None):
        if not message:
            message = "Please enter a valid UofT email address"
        self.message = message

    def __call__(self, form, field):
        if "utoronto" not in field.data:
            raise ValidationError(self.message)

class UserAccountForm(FlaskForm):
    name             = StringField('Full Name:', validators = [DataRequired()])
    email            = StringField('UofT Email Address:', validators=[DataRequired(), Email(message = "Please include an '@' in the email address. Email address is missing an '@' "), UofTEmail()])
    program          = StringField('Program:', validators = [DataRequired()])
    year             = IntegerField('Graduating Year:', validators = [DataRequired(), NumberRange(min=1950, max=2050, message = "Please enter a valid year (example: 2026)")])
    password         = PasswordField('Create a Password:', validators = [DataRequired(), EqualTo('password_conf', message = "Password and confirm password do not match")])
    password_conf    = PasswordField('Confirm Password:', validators = [DataRequired()])
    submit           = SubmitField('Create Account') 

@user_account.route('/create_user_account', methods=['GET', 'POST'])
def create_user_account():
    form = UserAccountForm()
    if form.validate_on_submit():
        session['name']             = str(form.name.data)
        session['email']            = str(form.email.data)
        session['program']          = str(form.program.data)
        session['year']             = str(form.year.data)
        session['password']         = generate_password_hash(str(form.password.data))

        user_object = {
            'name': session.get('name'),
            'registered_events': [],
            'following_clubs': [],       
            'email': session.get('email'),
            'filtered_clubs': [],
            'filtered_events': [],
            'password': session.get('password'), 
            'program': session.get('program'), 
            'year': session.get('year'), 
        }

        # Insert new user profile into Users database once form successfully submitted
        success, user_id = insert_one('Users', user_object)      

        if success == False:
            return jsonify({'error'}), 500

        if request.method == 'POST':
            # Once the create user account form is sucessfully completed, user gets redirected to home page
            return redirect(url_for('index'))

        return redirect(url_for('user_account.create_user_account'))

    return render_template('create_user_account.html', form=form)
