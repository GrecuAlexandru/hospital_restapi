from sqlalchemy.orm import Session
from .. import models, schemas
from .base import get_password_hash
from .users import get_user


def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()


def get_doctors(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Doctor).offset(skip).limit(limit).all()


def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    # First create the user
    hashed_password = get_password_hash(doctor.password)
    db_user = models.User(
        email=doctor.email,
        hashed_password=hashed_password,
        full_name=doctor.full_name,
        role="doctor",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Then create the doctor
    db_doctor = models.Doctor(
        user_id=db_user.id,
        specialization=doctor.specialization,
        experience=doctor.experience,
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def update_doctor(db: Session, doctor_id: int, doctor: schemas.DoctorUpdate):
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor:
        update_data = doctor.dict(exclude_unset=True)

        # Update the doctor record
        for key, value in update_data.items():
            if hasattr(db_doctor, key) and value is not None:
                setattr(db_doctor, key, value)

        if "is_active" in update_data:
            db_user = get_user(db, db_doctor.user_id)
            if db_user:
                db_user.is_active = update_data["is_active"]

        db.commit()
        db.refresh(db_doctor)

    return db_doctor


def delete_doctor(db: Session, doctor_id: int):
    db_doctor = get_doctor(db, doctor_id)
    if db_doctor:
        db_doctor.is_active = False

        db_user = get_user(db, db_doctor.user_id)
        if db_user:
            db_user.is_active = False

        db.commit()
        return True
    return False


def get_doctor_by_user_id(db: Session, user_id: int):
    return db.query(models.Doctor).filter(models.Doctor.user_id == user_id).first()
