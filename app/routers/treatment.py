from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, schemas
from ..dependencies import get_db
from ..auth_utils import get_current_user_by_email, check_doctor_or_manager

router = APIRouter(
    prefix="/treatments",
    tags=["treatments"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Treatment)
def create_treatment(
    treatment: schemas.TreatmentCreate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Create a new treatment.
    Doctors can only create treatments for their own patients.
    General managers can create treatments for any patient.
    """
    if not current_user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    current_user = get_current_user_by_email(db, current_user_email)

    # Check if user is doctor or general manager
    if current_user.role == "doctor":
        # If user is doctor, get their doctor profile
        doctor = crud.doctors.get_doctor_by_user_id(db, current_user.id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor profile not found")

        # Check if patient belongs to this doctor
        patient = crud.patients.get_patient(db, treatment.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Print debug info to help diagnose issues
        print(f"Patient doctor_id: {patient.doctor_id}, Doctor id: {doctor.id}")

        if patient.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only create treatments for your own patients",
            )

        return crud.treatments.create_treatment(
            db=db, treatment=treatment, doctor_id=doctor.id
        )
    elif current_user.role == "general_manager":
        # Get first doctor to assign as creator (this is temporary)
        doctor = crud.doctors.get_doctors(db, limit=1)[0]
        return crud.treatments.create_treatment(
            db=db, treatment=treatment, doctor_id=doctor.id
        )
    else:
        raise HTTPException(
            status_code=403,
            detail="Only doctors and general managers can create treatments",
        )


@router.get("/", response_model=List[schemas.Treatment])
def read_treatments(
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Get all treatments with optional filtering.
    Only doctors and general managers have access to this endpoint.
    """
    if not current_user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    current_user = get_current_user_by_email(db, current_user_email)

    # Get treatments with filters
    treatments = crud.treatments.get_treatments(
        db=db,
        patient_id=patient_id,
        doctor_id=doctor_id,
        skip=skip,
        limit=limit,
        current_user=current_user,
    )

    return treatments


@router.get("/{treatment_id}", response_model=schemas.Treatment)
def read_treatment(
    treatment_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Get a specific treatment by ID.
    """
    if not current_user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    current_user = get_current_user_by_email(db, current_user_email)

    treatment = crud.treatments.get_treatment(db, treatment_id)
    if treatment is None:
        raise HTTPException(status_code=404, detail="Treatment not found")

    # Check permissions
    if current_user.role == "doctor":
        doctor = crud.doctors.get_doctor_by_user_id(db, current_user.id)
        if doctor and treatment.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view treatments for your own patients",
            )
    elif current_user.role == "assistant":
        assistant = crud.assistants.get_assistant_by_user_id(db, current_user.id)
        if assistant:
            assigned_patients = crud.assistants.get_patients_by_assistant(
                db, assistant.id
            )
            patient_ids = [p.id for p in assigned_patients]
            if treatment.patient_id not in patient_ids:
                raise HTTPException(
                    status_code=403,
                    detail="You can only view treatments for patients assigned to you",
                )
    elif current_user.role != "general_manager":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return treatment


@router.put("/{treatment_id}", response_model=schemas.Treatment)
def update_treatment(
    treatment_id: int,
    treatment: schemas.TreatmentUpdate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Update a treatment.
    Only doctors and general managers have access to this endpoint.
    """
    if not current_user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    current_user = get_current_user_by_email(db, current_user_email)
    check_doctor_or_manager(current_user)

    # Get treatment
    db_treatment = crud.treatments.get_treatment(db, treatment_id)
    if db_treatment is None:
        raise HTTPException(status_code=404, detail="Treatment not found")

    # If doctor, check if treatment was created by this doctor
    if current_user.role == "doctor":
        doctor = crud.doctors.get_doctor_by_user_id(db, current_user.id)
        if doctor and db_treatment.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403, detail="You can only update treatments you created"
            )

    return crud.treatments.update_treatment(db, treatment_id, treatment)


@router.delete("/{treatment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_treatment(
    treatment_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Delete a treatment.
    Only doctors and general managers have access to this endpoint.
    """
    if not current_user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    current_user = get_current_user_by_email(db, current_user_email)
    check_doctor_or_manager(current_user)

    # Get treatment
    db_treatment = crud.treatments.get_treatment(db, treatment_id)
    if db_treatment is None:
        raise HTTPException(status_code=404, detail="Treatment not found")

    # If doctor, check if treatment was created by this doctor
    if current_user.role == "doctor":
        doctor = crud.get_doctor_by_user_id(db, current_user.id)
        if doctor and db_treatment.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403, detail="You can only delete treatments you created"
            )

    # Check if treatment has been applied
    applications = crud.treatments.get_treatment_applications(db, treatment_id)
    if applications:
        raise HTTPException(
            status_code=400, detail="Cannot delete treatment that has been applied"
        )

    crud.treatments.delete_treatment(db, treatment_id)
