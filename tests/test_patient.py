from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import SessionLocal
from app import models
from app.auth_utils import get_password_hash

# Create test client
client = TestClient(app)


def create_test_doctor():
    with SessionLocal() as db:
        # Check if doctor user already exists
        user = (
            db.query(models.User)
            .filter(models.User.email == "testdoctor@hospital.com")
            .first()
        )
        if not user:
            user = models.User(
                email="testdoctor@hospital.com",
                hashed_password=get_password_hash("doctor123"),
                full_name="Test Doctor",
                role="doctor",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create doctor record
            doctor = models.Doctor(user_id=user.id)
            db.add(doctor)
            db.commit()
            db.refresh(doctor)
            print(f"Created test doctor: {user.email}")
            return doctor
        else:
            # Get doctor record
            doctor = (
                db.query(models.Doctor).filter(models.Doctor.user_id == user.id).first()
            )
            if not doctor:
                doctor = models.Doctor(user_id=user.id)
                db.add(doctor)
                db.commit()
                db.refresh(doctor)
            print(f"Using existing test doctor: {user.email}")
            return doctor


def cleanup_test_patient():
    with SessionLocal() as db:
        existing_patient = (
            db.query(models.Patient)
            .filter(
                models.Patient.first_name == "Test",
                models.Patient.last_name == "Patient",
            )
            .first()
        )

        if existing_patient:
            print(
                f"Deleting existing test patient: {existing_patient.first_name} {existing_patient.last_name}"
            )
            db.delete(existing_patient)
            db.commit()


def test_create_patient():
    # Create test doctor if not exists
    create_test_doctor()

    # Clean up any existing test patient
    cleanup_test_patient()

    # Create patient data
    patient_data = {
        "first_name": "Test",
        "last_name": "Patient",
        "age": 25,
    }

    # Create patient as doctor
    response = client.post(
        "/patients/",
        json=patient_data,
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert response.status_code == 200
    data = response.json()
    print(f"Created patient: {data}")
    assert data["first_name"] == patient_data["first_name"]
    assert data["last_name"] == patient_data["last_name"]
    assert "id" in data

    patient_id = data["id"]
    return patient_id


def test_read_patients():
    # Ensure doctor exists
    create_test_doctor()

    response = client.get(
        "/patients/", params={"current_user_email": "testdoctor@hospital.com"}
    )

    assert response.status_code == 200
    patients = response.json()
    print(f"Retrieved {len(patients)} patients")
    assert isinstance(patients, list)
    return patients


def test_read_specific_patient():
    # First create a patient to ensure we have one to read
    patient_id = test_create_patient()

    # Now read that specific patient
    response = client.get(
        f"/patients/{patient_id}",
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert response.status_code == 200
    patient = response.json()
    print(f"Retrieved patient: {patient}")
    assert patient["id"] == patient_id
    assert patient["first_name"] == "Test"
    assert patient["last_name"] == "Patient"
    return patient


def test_delete_patient():
    # First create a patient to delete
    patient_id = test_create_patient()

    # Delete the patient
    response = client.delete(
        f"/patients/{patient_id}",
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert response.status_code == 204

    # Verify the patient is deactivated
    response = client.get(
        f"/patients/{patient_id}",
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    patient = response.json()
    print(f"Patient after deletion: {patient}")
    assert patient["is_active"] == False


def run_patient_tests():
    print("Running patient management tests...\n")

    print("\n1. Creating test doctor:")
    create_test_doctor()

    print("\n2. Testing patient creation:")
    patient_id = test_create_patient()

    print("\n3. Testing reading all patients:")
    patients = test_read_patients()

    print("\n4. Testing reading specific patient:")
    patient = test_read_specific_patient()

    print("\n5. Testing deleting patient:")
    test_delete_patient()

    print("\nAll patient management tests completed successfully!")


if __name__ == "__main__":
    run_patient_tests()
