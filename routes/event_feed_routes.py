from flask import request, Blueprint, jsonify, json, render_template, session
from database import get_data, get_data_one, update_one
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime

event_feed = Blueprint('event_feed', __name__)

# Events

def get_explore_feed(filter=None):
    # get most recent events
    success, result = get_data('Events', query={}, sort=[{"time", -1}])

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(result)}), 500

def get_following_feed(user_id, filter=None):

    # Get clubs user follows
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'following_clubs': 1})
    clubs = [item for item in data['following_clubs']]

    if not success:
        return jsonify({'error': str(clubs)}), 500

    # get events from all the club ids
    success, results = get_data('Events', {'club_id': {'$in': clubs}}, {'event_rating': 1}, sort=[{"time", -1}])

    if success:
        return json.loads(json_util.dumps(results))
    else:
        return jsonify({'error': str(results)}), 500

def get_registered_feed(user_id, filter=None):
    # Get the list of the user's registered event IDs
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'registered_events': 1})
    data = [item for item in data['registered_events']]

    if not success:
        return jsonify({'error': str(data)}), 500
    
    # Get the list of the events from the event IDs
    success, results = get_data('Events', {'_id': {'$in': data}}, {'event_rating': 1})
    
    if success:
        return json.loads(json_util.dumps(results))
    
    else:
        return jsonify({'error': str(results)}), 500

@event_feed.route('/register_event', methods=['PATCH'])
def register_for_event():
    data = request.form
    event_id = data['event_id']
    user_id = data['user_id']
    print(f"Registering user {user_id} to event {event_id}")

    # Add user to the list of registered attendees for the given event
    success, result = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'attendees': ObjectId(user_id)}})
    _,result = get_data_one('Events', {'_id': ObjectId(event_id)})

    if not success:
        return jsonify({'error': str(result)}), 400

    # Add the event to the list of registered events for the user
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$addToSet': {'registered_events': ObjectId(event_id)}})

    #print(result['registered_events'])
    if success:
        return jsonify({'message': "registered successfully"})

    else:
        return jsonify({'error': result}), 500

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

def get_clubs(filter=None):
    # get most recent events
    success, result = get_data('Clubs', query={})

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(result)}), 500

def get_following_clubs(user_id, filter=None):

    # Get club ids user follows
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'following_clubs': 1})
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
    
    # Club data
    # TODO add imgs
    data['club_name'] = club['club_name']
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
    
    return render_template('view_event_user.html', data=data)
