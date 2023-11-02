from flask import Blueprint, request, jsonify

# Create a Blueprint
posting = Blueprint('posting', __name__)

# Route to create a new post (POST request)
@posting.route('/event_post', methods=['POST'])
def create_post():
    # Get data from the request
    data = request.json  # Assuming the data is sent as JSON

    # Process and store the post data (e.g., save it in a database)
    # Example: You can save the post data to a database
    # Replace this with your database interaction code
    # db.save_post(data)

    # Return a response
    return jsonify({"message": "Post created successfully"})

# Route to get/delete a post (DELETE request)
@posting.route('/event_post/<post_id>', methods=['GET', 'DELETE'])
def get_or_delete_post(post_id):
    # Retrieve the post with the specified ID from the database
    # Example: You can fetch the post from a database
    # Replace this with your database interaction code
    # post_id = db.get_post(post_id)

    # Check if the post exists
    if post_id is None:
        return jsonify({"error": "Post not found"}, 404)

    if request.method == "GET":
        # Return the post data as JSON
        return jsonify(post_id)
    
    elif request.method == "DELETE":
        return ""
