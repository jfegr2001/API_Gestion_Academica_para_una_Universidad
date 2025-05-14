# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    document_id: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    model_config = {
        "from_attributes": True
    }


class UserInDB(User):
    hashed_password: str