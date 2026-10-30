from sqlalchemy import create_engine,select,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session

engine = create_engine("sqlite:///students.db")

class Base(DeclarativeBase):
    pass

class StudentDB(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    mark: Mapped[int]
    city: Mapped[str] = mapped_column(String(50), default="Unknown")

Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(StudentDB(name="Mahi",mark=80, city="Kum"))
    session.add(StudentDB(name="Dhivi", mark=35, city="Che"))
    session.add(StudentDB(name="Keerthi", mark=40, city="Kum"))
    session.add(StudentDB(name="Ammu", mark=39, city="Kab"))
    session.commit()

with Session(engine) as session:
    for s in session.scalars(select(StudentDB).where(StudentDB.mark>=40)).all():
        print(s.id, s.name, s.mark, s.city)