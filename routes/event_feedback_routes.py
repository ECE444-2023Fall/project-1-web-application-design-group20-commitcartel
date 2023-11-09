from flask import request, Blueprint, jsonify
from database import update_one
from bson.objectid import ObjectId

event_feedback = Blueprint('event_feedback', __name__)

@event_feedback.route('/leave_event_feedback', methods=['POST'])
def leave_event_feedback():
    data = request.json  # TODO: Adapt implementation depending on frontend
    event_id = data['event_id']
    feedback_id = ObjectId()
    
    event_object = {
        'event_feedback_id': str(feedback_id),
        'user_id': data['user_id'],
        'rating': data['rating'],
        'comments': data['comments'],
    }

    # Add the event rating and comments to corresponding event                        
    success_events, result_events = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'event_ratings': event_object}})

    if success_events:
        return jsonify({'message': result_events})

    else:
        return jsonify({'error': result_events}), 500
