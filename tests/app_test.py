import pytest
import json
from pathlib import Path
from app import app

@pytest.fixture
def client():
    BASE_DIR = Path(__file__).resolve().parent.parent

    with app.app_context():
        yield app.test_client() # tests run here


def test_search_events_with_user_input(client, user_search_string):
    response = client.post('/search', data={'query': user_search_string})

    # Check if the response contains the search string
    assert user_search_string.encode() in response.data

    # Parse the response as JSON
    response_data = json.loads(response.data)

    # Check if the response is a list of events that contain the user's input string
    # This assumes that the database will use "name" as a var that holds each Event's name
    for event in response_data:
        assert user_search_string in event['name']


def test_delete_event(client, event_id):
    # Ensure the event is being deleted
    rv = client.delete("/event_post/1")
    assert rv.status_code == 200