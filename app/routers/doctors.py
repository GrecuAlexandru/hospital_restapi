from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import crud, schemas
from ..dependencies import get_db
from ..auth_utils import get_current_user_by_email, check_general_manager

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=List[schemas.DoctorList])
def read_doctors(
    skip: int = 0,
    limit: int = 100,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Get all doctors.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    doctors = crud.doctors.get_doctors(db, skip=skip, limit=limit)
    return doctors


@router.post("/", response_model=schemas.Doctor)
def create_doctor(
    doctor: schemas.DoctorCreate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Create a new doctor.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    # Check if email already exists
    db_user = crud.users.get_user_by_email(db, email=doctor.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.doctors.create_doctor(db=db, doctor=doctor)


@router.get("/{doctor_id}", response_model=schemas.Doctor)
def read_doctor(
    doctor_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Get a specific doctor by ID.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    db_doctor = crud.doctors.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor


@router.put("/{doctor_id}", response_model=schemas.Doctor)
def update_doctor(
    doctor_id: int,
    doctor: schemas.DoctorUpdate,
    current_user_email: str = None,
    db: Session = Depends(get_db),
):
    """
    Update a doctor's information.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    db_doctor = crud.doctors.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")

    updated_doctor = crud.doctors.update_doctor(db, doctor_id=doctor_id, doctor=doctor)
    return updated_doctor


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_doctor(
    doctor_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Delete (deactivate) a doctor.

    Only general managers have access to this endpoint if current_user_email is provided.
    """
    if current_user_email:
        current_user = get_current_user_by_email(db, current_user_email)
        check_general_manager(current_user)

    db_doctor = crud.doctors.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")

    success = crud.doctors.delete_doctor(db, doctor_id=doctor_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete doctor")
