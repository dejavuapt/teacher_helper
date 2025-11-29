from datetime import datetime, date
from sqlalchemy import String, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import  Literal, List
from app.db.engine import Base

Reason = Literal['excused', 'sick', 'cut']

class Teacher(Base):
    __tablename__ = "teachers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    telegram_id: Mapped[str] = mapped_column(String(19), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    students: Mapped[List["Student"]] = relationship(back_populates="teacher")
    school_days: Mapped[List["SchoolDay"]] = relationship(back_populates='teacher')

    def __repr__(self) -> str:
        return f"Teacher(id={self.id!r}, telegram={self.telegram_id!r}, created_at={self.created_at.strftime("%d.%m.%y, %H:%M:%S")!r})"

# INFO: По сути у одного студента может быть много учителей, но
# у текущего бизнес процесса именно учителя работают со своими студентами.
class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    
    name: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    
    teacher: Mapped[Teacher] = relationship(back_populates="students") 
    absences: Mapped[List['Absence']] = relationship(back_populates='student')

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r})"

class SchoolDay(Base):
    __tablename__ = "schooldays"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))

    day: Mapped[date] = mapped_column(nullable=False)
    lessons: Mapped[int] = mapped_column(unique=False, nullable=False)

    teacher: Mapped[Teacher] = relationship(back_populates="school_days") 
    absences: Mapped[List['Absence']] = relationship(back_populates='school_day')

    __table_args__ = (UniqueConstraint('teacher_id', 'day', name='uq_teacher_day'),)

    def __repr__(self) -> str:
        return f"SchoolDay(id={self.id!r}, day={self.day.strftime("%d.%m.%y")!r}, lessons={self.lessons!r})"

class Absence(Base):
    __tablename__ = "absences"
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    schoolday_id: Mapped[int] = mapped_column(ForeignKey("schooldays.id"), primary_key=True)

    number: Mapped[int] = mapped_column(unique=False, nullable=False)
    reason: Mapped[Reason] = mapped_column(
        Enum("excused", "sick", "cut", name="reason_enum")
    )
    
    student: Mapped[Student] = relationship(back_populates="absences")
    school_day: Mapped[SchoolDay] = relationship(back_populates="absences")

    def __repr__(self):
        return f"Absence(student_id={self.student_id!r}, day_id={self.schoolday_id!r}, number={self.number!r}, reason={self.reason!r})"

