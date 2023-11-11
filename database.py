from pymongo.mongo_client import MongoClient
from pymongo.errors import *
from bson.timestamp import Timestamp
import certifi

# Connect to MongoDB
uri = "mongodb+srv://admin_user:admin@campusconnect.mlzgisz.mongodb.net/?retryWrites=true&w=majority"
try:
    client = MongoClient(uri, tlsCAFile=certifi.where())
    db_client = client['CampusConnect']
    print("Connected to database")
  
# return a friendly error if a URI error is thrown 
except ConfigurationError:
    print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")

# Database wrapper functions for all database related tasks
# Add in other wrappers as we need them

# Get multiple documents
def get_data(collection_name, filter=None, projection=None, sort=None):
    try:
        collection = db_client[collection_name]
        result = collection.find(filter, projection, sort=sort)

        return (True, list(result))

    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, e)

# Get one document
def get_data_one(collection_name, filter=None, projection=None):
    try:
        collection = db_client[collection_name]
        result = collection.find_one(filter, projection)

        return (True, result)

    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, e)

# Update one document
def update_one(collection_name, filter, update):
    try:
        collection = db_client[collection_name]
        result = collection.update_one(filter, update)

        if result.modified_count > 0:
            return (True, "Update Successful")
        else:
            return (False, "No matching documents found")
        
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, e)


def delete_one(collection_name, filter):
    try:
        collection = db_client[collection_name]
        result = collection.delete_one(filter)

        if result.deleted_count > 0:
            return (True, "Delete Successful")
        else:
            return (False, "No matching documents found")
        
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, str(e))


def insert_one(collection_name, data):
    try:
        collection = db_client[collection_name]
        result = collection.insert_one(data)

        if result.inserted_id:
            return (True, result.inserted_id)
        else:
            return (False, "Failed to insert document")

    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, e)
