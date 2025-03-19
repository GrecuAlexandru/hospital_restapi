from sqlalchemy.orm import Session
from .. import models, schemas


def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Patient).offset(skip).limit(limit).all()


def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()


def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(
        first_name=patient.first_name,
        last_name=patient.last_name,
        age=patient.age,
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient


def update_patient(db: Session, patient_id: int, patient: schemas.PatientUpdate):
    db_patient = get_patient(db, patient_id)

    # Update only provided fields
    update_data = patient.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_patient, key, value)

    db.commit()
    db.refresh(db_patient)
    return db_patient


def delete_patient(db: Session, patient_id: int):
    db_patient = get_patient(db, patient_id)
    if db_patient:
        db_patient.is_active = False
        db.commit()
        return True
    return False
