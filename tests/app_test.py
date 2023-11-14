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
