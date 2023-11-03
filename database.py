from pymongo.mongo_client import MongoClient
from pymongo.errors import *
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
def get_data(collection_name, query):
    try:
        collection = db_client[collection_name]
        result = collection.find(query)
        return list(result)
    
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, "Failed to get data")

def update_one(collection_name, query, update):
    try:
        collection = db_client[collection_name]
        result = collection.update_one(query, update)

        if result.modified_count > 0:
            return (True, "Update Successful")
        else:
            return (False, "No matching documents found")
        
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, "Failed to update data")
    
def insert_one(collection_name, query):
    try:
        collection = db_client[collection_name]
        result = collection.insert_one(query)
        result_id = result.inserted_id
        return (result_id)
    
    except PyMongoError as e:
        print(f"Database error: {str(e)}")
        return (False, "Failed to insert data")