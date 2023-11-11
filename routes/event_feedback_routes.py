from flask import request, Blueprint, jsonify
from database import update_one, get_data_one
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
        success1, current_event = get_data_one('Events', {'_id': ObjectId(event_id)})
    
    # Add the event rating average to corresponding event
    if success1 and current_event:
        event_ratings = [int(rating['rating']) for rating in current_event['event_ratings']]
        
        if event_ratings:
            avg_rating = sum(event_ratings)/len(event_ratings)
        else:
            avg_rating = 0

        success_avg_rating, result_avg_rating = update_one('Events', {'_id': ObjectId(event_id)}, {'$set': {'event_rating_avg': avg_rating}})

        if success_avg_rating:
            return jsonify({'message': result_events})
        else:
            return jsonify({'error': result_avg_rating}), 500
    else:
        return jsonify({'error': result_events}), 500
