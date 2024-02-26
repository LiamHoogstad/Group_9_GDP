# Group_9_GDP

This repository will host the code and implementation for group 9's project in the CSU44098 module

## Set the backend up

Ensure that the latest version of python is installed on your device

### 1

- In your terminal type cd backend

### 2

- For Windows
  -- python -m venv venv
- For macOS/Unix
  -- python3 -m venv venv

### 3

- For Windows, paste this in your terminal
  -- [path to Activate.ps1, should be something like C:\...\venv\Scripts\Activate.ps1]
- For macOS/Unix, paste this in your terminal
  -- [path to Activate.ps1 (i think, it's one of the activates anyway), should be something like C:\...\venv\bin\Activate...]

### 4

- Paste this in your terminal
  -- pip install Flask pymongo[srv] flask-cors

### 5

- Run the application with
  -- flask run OR
  -- python app.py

### Code Explanation

This Python code is for a backend application built with Flask, which serves as a web server. It interacts with a MongoDB database to store user data. Here's a simplified explanation of each part:

- Imports and Setup:

  -- Various modules are imported, including Flask for the web server, CORS (Cross-Origin Resource Sharing) to allow requests from different domains, and MongoClient for interacting with MongoDB.
  An instance of the Flask app is created, and CORS is enabled for it.

- MongoDB Connection:

-- A connection to MongoDB is established using a URI (Uniform Resource Identifier), which contains the credentials and location of the database. The actual URI is replaced with 'blah blah blah' as a placeholder.
A test command (ping) is sent to the database to confirm connectivity.

- Routes and Endpoints:

-- Two routes (endpoints) are defined for the web server:
--- The root (/) route simply returns "Hello, World!" as a response to GET requests.
--- The /submit route listens for POST requests. When data is submitted to this route, it's expected to be in JSON format. This data is then inserted into the MongoDB database under the MusiCollab database and users collection.
After successfully inserting the data, the server responds with a JSON object indicating success and the inserted document's ID.

- Running the Server:

-- Finally, if the script is run directly (not imported as a module), the Flask app starts and listens for incoming requests on the default port (usually 5000 for Flask apps).
In essence, this application can receive user data through its /submit endpoint and store that data in a MongoDB database, providing a basic backend for a user signup feature.

## Set the frontend up

Ensure the latest version of Node.js is installed on your device

### 1

- In your terminal type cd frontend

### 2

- Install dependencies, run the following:
  -- npm install
  -- npm install vue@next axios vuetify@next

### 3

- Run the project by typing npm run dev in the terminal

### Code Explanation

- Script Section:
  -- Imports and Setup: The script imports Vue's ref function and axios for state management and making HTTP requests, respectively.
  -- Reactive State: It defines reactive state variables for email, password, username, dateOfBirth, and menu using the ref function. These variables will store the input values from the form.
  -- Submit Form Method: This method is defined under methods and is responsible for taking the form data, encapsulating it into formData, and sending it to a backend server located at "http://localhost:5000/submit" using axios.post. It logs the response from the server or catches and logs any error if the request fails.
- Template Section:
  -- Structure: The template markup defines the structure of the signup form, including fields for email, password, username, and date of birth.
  -- Data Binding: Uses v-model to bind input fields to the reactive state variables (email, password, username, dateOfBirth), enabling two-way data binding.
  -- Date Picker: Includes a v-date-picker component for selecting a date of birth, which updates the dateOfBirth variable.
  -- Submit Button: Contains a button that, when clicked, triggers the submitForm method.
- Style Section:
  -- Defines CSS styles scoped to this component, styling the signup form's appearance, including the layout of the form container and the positioning of the header.

  In Simple Terms:
  When a user fills out the form on the webpage and clicks the "Submit" button, the form data is collected and sent to a server. The server's address is "http://localhost:5000/submit". If the data is sent successfully, the server's response is logged to the console. If there's an error (like the server is down or the URL is incorrect), the error information is logged to the console. The style section makes sure the form looks nice and is positioned correctly on the page.

## To run the whole project

- Have 2 terminals open. One where you cd into the backend and the other where you cd into the frontend
  -- In the backend run one of these 2 commands
  --- flask run
  --- python app.py
  -- You should now see in the terminal that we have connected to the MongoDB database
  -- For the front end, type in the following command:
  --- npm run dev
  -- now if you go to the localhost portal enter the details, open the web console and you will be able to see the success token after submitting. The user information has not been error handled. Make sure you change the uri with the one from discord
