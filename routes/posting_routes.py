# Import the necessary libraries
from flask import Blueprint, request, jsonify, json
from database import get_data, get_data_one, update_one, get_mongo_database, insert_one, delete_one
from bson import ObjectId, json_util

# Create a Blueprint
posting = Blueprint('posting', __name__)

# Route to create a new post (POST request)
@posting.route('/event_post', methods=['POST'])
def create_post():
    # Get data from the request
    data = request.json  # Assuming the data is sent as JSON

    # Insert the post data into the database
    success, post_id = insert_post(data)

    if success:
        return jsonify({"message": "Post created successfully", "post_id": str(post_id)})
    else:
        return jsonify({"error": "Failed to create the post"}, 500)

# Function to validate data against the schema
def validate_data(data):
    required_keys = [
        "name",
        "time",
        "category",
        "club_id",
    ]

    # Check if all required keys are present
    for key in required_keys:
        if key not in data:
            return False, f"Missing key: {key}"

    # Initialize the attendees and event_rating fields if they don't exist
    if "attendees" not in data:
        data["attendees"] = []

    if "event_rating" not in data:
        data["event_rating"] = []

    # Initialize the event_rating_avg field if it doesn't exist
    if "event_rating_avg" not in data:
        data["event_rating_avg"] = -1

    # Additional validation checks can be added here

    return True, "Data is consistent with the schema"

# Function to insert a post into the database with initialized fields
def insert_post(data):
    # Validate the data
    is_valid, validation_message = validate_data(data)
    if not is_valid:
        return False, validation_message

    result = insert_one("Events", data)
    return True, result.inserted_id


# Route to get/delete a post (GET or DELETE request)
@posting.route('/event_post/<post_id>', methods=['GET', 'DELETE'])
def get_or_delete_post(post_id):
    print("hello")
    # Find the post with the specified ID in the database
    post = get_data_one('Events', {"_id": ObjectId(post_id)})

    if post is None:
        return jsonify({"error": "Post not found"}, 404)

    if request.method == "GET":
        # Return the post data as JSON
        return json.loads(json_util.dumps(post))
    
    elif request.method == "DELETE":
        # Delete the post from the database
        success, message = delete_post(ObjectId(post_id))
        if success:
            return jsonify({"message": "Post deleted successfully"})
        else:
            return jsonify({"error": message}, 500)

# Function to delete a post from the database
def delete_post(post_id):

    result = delete_one("Events", {"_id": post_id})

    if result.deleted_count > 0:
        return True, "Post deleted successfully"
    else:
        return False, "No matching documents found"

