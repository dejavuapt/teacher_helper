from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import  List, Any
from app.bot.markly.models import Teacher, Absence
from app.db.engine import Base

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey('teachers.id'))
    
    name: Mapped[str] = mapped_column(String(50), unique=False, nullable=False)
    
    teacher: Mapped[Teacher] = relationship(back_populates="students") 
    absences: Mapped[List[Absence]] = relationship(back_populates='student')

    def __repr__(self) -> str:
        return f"Student(id={self.id!r}, name={self.name!r})"
    
    def to_dict(self) -> dict[str, Any]:
        return { c.name: getattr(self, c.name) for c in self.__table__.columns }

