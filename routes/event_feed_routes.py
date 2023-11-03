from flask import request, Blueprint, jsonify, json
from database import get_data, get_data_one, update_one
from bson.objectid import ObjectId
from bson import json_util

event_feed = Blueprint('event_feed', __name__)

@event_feed.route('/explore_feed', methods=['GET'])
def get_explore_feed():
    # get most recent events
    success, result = get_data('Events', query={}, sort=[{"time", -1}])

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(result)}), 500

@event_feed.route('/following_feed/<user_id>', methods=['GET'])
def get_following_feed(user_id):

    # Get clubs user follows
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'following_clubs': 1})
    clubs = [item for item in data['following_clubs']]

    if not success:
        return jsonify({'error': str(clubs)}), 500

    # get events from all the club ids
    success, results = get_data('Events', {'club_id': {'$in': clubs}}, sort=[{"time", -1}])

    if success:
        return json.loads(json_util.dumps(results))
    else:
        return jsonify({'error': str(results)}), 500

@event_feed.route('/registered_feed/<user_id>', methods=['GET'])
def get_registered_feed(user_id):
    # Get the list of the user's registered event IDs
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'registered_events': 1})
    data = [item for item in data['registered_events']]

    if not success:
        return jsonify({'error': str(data)}), 500
    
    # Get the list of the events from the event IDs
    success, results = get_data('Events', {'_id': {'$in': data}})
    
    if success:
        return json.loads(json_util.dumps(results))
    
    else:
        return jsonify({'error': str(results)}), 500

@event_feed.route('/favourite_event', methods=['POST'])
def update_favourite_event(event_id):
    #TODO
    return "append the event to the favourite list of user"

@event_feed.route('/register_event', methods=['PATCH'])
def register_for_event():
    data = request.form
    event_id = data['event_id']
    user_id = data['user_id']
    print(f"Registering user {user_id} to event {event_id}")

    # Add user to the list of registered attendees for the given event
    success, result = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'attendees': ObjectId(user_id)}})

    if not success:
        return jsonify({'error': str(result)})

    # Add the event to the list of registered events for the user
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$addToSet': {'registered_events': ObjectId(event_id)}})

    if success:
        return jsonify({'message': "registered successfully"})

    else:
        return jsonify({'error': result}), 500
