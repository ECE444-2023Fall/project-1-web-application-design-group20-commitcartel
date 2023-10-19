from pymongo.mongo_client import MongoClient
from pymongo.errors import *
import certifi

#Connect to MongoDB
uri = "mongodb+srv://admin_user:admin@campusconnect.mlzgisz.mongodb.net/?retryWrites=true&w=majority"
try:
    client = MongoClient(uri, tlsCAFile=certifi.where())
    print("connected")
  
# return a friendly error if a URI error is thrown 
except ConfigurationError:
    print("An Invalid URI host error was received. Is your Atlas host name correct in your connection string?")

db = client.TestDB
collection = db.TestGuy

doc = [{"1": "A", "Bob":"Alice"}, {"2": "B", "Hobo": "Bobo"}, {"1": 2}]

try: 
    result = collection.insert_many(doc)
    print("inserted doc")

# return a friendly error if the operation fails
except OperationFailure:
    print("An authentication error was received. Are you sure your database user is authorized to perform write operations?")