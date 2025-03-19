from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..dependencies import get_db
from ..auth_utils import get_current_user_by_email, check_doctor_or_manager

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[schemas.Patient])
def read_patients(
    skip: int = 0,
    limit: int = 100,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Get all patients.

    Only doctors and general managers have access to this endpoint.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_doctor_or_manager(current_user)

    patients = crud.patients.get_patients(db, skip=skip, limit=limit)
    return patients


@router.post("/", response_model=schemas.Patient)
def create_patient(
    patient: schemas.PatientCreate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Create a new patient record.

    Only doctors and general managers have access to this endpoint.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_doctor_or_manager(current_user)

    return crud.patients.create_patient(db=db, patient=patient)


@router.get("/{patient_id}", response_model=schemas.Patient)
def read_patient(
    patient_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Get a specific patient by ID.

    Only doctors and general managers have access to this endpoint.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_doctor_or_manager(current_user)

    db_patient = crud.patients.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient


@router.put("/{patient_id}", response_model=schemas.Patient)
def update_patient(
    patient_id: int,
    patient: schemas.PatientUpdate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Update a patient's information.

    Only doctors and general managers have access to this endpoint.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_doctor_or_manager(current_user)

    db_patient = crud.patients.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    updated_patient = crud.patients.update_patient(
        db, patient_id=patient_id, patient=patient
    )
    return updated_patient


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Delete (deactivate) a patient record.

    Only doctors and general managers have access to this endpoint.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_doctor_or_manager(current_user)

    db_patient = crud.patients.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")

    success = crud.patients.delete_patient(db, patient_id=patient_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete patient")
