import requests
import sqlite3
import time

#main url
url = "http://127.0.0.1:5003" # For creating the session


# url_gerald(not using) = "http://127.0.0.1:5002" # For testing your logic
DATABASE = "sessions.db"

# 1. Create a session using Armita's server
create_res = requests.post(f"{url}/sessions", json={"user_id": "test_user"})
if create_res.status_code != 201:
    print("Failed to create session. Make sure Armita's app.py is running on port 5001.")
    print("Error:", create_res.text)
    exit()

session_id = create_res.json().get("session_id")
print("Created Session in Armita's App:", session_id)

# 2. Test Active Status (using your server)
print("\n--- Test 1: Active Status ---")
res = requests.post(f"{url}/sessions/check_timeout", json={"session_id": session_id})
print(res.status_code, res.json())

# 3. Test Warning Status (Simulate 10.5 minutes passing)
print("\n--- Test 2: Warning Status (Simulating 10.5 mins) ---")
conn = sqlite3.connect(DATABASE)
past_time = time.time() - 630 # 10.5 minutes in seconds
conn.execute("UPDATE sessions SET last_activity = ? WHERE session_id = ?", (past_time, session_id))
conn.commit()
conn.close()

res = requests.post(f"{url}/sessions/check_timeout", json={"session_id": session_id})
print(res.status_code, res.json()) # Should say "warning"

# 4. Test Expiration Status (Simulate 11.5 minutes passing)
print("\n--- Test 3: Expired Status (Simulating 11.5 mins) ---")
conn = sqlite3.connect(DATABASE)
past_time = time.time() - 690 # 11.5 minutes in seconds
conn.execute("UPDATE sessions SET last_activity = ? WHERE session_id = ?", (past_time, session_id))
conn.commit()
conn.close()

res = requests.post(f"{url}/sessions/check_timeout", json={"session_id": session_id})
print(res.status_code, res.json()) # Should say "expired"

# 5. Test Terminate
print("\n--- Test 4: Terminate Session ---")
res = requests.delete(f"{url}/sessions/{session_id}")
print(res.status_code, res.json())

