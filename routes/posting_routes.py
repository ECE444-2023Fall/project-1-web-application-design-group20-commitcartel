# Import the necessary libraries
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for, request
from database import get_data, get_data_one, update_one, insert_one, delete_one
from bson import ObjectId, json_util, Timestamp
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField, DateField, TimeField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms import widgets
from datetime import datetime
from markupsafe import Markup
# Create a Blueprint
posting = Blueprint('posting', __name__)


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

class CreateEventForm(FlaskForm):
    event_name      = StringField('Event Name')
    event_date      = DateField('Event Date')
    event_start_time = TimeField('Event Start Time')
    location        = StringField('Location')
    event_category = MultiCheckboxField('Event Category', choices=[
        ('academic', 'Academic'),
        ('arts', 'Arts'),
        ('athletics_recreation', 'Athletics and Recreation'),
        ('community_service', 'Community Service'),
        ('culture_identities', 'Culture and Identities'),
        ('environment_sustainability', 'Environment and Sustainability'),
        ('global_interests', 'Global Interests'),
        ('hobby_leisure', 'Hobby and Leisure'),
        ('leadership', 'Leadership'),
        ('media', 'Media'),
        ('politics', 'Politics'),
        ('social', 'Social'),
        ('social_justice_advocacy', 'Social Justice and Advocacy'),
        ('spirituality_faith_communities', 'Spirituality and Faith Communities'),
        ('student_governments_councils_unions', 'Student Governments, Councils, and Unions'),
        ('work_career_development', 'Work and Career Development')
    ])
    description     = TextAreaField('Description')
    submit          = SubmitField('Create Event')


@posting.route('/create_event', methods=['GET', 'POST'])
def create_event():
    form = CreateEventForm()
    if not session.get('club_id', False) or session.get('is_user', True):
        return redirect(url_for('user_auth.login'))

    if form.validate_on_submit():
        datetime_str = f"{form.event_date.data} {form.event_start_time.data}"
        timestamp = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").timestamp()
        club_id = session['club_id']
        event_object = {
            'name': form.event_name.data,
            'time': Timestamp(int(timestamp), 0),
            'attendees': [],
            'category': form.event_category.data,
            'club_id': ObjectId(club_id), # should be session.get('club_id') when login is merged
            'description': form.description.data,
            'location': form.location.data,
            'event_ratings': [],
            'event_rating_avg': 0.0
        }

        # add to events
        success, id = insert_one('Events', event_object)
        if not success:
            return redirect(url_for('posting.create_event'))
        
        # append events array for club
        success, count = update_one('Clubs', {'_id': ObjectId(club_id)}, {'$addToSet': {'events': ObjectId(id)}}) # club_id should be session['club_id']
        if not success:
            return redirect(url_for('posting.create_event'))
    
        return redirect(url_for('club_pg.club_event_view', club_id=str(club_id), event_id=str(id))) # club_id should be session['club_id']
    return render_template('create_event.html', form=form)

# Route to create a new post (POST request)
@posting.route('/event_post', methods=['POST'])
def create_post():
    # Get data from the request
    data = request.json  # Assuming the data is sent as JSON

    # Insert the post data into the database
    success, post_id = insert_post(data)

    if success:
        return jsonify({"message": "Post created successfully", "post_id": str(post_id)})
    else:
        return jsonify({"error": "Failed to create the post"}, 500)

# Function to validate data against the schema
def validate_data(data):
    required_keys = [
        "name",
        "time",
        "category",
        "club_id",
    ]

    # Check if all required keys are present
    for key in required_keys:
        if key not in data:
            return False, f"Missing key: {key}"

    # Initialize the attendees and event_rating fields if they don't exist
    if "attendees" not in data:
        data["attendees"] = []

    if "event_rating" not in data:
        data["event_rating"] = []

    # Initialize the event_rating_avg field if it doesn't exist
    if "event_rating_avg" not in data:
        data["event_rating_avg"] = -1

    # Additional validation checks can be added here

    return True, "Data is consistent with the schema"

# Function to insert a post into the database with initialized fields
def insert_post(data):
    # Validate the data
    is_valid, validation_message = validate_data(data)
    if not is_valid:
        return False, validation_message

    result = insert_one("Events", data)
    return True, result.inserted_id


# Route to get/delete a post (GET or DELETE request)
@posting.route('/event_post/<post_id>', methods=['GET', 'DELETE'])
def get_or_delete_post(post_id):
    # Find the post with the specified ID in the database
    post = get_data_one('Events', {"_id": ObjectId(post_id)})

    if post is None:
        return jsonify({"error": "Post not found"}, 404)

    if request.method == 'GET':
        # Return the post data as JSON
        return json.loads(json_util.dumps(post))
    
    elif request.method == "DELETE":
        # Delete the post from the database
        success, message = delete_one('Events', {"_id": ObjectId(post_id)})
        if success:
            return jsonify({"message": "Post deleted successfully"})
        else:
            return jsonify({"error": message}, 500)
