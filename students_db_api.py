from fastapi import FastAPI,HTTPException,Depends
from pydantic import BaseModel,ConfigDict
from sqlalchemy import create_engine,select,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
import bcrypt
import jwt
from datetime import datetime,timedelta,timezone
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os


engine = create_engine("sqlite:///students.db",connect_args={"check_same_thread": False},)

class Base(DeclarativeBase):
    pass

class StudentDB(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    mark: Mapped[int]
    city: Mapped[str] = mapped_column(String(50), default="Unknown")

class UserDB(Base):                                              # ← pudhusu
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="user")

Base.metadata.create_all(engine)

class StudentIn(BaseModel):
    name: str
    mark: int
    city: str = "Unknown"

class  StudentOut(StudentIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)

app = FastAPI()

def get_db():
    with Session(engine) as session:
        yield session

bearer = HTTPBearer()

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    username = payload.get("sub")
    row = db.scalars(select(UserDB).where(UserDB.username == username)).first()
    if row is None:
        raise HTTPException(status_code=401, detail="User not found")
    return row

def require_admin(current_user: UserDB = Depends(get_current_user)):
    if current_user.role!="admin":                                   # neeye ezhudhu
        raise HTTPException(status_code=403, detail="Admin only")
    return current_user

@app.post("/students",response_model=StudentOut)
def add_student(student: StudentIn, db: Session = Depends(get_db)):
    row = StudentDB(name=student.name, mark=student.mark, city=student.city)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@app.get("/students",response_model=list[StudentOut])
def get_students(db: Session = Depends(get_db),current_user: UserDB = Depends(get_current_user)):
    return db.scalars(select(StudentDB)).all()

@app.get("/students/pass",response_model=list[StudentOut])
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
def delete_student(id: int, db: Session = Depends(get_db),admin: UserDB = Depends(require_admin)):
    row = db.get(StudentDB, id)
    if row is None:
         raise HTTPException(status_code=404, detail="Student not found")    
    db.delete(row)
    db.commit()
    return {"message": "Deleted"}

@app.get("/users",response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.scalars(select(UserDB)).all()

@app.post("/register",response_model=UserOut)
def register(user:UserIn, db: Session = Depends(get_db)):
    existing = db.scalars(select(UserDB).where(UserDB.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=404, detail="Username already exists")

    hashed = bcrypt.hashpw(user.password.encode(),bcrypt.gensalt()).decode()

    row = UserDB(username=user.username,hashed_password=hashed)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-key-change-me-0123456789abcdef")
ALGORITHM = "HS256"

def create_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/login")
def login(user: UserIn, db: Session = Depends(get_db)):
    row = db.scalars(select(UserDB).where(UserDB.username == user.username)).first()
    if row is None:
            raise HTTPException(status_code=401, detail="Invalid username or password")  
    
    match = bcrypt.checkpw(user.password.encode(),row.hashed_password.encode())
    if not match:
        raise HTTPException(status_code=401, detail="Invalid username or password")    
    
    token = create_token(row.username,row.role)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me",response_model=UserOut)
def me(current_user: UserDB = Depends(get_current_user)):    
    return current_user