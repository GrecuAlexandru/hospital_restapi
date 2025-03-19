from sqlalchemy.orm import Session
from .. import models
from .patients import get_patient
from .treatments import get_treatments


def get_patient_treatment_report(db: Session, patient_id: int):
    treatments = get_treatments(db, patient_id=patient_id, active_only=False)

    report = []
    for treatment in treatments:
        applications = (
            db.query(models.TreatmentApplication)
            .filter(models.TreatmentApplication.treatment_id == treatment.id)
            .all()
        )

        report.append({"treatment": treatment, "applications": applications})

    return report


def get_doctor_patient_statistics(db: Session):
    doctors = db.query(models.Doctor).all()

    stats = []
    total_patients = db.query(models.Patient).count()
    total_treatments = db.query(models.Treatment).count()

    for doctor in doctors:
        # Get user details
        user = db.query(models.User).filter(models.User.id == doctor.user_id).first()

        # Count patients
        patient_count = (
            db.query(models.Patient)
            .filter(models.Patient.doctor_id == doctor.id)
            .count()
        )

        # Count treatments
        treatment_count = (
            db.query(models.Treatment)
            .filter(models.Treatment.doctor_id == doctor.id)
            .count()
        )

        # Get patients with details
        patients = (
            db.query(models.Patient).filter(models.Patient.doctor_id == doctor.id).all()
        )

        doctor_stats = {
            "doctor_id": doctor.id,
            "name": user.full_name if user else "Unknown",
            "email": user.email if user else "Unknown",
            "patient_count": patient_count,
            "treatment_count": treatment_count,
            "patients": patients,
        }

        stats.append(doctor_stats)

    return {
        "total_doctors": len(doctors),
        "total_patients": total_patients,
        "total_treatments": total_treatments,
        "doctors": stats,
    }


def get_doctor_patient_report(db: Session):
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
                    "email": patient.email,
                    "phone": patient.phone,
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
        report["statistics"]["patients_per_doctor"][doc["id"]] = doc["patient_count"]
        report["statistics"]["treatments_per_doctor"][doc["id"]] = doc[
            "treatment_count"
        ]

    return report


def get_patient_treatment_report(db: Session, patient_id: int):
    # Get the patient with all basic information
    patient = get_patient(db, patient_id)
    if not patient:
        return []

    # Get all treatments for this patient
    treatments = (
        db.query(models.Treatment)
        .filter(models.Treatment.patient_id == patient_id)
        .all()
    )

    report_data = []

    # Process each treatment
    for treatment in treatments:
        # Get treatment applications
        applications = (
            db.query(models.TreatmentApplication)
            .filter(models.TreatmentApplication.treatment_id == treatment.id)
            .all()
        )

        # Get doctor information
        doctor_query = (
            db.query(models.Doctor, models.User)
            .join(models.User, models.Doctor.user_id == models.User.id)
            .filter(models.Doctor.id == treatment.doctor_id)
            .first()
        )

        doctor_name = "Unknown"
        if doctor_query:
            doctor_obj, user_obj = doctor_query
            doctor_name = user_obj.full_name

        # Create treatment entry
        treatment_entry = {
            "id": treatment.id,
            "name": treatment.name,
            "description": treatment.description,
            "prescribed_by": doctor_name,
            "is_active": treatment.is_active,
            "applications": [],
        }

        # Add application details
        for app in applications:
            # Get assistant information
            assistant_query = (
                db.query(models.Assistant, models.User)
                .join(models.User, models.Assistant.user_id == models.User.id)
                .filter(models.Assistant.id == app.assistant_id)
                .first()
            )

            assistant_name = "Unknown"
            if assistant_query:
                assistant_obj, user_obj = assistant_query
                assistant_name = user_obj.full_name

            # Add application entry
            application_entry = {
                "id": app.id,
                "applied_by": assistant_name,
                "notes": app.notes,
            }

            treatment_entry["applications"].append(application_entry)

        report_data.append(treatment_entry)

    return report_data
