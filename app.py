from flask import Flask, render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError

from flask_bootstrap import Bootstrap
from flask_moment import Moment

# import API routes
from routes.user_auth_routes import user_auth
from routes.event_feed_routes import event_feed
from routes.club_pg_routes import club_pg
from routes.query_routes import query
from routes.user_account_routes import user_account

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = "hard to guess string"
app.register_blueprint(event_feed)
app.register_blueprint(club_pg)
app.register_blueprint(query)
app.register_blueprint(user_auth)
app.register_blueprint(user_account)


bootstrap = Bootstrap(app)
moment  = Moment(app)

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

@app.route('/following')
def following():
    return render_template('following.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

if __name__ == '__main__':
    app.run()