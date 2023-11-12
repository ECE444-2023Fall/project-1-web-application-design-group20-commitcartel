from flask import Flask, render_template, session, redirect, url_for, flash, request, g
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, widgets, DateField
from wtforms.validators import DataRequired, ValidationError

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from markupsafe import Markup
from database import get_data_one
from bson.objectid import ObjectId
# import API routes
from routes.user_auth_routes import user_auth

#get_explore_feed, get_following_feed, get_registered_feed, get_clubs,
from routes.event_feed_routes import event_feed, get_explore_events, get_following_events, get_registered_events, get_explore_clubs, get_following_clubs, fix_events_format

from routes.club_pg_routes import club_pg
from routes.event_feedback_routes import event_feedback
from routes.user_account_routes import user_account

from routes.posting_routes import posting

from route_permissions import ALLOWED_ROUTES  # Import the ALLOWED_ROUTES object

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
        
class BootstrapListWidget(widgets.ListWidget):

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        html = [f"<{self.html_tag} {widgets.html_params(**kwargs)}>"]
        for subfield in field:
            if self.prefix_label:
                html.append(f"<li class='list-group-item'>{subfield.label} {subfield(class_='form-check-input ms-1')}</li>")
            else:
                html.append(f"<li class='list-group-item'>{subfield(class_='form-check-input me-1')} {subfield.label}</li>")
        html.append("</%s>" % self.html_tag)
        return Markup("".join(html))

class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.
 
    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = BootstrapListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class ClubFilterForm(FlaskForm):
    search = StringField('Enter search query')
    category = MultiCheckboxField('Category', choices= ['AI', 'World', 'Tech', 'Design Team'])
    date = DateField('Date',format='%Y-%m-%d')
    submit      = SubmitField('Submit')
class EventFilterForm(FlaskForm):
    search = StringField('Enter search query')
    category = MultiCheckboxField('Category', choices= ['Fundraising', 'Kickoff', 'Fun', 'Idk what else to put'])
    date = DateField('Date',format='%Y-%m-%d')
    submit      = SubmitField('Submit')


def fetch_user_name(user_id):
    success, user_data = get_data_one("Users", {"_id": ObjectId(user_id)}, {'name': 1})

    if success and user_data:
        return user_data.get('name', 'Unknown User')
    return 'Unknown User'


def fetch_club_name(club_id):
    success, club_data = get_data_one("Clubs", {"_id": ObjectId(club_id)}, {'name': 1})

    if success and club_data:
        return club_data.get('name', 'Unknown Club')
    return 'Unknown Club'


def get_user_or_club_name():
    if 'is_user' in session and session['is_user']:
        # Fetch user name for user
        user_name = fetch_user_name(session['user_id'])
        return user_name
    elif 'is_user' in session and not session['is_user']:
        # Fetch club name for club
        club_name = fetch_club_name(session['club_id'])
        return club_name
    else:
        return None

@app.route('/')
def index():
    return render_template("homepage.html")

@app.before_request
def check_session():
    if (request.endpoint != 'static'):
        # Get the user type from the session
        user_type = 'anonymous'
        if session.get('is_user') is not None:
            if session.get('club_id') is not None and not session.get('is_user'):
                user_type = 'club'
            elif session.get('user_id') is not None:
                user_type = 'user'
            # Fetch user or club name based on the session
            user_or_club_name = get_user_or_club_name()
            # Make it available globally to all templates
            g.user_or_club_name = user_or_club_name

        # Check if the requested endpoint is allowed for the user type
        if request.endpoint not in ALLOWED_ROUTES[user_type]:
            if user_type == 'anonymous':
                return redirect(url_for('user_auth.login'))
            
            elif user_type == 'club':
                return redirect(url_for('club_pg.clubs', club_id = session['club_id']))
            
            elif user_type == 'user':
                return redirect(url_for('index'))

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
    
    events = fix_events_format(events)
    
    session['query'] = {}

    return render_template('events.html', form=form, events=events, type=type)

if __name__ == '__main__':
    app.run(debug=True)