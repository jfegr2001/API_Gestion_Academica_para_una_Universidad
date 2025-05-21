# app/schemas/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    document_id: str
    role: UserRole

    model_config = {
        "from_attributes": True
    }


class UserCreate(UserBase):
    password: str
    is_active: bool = True
    is_admin: bool = False


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

    model_config = {
        "from_attributes": True
    }


class UserSchema(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    hashed_password: str

    model_config = {
        "from_attributes": True
    }


