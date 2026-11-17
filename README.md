# CS361-Session-Management
Sprint 2-Session Management Microservice
Overview: The Session Management microservice creates and validates user sessions. It uses Python, Flask, and SQLite to store session information.
Tto Run the Microservice:
1. Install Flask: python -m pip install flask
2.Start the microservice: python app.py
3.The microservice runs at: http://127.0.0.1:5003


The database is created automatically when the microservice starts.
Tests can be ran with the following command: python test.py


##UML Diagram:
![Session Management UML Sequence Diagram](updatedUML)


API Communication:
The microservice communicates with other programs using HTTP requests through a REST API. Request and response data are formatted as JSON.

1. Create a Session:

Endpoint: /sessions
Method: POST
Request:
{
  "user_id": "user01"
}
Successful response (201):
{
  "message": "Session created successfully",
  "session_id": "generated-session-id",
  "user_id": "user01"
}


2. Validate a Session:

Endpoint: /sessions/validate
Method: POST
Request:
{
  "session_id": "generated-session-id"
}
Successful response (200):
{
  "valid": true,
  "user_id": "user01",
  "message": "Session is valid"
}


3. Update Session Activity

Endpoint: `/sessions/activity`

Method: POST

Request:
```json
{
  "session_id": "generated-session-id"
}


4. Check Session Timeout

Endpoint: `/sessions/check_timeout`
Method: POST
Request:
```json
{
  "session_id": "generated-session-id"
}


5. Terminate a Session

Endpoint: `/sessions/<session_id>`
Method: DELETE
Description: Ends an active session by marking it as inactive in the database.
Successful response (200):
{
  "message": "Session terminated successfully"
}
Error response (404):
{
  "error": "Session not found"
}



## Example: Requesting and Receiving Data

The following Python example shows how another program can communicate with the Session Management microservice using HTTP requests.

Requesting data:

import requests

url = "http://127.0.0.1:5003"

response = requests.post(
    url + "/sessions",
    json={"user_id": "user01"}
)

Receiving data:

if response.status_code == 201:
    session_data = response.json()

    session_id = session_data["session_id"]
    user_id = session_data["user_id"]

    print("Session ID:", session_id)
    print("User ID:", user_id)

Explanation:The test program sends a POST request with a user ID. The microservice processes the request and returns a JSON response containing the session ID and user ID. The test program receives and reads that response using response.json().
