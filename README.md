# CS361-Session-Management
Sprint 2-Session Management Microservice
Overview: The Session Management microservice creates and validates user sessions. It uses Python, Flask, and SQLite to store session information.
Tto Run the Microservice:
1. Install Flask: python -m pip install flask
2.Start the microservice: python app.py
3.The microservice runs at: http://127.0.0.1:5001
API Communication

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

The database is created automatically when the microservice starts.
Tests can be ran with the following command: python test.py
