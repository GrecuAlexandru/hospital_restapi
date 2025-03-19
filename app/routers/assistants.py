from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..dependencies import get_db
from ..auth_utils import (
    get_current_user_by_email,
    check_general_manager,
    check_doctor_or_manager,
    check_assistant,
)

router = APIRouter(
    prefix="/assistants",
    tags=["assistants"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[schemas.AssistantList])
def read_assistants(
    skip: int = 0,
    limit: int = 100,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Get all assistants.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    assistants = crud.assistants.get_assistants(db, skip=skip, limit=limit)
    return assistants


@router.post("/", response_model=schemas.Assistant)
def create_assistant(
    assistant: schemas.AssistantCreate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Create a new assistant.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    # Check if email already exists
    db_user = crud.users.get_user_by_email(db, email=assistant.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.assistants.create_assistant(db=db, assistant=assistant)


@router.get("/{assistant_id}", response_model=schemas.Assistant)
def read_assistant(
    assistant_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Get a specific assistant by ID.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    db_assistant = crud.assistants.get_assistant(db, assistant_id=assistant_id)
    if db_assistant is None:
        raise HTTPException(status_code=404, detail="Assistant not found")
    return db_assistant


@router.put("/{assistant_id}", response_model=schemas.Assistant)
def update_assistant(
    assistant_id: int,
    assistant: schemas.AssistantUpdate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Update an assistant's information.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    db_assistant = crud.assistants.get_assistant(db, assistant_id=assistant_id)
    if db_assistant is None:
        raise HTTPException(status_code=404, detail="Assistant not found")

    updated_assistant = crud.assistants.update_assistant(
        db, assistant_id=assistant_id, assistant=assistant
    )
    return updated_assistant


@router.delete("/{assistant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assistant(
    assistant_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Delete (deactivate) an assistant.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    db_assistant = crud.assistants.get_assistant(db, assistant_id=assistant_id)
    if db_assistant is None:
        raise HTTPException(status_code=404, detail="Assistant not found")

    success = crud.assistants.delete_assistant(db, assistant_id=assistant_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete assistant")


# Patient Assignment endpoints
@router.get("/patients/assignments", response_model=List[schemas.PatientAssistant])
def get_patient_assignments(
    patient_id: int = None,
    assistant_id: int = None,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Get all patient-assistant assignments.
    Filter by patient_id or assistant_id if provided.

    Only doctors and general managers have full access.
    Assistants can only view their own assignments.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)

        # If assistant, they can only see their own assignments
        if current_user.role == "assistant":
            db_assistant = (
                db.query(models.Assistant)
                .filter(models.Assistant.user_id == current_user.id)
                .first()
            )
            if not db_assistant:
                raise HTTPException(
                    status_code=404, detail="Assistant profile not found"
                )
            assistant_id = db_assistant.id

    assignments = crud.assistants.get_patient_assistants(
        db, patient_id=patient_id, assistant_id=assistant_id
    )
    return assignments


@router.post("/patients/assign", response_model=schemas.PatientAssistant)
def assign_patient_to_assistant(
    assignment: schemas.PatientAssistantCreate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Assign a patient to an assistant.
    Only doctors and general managers can make assignments.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_doctor_or_manager(current_user)

        # Get doctor ID if it's a doctor making the assignment
        doctor_id = None
        if current_user.role == "doctor":
            db_doctor = (
                db.query(models.Doctor)
                .filter(models.Doctor.user_id == current_user.id)
                .first()
            )
            if not db_doctor:
                raise HTTPException(status_code=404, detail="Doctor profile not found")
            doctor_id = db_doctor.id
        elif current_user.role == "general_manager":
            # For general manager, use first available doctor or create a system doctor
            db_doctor = db.query(models.Doctor).first()
            if not db_doctor:
                # Create a system doctor if none exists
                raise HTTPException(status_code=404, detail="No doctors in system")
            doctor_id = db_doctor.id

    # Verify patient exists
    patient = crud.patients.get_patient(db, patient_id=assignment.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Verify assistant exists
    assistant = crud.assistants.get_assistant(db, assistant_id=assignment.assistant_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="Assistant not found")

    return crud.assistants.assign_patient_to_assistant(
        db, assignment=assignment, doctor_id=doctor_id
    )


@router.put(
    "/patients/assignments/{assignment_id}", response_model=schemas.PatientAssistant
)
def update_assignment(
    assignment_id: int,
    update: schemas.PatientAssistantUpdate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Update a patient-assistant assignment.
    Only doctors and general managers can update assignments.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_doctor_or_manager(current_user)

    updated_assignment = crud.assistants.update_patient_assistant_assignment(
        db, assignment_id, update
    )
    if not updated_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    return updated_assignment


# Treatment application endpoints
@router.post("/treatments/apply", response_model=schemas.TreatmentApplication)
def apply_treatment(
    application: schemas.TreatmentApplicationCreate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Record a treatment application by an assistant.
    Only assistants can apply treatments.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_assistant(current_user)

        # Get assistant ID
        db_assistant = (
            db.query(models.Assistant)
            .filter(models.Assistant.user_id == current_user.id)
            .first()
        )
        if not db_assistant:
            raise HTTPException(status_code=404, detail="Assistant profile not found")

        # Verify the assistant is assigned to the patient receiving this treatment
        treatment = (
            db.query(models.Treatment)
            .filter(models.Treatment.id == application.treatment_id)
            .first()
        )
        if not treatment:
            raise HTTPException(status_code=404, detail="Treatment not found")

        # Check if assistant is assigned to this patient
        assignment = (
            db.query(models.PatientAssistant)
            .filter(
                models.PatientAssistant.assistant_id == db_assistant.id,
                models.PatientAssistant.patient_id == treatment.patient_id,
                models.PatientAssistant.is_active == True,
            )
            .first()
        )

        if not assignment:
            raise HTTPException(
                status_code=403,
                detail="You are not assigned to the patient receiving this treatment",
            )

        return crud.treatments.apply_treatment(db, application, db_assistant.id)


@router.get(
    "/treatments/applications", response_model=List[schemas.TreatmentApplication]
)
def get_treatment_applications(
    treatment_id: int = None,
    assistant_id: int = None,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Get treatment applications.
    Filter by treatment_id or assistant_id if provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)

        # If assistant, they can only see their own applications
        if current_user.role == "assistant":
            db_assistant = (
                db.query(models.Assistant)
                .filter(models.Assistant.user_id == current_user.id)
                .first()
            )
            if not db_assistant:
                raise HTTPException(
                    status_code=404, detail="Assistant profile not found"
                )
            assistant_id = db_assistant.id

    applications = crud.treatments.get_treatment_applications(
        db, treatment_id=treatment_id, assistant_id=assistant_id
    )
    return applications
