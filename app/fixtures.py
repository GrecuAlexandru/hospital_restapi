from sqlalchemy.orm import Session
from . import models
from .auth_utils import get_password_hash


def create_initial_fixtures(db: Session):
    print("Creating initial database fixtures...")

    # Check if data already exists
    if db.query(models.User).count() > 0:
        print("Database already has data, skipping fixture creation")
        return

    # Create admin user
    admin = models.User(
        email="admin@hospital.com",
        hashed_password=get_password_hash("admin123"),
        full_name="Hospital Administrator",
        role="general_manager",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    print(f"Created admin user: {admin.email}")

    # Create doctors
    doctors_data = [
        {
            "email": "cardio@hospital.com",
            "password": "doctor123",
            "full_name": "Dr. Jane Cardio",
            "specialization": "Cardiology",
            "experience": 15,
        },
        {
            "email": "neuro@hospital.com",
            "password": "doctor123",
            "full_name": "Dr. John Neuro",
            "specialization": "Neurology",
            "experience": 12,
        },
        {
            "email": "dentist@hospital.com",
            "password": "doctor123",
            "full_name": "Dr. Mary Dental",
            "specialization": "Dentistry",
            "experience": 8,
        },
    ]

    created_doctors = []

    for doctor_data in doctors_data:
        # Create user
        user = models.User(
            email=doctor_data["email"],
            hashed_password=get_password_hash(doctor_data["password"]),
            full_name=doctor_data["full_name"],
            role="doctor",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create doctor
        doctor = models.Doctor(
            user_id=user.id,
            specialization=doctor_data["specialization"],
            experience=doctor_data["experience"],
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        created_doctors.append(doctor)
        print(f"Created doctor: {user.full_name}")

    # Create assistants
    assistants_data = [
        {
            "email": "assist1@hospital.com",
            "password": "assist123",
            "full_name": "Alex Assistant",
            "age": 28,
            "specialization": "Cardiology",
        },
        {
            "email": "assist2@hospital.com",
            "password": "assist123",
            "full_name": "Sam Support",
            "age": 32,
            "specialization": "General",
        },
        {
            "email": "assist3@hospital.com",
            "password": "assist123",
            "full_name": "Taylor Helper",
            "age": 25,
            "specialization": "Dental",
        },
    ]

    created_assistants = []

    for assistant_data in assistants_data:
        # Create user
        user = models.User(
            email=assistant_data["email"],
            hashed_password=get_password_hash(assistant_data["password"]),
            full_name=assistant_data["full_name"],
            role="assistant",
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Create assistant
        assistant = models.Assistant(
            user_id=user.id,
            age=assistant_data["age"],
            specialization=assistant_data["specialization"],
        )
        db.add(assistant)
        db.commit()
        db.refresh(assistant)
        created_assistants.append(assistant)
        print(f"Created assistant: {user.full_name}")

    # Create patients
    patients_data = [
        {
            "first_name": "James",
            "last_name": "Smith",
            "age": 45,
            "doctor_id": created_doctors[0].id,
        },
        {
            "first_name": "Sarah",
            "last_name": "Johnson",
            "age": 32,
            "doctor_id": created_doctors[0].id,
        },
        {
            "first_name": "Michael",
            "last_name": "Williams",
            "age": 58,
            "doctor_id": created_doctors[1].id,
        },
        {
            "first_name": "Emily",
            "last_name": "Brown",
            "age": 27,
            "doctor_id": created_doctors[1].id,
        },
        {
            "first_name": "Robert",
            "last_name": "Jones",
            "age": 41,
            "doctor_id": created_doctors[2].id,
        },
    ]

    created_patients = []

    for patient_data in patients_data:
        patient = models.Patient(
            first_name=patient_data["first_name"],
            last_name=patient_data["last_name"],
            age=patient_data["age"],
            doctor_id=patient_data["doctor_id"],
            is_active=True,
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        created_patients.append(patient)
        print(f"Created patient: {patient.first_name} {patient.last_name}")

    # Create some treatments
    treatments_data = [
        {
            "name": "Blood Pressure Monitoring",
            "description": "Regular monitoring of blood pressure 3 times daily",
            "doctor_id": created_doctors[0].id,
            "patient_id": created_patients[0].id,
        },
        {
            "name": "Medication Schedule",
            "description": "Administration of prescribed medications at specified times",
            "doctor_id": created_doctors[0].id,
            "patient_id": created_patients[1].id,
        },
        {
            "name": "Physical Therapy",
            "description": "Daily mobility exercises as prescribed",
            "doctor_id": created_doctors[1].id,
            "patient_id": created_patients[2].id,
        },
        {
            "name": "Dental Cleaning",
            "description": "Weekly deep cleaning and checkup",
            "doctor_id": created_doctors[2].id,
            "patient_id": created_patients[4].id,
        },
    ]

    created_treatments = []

    for treatment_data in treatments_data:
        treatment = models.Treatment(
            name=treatment_data["name"],
            description=treatment_data["description"],
            doctor_id=treatment_data["doctor_id"],
            patient_id=treatment_data["patient_id"],
            is_active=True,
        )
        db.add(treatment)
        db.commit()
        db.refresh(treatment)
        created_treatments.append(treatment)
        print(f"Created treatment: {treatment.name}")

    # Create patient-assistant assignments
    assignments_data = [
        {
            "patient_id": created_patients[0].id,
            "assistant_id": created_assistants[0].id,
            "assigned_by_doctor_id": created_doctors[0].id,
        },
        {
            "patient_id": created_patients[1].id,
            "assistant_id": created_assistants[0].id,
            "assigned_by_doctor_id": created_doctors[0].id,
        },
        {
            "patient_id": created_patients[2].id,
            "assistant_id": created_assistants[1].id,
            "assigned_by_doctor_id": created_doctors[1].id,
        },
        {
            "patient_id": created_patients[4].id,
            "assistant_id": created_assistants[2].id,
            "assigned_by_doctor_id": created_doctors[2].id,
        },
    ]

    for assignment_data in assignments_data:
        assignment = models.PatientAssistant(
            patient_id=assignment_data["patient_id"],
            assistant_id=assignment_data["assistant_id"],
            assigned_by_doctor_id=assignment_data["assigned_by_doctor_id"],
            is_active=True,
        )
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        print(f"Created patient-assistant assignment: {assignment.id}")

    # Create some treatment applications
    applications_data = [
        {
            "treatment_id": created_treatments[0].id,
            "assistant_id": created_assistants[0].id,
            "notes": "Patient showed normal blood pressure readings",
        },
        {
            "treatment_id": created_treatments[1].id,
            "assistant_id": created_assistants[0].id,
            "notes": "All medications administered on schedule",
        },
        {
            "treatment_id": created_treatments[2].id,
            "assistant_id": created_assistants[1].id,
            "notes": "Patient completed all exercises successfully",
        },
    ]

    for application_data in applications_data:
        application = models.TreatmentApplication(
            treatment_id=application_data["treatment_id"],
            assistant_id=application_data["assistant_id"],
            notes=application_data["notes"],
        )
        db.add(application)
        db.commit()
        db.refresh(application)
        print(f"Created treatment application: {application.id}")

    print("Database fixtures created successfully")
