from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import models
from .dependencies import get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def get_current_user_by_email(db: Session, email: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return user


def check_general_manager(user: models.User):
    if user.role != "general_manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return True


def check_doctor(user: models.User):
    if user.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Must be a doctor"
        )
    return True


def check_doctor_or_manager(user: models.User):
    if user.role not in ["doctor", "general_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be a doctor or general manager",
        )
    return True


def check_assistant(user: models.User):
    if user.role != "assistant":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Must be an assistant"
        )
    return True


def check_doctor_or_manager(user):
    if user.role not in ["doctor", "general_manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Only doctors and managers can access patient records.",
        )
