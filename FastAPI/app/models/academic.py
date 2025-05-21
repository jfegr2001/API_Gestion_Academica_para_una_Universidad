# app/models/academic.py
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Float, DateTime, Table, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base

# Tabla de relación muchos a muchos para prerrequisitos
subject_prerequisites = Table(
    'subject_prerequisites',
    Base.metadata,
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('subjects.id'), primary_key=True)
)

class Semester(Base):
    __tablename__ = "semesters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    schedules = relationship("Schedule", back_populates="semester")
    enrollments = relationship("Enrollment", back_populates="semester")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True)
    name = Column(String(100), index=True)
    credits = Column(Integer)
    max_students = Column(Integer)
    
    # Relación muchos a muchos para los prerrequisitos
    prerequisites = relationship(
        "Subject",
        secondary=subject_prerequisites,
        primaryjoin=(subject_prerequisites.c.subject_id == id),
        secondaryjoin=(subject_prerequisites.c.prerequisite_id == id),
        backref="required_for"
    )
    
    schedules = relationship("Schedule", back_populates="subject")
    enrollments = relationship("Enrollment", back_populates="subject")


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    day_of_week = Column(Integer)  # 0=Monday, 6=Sunday
    start_time = Column(String(5))  # Format: "HH:MM"
    end_time = Column(String(5))  # Format: "HH:MM"
    classroom = Column(String(50))
    
    subject = relationship("Subject", back_populates="schedules")
    teacher = relationship("User")
    semester = relationship("Semester", back_populates="schedules")
    
    __table_args__ = (
        UniqueConstraint('classroom', 'day_of_week', 'start_time', 'semester_id', 
                         name='uq_classroom_time'),
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    semester_id = Column(Integer, ForeignKey("semesters.id"))
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    
    student = relationship("User")
    subject = relationship("Subject", back_populates="enrollments")
    schedule = relationship("Schedule")
    semester = relationship("Semester", back_populates="enrollments")
    grades = relationship("Grade", back_populates="enrollment")
    
    __table_args__ = (
        UniqueConstraint('student_id', 'subject_id', 'semester_id', 
                         name='uq_student_subject_semester'),
    )


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"))
    evaluation_type = Column(String(20))  # "partial1", "partial2", "final", etc.
    weight = Column(Float)  # Percentage weight of the grade (0.0 to 1.0)
    score = Column(Float)  # 0.0 to 5.0
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    enrollment = relationship("Enrollment", back_populates="grades")
