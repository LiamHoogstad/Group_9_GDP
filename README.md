# Group_9_GDP - Release 1

This branch is our release 1 of our Group Design Project, MusiCollab. MusiCollab is aimed to be a colaborative music creation website where you can create and edit projects with friends and strangers by adding tracks, manipulating their audio settings and much more! We achieved all of goal for this release and an extra feature of a working custom volume slider.

# ——————————————— Setting up the Backend ——————————————————— #

Ensure that the latest version of python is installed on your device

### 1

- In your terminal, starting from root directory type cd backend

### 2

- For Windows
  -- python -m venv venv
- For macOS/Unix
  -- python3 -m venv venv

### 3

  # Setting up the development environment

- The step the above creates a folder called 'venv' within the backend folder. Within the venv
  folder is a 'bin' folder, which has a file called "Activeate.ps1" inside it.

- Past the below to set up the virtual environment:

  - Ensure you are in the backend directory, Then:
    - For Windows, paste this in your terminal to enter the development environment
      -- [Absolute (not relative) path to the 'Activate.ps1' file]
            - should be something like "C:\...\venv\Scripts\Activate.ps1"
    - For macOS/Unix, paste this in your terminal to enter the development environment
      -- [Absolute (not relative) path to the 'Activate.ps1' file], minus the '.ps1' at the end
            - should be something like "C:\...\venv\bin\Activate"

### 4

- Paste this in your terminal
  -- pip install -r requirements.txt

### 6

- Run the application with:
  -- python app.py

# Backed Code Explanation:

  This code represents a backend application developed using Flask, a popular Python web framework. It integrates   various functionalities including user management, file upload, and interaction with MongoDB. Below is a brief  explanation of the key parts of this code:
  
  #### Imports and Initial Setup:
  
  - Various libraries are imported for handling web requests, security, file management, and database interactions.
  - A Flask application instance is created, and Flask extensions like Bcrypt for password hashing and JWTManager for   token-based authentication are initialized.
  - CORS (Cross-Origin Resource Sharing) is enabled allowing the backend to accept requests from different origins.
  
  #### Configuration:
  
  - A secret key for JWT (JSON Web Tokens) is generated for securing token-based authentication.
  - Environment variables are loaded (e.g., database connection strings) using dotenv.
  - MongoDB client is set up to connect to a database, and collections and GridFSBucket for file storage are initialized.
  
  #### Routes and Endpoints:
  
  - Various endpoints are defined for different functionalities such as user registration, login, email and username  checks, file uploads (both general and specific to a user's profile picture), and project management.
  - The /upload endpoint allows files to be uploaded and stored in MongoDB using GridFS.
  - The /checkEmail, /checkUsername, /submit, /login, and other user-related endpoints allow for user management such as  registration, email validation, and authentication.
  - Password validation for login uses bcrypt to securely check hashed passwords.
  - JWT tokens are used for authentication and are required for certain actions like uploading a profile picture or   adding a project.
  - Project and audio management is facilitated through endpoints that allow adding projects, uploading audio files to  projects, and retrieving project-related information.
  
  #### File Upload and Retrieval:
  
  - Files (like profile pictures and audio files) can be uploaded and linked to users or projects. GridFS is used for   storing files that exceed the BSON document size limit in MongoDB.
  - File metadata is managed, and files can be retrieved via specific endpoints, allowing for dynamic content management  related to user profiles and projects.
  
  #### Security and Data Management:
  
  - jwt_required decorator is used to protect routes that require user authentication.
  - Data validation and error handling are implemented to ensure that the backend responds appropriately to invalid   requests or database errors.
  
  #### Running the Application:
  
  Overall, this backend is designed for a platform where users can create profiles, manage projects, and upload files,  with secure authentication and data storage practices.

# ——————————————— Setting up the Frontend ——————————————————— #

Ensure the latest version of Node.js is installed on your device

### 1

- In your terminal, ensure you are in the root directory

### 2

- Install npm in the directory. Paste this in the terminal:
  -- npm init -y 
        AND
  -- npm install

### 3

- Run the project with:
  -- npm run dev

# Frontend Code Explanation

# Overall Structure and Configuration:

- App.vue
  This is the root component of the Vue application. It primarily serves as a container for the app, with a <router-view /> tag that serves as the outlet for displaying components based on the current route.
- main.js
  This is the entry point of the Vue application. It creates the Vue instance, applies global configurations, and mounts the app to the DOM. It includes setup for Vuetify (a material design component library) and Vue Router for managing navigation.
- index.js
  Defines the routes for the application, linking URLs to components. It includes routes for the landing page, sign-in, sign-up, profile page, and project view.

# Components:

- LandingPage.vue
  Serves as the homepage, guiding users to sign in or sign up.
- SignIn.vue
  Allows existing users to sign in by entering their email and password. It communicates with the backend to validate user credentials and handle session management.
- SignUp.vue
  Enables new users to create an account by providing details like email, password, username, and date of birth. It includes validation for each field and communicates with the backend to check the availability of email and username and to register the user.
- ProfilePage.vue
  Displays user information and a list of projects associated with the logged-in user. It allows users to upload a profile picture and add new projects. This component interacts with the backend for fetching and updating user-related data.
- ProjectView.vue
  A detailed view for individual projects, containing specific functionalities for project management and collaboration.
- Slider.vue
  A custom slider component, used within the application for settings such as volume control.

# Communication with Flask Backend:

- The Vue components use axios for HTTP requests, interacting with the Flask backend endpoints you provided earlier. This includes user authentication, profile updates, project management, and file uploads.
- Data fetched from the backend (like user details or project information) is displayed in the respective components. For instance, ProfilePage.vue would display user projects and personal information retrieved from the backend.
- Actions like signing in, signing up, uploading pictures, or adding projects involve sending data to the backend and handling responses, which may involve updating the local Vue state or redirecting the user based on the outcome.

# Style and Appearance:

- The application uses Vuetify for UI components and styling, ensuring a material design look and feel across the application.
- Each Vue file contains a <style></style> section, scoped to the component, defining CSS rules specific to the component's elements for customized styling.

#### Functionality and Flow:

- The application flow is managed by Vue Router, guiding users through different components based on their actions and authentication status.
- User authentication status (e.g., logged in/out) could influence navigational options and accessible content, directing users to the appropriate pages.
- The frontend interacts with the backend for various operations, ensuring that user data and project information are up-to-date and consistent with the database.

# ———————————————— To run the whole project ——————————————— #

- Have 2 terminals open, each starting from the project root diectory:
  - Terminal 1:
    Run:
    cd backend
    Then:
    [run the development environment] - Refer to setting up backend step 3
    Finally, run:
    python app.py
  - Terminal 2:
    Run:
    npm run dev

- This should launch the backend and frontend components, each running on a different localhost port/address
- To load the web application, ctrl/cmd click the link in the frontend terminal, or copy/paste the link into
  your browser

## Demonstration Purposes

We would like to guide you through 2 processes for your assesment.

- 1. Existing user:
     On the landing page you will click on the page that allows you to SIGN IN.
     Use:
     username: jbcfenlon@gmail.com
     password: GroupDesignProject9!  
     here you will be brought to an existing user profile page with their own custom profile picture and their projects that exist already. Feel free to click and test any of these. You can change the profile picture, or click on any of the projects and use the play/pause button as you wish and make use of our custom volume slider.
- 2. New user:
     On the landing page you will click on the page that allows you to SIGN UP.
     Sign up with your own details ensuring a valid email, password that is atleast 8 characters long, has a number, capital letter and a special character (all passwords are hashed for privacy reasons), a username, and a DOB (must be over 18)
     Upon completion you will be brought to the profile page where you can customise your profile with your own profile picture, add your own projects, and add some of your own audio files to the project you created, or you can use the files we have provided in the assets folder in frontend. Your signup information has all been saved to the database and where applicable the profile picture, audio files and project details are also all saved for future use so they can be played and streamed rather than locally.
