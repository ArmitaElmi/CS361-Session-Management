from flask import Flask, request, jsonify
from database import create_database
import sqlite3
# to generate difficult session IDs.
import secrets
import time

app = Flask(__name__)

DATABASE = "sessions.db"
TIMEOUT_SECONDS = 600  # 10 minutes
WARNING_SECONDS = 60  # 1 minute warning before hard timeout

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



# 2. Check Timeout Status
@app.route("/sessions/check_timeout", methods=["POST"])
def check_timeout():
    data = request.get_json()
    if not data or "session_id" not in data:
        return jsonify({"error": "Session ID is required"}), 400

    session_id = data["session_id"]
    current_time = time.time()

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row  # Allows dictionary-like access
    cursor = connection.cursor()

    result = cursor.execute("""
        SELECT last_activity, is_active 
        FROM sessions 
        WHERE session_id = ?
    """, (session_id,)).fetchone()
    connection.close()

    if not result:
        return jsonify({"status": "expired", "message": "Session not found"}), 404

    if result["is_active"] == 0:
        return jsonify({"status": "expired", "message": "Session already terminated"}), 401

    # Calculate time since last activity
    time_since_activity = current_time - result["last_activity"]

    # Logic:
    # 0-600s (0-10m): Active
    # 600-660s (10-11m): Warning (1 minute left)
    # >660s (11m+): Expired

    if time_since_activity > (TIMEOUT_SECONDS + WARNING_SECONDS):
        # Hard expiration: Mark inactive in DB
        connection = sqlite3.connect(DATABASE)
        connection.execute("UPDATE sessions SET is_active = 0 WHERE session_id = ?", (session_id,))
        connection.commit()
        connection.close()
        return jsonify({"status": "expired", "message": "Session timed out due to inactivity"}), 401

    elif time_since_activity > TIMEOUT_SECONDS:
        # In the 1-minute warning window
        time_left = int((TIMEOUT_SECONDS + WARNING_SECONDS) - time_since_activity)
        return jsonify({
            "status": "warning",
            "message": f"Session expiring soon. You have {time_left} seconds to stay signed in.",
            "time_left": time_left
        }), 200

    else:
        # Normal active state
        return jsonify({"status": "active"}), 200



# 1. Update Activity (Refresh the timer)
@app.route("/sessions/activity", methods=["POST"])
def update_activity():
    data = request.get_json()
    if not data or "session_id" not in data:
        return jsonify({"error": "Session ID is required"}), 400

    session_id = data["session_id"]
    current_time = time.time()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Update the last_activity timestamp
    cursor.execute("""
        UPDATE sessions 
        SET last_activity = ? 
        WHERE session_id = ? AND is_active = 1
    """, (current_time, session_id))

    connection.commit()
    rows_updated = cursor.rowcount
    connection.close()

    if rows_updated == 0:
        return jsonify({"error": "Session not found or inactive"}), 404

    return jsonify({"message": "Activity updated", "last_activity": current_time}), 200



# 3. Terminate / Logout Session
@app.route("/sessions/<session_id>", methods=["DELETE"])
def terminate_session(session_id):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Set active status to 0 (soft delete for audit purposes)
    cursor.execute("""
        UPDATE sessions 
        SET is_active = 0 
        WHERE session_id = ?
    """, (session_id,))

    connection.commit()
    rows_updated = cursor.rowcount
    connection.close()

    if rows_updated == 0:
        return jsonify({"error": "Session not found"}), 404

    return jsonify({"message": "Session terminated successfully"}), 200


if __name__ == "__main__":
    create_database()
    app.run(debug=True, port=5003)
