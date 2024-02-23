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

@@ -16,7 +15,7 @@

load_dotenv()
# Create a new client and connect to the server
client = MongoClient(os.getenv("DATABASE_URI"), server_api=ServerApi('1'))
client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
@@ -29,42 +28,76 @@
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

@@ -75,7 +108,20 @@ def submit_form():
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


@app.route('/upload', methods=['POST'])
def audio_upload():
    data = request.json
    if data:
        audio = data.get('audio')
        audioFile = base64.b64decode(audio)
        user = 1234

        if audio and user:
            db = client.MusiCollab
            audio_collection = db.audiofiles
            result = audio_collection.insert_one({
                'id': user,
                'audio': audioFile
            })
            return jsonify({"success": True, "id": str(result.inserted_id)})
        else:
            return jsonify({'error': 'Wrong data'}), 422
    else:
        return jsonify({'error': 'No files received'}), 422


@app.route('/audio_files/<user_id>', methods=['GET'])
def get_audio_files(user_id):
    db = client.MusiCollab
    audio_collection = db.audio_files

    # hard coded
    id = 1234

    # get all the audio files belonging to the specified user
    audio_files = audio_collection.find({'id': id})

    audio_list = []
    for audio_file in audio_files:
        audio_list.append({
            'audio_id': str(audio_file['_id']),
            'audio_data': audio_file['audio_data']
        })

    return jsonify(audio_list)


if __name__ == '__main__':
    app.run(debug=True)
