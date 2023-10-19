from flask import Blueprint

event_feed = Blueprint('event_feed', __name__)

@event_feed.route('/explore_feed', methods = ['GET'])
def get_explore_feed():
    #TODO
    return "a json object of current events to explore"

@event_feed.route('/following_feed', methods = ['GET'])
def get_following_feed():
    #TODO
    return "a json object of current events from users following"

@event_feed.route('/favourite_event', methods = ['POST'])
def update_favourite_event():
    #TODO
    return "append the event to the favourite list of user"