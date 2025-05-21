# app/models/user.py
from sqlalchemy import Boolean, Column, Integer, String, Enum
import enum
from core.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"
    TEACHER = "teacher"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    document_id = Column(String(20), unique=True, index=True)
    hashed_password = Column(String(100))
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
