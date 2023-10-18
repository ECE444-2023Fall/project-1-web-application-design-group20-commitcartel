#Helper functions
from flask              import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap    import Bootstrap
from flask_moment       import Moment
from datetime           import datetime
from flask_wtf          import FlaskForm
from wtforms            import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

class validateEmail(object):
    def __call__(self, form, field):
        email = field.data
        if '@' not in email:

            raise ValidationError("Please include an '@' in the email address. '" + str(email) + "' is missing an '@'")
        elif '@' in email and "utoronto" not in email:

            raise ValidationError("Please include a valid UofT email address. '" + str(email) + "' is not a UofT email address.")
        
class NameForm(FlaskForm):
    password    = StringField( 'Enter your Password', validators = [DataRequired()] )
    email       = StringField( 'Enter your Email Address', validators = [DataRequired(), validateEmail()] )
    submit      = SubmitField( 'Submit' )