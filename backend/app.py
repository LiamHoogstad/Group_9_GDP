import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)
CORS(app)  

# Temporary hard-coded constants for development purposes only
uri = 'blah blah blah'

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    db = client.MusiCollab  
    users_collection = db.users  

    # insert the date into the DB
    result = users_collection.insert_one(data)
    
    # Success message if data was transferred successfully
    return jsonify({"success": True, "id": str(result.inserted_id)})

if __name__ == '__main__':
    app.run(debug=True)
