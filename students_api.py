from fastapi import FastAPI,HTTPException
from pydantic import BaseModel

app = FastAPI()

class Student(BaseModel):
    name: str
    mark: int
    city: str = "Unknown"

Students = []

@app.post("/students")
def add_student(student: Student):
    Students.append(student)
    return {"message": "Student added", "student": student}

@app.get("/students")
def get_students():
    return Students

@app.get("/students/pass")
def get_passed():
    result = [s for s in Students if s.mark >=40 ]
    return result

@app.get("/students/{index}")
def get_student(index: int):
    if index < 0 or index > len(Students):
        raise HTTPException(status_code=404, detail="Student not found")
    return Students[index]

@app.put("/students/{index}")
def get_student(index: int, student: Student):
    if index < 0 or index > len(Students):
        raise HTTPException(status_code=404, detail="Student not found")
    Students[index]= student
    return Students[index]

@app.delete("/students/{index}")
def get_student(index: int, student: Student):
    if index < 0 or index > len(Students):
        raise HTTPException(status_code=404, detail="Student not found")
    Students.pop(index)
    return {"message": "Deleted"}