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
from pydub import AudioSegment
from werkzeug.utils import secure_filename

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

@app.route('/fetchUsername/<user_id>', methods=['GET'])
def fetch_Username(user_id):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if user:
        projects_serializable = []
        for project in user.get('projects', []):
            project_modified = project.copy()
            if 'audioFileId' in project:
                project_modified['audioFileId'] = str(project['audioFileId'])
            projects_serializable.append(project_modified)

    return jsonify(username=user.get('username'), projects=projects_serializable), 200

@app.route('/addProject', methods=['POST'])
@jwt_required()
def add_project():
    current_user_id = get_jwt_identity()
    data = request.json
    project = {
        'id': data.get('id'),
        'title': data.get('title'),
        'description': data.get('description'),
        'genre': data.get('genre'),
    }
    
    users_collection.update_one(
        {"_id": ObjectId(current_user_id)},
        {"$push": {"projects": project}}
    )
    
    return jsonify({"success": True, "message": "Project added successfully"})

@app.route('/getProjects/<user_id>', methods=['GET'])
def get_projects(user_id):
    print("SMELLY BUM BUM")
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {'projects': 1})
    if user and 'projects' in user:
        return jsonify(user['projects']), 200
    else:
        return jsonify({"message": "User not found or no projects available"}), 404


@app.route('/uploadAudioToProject', methods=['POST'])
@jwt_required()
def upload_audio_to_project():
    current_user_id = get_jwt_identity()
    project_title = request.form['title']

    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    user = users_collection.find_one({"_id": ObjectId(current_user_id)})
    if user:
        filename = secure_filename(file.filename)
        content_type = file.content_type

        project = next((project for project in user.get('projects', []) if project['title'] == project_title), None)
        if project and 'audioFileId' in project:
            old_file_id = project['audioFileId']
            grid_fs_bucket.delete(ObjectId(old_file_id))

        file_id = grid_fs_bucket.upload_from_stream(filename, file, metadata={"content_type": content_type, "user_id": current_user_id})

        result = users_collection.update_one(
            {'_id': ObjectId(current_user_id), 'projects.title': project_title},
            {'$set': {'projects.$.audioFilename': filename, 'projects.$.audioFileId': file_id}}
        )

        if result.modified_count:
            return jsonify({'message': 'Audio file uploaded and linked to project', 'file_id': str(file_id)}), 200
        else:
            return jsonify({'message': 'Project not found or update failed'}), 400

    return jsonify({'message': 'User not found'}), 404

# New Audio function that loads audio from database and loads a local audio file, streaming them together.
@app.route('/getAudio/<user_id>/<project_title>/<startPointStr>', methods=['GET'])
def get_audio(user_id, project_title, startPointStr):

    startPoint = int(startPointStr)

    user = users_collection.find_one({"_id": ObjectId(user_id), "projects.title": project_title})
    if user:
        project = next((p for p in user.get('projects', []) if p['title'] == project_title), None)
        if project and 'audioFileId' in project:
            # Retrieve audio from MongoDB
            grid_out = grid_fs_bucket.open_download_stream(ObjectId(project['audioFileId']))
            db_audio = AudioSegment.from_file(io.BytesIO(grid_out.read()))

            # Load the local file
            # Replace path to audio file with your own path to audio file
            local_audio_path = '/Users/liamhoogstad/Desktop/College/SWENG/Group_9_GDP/frontend/assets/Super Mario Theme.mp3'
            local_audio = AudioSegment.from_mp3(local_audio_path)

            # Adjust local audio volume to 60% of the database audio file
            # This is a simple approximation; adjust dB reduction as needed
            local_audio = local_audio - 25  # Reducing volume by 5 dB

            # Ensure both audio segments are at the same frame rate
            if db_audio.frame_rate != local_audio.frame_rate:
                local_audio = local_audio.set_frame_rate(db_audio.frame_rate)

            # Mix the audio files
            mixed_audio = db_audio.overlay(local_audio, position=0)

            # Trim the mixed audio to start from the specified startPoint
            if startPoint > 0:
                mixed_audio = mixed_audio[startPoint:]

            # Convert the mixed audio to bytes for streaming
            mixed_audio_bytes = io.BytesIO()
            mixed_audio.export(mixed_audio_bytes, format="mp3")
            mixed_audio_bytes.seek(0)  # Reset the pointer to the start of the bytes object

            # Stream the mixed audio to the client
            return send_file(
                mixed_audio_bytes,
                mimetype="audio/mp3",
                as_attachment=True,
                download_name="mixed_audio.mp3"
            )
    return jsonify({'message': 'Project or audio file not found'}), 404


""" ------------------------- Old Audio Retrieving Function: ----------------------- """
""" @app.route('/getAudio/<user_id>/<project_title>', methods=['GET'])
def get_audio(user_id,project_title):
    user = users_collection.find_one({"_id": ObjectId(user_id), "projects.title": project_title})
    print(user)
    if user:
        project = next((p for p in user.get('projects', []) if p['title'] == project_title), None)
        if project and 'audioFileId' in project:
            grid_out = grid_fs_bucket.open_download_stream(ObjectId(project['audioFileId']))
            response = send_file(
                io.BytesIO(grid_out.read()),
                mimetype='audio/mpeg',
            )
            return response
    return jsonify({'message': 'Project or audio file not found'}), 404 """

@app.route('/getAudioFilename/<user_id>/<project_title>', methods=['GET'])
def get_audio_filename(user_id, project_title):
    user = users_collection.find_one({"_id": ObjectId(user_id), "projects.title": project_title})
    if user:
        project = next((p for p in user.get('projects', []) if p['title'] == project_title), None)
        if project and 'audioFilename' in project:
            return jsonify({'audioFilename': project['audioFilename']})
    return jsonify({'message': 'Project or audio filename not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
