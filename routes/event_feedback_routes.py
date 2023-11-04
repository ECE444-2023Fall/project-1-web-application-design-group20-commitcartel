from flask import request, Blueprint, jsonify
from database import update_one
from bson.objectid import ObjectId

event_feedback = Blueprint('event_feedback', __name__)

@event_feedback.route('/leave_event_feedback', methods=['POST'])
def leave_event_feedback():
    data = request.json  # TODO: Adapt implementation depending on frontend
    feedback_id = data['_id']
    event_id = data['event_id']
    user_id = data['user_id']
    rating = data['rating']
    comments = data['comments']
    print(feedback_id, event_id, user_id, rating, comments)

    # Add the event rating and comments to corresponding event                        
    success_events, result_events = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'event_rating': rating, 'event_comments': comments}})
    print(success_events, result_events)

    # Add the event rating and comments to Ratings
    success_ratings, result_ratings = update_one('Ratings', {'_id': ObjectId(feedback_id)}, {'$set': {'event_id': ObjectId(event_id), 'user_id': ObjectId(user_id), 'rating': rating, 'comments': comments}})
    print(success_ratings, result_ratings)

    if success_events and success_ratings:
        return jsonify({'message': result_events + " " + result_ratings})

    else:
        return jsonify({'error': result_events + " " + result_ratings}), 500
