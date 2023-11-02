from flask import request, Blueprint, jsonify
from database import update_one
from bson.objectid import ObjectId

event_feed = Blueprint('event_feed', __name__)

@event_feed.route('/explore_feed', methods=['GET'])
def get_explore_feed():
    #TODO
    return "a json object of current events to explore"

@event_feed.route('/following_feed', methods=['GET'])
def get_following_feed():
    #TODO
    return "a json object of current events from users following"

@event_feed.route('/favourite_event', methods=['POST'])
def update_favourite_event(event_id):
    #TODO
    return "append the event to the favourite list of user"

@event_feed.route('/register_event', methods=['PATCH'])
def register_for_event():
    data = request.form
    event_id = data['event_id']
    user_id = data['user_id']
    print(event_id, user_id)

    # Add user to the list of registered attendees for the given event
    success1, result1 = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'attendees': ObjectId(user_id)}})
    print(success1, result1)

    # Add the event to the list of registered events for the user
    success2, result2 = update_one('Users', {'_id': ObjectId(user_id)}, {'$addToSet': {'registered_events': ObjectId(user_id)}})
    print(success1, result2)

    if success1 and success2:
        return jsonify({'message': result1 + " " + result2})

    else:
        return jsonify({'error': result1 + " " + result2}), 500