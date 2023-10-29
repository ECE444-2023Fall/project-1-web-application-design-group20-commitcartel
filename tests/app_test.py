import pytest
import json

@pytest.fixture
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