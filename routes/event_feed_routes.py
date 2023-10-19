from flask import Blueprint

event_feed = Blueprint('event_feed', __name__)

@event_feed.route('/explore_feed')
def create_explore_feed():
    #TODO
    return "a json object of current events to explore"

@event_feed.route('/following_feed')
def create_following_feed():
    #TODO
    return "a json object of current events from users following"

@event_feed.route('/favourite_event')
def create_following_feed():
    #TODO
    return "append the event to the favourite list of user"