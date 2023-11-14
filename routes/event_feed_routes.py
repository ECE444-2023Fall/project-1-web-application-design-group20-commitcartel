from flask import request, Blueprint, jsonify, json, render_template, session, redirect, url_for, flash
from database import get_data, get_data_one, update_one
from flask_wtf import FlaskForm
from wtforms import SubmitField
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime

event_feed = Blueprint('event_feed', __name__)

class RegisterForEvent(FlaskForm):
    register           = SubmitField('Register')

class UnRegisterForEvent(FlaskForm):
    unregister         = SubmitField('Unregister')

club_cats = {
    'academic': 'Academic',
    'arts_culture': 'Arts/Culture',
    'community_service': 'Community Service',
    'environment_sustainability': 'Environment',
    'health_wellness': 'Health/Wellness',
    'hobby_special_interest': 'Hobby',
    'leadership': 'Leadership',
    'misc': 'Miscellaneous',
    'sports_athletics': 'Sports/Athletics',
    'technology_innovation': 'Technology'
}

event_cats = {
    'arts': 'Arts',
    'competition': 'Competitions',
    'community': 'Community',
    'culinary': 'Culinary',
    'educational': 'Educational',
    'fundraiser': 'Fundraiser',
    'information': 'Information',
    'networking': 'Networking',
    'sports': 'Sports',
    'other': 'Other'
}

# Events
def fix_events_format(events):
    current_time = datetime.now()
    for event in events:
        event['id'] = event['_id']['$oid']
        if "time" not in event:
            continue

        timestamp = datetime.strptime(event['time']['$date'], "%Y-%m-%dT%H:%M:%SZ")
        event['date_formatted'] = timestamp.strftime("%B %d, %Y")
        event['time_formatted'] = timestamp.strftime("%I:%M %p")
        res, club_info = get_data_one('Clubs', {'_id': ObjectId(event['club_id']['$oid'])}, {'name': 1, 'photo': 1})
        if(res):
            event['club_name'] = club_info['name']
            event['club_img'] = club_info['photo']
        if('description' in event and len(event['description'])>300):
            event['description'] = event['description'][:300] + "..."
       
        event['completed'] = timestamp<=current_time
        
        for i in range(len(event['categories'])):
            event['categories'][i] = event_cats[event['categories'][i]]
    return events

def fix_clubs_format(clubs):

    for club in clubs:
        club['id'] = club['_id']['$oid']
        if('description' in club and len(club['description'])>300):
            club['description'] = club['description'][:300] + "..."
        club['category'] = club_cats[club['category']]
    return clubs

# Events
def get_explore_events(filter=None):
    # Get most recent events
    success, result = get_data('Events', filter=filter, sort=[("time", -1)])

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(result)}), 500


def get_following_events(user_id, filter={}):
    # Get the list of clubs that user follows
    user_selected_filter = {'_id': ObjectId(user_id)}

    success, data = get_data_one('Users', filter=user_selected_filter, projection={'following_clubs': 1})

    if not success:
        return jsonify({'error': str(data)}), 500
    
    if data is None:
        return []

    followed_clubs = [item for item in data['following_clubs']]

    # Filtered followed clubs' events
    filtered_events = {'club_id': {'$in': followed_clubs}}

    # Apply the category and time filters if applicable
    if 'categories' in filter:
        filtered_events['categories'] = filter['categories']
    
    if 'time' in filter:
        filtered_events['time'] = filter['time']
    
    # Get events from all the club ids
    success, results = get_data('Events', filter = filtered_events, sort=[("time", -1)])
   
    if success:
        return json.loads(json_util.dumps(results))
    else:
        return jsonify({'error': str(results)}), 500

def get_registered_events(user_id, filter={}):
    # Get the list of the user's registered event IDs
    user_selected_filter = {'_id': ObjectId(user_id)}

    success, data = get_data_one('Users', filter=user_selected_filter, projection={'registered_events': 1})

    if not success:
        return jsonify({'error': str(data)}), 500
    
    registered_events = [item for item in data['registered_events']]

    # Filter that fetches events
    filtered_events = {'_id': {'$in': registered_events}}

    # Apply the category and time filters if applicable
    if 'categories' in filter:
        filtered_events['categories'] = filter['categories']
    
    if 'time' in filter:
        filtered_events['time'] = filter['time']
    
    # Get the list of the events from the event IDs
    success, results = get_data('Events', filter = filtered_events, sort=[("time", -1)])
    
    if success:
        return json.loads(json_util.dumps(results))
    
    else:
        return jsonify({'error': str(results)}), 500

def unregister_from_event(user_id, event_id):
    print(f"Unregistering user {user_id} from event {event_id}")

    # Remove user from the list of registered attendees for the given event
    success, result = update_one('Events', {'_id': ObjectId(event_id)}, {'$pull': {'attendees': ObjectId(user_id)}})

    if not success:
        return False, result

    # Remove the event from the list of registered events for the user
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$pull': {'registered_events': ObjectId(event_id)}})

    if success:
        return True, result
    else:
        return False, result

def register_for_event(user_id, event_id):
    print(f"Registering user {user_id} to event {event_id}")

    # Add user to the list of registered attendees for the given event
    success, result = update_one('Events', {'_id': ObjectId(event_id)}, {'$addToSet': {'attendees': ObjectId(user_id)}})

    if not success:
        return False, result

    # Add the event to the list of registered events for the user
    success, result = update_one('Users', {'_id': ObjectId(user_id)}, {'$addToSet': {'registered_events': ObjectId(event_id)}})

    if success:
        return True, result

    else:
        return False, result

def is_user_registered(user_id, event_id):
    # determine if user is registered for this event
    success, data = get_data_one('Users', {'_id': ObjectId(user_id)}, {'registered_events': 1})
    if success:
        return ObjectId(event_id) in data['registered_events']
    
    return False

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
def get_explore_clubs(filter=None):
    # Get clubs
    success, result = get_data('Clubs', filter=filter)

    if success:
        return json.loads(json_util.dumps(result))
    else:
        return jsonify({'error': str(result)}), 500


def get_following_clubs(user_id, filter={}):
    # Get club ids user follows
    filter['_id'] = ObjectId(user_id)

    success, data = get_data_one('Users', filter=filter, projection={'following_clubs': 1})
    
    if not success:
        return jsonify({'error': str(data)}), 500
    
    if data is None:
        return {}
    
    clubs = [item for item in data['following_clubs']]

    # Get clubs from all the club ids
    success, results = get_data('Clubs', {'_id': {'$in': clubs}})
    
    if success:
        return json.loads(json_util.dumps(results))
    else:
        return jsonify({'error': str(results)}), 500


@event_feed.route('/events/<event_id>', methods=['GET', 'POST'])
def view_event_user(event_id):
    register_form = RegisterForEvent()
    unregister_form = UnRegisterForEvent()

    success_1, event = get_data_one('Events', {'_id': ObjectId(event_id)})
    if not success_1:
        return "<h1> Error </h1>"
    
    success_2, club = get_data_one('Clubs', {'_id': ObjectId(event['club_id'])})
    if not success_2:
        return "Error"

    # determine if a event has already passed
    current_time = datetime.utcnow()
    timestamp = event['time']
    event_completed = timestamp <= current_time
    
    is_registered = is_user_registered(session['user_id'], str(event['_id']))
    
    data = {
        'event_name': event['name'],
        'event_description': event['description'],
        'num_attending': len(event['attendees']),
        'categories': event['categories'],
        'date': timestamp.strftime("%B %d, %Y"),
        'time': timestamp.strftime("%I:%M %p"),
        'location': event['location'],
        'completed': event_completed,
        'is_user': session['is_user'],
        'event_id': str(event['_id']),
        'user_id': str(session['user_id']),
        'is_registered': is_registered,
        'club_name': club['name'],
        'club_id': str(club['_id']),
        'club_img': club['photo'],
    }

    if event_completed:
        # get all reviews of event
        reviews = []
        for review in event['event_ratings']:
            success, user_data = get_data_one('Users', {'_id': ObjectId(review['user_id'])}, {'name': 1})

            if success:
                review_obj = {
                    'name': review.get('name', "Anonymous"),
                    'rating': int(review['rating']),
                    'comment': review['comments']
                }

                reviews.append(review_obj)        
        
        # get event rating average
        data['event_rating_avg'] = int(event['event_rating_avg'])
        data['reviews'] = reviews
    
    if request.method == 'POST':
        if is_registered:
            success,_ = unregister_from_event(str(session['user_id']), str(event['_id']))
            if success:
                flash("Succesfully unregistered for the event")
                return redirect(url_for('event_feed.view_event_user', event_id=data['event_id'])) 
        else:
            success,_ = register_for_event(str(session['user_id']), str(event['_id']))
            if success:
                flash("Succesfully registered for the event!")
                return redirect(url_for('event_feed.view_event_user', event_id=data['event_id']))  

    if is_registered:
        return render_template('view_event_user.html', data=data, form=unregister_form, is_user=session['is_user'], name=session['name'])
    else:
        return render_template('view_event_user.html', data=data, form=register_form, is_user=session['is_user'], name=session['name'])
