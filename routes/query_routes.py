from flask import Blueprint, request, jsonify
from database import get_data_from_search

query = Blueprint('query', __name__)

@query.route("/search", methods=['GET'])
def search_event_and_club():
    # Use request.args to get query string from URL
    data = request.args  # [adrian] TODO: change implementation when front end is developed
    query_string = data.get('query')

    # Search the event database
    event_results = search_events(query_string)

    # Search the clubs database
    club_results = search_clubs(query_string)

    results = {
        "event_results": event_results,
        "club_results": club_results
    }

    return jsonify(results)

def search_events(query_string):
    query = {"name": {"$regex": query_string, "$options": "i"}}

    # Search the event database
    query_result = get_data_from_search('Events', query)

    return query_result

def search_clubs(query_string):
    query = {"club_name": {"$regex": query_string, "$options": "i"}}

    # Search the clubs database
    query_result = get_data_from_search('Clubs', query)

    return query_result