# FastAPI Students API

CRUD API built with FastAPI, SQLAlchemy and SQLite.

## Features
- Add, list, get, update, delete students
- List students who passed (mark >= 40)
- Request validation with Pydantic
- 404 handling for missing students

## Run
pip install -r requirements.txt
fastapi dev students_db_api.py

Swagger docs: http://127.0.0.1:8000/docs