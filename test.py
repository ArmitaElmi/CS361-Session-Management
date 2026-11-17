import requests
url = "http://127.0.0.1:5003"

#test 1:
# expected result: Test 1: Create Session,Code 201, Session created successfully,
# session_id:..., user_id: ...
data = {
    "user_id": "user01"
}
response = requests.post(url + "/sessions", json=data)
created_session = response.json()

print("Test 1: Create Session")
print("Status Code:", response.status_code)
print("Response:", response.json())



#test 2: no user ID provided.
#expected result: missing user ID, code 400, user ID required.
data = {}
response = requests.post(url + "/sessions", json=data)

print("\nTest 2: Missing User ID")
print("Status Code:", response.status_code)
print("Response:", response.json())



#test 3: validate an existing session
#expected result: Code 200, Response: valid: true, user_id:...,message: session is valid.

#retrieve session ID from the previous response.
session_id = created_session["session_id"]
data = {
    "session_id": session_id
}
response = requests.post(url + "/sessions/validate", json=data)

print("\nTest 3: Validate Existing Session")
print("Status Code:", response.status_code)
print("Response:", response.json())



#test 4: validate a session that does not exist.
#expected result: Invalid session ID, code 404, session not found.
data = {
    "session_id": "fake-session-123"
}
response = requests.post(url + "/sessions/validate", json=data)

print("\nTest 4: Invalid Session ID")
print("Status Code:", response.status_code)
print("Response:", response.json())




#test 5: Validate without providing a session ID
#expected result: session ID missing, code 400, session ID required.
data = {}
response = requests.post(url + "/sessions/validate", json=data)

print("\nTest 5: Missing Session ID")
print("Status Code:", response.status_code)
print("Response:", response.json())
