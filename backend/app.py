import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import bcrypt


app = Flask(__name__)
CORS(app)  

# Temporary hard-coded constants for development purposes only
#uri ='blah blah blah'

load_dotenv()
# Create a new client and connect to the server
client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/checkEmail', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email')
    db = client.MusiCollab
    users_collection = db.users

    email_exists = users_collection.find_one({'email': email})

    if email_exists:
        return jsonify({'isAvailable': False, 'message': 'Email is already taken.'})
    else:
        return jsonify({'isAvailable': True, 'message': 'Email is available.'})
    

@app.route('/checkEmailForLogin', methods=['POST'])
def check_email_for_login():
    data = request.json
    email = data.get('email')
    db = client.MusiCollab
    users_collection = db.users

    email_exists = users_collection.find_one({'email': email})

    if email_exists:
        return jsonify({'exists': True, 'message': 'Email exists.'})
    else:
        return jsonify({'exists': False, 'message': 'No account found with that email.'})

@app.route('/validatePasswordForLogin', methods=['POST'])
def validate_password():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    db = client.MusiCollab
    users_collection = db.users

    user = users_collection.find_one({'email': email})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'isValid': True, 'message': 'Password is correct.'})
    else:
        return jsonify({'isValid': False, 'message': 'Incorrect password.'})

@app.route('/checkUsername', methods=['POST'])
def check_username():
    data = request.json
    username = data.get('username')
    db = client.MusiCollab
    users_collection = db.users

    user_exists = users_collection.find_one({'username': username})

    if user_exists:
        return jsonify({'isAvailable': False, 'message': 'Username is already taken.'})
    else:
        return jsonify({'isAvailable': True, 'message': 'Username is available.'})
    

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json

    db = client.MusiCollab  
    users_collection = db.users  
    email = data.get('email')
    password = data.get('password').encode("utf-8")
    username = data.get('username')
    dob = data.get('dateOfBirth')

    hashed = bcrypt.hashpw(password,bcrypt.gensalt())
    data['password']=hashed

    # insert the date into the DB
    result = users_collection.insert_one(data)
    
    # Success message if data was transferred successfully
    return jsonify({"success": True, "id": str(result.inserted_id)})
       

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    db = client.MusiCollab
    users_collection = db.users

    user = users_collection.find_one({'email': email})

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):  # No need to encode user['password']
        return jsonify({"successful": True})
    else:
        return jsonify({"successful": False})



if __name__ == '__main__':
    app.run(debug=True)
