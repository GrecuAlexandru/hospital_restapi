from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from collections import defaultdict

from .. import crud, models, schemas
from ..dependencies import get_db
from ..auth_utils import get_current_user_by_email, check_general_manager

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Report not found"}},
)


@router.get("/doctors-patients", response_model=Dict[str, Any])
def get_doctors_patients_report(
    current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Get a report of all doctors and their associated patients with statistics.
    Only accessible by general managers.
    """
    if not current_user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    current_user = get_current_user_by_email(db, current_user_email)

    # Check if user is general_manager
    if current_user.role != "general_manager":
        raise HTTPException(
            status_code=403, detail="Only general managers can access this report"
        )

    # Get all active doctors with their user information
    doctors_query = (
        db.query(models.Doctor, models.User)
        .join(models.User, models.Doctor.user_id == models.User.id)
        .filter(models.User.is_active == True)
        .all()
    )

    report = {
        "doctors": [],
        "statistics": {
            "total_doctors": 0,
            "total_patients": 0,
            "patients_per_doctor": {},
            "treatments_per_doctor": {},
            "avg_patients_per_doctor": 0,
        },
    }

    doctor_treatment_counts = {}
    all_patients_count = 0

    # Process each doctor and their patients
    for doctor_obj, user_obj in doctors_query:
        doctor_id = doctor_obj.id

        # Get patients for this doctor
        patients = (
            db.query(models.Patient)
            .filter(
                models.Patient.doctor_id == doctor_id, models.Patient.is_active == True
            )
            .all()
        )

        # Get treatments created by this doctor
        treatments = (
            db.query(models.Treatment)
            .filter(models.Treatment.doctor_id == doctor_id)
            .all()
        )

        doctor_data = {
            "id": doctor_id,
            "name": user_obj.full_name,
            "email": user_obj.email,
            "specialization": (
                doctor_obj.specialization
                if hasattr(doctor_obj, "specialization")
                else ""
            ),
            "patients": [],
            "patient_count": len(patients),
            "treatment_count": len(treatments),
        }

        # Add patient details
        for patient in patients:
            doctor_data["patients"].append(
                {
                    "id": patient.id,
                    "name": f"{patient.first_name} {patient.last_name}",
                }
            )

        report["doctors"].append(doctor_data)
        doctor_treatment_counts[doctor_id] = len(treatments)
        all_patients_count += len(patients)

    # Calculate statistics
    total_doctors = len(doctors_query)
    report["statistics"]["total_doctors"] = total_doctors
    report["statistics"]["total_patients"] = all_patients_count

    if total_doctors > 0:
        report["statistics"]["avg_patients_per_doctor"] = round(
            all_patients_count / total_doctors, 2
        )

    # Add patient count per doctor
    for doc in report["doctors"]:
        report["statistics"]["patients_per_doctor"][str(doc["id"])] = doc[
            "patient_count"
        ]
        report["statistics"]["treatments_per_doctor"][str(doc["id"])] = doc[
            "treatment_count"
        ]

    return report


@router.get("/patients/{patient_id}/treatments", response_model=List[Dict[str, Any]])
def get_patient_treatments_report(
    patient_id: int, current_user_email: str = None, db: Session = Depends(get_db)
):
    """
    Get a report with all treatments applied to a specific patient.
    Only accessible by general managers and the patient's doctor.
    """
    if not current_user_email:
        raise HTTPException(status_code=401, detail="Authentication required")

    current_user = get_current_user_by_email(db, current_user_email)

    # Check if patient exists
    patient = crud.patients.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check permissions
    if current_user.role == "doctor":
        # If user is a doctor, they can only access their own patients
        doctor = crud.doctors.get_doctor_by_user_id(db, current_user.id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor profile not found")

        # The key fix: check if this patient belongs to this doctor
        if patient.doctor_id != doctor.id:
            raise HTTPException(
                status_code=403,
                detail="You can only access treatment reports for your own patients",
            )
    elif current_user.role != "general_manager":
        raise HTTPException(
            status_code=403,
            detail="Only doctors and general managers can access this report",
        )

    # Get patient treatment report from crud
    return crud.reports.get_patient_treatment_report(db, patient_id)
