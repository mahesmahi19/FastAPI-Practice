from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel,ConfigDict
from sqlalchemy import create_engine,select,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session


engine = create_engine("sqlite:///students.db",connect_args={"check_same_thread": False},)

class Base(DeclarativeBase):
    pass

class StudentDB(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    mark: Mapped[int]
    city: Mapped[str] = mapped_column(String(50), default="Unknown")

class StudentIn(BaseModel):
    name: str
    mark: int
    city: str = "Unknown"

class  StudentOut(StudentIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

app = FastAPI()

def get_db():
    with Session(engine) as session:
        yield session

@app.post("/students",response_model=StudentOut)
def add_student(student: StudentIn, db: Session = Depends(get_db)):
    row = StudentDB(name=student.name, mark=student.mark, city=student.city)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@app.get("/students",response_model=list[StudentOut])
def get_student(db: Session = Depends(get_db)):
    return db.scalars(select(StudentDB)).all()

@app.get("/students/pass")
def get_passed(db: Session = Depends(get_db)):
    return db.scalars(select(StudentDB).where(StudentDB.mark >= 40)).all()        

@app.get("/students/{id}",response_model=StudentOut)
def get_student(id: int, db: Session = Depends(get_db)):
    row = db.get(StudentDB, id)
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return row

@app.put("/students/{id}",response_model=StudentOut)
def update_student(id: int, student: StudentIn, db: Session = Depends(get_db)):
    row = db.get(StudentDB, id)
    if row is None:
         raise HTTPException(status_code=404, detail="Student not found")    
    row.name = student.name
    row.mark = student.mark
    row.city = student.city
    db.commit()
    db.refresh(row)
    return row

@app.delete("/students/{id}")
def delete_student(id: int, db: Session = Depends(get_db)):
    row = db.get(StudentDB, id)
    if row is None:
         raise HTTPException(status_code=404, detail="Student not found")    
    db.delete(row)
    db.commit()
    return {"message": "Deleted"}