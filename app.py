from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, widgets, DateField
from wtforms.validators import DataRequired, ValidationError, Optional

from flask_bootstrap import Bootstrap
from flask_moment import Moment
from markupsafe import Markup
from datetime import datetime
from bson import Timestamp

# import API routes
from routes.user_auth_routes import user_auth
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

# Custom Validators
class validateEmail(object):
    def __call__(self, form, field):
        email = field.data
        if '@' not in email:

            raise ValidationError("Please include an '@' in the email address. '" + str(email) + "' is missing an '@'")
        elif '@' in email and "utoronto" not in email:

            raise ValidationError("Please include a valid UofT email address. '" + str(email) + "' is not a UofT email address.")

class validateRange(object):
    def __call__(self, form, field):
        if form.start_date.data is not None and field.data is not None and field.data < form.start_date.data:
            raise ValidationError("End date must not be earlier than start date.") 
              
# Custom Forms
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
    categories = MultiCheckboxField('Categories', choices= ['AI', 'World', 'Tech', 'Design Team'])
    submit      = SubmitField('Submit')
    
class EventFilterForm(FlaskForm):
    search = StringField('Enter search query')
    categories = MultiCheckboxField('Categories', choices=['Arts', 'Competitions', 'Community', 'Culinary', 'Educational', 'Fundraiser', 'Information', 'Networking', 'Sports', 'Other'])
    start_date = DateField('Start Date', validators=[Optional()])
    end_date = DateField('End Date', validators=[validateRange(), Optional()])
    submit      = SubmitField('Submit')


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
    type = request.args.get('type')

    if form.validate_on_submit():
        filter_data = {}
        date_query = {}

        # Search
        if form.search.data is not None:
            filter_data['name'] = {
                '$regex': form.search.data, 
                '$options': 'i'
            }

        # Categories    
        if len(form.categories.data):
            filter_data['categories'] = {"$in": form.categories.data}

        # Date
        # Start date
        if form.start_date.data is not None:
            start_timestamp = datetime.strptime(form.start_date.data, "%Y-%m-%d").timestamp()
            date_query['$gte'] = start_timestamp

        # End date
        if form.end_date.data is not None:
            end_timestamp = datetime.strptime(form.end_date.data, "%Y-%m-%d").timestamp()
            date_query['$lte'] = end_timestamp

        if date_query != {}:
            filter_data['time'] = date_query

        session['filter'] = filter_data
        session['search'] = form.search.data
        session['categories'] = form.categories.data
        session['start_date'] = form.start_date.data
        session['end_date'] = form.end_date.data

        print(filter_data)
        
        return redirect(url_for('events', type=type))

    form.search.data = session['search']
    form.categories.data = session['categories']
    form.start_date.data = session['start_date']
    form.end_date.data = session['end_date']

    if type == 'following':
        events = get_following_events(session['user_id'], session['filter'])

    elif type == 'explore':
        events = get_explore_events(session['filter'])

    elif type == 'registered':
        events = get_registered_events(session['user_id'], session['filter'])

    else:
        return "Error"
    
    print(events)
    events = fix_events_format(events)
    
    # Reset the filter
    session['filter'] = {}

    return render_template('events.html', form=form, events=events, type=type)

if __name__ == '__main__':
    app.run(debug=True)