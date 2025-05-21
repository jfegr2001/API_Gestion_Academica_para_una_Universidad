# app/services/user.py
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import List, Optional

from models.user import User, UserRole
from schemas.user import UserCreate, UserUpdate, UserSchema
from core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> UserSchema:
    user =  db.query(User).filter(User.id == user_id).first()
    if user:
        return UserSchema.model_validate(user)
    return None


def get_user_by_email(db: Session, email: str) -> UserSchema:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return UserSchema.model_validate(user)
    return None


def get_user_by_document_id(db: Session, document_id: str) -> Optional[User]:
    return db.query(User).filter(User.document_id == document_id).first()


def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    role: Optional[UserRole] = None
) -> List[User]:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    users = query.offset(skip).limit(limit).all()
    return [UserSchema.model_validate(user) for user in users]


def create_user(db: Session, user: UserCreate) -> User:
    # Check if user with email already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Check if user with document_id already exists
    db_user = get_user_by_document_id(db, document_id=user.document_id)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document ID already registered",
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        document_id=user.document_id,
        hashed_password=hashed_password,
        role=user.role,
        is_admin=user.is_admin,
        is_active=user.is_active,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserSchema.model_validate(db_user)


def update_user(db: Session, user_id: int, user: UserUpdate) -> User:
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    update_data = user.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data["password"])
        del update_data["password"]
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return UserSchema.model_validate(db_user)


def delete_user(db: Session, user_id: int) -> User:
    db_user = get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    db.delete(db_user)
    db.commit()
    return UserSchema.model_validate(db_user)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
