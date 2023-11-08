from flask import Blueprint, request, jsonify
import bcrypt
from database import insert_one, get_data_one

user_auth = Blueprint('user_auth', __name__)

@user_auth.route('/register', methods=['POST'])
def register_user():
    data = request.json

    # Validate input data
    required_fields = ["email", "password", "name", "is_user"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing '{field}' in request data"}), 400

    # Check if UofT Email
    if "utoronto" not in data["email"]:
        return jsonify({"error": "Email not a UofT email"}), 400

    # Check if the user already exists based on email (you might want to use a unique index in MongoDB)
    _, existing_user = get_data_one("Users", {"email": data["email"]})
    if existing_user:
        return jsonify({"error": "Email is already registered"}), 400

    # Hash the user's password
    hashed_password = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())

    # Convert "is_user" to a boolean
    is_user = data["is_user"].lower() == "true" if isinstance(data["is_user"], str) else bool(data["is_user"])

    # Create a user document
    user = {
        "email": data["email"],
        "password": hashed_password,
        "name": data["name"],
        "is_user": is_user,
        "registered_events": [],
        "following_clubs": [],
        "filters_events": [],
        "filters_clubs": [],
        "program": data.get("program", ""),
        "year": data.get("year", "")
    }

    # Insert the user document into MongoDB
    inserted_user = insert_one("Users", user)
    if inserted_user is False:
        return jsonify({"error": "Failed to register user"}), 400

    return jsonify({"message": "User registered successfully"}), 201

@user_auth.route('/login', methods=['POST'])
def login():
    data = request.json

    # Validate input dataa
    required_fields = ["email", "password"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing '{field}' in request data"}), 400

    # Check if the user exists based on email
    success, user_data = get_data_one("Users", {"email": data["email"]}, {'_id': 1, 'email': 1, 'password': 1, "is_user": 1, 'name': 1})

    if not success or not user_data:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Compare the hashed password
    stored_password = user_data["password"]
    if bcrypt.checkpw(data["password"].encode('utf-8'), stored_password):
        # Passwords match; user is authenticated
        response_data = {
            "message": "Login successful",
            "user_id": str(user_data["_id"]),
            "email": user_data["email"],
            "is_user": user_data.get("is_user", ""),
            "name": user_data.get("name", "")
        }
        return jsonify(response_data), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401
