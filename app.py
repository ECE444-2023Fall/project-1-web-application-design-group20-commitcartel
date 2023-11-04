from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
# import API routes
from routes.user_auth_routes import user_auth
from routes.event_feed_routes import event_feed
from routes.query_routes import query
from routes.event_feedback_routes import event_feedback

app = Flask(__name__)
app.config['SECRET_KEY'] = "hard to guess string"
app.register_blueprint(event_feed)
app.register_blueprint(query)
app.register_blueprint(event_feedback)

#Helper functions
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

@app.route('/')
def index():
    return render_template("homepage.html")