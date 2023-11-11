from flask import request, Blueprint, jsonify, json, render_template, session, redirect, url_for, flash
from database import get_data, get_data_one, update_one
from flask_wtf import FlaskForm
from wtforms import SubmitField
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime

event_feed = Blueprint('event_feed', __name__)


class RegisterForEvent(FlaskForm):
    register           = SubmitField('Register')

class UnRegisterForEvent(FlaskForm):
    unregister         = SubmitField('Unregister')

def get_explore_events(filter={}, search_string=None):
    # Get most recent events
    if search_string:
        filter["name"] = {"$regex": search_string, "$options": "i"}

    success, result = get_data('Events', filter=filter, sort=[{"time", -1}])

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(result)}), 500


def get_following_events(user_id, filter={}, search_string=None):
    # Get clubs user follows
    filter['_id'] = ObjectId(user_id)

    if search_string:
        filter["name"] = {"$regex": search_string, "$options": "i"}
    
    success, data = get_data_one('Users', filter=filter, projection={'following_clubs': 1})
    clubs = [item for item in data['following_clubs']]

    if not success:
        return jsonify({'error': str(clubs)}), 500

    # get events from all the club ids
    success, results = get_data('Events', {'club_id': {'$in': clubs}}, {'event_rating': 1}, sort=[{"time", -1}])

    if success:
        return json.loads(json_util.dumps(results))
    else:
        return jsonify({'error': str(results)}), 500


def get_registered_events(user_id, filter={}, search_string=None):
    # Get the list of the user's registered event IDs
    filter['_id'] = ObjectId(user_id)

    if search_string:
        filter["name"] = {"$regex": search_string, "$options": "i"}

    success, data = get_data_one('Users', filter=filter, projection={'registered_events': 1})
    data = [item for item in data['registered_events']]

    if not success:
        return jsonify({'error': str(data)}), 500
    
    # Get the list of the events from the event IDs
    success, results = get_data('Events', {'_id': {'$in': data}}, {'event_rating': 1})
    
    if success:
        return json.loads(json_util.dumps(results))
    
    else:
        return jsonify({'error': str(results)}), 500

def unregister_from_event(user_id, event_id):
    print(f"Unregistering user {user_id} from event {event_id}")

    # Remove user from the list of registered attendees for the given event
    success, result = update_one('Events', {'_id': ObjectId(event_id)}, {'$pull': {'attendees': ObjectId(user_id)}})

    if not success:
        return False, result

    # Remove the event from the list of registered events for the user
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$pull': {'registered_events': ObjectId(event_id)}})

    if success:
        return True, result
    else:
        return False, result

def register_for_event(user_id, event_id):
    print(f"Registering user {user_id} to event {event_id}")

    # Add user to the list of registered attendees for the given event
    success, result = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'attendees': ObjectId(user_id)}})

    if not success:
        return False, result

    # Add the event to the list of registered events for the user
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$addToSet': {'registered_events': ObjectId(event_id)}})

    if success:
        return True, result

    else:
        return False, result

def is_user_registered(user_id, event_id):
    # determine if user is registered for this event
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'registered_events': 1})
    if success:
        return ObjectId(event_id) in data['registered_events']
    
    return False

@event_feed.route('/event_attendees/<event_id>', methods=['GET'])
def get_event_attendees(event_id):
    # Get the list of the event's registered user IDs
    success, data = get_data_one('Events', {'_id': ObjectId(event_id)}, {'attendees': 1})
    data = [item for item in data['attendees']]

    if not success:
        return jsonify({'error': str(data)}), 500

    # Get the list of users from the user IDs
    success, results = get_data('Users', {'_id': {'$in': data}})

    if success:
        return json.loads(json_util.dumps(results))
    
    else:
        return jsonify({'error': str(results)}), 500
    
# Clubs
def get_explore_clubs(filter={}, search_string=None):
    # Get clubs
    if search_string:
        filter["name"] = {"$regex": search_string, "$options": "i"}

    success, result = get_data('Clubs', filter=filter)

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(result)}), 500


def get_following_clubs(user_id, filter={}, search_string=""):
    # Get club ids user follows
    filter['_id'] = ObjectId(user_id)

    if search_string:
        filter["name"] = {"$regex": search_string, "$options": "i"}

    success, data = get_data_one('Users', filter=filter, projection={'following_clubs': 1})
    clubs = [item for item in data['following_clubs']]

    if not success:
        return jsonify({'error': str(data)}), 500

    # Get clubs from all the club ids
    success, results = get_data('Clubs', {'club_id': {'$in': clubs}})

    if success:
        return json.loads(json_util.dumps(results))
    else:
        return jsonify({'error': str(results)}), 500

@event_feed.route('/events/<event_id>', methods=['GET', 'POST'])
def view_event_user(event_id):
    register_form = RegisterForEvent()
    unregister_form = UnRegisterForEvent()

    success_1, event = get_data_one('Events', {'_id': ObjectId(event_id)})
    if not success_1:
        return "<h1> Error </h1>"
    
    success_2, club = get_data_one('Clubs', {'_id': ObjectId(event['club_id'])})
    if not success_2:
        return "Error"

    # determine if a event has already passed
    current_time = datetime.utcnow()
    timestamp = datetime.fromtimestamp(event['time'].time)
    event_completed = timestamp <= current_time
    
    is_registered = is_user_registered(session['user_id'], str(event['_id']))
    data = {}
    # Event data
    data['event_name'] = event['name']
    data['event_description'] = event['description']
    data['num_attending'] = len(event['attendees'])
    data['date'] = timestamp.strftime("%B %d, %Y")
    data['time'] = timestamp.strftime("%I:%M %p")
    data['location'] = event['location']
    data['completed'] = event_completed
    data['is_user'] = session['is_user']
    data['event_id'] = str(event['_id'])
    data['user_id'] = str(session['user_id'])
    data['is_registered'] = is_registered

    # Club data
    # TODO add imgs
    data['club_name'] = club['name']
    data['club_id'] = str(club['_id'])

    if event_completed:
        # get all reviews of event
        reviews = []
        for review in event['event_ratings']:
            success, user_data = get_data_one('Users', {'_id': ObjectId(review['user_id'])}, {'name': 1})

            if success:
                review_obj = {
                    'name': user_data.get('name', "N/A"),
                    'rating': int(review['rating']),
                    'comment': review['comments']
                }

                reviews.append(review_obj)        
        
        # get event rating average
        data['event_rating_avg'] = int(event['event_rating_avg'])
        data['reviews'] = reviews
    
    if request.method == 'POST':
        if is_registered:
            success,_ = unregister_from_event(str(session['user_id']), str(event['_id']))
            if success:
                return redirect(url_for('event_feed.view_event_user', event_id=data['event_id'])) 
        else:
            success,_ = register_for_event(str(session['user_id']), str(event['_id']))
            if success:
                return redirect(url_for('event_feed.view_event_user', event_id=data['event_id']))  

    if is_registered:
        return render_template('view_event_user.html', data=data, form=unregister_form)
    else:
        return render_template('view_event_user.html', data=data, form=register_form)
