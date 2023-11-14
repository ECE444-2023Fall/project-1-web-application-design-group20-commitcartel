import pytest
import json
from pathlib import Path
from app import app
from database import db_client, insert_one, update_one, get_data_one, get_data, delete_one

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent
    with app.app_context():
        yield app.test_client() # tests run here

@pytest.fixture
def db():
    # Empty out the DB
    db_client['Test'].delete_many()
    yield db


def test_insert_one():
    # Sample data
    data = {'Name': 'Test', 'program': 'Test Program'}

    # Insert test user
    response = insert_one('Test', data)

    # Check if the response is correct
    assert response[0] == True

def test_update_one():
    # Sample data
    insert_data = {'Name': 'Test2', 'program': 'Test Program 2'}
    insert_one('Test', insert_data)

    data = {'$set': {'program': 'New Program'}}

    # Update the previously created user
    response = update_one('Test', {'Name': 'Test2'}, data)

    # Check if the response is correct
    assert response == (True, "Update Successful")

def test_get_data_one():
    insert_data = {'Name': 'Test3', 'program': 'Test Program 3'}
    insert_one('Test', insert_data)

    # Get the previously created user
    response = get_data_one('Test', {'Name': 'Test3'})

    # Remove the object ID from response
    del response[1]['_id']
    
    # Check if the response is correct
    assert response == (True, {'Name': 'Test3', 'program': 'Test Program 3'})

def test_delete_one():
    insert_data = {'Name': 'Test4', 'program': 'Test Program 4'}
    insert_one('Test', insert_data)

    # Delete the previously created user
    response = delete_one('Test', {'Name': 'Test4'})

    # Check if the response is correct
    assert response == (True, "Delete Successful")


# # Ismail Bennani
# def test_make_account(client):
#     # Create a sample post data as a dictionary
#     post_data = {"title": "Test Post", "content": "This is a test post."}

#     # Send a POST request to the /make_post route with the sample post data
#     response = client.post('/make_post', json=post_data)

#     # Check if the response status code is 200 (OK)
#     assert response.status_code == 200

#     # Parse the response as JSON
#     response_data = json.loads(response.data)

#     # Check if the response contains the expected message
#     assert response_data["message"] == "Post created successfully"



# # Adrian Chow
# def test_search_events_with_user_input(client, user_search_string):
#     response = client.post('/search', data={'query': user_search_string})

#     # Check if the response contains the search string
#     assert user_search_string.encode() in response.data

#     # Parse the response as JSON
#     response_data = json.loads(response.data)

#     # Check if the response is a list of events that contain the user's input string
#     # This assumes that the database will use "name" as a var that holds each Event's name
#     for event in response_data:
#         assert user_search_string in event['name']


# # Navidur Rahman
# def test_delete_event(client, event_id):
#     # Ensure the event is being deleted by sending a DELETE request
#     response = client.delete("/event_post/1")

#     # Check if the response status code is 200 (OK)
#     assert response.status_code == 200

#     # Parse the response as JSON
#     response_data = json.loads(response.data)

#     # Check if the response contains the expected message
#     assert response_data["message"] == "Post deleted successfully"


# # Ismail Bennani
# def test_make_post(client):
#     # Create a sample post data as a dictionary
#     post_data = {"title": "Test Post", "content": "This is a test post."}

#     # Send a POST request to the /make_post route with the sample post data
#     response = client.post('/make_post', json=post_data)

#     # Check if the response status code is 200 (OK)
#     assert response.status_code == 200

#     # Parse the response as JSON
#     response_data = json.loads(response.data)

#     # Check if the response contains the expected message
#     assert response_data["message"] == "Post created successfully"


# # Arafat Syed Shah
# def test_latest_events(client):
#     # Send a GET request to the /latest_events endpoint
#     response = client.get('/latest_events')

#     # Check if the response status code is 200, indicating success
#     assert response.status_code == 200

#     # Parse the response as JSON
#     response_data = json.loads(response.data)

#     # Check if the response_data is a list
#     assert isinstance(response_data, list)

#     # check that given events are in order of date
#     for i in range(1, len(response_data)):
#         current_event = response_data[i]
#         previous_event = response_data[i - 1]
        
#         assert 'date' in current_event
#         assert 'date' in previous_event
#         assert current_event['date'] >= previous_event['date']


# # Kavya Kadi
# def test_following_feed(client):
# 	# Send a GET request to obtain following feed from the /following_feed route
# 	response = client.get('/following_feed')

# 	# Check if the response status is 200, ensuring it is OK
# 	assert response.status_code == 200

# 	# Parse the response as JSON
# 	response_data = json.loads(response.data)

# 	# Check if the response is a list
# 	assert isinstance(response_data, list)

# 	# Check if the response corresponds to the user’s followed clubs
# 	for event in response_data:
# 		assert "club_id" in event
# 		assert club_followed(event["club_id"])
        

# # Mahiliny Santhirakumar
# def test_search_clubs_with_user_input(client, user_search_string):
#     #This test is for the club page search bar to ensure output contains search string

#     response = client.post('/club_search', data={'query': user_search_string})

#     # Check if the response contains the search string
#     assert user_search_string.encode() in response.data

#     # Parse the response as JSON
#     response_data = json.loads(response.data)

#     # Check if the response is a list of club pages that contain the user's input string
#     for club in response_data:
#         assert user_search_string in club['name']
