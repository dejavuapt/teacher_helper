from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Date, ForeignKey

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    
class Student(Base):
    __tablename__ = 'student'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String, unique=False, nullable=False)
    
class DateLessons(Base):
    __tablename__ = "date_lessons"
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    total_lessons = Column(Integer, unique=False, nullable=False)
    
class StudentSkips(Base):
    __tablename__ = "student_skips"
    
    student_id = Column(Integer, ForeignKey("student.id"), primary_key=True)
    datelessons_id = Column(Integer, ForeignKey("date_lessons.id"), primary_key=True)
    count_lessons = Column(Integer, unique=False, nullable=False)
    reason = Column() #need choice like in django
    
    student = relationship("Student", back_populates="skips")
    datelessons = relationship("DateLessons", back_populates="study_days")
    