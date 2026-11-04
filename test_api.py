from fastapi.testclient import TestClient
from students_db_api import app
import uuid

client = TestClient(app)

def test_students_without_token():
    response = client.get("/students")
    assert response.status_code == 401

def test_me_without_token():
    response = client.get("/me")
    assert response.status_code == 401

def test_login_unknown_user():
    response = client.post("/login", json={"username": "nouser", "password": "x"})
    assert response.status_code == 401

def test_login_message():
    response = client.post("/login", json={"username": "nouser", "password": "x"})
    assert response.json()["detail"] == "Invalid username or password"

def test_register():
    username = "user_" + uuid.uuid4().hex[:8]
    response = client.post("/register", json={"username": username, "password": "abc12345"})
    assert response.status_code == 200

def test_register_and_login():
    username = "user_" + uuid.uuid4().hex[:8]
    r = client.post("/register",json={"username":username,"password":"abc12345"})
    assert r.status_code == 200

    r = client.post("/login",json={"username":username,"password":"abc12345"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    print(token)

    headers = {"Authorization": "Bearer " + token}

    r = client.get("/students", headers=headers)
    assert r.status_code == 200
    
    r = client.delete("/students/1", headers=headers)
    assert r.status_code == 403