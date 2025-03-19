from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import SessionLocal
from app import models

# Create test client
client = TestClient(app)


def count_fixtures_in_db():
    """Count records in the database to verify fixtures were loaded."""
    with SessionLocal() as db:
        user_count = db.query(models.User).count()
        doctor_count = db.query(models.Doctor).count()
        patient_count = db.query(models.Patient).count()
        assistant_count = db.query(models.Assistant).count()
        treatment_count = db.query(models.Treatment).count()
        assignment_count = db.query(models.PatientAssistant).count()
        treatment_app_count = db.query(models.TreatmentApplication).count()

        return {
            "users": user_count,
            "doctors": doctor_count,
            "patients": patient_count,
            "assistants": assistant_count,
            "treatments": treatment_count,
            "assignments": assignment_count,
            "treatment_applications": treatment_app_count,
        }


def test_admin_user_exists():
    """Test that the admin user exists in the database."""
    with SessionLocal() as db:
        admin = (
            db.query(models.User)
            .filter(models.User.email == "admin@hospital.com")
            .first()
        )
        assert admin is not None
        assert admin.role == "general_manager"
        print(f"Admin user verified: {admin.email}")


def test_fixture_doctors():
    """Test that fixture doctors can be retrieved through the API."""
    response = client.get(
        "/doctors/", params={"current_user_email": "admin@hospital.com"}
    )
    assert response.status_code == 200
    doctors = response.json()
    assert len(doctors) >= 3  # At least 3 doctors from fixtures

    # Look for our fixture doctors
    doctor_emails = [doc["user"]["email"] for doc in doctors]
    expected_emails = [
        "cardio@hospital.com",
        "neuro@hospital.com",
        "dentist@hospital.com",
    ]

    for email in expected_emails:
        assert email in doctor_emails

    print(f"Found {len(doctors)} doctors in the system")


def test_fixture_patients():
    """Test that fixture patients can be retrieved through the API."""
    response = client.get(
        "/patients/", params={"current_user_email": "admin@hospital.com"}
    )
    assert response.status_code == 200
    patients = response.json()
    assert len(patients) >= 5  # At least 5 patients from fixtures

    # Check for some fixture patient names
    patient_full_names = [f"{p['first_name']} {p['last_name']}" for p in patients]
    expected_names = ["James Smith", "Sarah Johnson", "Michael Williams"]

    for name in expected_names:
        assert name in patient_full_names

    print(f"Found {len(patients)} patients in the system")


def test_fixture_treatments():
    """Test that fixture treatments can be retrieved through the API."""
    response = client.get(
        "/treatments/", params={"current_user_email": "admin@hospital.com"}
    )
    assert response.status_code == 200
    treatments = response.json()
    assert len(treatments) >= 4  # At least 4 treatments from fixtures

    # Check for fixture treatment names
    treatment_names = [t["name"] for t in treatments]
    expected_treatments = [
        "Blood Pressure Monitoring",
        "Medication Schedule",
        "Physical Therapy",
        "Dental Cleaning",
    ]

    for name in expected_treatments:
        assert name in treatment_names

    print(f"Found {len(treatments)} treatments in the system")


def test_fixture_assistants():
    """Test that fixture assistants can be retrieved through the API."""
    response = client.get(
        "/assistants/", params={"current_user_email": "admin@hospital.com"}
    )
    assert response.status_code == 200
    assistants = response.json()
    assert len(assistants) >= 3  # At least 3 assistants from fixtures

    # Check for fixture assistant emails
    assistant_emails = [a["user"]["email"] for a in assistants]
    expected_emails = [
        "assist1@hospital.com",
        "assist2@hospital.com",
        "assist3@hospital.com",
    ]

    for email in expected_emails:
        assert email in assistant_emails

    print(f"Found {len(assistants)} assistants in the system")


def run_fixture_tests():
    """Run all fixture tests."""
    print("\nRunning fixture tests...")
    print("\nDatabase record counts:")
    counts = count_fixtures_in_db()
    for entity, count in counts.items():
        print(f"- {entity}: {count}")

    print("\nTesting admin user:")
    test_admin_user_exists()

    print("\nTesting fixture doctors:")
    test_fixture_doctors()

    print("\nTesting fixture patients:")
    test_fixture_patients()

    print("\nTesting fixture treatments:")
    test_fixture_treatments()

    print("\nTesting fixture assistants:")
    test_fixture_assistants()

    print("\nAll fixture tests completed successfully!")


if __name__ == "__main__":
    run_fixture_tests()
