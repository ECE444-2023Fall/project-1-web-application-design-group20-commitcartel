from flask import Blueprint, request, jsonify, json
from database import get_data
from bson import json_util

query = Blueprint('query', __name__)

@query.route("/search-event", methods=['GET'])
def search_events():
    data = request.args  # [adrian] TODO: change implementation when front end is developed
    query_string = data.get('query')
    query = {"name": {"$regex": query_string, "$options": "i"}}

    # Search the event database
    success, result = get_data('Events', query)

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(results)}), 500

@query.route("/search-club", methods=['GET'])
def search_clubs():
    data = request.args  # [adrian] TODO: change implementation when front end is developed
    query_string = data.get('query')
    query = {"name": {"$regex": query_string, "$options": "i"}}

    # Search the clubs database
    success, result = get_data('Clubs', query)

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(results)}), 500