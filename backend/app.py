import os
import io
import binascii
from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from bson.objectid import ObjectId
from gridfs import GridFSBucket, NoFile
from datetime import timedelta
from werkzeug.utils import secure_filename
from datetime import datetime
from pydub import AudioSegment
from datetime import datetime
from math import log10

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

# used to delete projects from a specific user
if False:
    print("doing it")
    # result = users_collection.update_one({'username': "iluvemusic"}, {'$unset': {'projects': ''}})
    result = users_collection.update_one(
        {'username': "MrDemo123"},
        {'$pull': {'projects': {'title': '', 'description': ''}}}
    )
    # Check if the update was successful
    if result.modified_count > 0:
        print("All projects deleted successfully")
    else:
        print("User not found or no projects deleted")

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
    if isinstance(dob, str):
        try:
            dob = datetime.fromisoformat(dob)
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
    if isinstance(dob, datetime):
        dob = dob.isoformat()
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
            # Shallow copy of the project dictionary and ensure all ObjectIds are strings
            project_modified = {
                **project,
                'id': str(project['id']),  # Convert project id if it's an ObjectId
                'audioFiles': [
                    {
                        **audio_file,
                        'audioFileId': str(audio_file['audioFileId'])  # Convert audio file ids
                    } for audio_file in project.get('audioFiles', [])
                ],
            }

            # Convert combinedAudioId if it exists
            if 'combinedAudioId' in project:
                project_modified['combinedAudioId'] = str(project['combinedAudioId'])

            projects_serializable.append(project_modified)

        # User username and projects are now ready for JSON serialization
        return jsonify(username=user.get('username'), projects=projects_serializable), 200
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/addProject/<user_id>', methods=['POST'])
def add_project(user_id):
    data = request.json
    print(data.get('genres') == '')
    print(data.get('genres'))
    project = {
        'id': data.get('id'),
        'title': data.get('title'),
        'description': data.get('description'),
        'date': datetime.now(),
    }
    if data.get('genres') != '':
        project['genres'] = data.get('genres').split(',')
    if data.get('instruments') != '':
        project['instruments'] = data.get('instruments').split(',')
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"projects": project}}
    )
    return jsonify({"success": True, "message": "Project added successfully"})

@app.route('/getProjects/<user_id>', methods=['GET'])
def get_projects(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {'projects': 1})
    if user and 'projects' in user:
        return jsonify(user['projects']), 200
    else:
        return jsonify({"message": "User not found or no projects available"}), 404

from bson import ObjectId  # Make sure to import ObjectId from bson

@app.route('/getAllProjects', methods=['GET'])
def get_all_projects():
    all_projects = []
    # Query the database to retrieve all users and their projects
    for user in users_collection.find({}, {'projects': 1, 'username': 1}):
        if user:
            for project in user.get('projects', []):
                project_modified = project.copy()
                project_modified['user'] = user.get('username')
                # Convert ObjectId to string using the str function
                project_modified['userId'] = str(user['_id'])
                if 'audioFiles' in project:
                    del project_modified['audioFiles']
                if 'combinedAudioId' in project:
                    del project_modified['combinedAudioId']
                all_projects.append(project_modified)

    if all_projects:
        # print(all_projects)
        return jsonify(all_projects), 200
    else:
        return jsonify({"message": "No projects available"}), 404

    
@app.route('/uploadAudioToProject/<user_id>/<project_title>/<index>', methods=['POST'])
@jwt_required()
def upload_audio_to_project(user_id, project_title, index):
    current_user_id = get_jwt_identity()
    if str(current_user_id) != str(user_id):
        return jsonify({'message': 'Unauthorized'}), 403

    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    try:
        index = int(index)  # Convert index to integer
    except ValueError:
        return jsonify({'message': 'Invalid index provided'}), 400

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    project = next((p for p in user.get('projects', []) if p['title'] == project_title), None)
    if project is None:
        return jsonify({'message': 'Project not found'}), 404

    filename = secure_filename(file.filename)
    content_type = file.content_type

    # Replace or add new audio file
    if 0 <= index < len(project.get('audioFiles', [])):
        # Remove existing audio file from GridFS
        old_file_id = project['audioFiles'][index].get('audioFileId')
        if old_file_id:
            grid_fs_bucket.delete(ObjectId(old_file_id))

        # Upload new audio file to GridFS
        new_file_id = grid_fs_bucket.upload_from_stream(filename, file, metadata={"content_type": content_type, "user_id": user_id})

        # Update project document with new audio file ID
        users_collection.update_one(
            {'_id': ObjectId(user_id), 'projects.title': project_title},
            {'$set': {f'projects.$.audioFiles.{index}': {'audioFileId': new_file_id, 'audioFilename': filename}}}
        )
        return jsonify({'message': 'Audio file replaced and linked to project', 'file_id': str(new_file_id)}), 200
    else:
        # Append new audio file if index is at the end of the list
        new_file_id = grid_fs_bucket.upload_from_stream(filename, file, metadata={"content_type": content_type, "user_id": user_id})
        users_collection.update_one(
            {'_id': ObjectId(user_id), 'projects.title': project_title},
            {'$push': {f'projects.$.audioFiles': {'audioFileId': new_file_id, 
                        'audioFilename': filename, 'Mute': False,'Solo': False,
                            'Start_Position':0, 'Volumes': 75}}}
        )
        return jsonify({'message': 'Audio file added and linked to project', 'file_id': str(new_file_id)}), 200
    
@app.route('/getAudio/<user_id>/<project_title>', methods=['GET'])
def get_audio(user_id,project_title):
    user = users_collection.find_one({"_id": ObjectId(user_id), "projects.title": project_title})
    if user:
        project = next((p for p in user.get('projects', []) if p['title'] == project_title), None)
        if project and 'audioFileId' in project:
            grid_out = grid_fs_bucket.open_download_stream(ObjectId(project['audioFileId']))
            response = send_file(
                io.BytesIO(grid_out.read()),
                mimetype='audio/mpeg',
            )
            return response
    return jsonify({'message': 'Project or audio file not found'}), 404

@app.route('/getAudioFilename/<user_id>/<project_title>', methods=['GET'])
def get_audio_filename(user_id, project_title):
    user = users_collection.find_one({"_id": ObjectId(user_id), "projects.title": project_title})
    if user:
        project = next((p for p in user.get('projects', []) if p['title'] == project_title), None)
        if project and 'audioFilename' in project:
            return jsonify({'audioFilename': project['audioFilename']})
    return jsonify({'message': 'Project or audio filename not found'}), 404

@app.route('/getAudios/<user_id>/<project_title>', methods=['GET'])
def get_audios(user_id, project_title):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        project_title_decoded = project_title  
        project = next((project for project in user.get('projects', []) if project['title'] == project_title_decoded), None)
        if project:
            audio_files_serializable = []
            if 'audioFiles' in project:
                for audio_file in project['audioFiles']:
                    audio_file_copy = audio_file.copy()  
                    if 'audioFileId' in audio_file_copy and isinstance(audio_file_copy['audioFileId'], ObjectId):
                        audio_file_copy['audioFileId'] = str(audio_file_copy['audioFileId'])
                    audio_files_serializable.append(audio_file_copy)
            
            return jsonify(audio_files_serializable), 200
        else:
            return jsonify({'message': 'Project not found'}), 404
    return jsonify({'message': 'User not found'}), 404
    
@app.route('/streamAudio/<file_id>', methods=['GET'])
def stream_audio(file_id):
    try:
        file = grid_fs_bucket.open_download_stream(ObjectId(file_id))
        return send_file(
            io.BytesIO(file.read()),
            mimetype='audio/mpeg',
            as_attachment=False,
            download_name=file.filename
        )
    except NoFile:
        return jsonify({'message': 'File not found'}), 404





@app.route('/streamProjectCombinedAudio/<user_id>/<project_title>', methods=['GET'])
def stream_project_combined_audio(user_id, project_title):
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        project_title_decoded = project_title.replace("%20", " ")
        project = next((p for p in user.get('projects', []) if p['title'] == project_title_decoded), None)
        if project and 'combinedAudioId' in project:
            combined_audio_id = project['combinedAudioId']
            file = grid_fs_bucket.open_download_stream(ObjectId(combined_audio_id))
            return send_file(
                io.BytesIO(file.read()),
                mimetype='audio/mpeg',
                as_attachment=False
            )
        else:
            return jsonify({'message': 'Project or combined audio not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error streaming combined audio: ' + str(e)}), 500
    
# This function converts the volume level from 1 to 100 to decibels
def volume_to_decibels(volume_level):
    # Assuming volume_level 100 is 0 dB and 1 is -60 dB for example
    if volume_level == 100:
        return 0  # No change in volume
    else:
        # Convert the volume level to a decibel value
        # Here, we map volume level 1 to -60 dB and 100 to 0 dB
        return 20 * log10(volume_level / 100)

@app.route('/updateAudioVolume/<user_id>/<project_title>/<index>/<newVolume>', methods=['GET'])
def update_audio_volume(user_id, project_title, index, newVolume):

    print("MUAHAHAHHAHAHAHAAHAHA")

    try:
        # Convert index and newVolume to their appropriate types
        index = int(index)
        newVolume = int(newVolume)

        # Find the user by ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Decode the project title from URL encoding
        project_title_decoded = project_title.replace("%20", " ")
        project = next((proj for proj in user.get('projects', []) if proj['title'] == project_title_decoded), None)

        if not project:
            return jsonify({'message': 'Project not found'}), 404

        # Ensure the audio file index exists in the project
        if 'audioFiles' in project and len(project['audioFiles']) > index:
            # Update the volume of the specified audio file
            audio_files = project['audioFiles']
            audio_files[index]['Volumes'] = newVolume
            
            # Update the project in the database
            users_collection.update_one(
                {'_id': ObjectId(user_id), 'projects.title': project_title_decoded},
                {'$set': {'projects.$.audioFiles': audio_files}}
            )

            return jsonify({'message': 'Audio volume updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid audio file index'}), 404
    except ValueError:
        # Handle case where index or newVolume can't be converted to integers
        return jsonify({'message': 'Invalid input for index or volume'}), 400
    except Exception as e:
        # Catch-all for any other errors
        return jsonify({'message': str(e)}), 500
    

@app.route('/updateAudioPosition/<user_id>/<project_title>/<index>/<newPosition>', methods=['GET'])
def update_audio_position(user_id, project_title, index, newPosition):

    print("MUAHAHAHHAHAHAHAAHAHA   ---- Position")
    print("Index", index, "Start Position", newPosition)

    try:
        # Convert index and newVolume to their appropriate types

        print("MIDWAY 0 !")

        print(str.isdigit(index))
        print(str.isdigit(newPosition))

        #newPosition = newPosition.strip()

        print("MIDWAY 12312412")
        index = int(index)
        newPosition = int(float(newPosition))


        print("MIDWAY 1 !")

        # Find the user by ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        print("MIDWAY 2 !")

        # Decode the project title from URL encoding
        project_title_decoded = project_title.replace("%20", " ")
        project = next((proj for proj in user.get('projects', []) if proj['title'] == project_title_decoded), None)

        if not project:
            return jsonify({'message': 'Project not found'}), 404
        
        print("MIDWAY!")

        # Ensure the audio file index exists in the project
        if 'audioFiles' in project and len(project['audioFiles']) > index:
            # Update the volume of the specified audio file
            audio_files = project['audioFiles']
            audio_files[index]['Start_Position'] = newPosition
            
            # Update the project in the database
            users_collection.update_one(
                {'_id': ObjectId(user_id), 'projects.title': project_title_decoded},
                {'$set': {'projects.$.audioFiles': audio_files}}
            )

            return jsonify({'message': 'Audio position updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid audio file index'}), 404
    except ValueError:
        # Handle case where index or newVolume can't be converted to integers
        return jsonify({'message': 'Invalid input for index or track position'}), 400
    except Exception as e:
        # Catch-all for any other errors
        return jsonify({'message': str(e)}), 500
    

@app.route('/updateTrackMute/<user_id>/<project_title>/<index>', methods=['GET'])
def update_track_mute(user_id, project_title, index):

    print("::::::::::::::MUAHAHAHHAHAHAHAAHAHA::::::::::::::::")

    try:
        index = int(index)

        # Find the user by ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Decode the project title from URL encoding
        project_title_decoded = project_title.replace("%20", " ")
        project = next((proj for proj in user.get('projects', []) if proj['title'] == project_title_decoded), None)

        if not project:
            return jsonify({'message': 'Project not found'}), 404

        # Ensure the audio file index exists in the project
        if 'audioFiles' in project and len(project['audioFiles']) > index:
            # Update the mute status of the specified audio file
            audio_files = project['audioFiles']
            
            if 'Mute' in audio_files[index]:
                if audio_files[index]['Mute'] == True:
                    audio_files[index]['Mute'] = False
                else:
                    audio_files[index]['Mute'] = True
            else:
                # Handle the case where 'Mute' attribute does not exist
                # For example, you could initialize it here
                audio_files[index]['Mute'] = False # Or False, depending on your default

            
            # Update the project in the database
            users_collection.update_one(
                {'_id': ObjectId(user_id), 'projects.title': project_title_decoded},
                {'$set': {'projects.$.audioFiles': audio_files}}
            )

            return jsonify({'message': 'Audio volume updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid audio file index'}), 404
    except ValueError:
        # Handle case where index or newVolume can't be converted to integers
        return jsonify({'message': 'Invalid input for index or volume'}), 400
    except Exception as e:
        # Catch-all for any other errors
        return jsonify({'message': str(e)}), 500
    

@app.route('/updateTrackSolo/<user_id>/<project_title>/<index>', methods=['GET'])
def update_track_solo(user_id, project_title, index):

    print("SOLO :::::MUAHAHAHHAHAHAHAAHAHA::::::SOLOLOLOL:::::")

    try:
        print("Index:", index)
        index = int(index)
        print("SOLO :::::MUAHAHAHHAHAHAHAAHAHA::::::SOLOLOLOL::::: PART 2")
        # Find the user by ID
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Decode the project title from URL encoding
        project_title_decoded = project_title.replace("%20", " ")
        project = next((proj for proj in user.get('projects', []) if proj['title'] == project_title_decoded), None)

        if not project:
            return jsonify({'message': 'Project not found'}), 404

        # Ensure the audio file index exists in the project
        if 'audioFiles' in project and len(project['audioFiles']) > index:
            # Update the Solo status of the specified audio file
            audio_files = project['audioFiles']
            
            if 'Solo' in audio_files[index]:
                if audio_files[index]['Solo'] == True:
                    audio_files[index]['Solo'] = False
                else:
                    audio_files[index]['Solo'] = True
            else:
                # Handle the case where 'Solo' attribute does not exist
                # For example, you could initialize it here
                audio_files[index]['Solo'] = False # Or False, depending on your default

            
            # Update the project in the database
            users_collection.update_one(
                {'_id': ObjectId(user_id), 'projects.title': project_title_decoded},
                {'$set': {'projects.$.audioFiles': audio_files}}
            )

            return jsonify({'message': 'Audio volume updated successfully'}), 200
        else:
            return jsonify({'message': 'Invalid audio file index'}), 404
    except ValueError:
        # Handle case where index or newVolume can't be converted to integers
        return jsonify({'message': 'Invalid input for index or volume'}), 400
    except Exception as e:
        # Catch-all for any other errors
        return jsonify({'message': str(e)}), 500


@app.route('/streamProjectAudios/<user_id>/<project_title>', methods=['GET'])
def stream_project_audios(user_id, project_title):
    print("Processing combined audio files...")
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        project_title_decoded = project_title.replace("%20", " ")
        project = next((proj for proj in user.get('projects', []) if proj['title'] == project_title_decoded), None)

        isProjectSolo = False

        if project:
            if 'combinedAudioId' in project:
                try:
                    old_file_id = ObjectId(project['combinedAudioId'])
                    grid_fs_bucket.delete(old_file_id)
                    print(f"Deleted old combined audio file: {project['combinedAudioId']}")
                except Exception as e:
                    print(f"Error deleting old combined audio file: {e}")
            
            combined_audio = AudioSegment.silent(duration=300000)

            # Check if any audio file is set to Solo
            is_any_track_solo = any(audio_file.get('Solo', False) for audio_file in project.get('audioFiles', []))

            for audio_file in project.get('audioFiles', []):

                # Skip processing non-solo tracks if a solo track exists
                if is_any_track_solo and (audio_file.get('Solo', False) == False):
                    continue

                if 'audioFileId' in audio_file:
                    try:
                        file_id = ObjectId(audio_file['audioFileId'])
                        grid_out = grid_fs_bucket.open_download_stream(file_id)
                        audio_segment = AudioSegment.from_file(io.BytesIO(grid_out.read()), format="mp3")

                        print("Here is the mute status: ", audio_file['Mute'])
                        print("Here is the mute type: ", type(audio_file['Mute']))

                        audioOffset = int(audio_file['Start_Position'])
                        audioOffset = audioOffset * 1000
                        volume_adjustment = volume_to_decibels(audio_file['Volumes'])

                        if 'Mute' in audio_file:
                            
                            print("Mute is in the audio file: ", audio_file['audioFilename'] )
                            if audio_file['Mute'] == False:
                                audio_segment = audio_segment + volume_adjustment #((audio_file['Volumes']) - 100)
                                print("IT WAS FALSE!!")
                            elif audio_file['Mute'] == True:
                                audio_segment = audio_segment - 1000
                                print("IT WAS TRUE  !!!")
                            else:
                                print("SOmething went WRONG")
                        else:
                            print("Mute is NOT in the audio file: ", audio_file['audioFilename'] )
                            print("MUAHAHAHAHAIIIIIII")
                            audio_file['Mute'] = True
                            

                        combined_audio = combined_audio.overlay(audio_segment, position=audioOffset)
                    except Exception as e:
                        print(f"Error processinggggggggg file {audio_file['audioFileId']}: {e}")
                        continue

            buffer = io.BytesIO()
            combined_audio.export(buffer, format="mp3")
            buffer.seek(0)
            new_file_id = grid_fs_bucket.upload_from_stream(f"{project_title}_combined.mp3", buffer, metadata={"project_title": project_title, "user_id": user_id})

            users_collection.update_one(
                {'_id': ObjectId(user_id), 'projects.title': project_title_decoded},
                {'$set': {'projects.$.combinedAudioId': new_file_id}}
            )
            print(f"Updated project with new combined audio ID: {new_file_id}")

            buffer.seek(0)
            return send_file(
                buffer,
                mimetype='audio/mpeg',
                download_name=f"{project_title}_combined.mp3"  
            )
        else:
            return jsonify({'message': 'Project not found'}), 404
    return jsonify({'message': 'User not found'}), 404


@app.route('/deleteAudio/<user_id>/<audio_file_id>', methods=['DELETE'])
def delete_audio(user_id, audio_file_id):
    try:
        # Convert audio_file_id to ObjectId for MongoDB operations
        audio_file_object_id = ObjectId(audio_file_id)

        try:
            next_file = next(grid_fs_bucket.find({'_id': audio_file_object_id}), None)
            if next_file is None:
                return jsonify({'message': 'Audio file not found'}), 404
        except StopIteration:
            return jsonify({'message': 'Audio file not found'}), 404
        
        grid_fs_bucket.delete(audio_file_object_id)
        
        result = users_collection.update_one(
            {'_id': ObjectId(user_id), 'projects.audioFiles.audioFileId': audio_file_object_id},
            {'$pull': {'projects.$.audioFiles': {'audioFileId': audio_file_object_id}}}
        )

        if result.modified_count > 0:
            return jsonify({'message': 'Audio file deleted successfully'}), 200
        else:
            return jsonify({'message': 'Audio file reference not found or could not be deleted from project'}), 404
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'message': 'An error occurred while deleting the audio file'}), 500

@app.route('/deleteProject/<user_id>/<project_title>', methods=['DELETE'])
def delete_project(user_id, project_title):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        project_title_decoded = project_title  
        project = next((project for project in user.get('projects', []) if project['title'] == project_title_decoded), None)

        if project:
            if 'audioFiles' in project:
                for audio_file in project['audioFiles']:
                    if 'audioFileId' in audio_file:
                        grid_fs_bucket.delete(audio_file['audioFileId'])

            users_collection.update_one({'_id': ObjectId(user_id)}, {'$pull': {'projects': {'title': project_title_decoded}}})

            return jsonify({'message': 'Project and associated audio files deleted successfully'}), 200
        else:
            return jsonify({'message': 'Project not found'}), 404
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/explorePageAudio/<username>/<project_title>', methods=['GET'])
def play_explore_page_audio(username, project_title):
    try:
        user = users_collection.find_one({'username': username})
        #project_title_decoded = project_title.replace("%20", " ")
        project = next((p for p in user.get('projects', []) if p['title'] == project_title), None)
        if project and 'combinedAudioId' in project:
            combined_audio_id = project['combinedAudioId']
            file = grid_fs_bucket.open_download_stream(ObjectId(combined_audio_id))
            return send_file(
                io.BytesIO(file.read()),
                mimetype='audio/mpeg',
                as_attachment=False
            )
        else:
            return jsonify({'message': 'Project or combined audio not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error streaming combined audio: ' + str(e)}), 500

@app.route('/upvoteProject/<current_user_id>/<username>/<project_id>/<like>', methods=['POST'])
def upvote_project(current_user_id, username, project_id, like):
    like = like == 'True'
    project_id = int(project_id)
    try:
        project_user = users_collection.find_one({'username': username})
        if project_user:
            project = next((project for project in project_user.get('projects', []) if int(project['id']) == int(project_id)), None)
            if project:
                upvote_data = project.get('projectUpvote', [])
                user_upvote = next((data for data in upvote_data if data['user'] == current_user_id), None)
                if user_upvote:
                    # need to change the vote
                    if user_upvote.get('like') != like:
                        user_upvote['like'] = like
                        user_upvote['date'] = datetime.now()
                        # update in database
                        users_collection.update_one(
                            {'username': username, 'projects.id': project_id, 'projects.projectUpvote.user': current_user_id},
                            {'$set': {'projects.$.projectUpvote.$': user_upvote}}
                        )
                        return jsonify({"success": True, "message": "Vote successfully changed"})
                    # need to delete the vote
                    else:
                        users_collection.update_one(
                            {'username': username, 'projects.id': project_id},
                            { "$pull": { "projects.$.projectUpvote": { "user": current_user_id } } }
                        )
                        return jsonify({"success": True, "message": "Vote successfully deleted"})
                else:
                    project_user_id = project_user.get('_id')
                    data = {
                        'user': current_user_id,
                        'date': datetime.now(),
                        'like': like
                    }
                    users_collection.update_one(
                        {'_id': ObjectId(project_user_id), 'projects.id': project_id},
                        {'$push': {'projects.$.projectUpvote': data}}
                    )
                    return jsonify({"success": True, "message": "Vote added successfully"})
            else:
                return jsonify({'message': 'Project not found'}), 404
        return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        return jsonify({'message': 'Error upvoting project: ' + str(e)}), 500
    
@app.route('/contributeToProject', methods=['POST'])
def contribute_to_project():
    data = request.json
    project_id = int(data.get('projectId'))
    user_id = ObjectId(data.get('userId'))
    creator_username = data.get('projectCreator')

    project_to_copy = None
    project_creator = users_collection.find_one({'username': creator_username})

    if not project_creator:
        return jsonify({"message": "Project creator not found"}), 404

    for project in project_creator.get('projects', []):
        if project.get('id') == project_id:
            # Remove the creator's user_id before copying
            project_to_copy = project.copy()
            if 'user_id' in project_to_copy:
                del project_to_copy['user_id']
            break

    if not project_to_copy:
        return jsonify({"message": "Project not found"}), 404

    if project_creator['_id'] == user_id:
        return jsonify({"message": "Cannot copy your own project"}), 400

    update_result = users_collection.update_one(
        {'_id': user_id},
        {'$push': {'projects': project_to_copy}}
    )

    if update_result.modified_count == 0:
        return jsonify({"message": "Failed to copy project"}), 500

    # Retrieve the updated user document to get the index of the newly added project
    updated_user = users_collection.find_one({'_id': user_id})
    new_project_index = len(updated_user['projects']) - 1
    new_project_title = updated_user['projects'][new_project_index]['title']

    return jsonify({
        "message": "Project copied successfully",
        "newProjectTitle": new_project_title  # Send the index of the new project
    }), 200

if __name__ == '__main__':
    app.run(debug=True)