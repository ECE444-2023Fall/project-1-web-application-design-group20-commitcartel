from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, ValidationError

from flask_bootstrap import Bootstrap
from flask_moment import Moment

# import API routes
from routes.user_auth_routes import user_auth
from routes.event_feed_routes import event_feed, get_explore_events, get_following_events, get_registered_events, get_explore_clubs, get_following_clubs
from routes.club_pg_routes import club_pg
from routes.event_feedback_routes import event_feedback
from routes.user_account_routes import user_account

from routes.posting_routes import posting

app = Flask(__name__, static_folder='static')

app.config['SECRET_KEY'] = "hard to guess string"
app.register_blueprint(event_feed)
app.register_blueprint(club_pg)
app.register_blueprint(event_feedback)
app.register_blueprint(posting)
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
        
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ClubFilterForm(FlaskForm):
    search = StringField('Enter search query', validators = [DataRequired()])
    category = MultiCheckboxField('Category', choices= ['AI', 'World', 'Tech', 'Design Team'])
    submit      = SubmitField('Submit')
class EventFilterForm(FlaskForm):
    search = StringField('Enter search query', validators = [DataRequired()])
    category = MultiCheckboxField('Category', choices= ['Fundraising', 'Kickoff', 'Fun', 'Idk what else to put'])
    submit      = SubmitField('Submit')

@app.route('/')
def index():
    return render_template("homepage.html")

@app.route('/clubs', methods=['GET', 'POST'])
def following():
    form = ClubFilterForm()

    if form.validate_on_submit():
        session['search'] = form.search
        session['category'] = form.category

        return redirect(url_for('following'))

    type = request.args.get('type')

    if type == 'following':
        clubs = get_following_clubs("65409591870327a571edea4a")

    elif type == 'explore':
        clubs = get_explore_clubs()

    else:
        return "Error"

    session['query'] = {}

    return render_template('clubs.html', form=form, clubs=clubs, type=type)

@app.route('/events', methods=['GET', 'POST'])
def events():
    form = EventFilterForm()

    if form.validate_on_submit():
        session['search'] = form.search
        session['category'] = form.category
    
        return redirect(url_for('following'))

    type = request.args.get('type')

    if type == 'following':
        events = get_following_events("65409591870327a571edea4a")

    elif type == 'explore':
        events = get_explore_events()

    elif type == 'registered':
        events = get_registered_events("65409591870327a571edea4a")

    else:
        return "Error"

    session['query'] = {}

    return render_template('events.html', form=form, events=events, type=type)

if __name__ == '__main__':
    app.run(debug=True)