# FastAPI Students API

REST API built with FastAPI, SQLAlchemy and SQLite. It has CRUD operations for students, JWT authentication, bcrypt password hashing and role-based access control (admin / user).

## Features
- CRUD endpoints for students
- List students who passed (mark >= 40)
- User registration with bcrypt password hashing
- Login with JWT access token (30 minutes expiry)
- Protected endpoints (401 without a valid token)
- Role-based access: only admin can delete students (403 for normal users)
- Request validation with Pydantic and 404 handling
- Data stored in SQLite using SQLAlchemy

## Tech Stack
Python, FastAPI, SQLAlchemy, SQLite, Pydantic, PyJWT, bcrypt

## Endpoints
| Method | Path | Access |
|---|---|---|
| POST | /register | Public |
| POST | /login | Public (returns JWT) |
| GET | /me | Logged in |
| GET | /students | Logged in |
| GET | /students/pass | Public |
| GET | /students/{id} | Public |
| POST | /students | Public |
| PUT | /students/{id} | Public |
| DELETE | /students/{id} | Admin only |

## Run Locally
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
fastapi dev students_db_api.py
```

Swagger docs: http://127.0.0.1:8000/docs

## Authentication
1. Register a user with `POST /register`
2. Login with `POST /login` to get an `access_token`
3. Send it in the header: `Authorization: Bearer <token>`

New users always get the `user` role. The admin role is set directly in the database.

## Configuration
Set a secret key for signing tokens:
```
$env:SECRET_KEY = "your-long-random-key"
```
If it is not set, a development default is used. Do not use the default in production.

## Tests
```
pip install pytest httpx
pytest
```
Tests cover authentication (401 without token), registration, login and role-based access (403 for normal users on delete).