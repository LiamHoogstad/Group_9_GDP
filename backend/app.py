import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import re
from datetime import datetime
import bcrypt

app = Flask(__name__)
CORS(app)  

# Temporary hard-coded constants for development purposes only
#uri ='blah blah blah'

load_dotenv()
# Create a new client and connect to the server
client = MongoClient(os.getenv("DATABASE_URI"), server_api=ServerApi('1'))
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
    #check_signup(data, users_collection)
    email = data.get('email')
    password = data.get('password').encode("utf-8")
    username = data.get('username')
    dob = data.get('dateOfBirth')
        
    #check email validity
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'error': 'Invalid Email'})
    if users_collection.find_one({ 'email': email }) is not None:
        return jsonify({'error': 'Account Already Exists'})
    
    if users_collection.count_documents({ 'username': username }, limit = 1) != 0:
          return jsonify({'error': 'Username Taken'})
    
    try:
        date_obj = datetime.fromisoformat(dob[:-1])
    except ValueError:
        return jsonify({'error': 'Select a valid date'})

    #d_str=date_obj.strftime('%Y-%m-%d %H:%M:%S') #print(d_str)
    age = datetime.now() - date_obj
    years = age.days // 365
    # Check if the age is over 16
    if (years <= 16):
        return jsonify({'error': 'Must be 16 or over to sign up'})
    

    #all checks passed
    hashed = bcrypt.hashpw(password,bcrypt.gensalt())
    data['password']=hashed

    # insert the date into the DB
    result = users_collection.insert_one(data)
    
    # Success message if data was transferred successfully
    return jsonify({"success": True, "id": str(result.inserted_id)})
       





if __name__ == '__main__':
    app.run(debug=True)
