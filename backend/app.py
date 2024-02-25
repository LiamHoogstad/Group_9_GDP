import os
import io
import binascii
from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from bson.objectid import ObjectId
from gridfs import GridFSBucket
from datetime import timedelta

# Initialize Flask app
app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)

# Generate a random secret key for JWT
def generate_secret_key():
    return binascii.hexlify(os.urandom(32)).decode()

app.config['JWT_SECRET_KEY'] = generate_secret_key()
jwt = JWTManager(app)

# Load environment variables
load_dotenv()

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"), server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.MusiCollab
users_collection = db.users 
grid_fs_bucket = GridFSBucket(db)

# Routes
@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        grid_fs_bucket.upload_from_stream(file.filename, file)
        return 'File Uploaded'

@app.route('/checkEmail', methods=['POST'])
def check_email():
    data = request.json
    email = data.get('email')
    email_exists = users_collection.find_one({'email': email})
    if email_exists:
        return jsonify({'isAvailable': False, 'message': 'Email is already taken.'})
    return jsonify({'isAvailable': True, 'message': 'Email is available.'})

@app.route('/checkEmailForLogin', methods=['POST'])
def check_email_for_login():
    data = request.json
    email = data.get('email')
    email_exists = users_collection.find_one({'email': email})
    if email_exists:
        return jsonify({'exists': True, 'message': 'Email exists.'})
    return jsonify({'exists': False, 'message': 'No account found with that email.'})

@app.route('/validatePasswordForLogin', methods=['POST'])
def validate_password():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = users_collection.find_one({'email': email})
    if user and bcrypt.check_password_hash(user['password'], password):
        return jsonify({'isValid': True, 'message': 'Password is correct.'})
    return jsonify({'isValid': False, 'message': 'Incorrect password.'})

@app.route('/checkUsername', methods=['POST'])
def check_username():
    data = request.json
    username = data.get('username')
    user_exists = users_collection.find_one({'username': username})
    if user_exists:
        return jsonify({'isAvailable': False, 'message': 'Username is already taken.'})
    return jsonify({'isAvailable': True, 'message': 'Username is available.'})

@app.route('/submit', methods=['POST'])
def submit_form():
    data = request.json
    email = data.get('email')
    password = bcrypt.generate_password_hash(data.get('password').encode("utf-8")).decode('utf-8')
    username = data.get('username')
    dob = data.get('dateOfBirth')
    user_data = {'email': email, 'username': username, 'password': password, 'dateOfBirth': dob, 'profilePicture': None, 'projects': []}
    result = users_collection.insert_one(user_data)
    user = users_collection.find_one({'email': email})
    access_token = create_access_token(identity=str(user["_id"]), expires_delta=timedelta(hours=1))
    return jsonify({"success": True, "id": str(result.inserted_id), "access_token": access_token})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = users_collection.find_one({'email': email})
    if user and bcrypt.check_password_hash(user['password'], password):
        
        access_token = create_access_token(identity=str(user["_id"]), expires_delta=timedelta(hours=1))
        return jsonify({"successful": True, "access_token": access_token})
    return jsonify({"successful": False})


@app.route('/uploadProfilePicture', methods=['POST'])
@jwt_required()
def upload_profile_picture():
    current_user_id = get_jwt_identity()
    user = users_collection.find_one({"_id": ObjectId(current_user_id)})
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if user and file:
        
        content_type = file.content_type
        file_id = grid_fs_bucket.upload_from_stream(
            file.filename, file, metadata={"content_type": content_type, "user_id": current_user_id})
        
        users_collection.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': {'profilePicture': file_id}}
        )
        return jsonify({'message': 'File Uploaded', 'file_id': str(file_id)}), 200
    return jsonify({'message': 'User not found'}), 404

@app.route('/profilePicture/<user_id>', methods=['GET'])
def get_profile_picture(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user and user.get('profilePicture'):
        grid_out = grid_fs_bucket.open_download_stream(ObjectId(user['profilePicture']))
        response = send_file(
            io.BytesIO(grid_out.read()),
            mimetype='image/jpeg'  
        )
        return response
    return jsonify({'message': 'No profile picture found'}), 404

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    print("CURRENT USER "+current_user_id)
    user = users_collection.find_one({"_id": ObjectId(current_user_id)})
    if user:
        return jsonify(username=user.get('username')), 200
    return jsonify(message="User not found"), 404

@app.route('/addProject', methods=['POST'])
@jwt_required()
def add_project():
    current_user_id = get_jwt_identity()
    data = request.json
    project = {
        'id': data.get('id'),
        'title': data.get('title'),
        'description': data.get('description')
    }
    
    users_collection.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$push": {"projects": project}}
    )
    
    return jsonify({"success": True, "message": "Project added successfully"})

@app.route('/getProjects', methods=['GET'])
@jwt_required()
def get_projects():
    current_user_id = get_jwt_identity()
    user = users_collection.find_one({"_id": ObjectId(current_user_id)}, {'projects': 1})
    if user:
        return jsonify(user.get('projects', [])), 200
    else:
        return jsonify({"message": "User not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
