from sqlalchemy.orm import Session
from .. import models, schemas
from .base import get_password_hash
from .users import get_user


def get_assistant(db: Session, assistant_id: int):
    return (
        db.query(models.Assistant).filter(models.Assistant.id == assistant_id).first()
    )


def get_assistants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Assistant).offset(skip).limit(limit).all()


def create_assistant(db: Session, assistant: schemas.AssistantCreate):
    # First create the user
    hashed_password = get_password_hash(assistant.password)
    db_user = models.User(
        email=assistant.email,
        hashed_password=hashed_password,
        full_name=assistant.full_name,
        role="assistant",
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Then create the assistant
    db_assistant = models.Assistant(
        user_id=db_user.id,
        age=assistant.age,
        specialization=assistant.specialization,
    )
    db.add(db_assistant)
    db.commit()
    db.refresh(db_assistant)
    return db_assistant


def update_assistant(
    db: Session, assistant_id: int, assistant: schemas.AssistantUpdate
):
    db_assistant = get_assistant(db, assistant_id)
    if db_assistant:
        update_data = assistant.dict(exclude_unset=True)

        # Update the assistant record
        for key, value in update_data.items():
            if hasattr(db_assistant, key) and value is not None:
                setattr(db_assistant, key, value)

        if "is_active" in update_data:
            db_user = get_user(db, db_assistant.user_id)
            if db_user:
                db_user.is_active = update_data["is_active"]

        db.commit()
        db.refresh(db_assistant)

    return db_assistant


def delete_assistant(db: Session, assistant_id: int):
    db_assistant = get_assistant(db, assistant_id)
    if db_assistant:
        # Deactivate instead of deleting
        db_user = get_user(db, db_assistant.user_id)
        if db_user:
            db_user.is_active = False

        db.commit()
        return True
    return False


def get_assistant_by_user_id(db: Session, user_id: int):
    return (
        db.query(models.Assistant).filter(models.Assistant.user_id == user_id).first()
    )


def get_patients_by_assistant(db: Session, assistant_id: int):
    assignments = (
        db.query(models.PatientAssistant)
        .filter(
            models.PatientAssistant.assistant_id == assistant_id,
            models.PatientAssistant.is_active == True,
        )
        .all()
    )

    patient_ids = [assignment.patient_id for assignment in assignments]
    if not patient_ids:
        return []

    return db.query(models.Patient).filter(models.Patient.id.in_(patient_ids)).all()


# Patient-Assistant Assignment CRUD
def get_patient_assistants(
    db: Session, patient_id: int = None, assistant_id: int = None
):
    query = db.query(models.PatientAssistant)

    if patient_id:
        query = query.filter(models.PatientAssistant.patient_id == patient_id)

    if assistant_id:
        query = query.filter(models.PatientAssistant.assistant_id == assistant_id)

    return query.all()


def assign_patient_to_assistant(
    db: Session, assignment: schemas.PatientAssistantCreate, doctor_id: int
):
    db_assignment = models.PatientAssistant(
        patient_id=assignment.patient_id,
        assistant_id=assignment.assistant_id,
        assigned_by_doctor_id=doctor_id,
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def update_patient_assistant_assignment(
    db: Session, assignment_id: int, update: schemas.PatientAssistantUpdate
):
    db_assignment = (
        db.query(models.PatientAssistant)
        .filter(models.PatientAssistant.id == assignment_id)
        .first()
    )

    if db_assignment:
        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_assignment, key, value)

        db.commit()
        db.refresh(db_assignment)

    return db_assignment
