from flask import Flask, request, jsonify
from database import create_database
import sqlite3
# to generate difficult session IDs.
import secrets
import time

app = Flask(__name__)

# check whether the service is running
@app.route("/")
def home():
    return jsonify({
        "message": "Session Management Microservice is running."
    })

# Create a new session
# method is post because the app is sending requests to the microservice and
#asking it to create a new session.
@app.route("/sessions", methods=["POST"])
def create_session():

    # Get the information sent by the other program
    data = request.get_json()

    # Check if the user ID was provided
    if not data or "user_id" not in data:
        return jsonify({"error": "User ID is required"}), 400

    # get the user ID
    user_id = str(data["user_id"])

    # generate a random session ID using 32 bytes of randomness.
    session_id = secrets.token_urlsafe(32)


    current_time = time.time()

    # open the database
    connection = sqlite3.connect("sessions.db")

    # Save the new session
    connection.execute("""
        INSERT INTO sessions
        (session_id, user_id, created_at, last_activity, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, (session_id, user_id, current_time, current_time, 1))


    connection.commit()

    connection.close()

    # Send the session information back
    return jsonify({
        "message": "Session created successfully",
        "session_id": session_id,
        "user_id": user_id
    }), 201


# check whether a session is valid
@app.route("/sessions/validate", methods=["POST"])
def validate_session():

    #get the session ID sent by other program
    data = request.get_json()

    # Check if a session ID was provided
    if not data or "session_id" not in data:
        return jsonify({"error": "Session ID is required"}), 400

    #get the session ID
    session_id = data["session_id"]

    # connect with database
    connection = sqlite3.connect("sessions.db")

    # Look for the session in the database
    result = connection.execute("""
        SELECT user_id, is_active
        FROM sessions
        WHERE session_id = ?
    """, (session_id,)).fetchone()


    connection.close()

    # check if the session exists
    if result is None:
        return jsonify({
            "valid": False,
            "message": "Session not found"
        }), 404

    # check if the session is active
    if result[1] == 0:
        return jsonify({
            "valid": False,
            "message": "Session is inactive"
        }), 401

    return jsonify({
        "valid": True,
        "user_id": result[0],
        "message": "Session is valid"
    }), 200



if __name__ == "__main__":
    create_database()
    app.run(debug=True, port=5001)
