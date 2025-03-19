from sqlalchemy.orm import Session
from .. import models, schemas
from .doctors import get_doctor_by_user_id
from .assistants import get_assistant_by_user_id


def get_treatment(db: Session, treatment_id: int):
    return (
        db.query(models.Treatment).filter(models.Treatment.id == treatment_id).first()
    )


def get_treatments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    doctor_id: int = None,
    patient_id: int = None,
    active_only: bool = True,
    current_user=None,
):
    query = db.query(models.Treatment)

    # Apply filters based on current user's role
    if current_user:
        if current_user.role == "doctor":
            # Doctors can only see treatments they created
            doctor = get_doctor_by_user_id(db, current_user.id)
            if doctor:
                query = query.filter(models.Treatment.doctor_id == doctor.id)
            else:
                # If doctor profile not found, return empty list
                return []
        elif current_user.role == "assistant":
            # Assistants can only see treatments for patients assigned to them
            assistant = get_assistant_by_user_id(db, current_user.id)
            if assistant:
                # Get patient IDs assigned to this assistant
                assignments = (
                    db.query(models.PatientAssistant)
                    .filter(
                        models.PatientAssistant.assistant_id == assistant.id,
                        models.PatientAssistant.is_active == True,
                    )
                    .all()
                )

                patient_ids = [assignment.patient_id for assignment in assignments]
                if patient_ids:
                    query = query.filter(models.Treatment.patient_id.in_(patient_ids))
                else:
                    # If no assigned patients, return empty list
                    return []
            else:
                # If assistant profile not found, return empty list
                return []

    # Apply additional filters
    if doctor_id:
        query = query.filter(models.Treatment.doctor_id == doctor_id)

    if patient_id:
        query = query.filter(models.Treatment.patient_id == patient_id)

    if active_only:
        query = query.filter(models.Treatment.is_active == True)

    return query.offset(skip).limit(limit).all()


def create_treatment(db: Session, treatment: schemas.TreatmentCreate, doctor_id: int):
    db_treatment = models.Treatment(
        name=treatment.name,
        description=treatment.description,
        doctor_id=doctor_id,
        patient_id=treatment.patient_id,
    )
    db.add(db_treatment)
    db.commit()
    db.refresh(db_treatment)
    return db_treatment


def update_treatment(
    db: Session, treatment_id: int, treatment: schemas.TreatmentUpdate
):
    db_treatment = get_treatment(db, treatment_id)

    if db_treatment:
        update_data = treatment.dict(exclude_unset=True)

        for key, value in update_data.items():
            setattr(db_treatment, key, value)

        db.commit()
        db.refresh(db_treatment)

    return db_treatment


def delete_treatment(db: Session, treatment_id: int):
    db_treatment = get_treatment(db, treatment_id)

    if db_treatment:
        db_treatment.is_active = False
        db.commit()
        return True

    return False


def apply_treatment(
    db: Session, application: schemas.TreatmentApplicationCreate, assistant_id: int
):
    db_application = models.TreatmentApplication(
        treatment_id=application.treatment_id,
        assistant_id=assistant_id,
        notes=application.notes,
    )
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


def get_treatment_applications(
    db: Session, treatment_id: int = None, assistant_id: int = None
):
    query = db.query(models.TreatmentApplication)

    if treatment_id:
        query = query.filter(models.TreatmentApplication.treatment_id == treatment_id)

    if assistant_id:
        query = query.filter(models.TreatmentApplication.assistant_id == assistant_id)

    return query.all()


def get_treatment_application(db: Session, application_id: int):
    return (
        db.query(models.TreatmentApplication)
        .filter(models.TreatmentApplication.id == application_id)
        .first()
    )


def update_treatment_application(
    db: Session, application_id: int, update: schemas.TreatmentApplicationUpdate
):
    db_application = get_treatment_application(db, application_id)

    if db_application:
        update_data = update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_application, key, value)

        db.commit()
        db.refresh(db_application)

    return db_application
