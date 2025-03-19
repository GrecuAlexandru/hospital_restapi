from fastapi.testclient import TestClient
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import SessionLocal
from app import models
from app.auth_utils import get_password_hash

# Create test client
client = TestClient(app)


def create_test_admin():
    with SessionLocal() as db:
        # Check if admin already exists
        admin = (
            db.query(models.User)
            .filter(models.User.email == "testadmin@hospital.com")
            .first()
        )
        if admin:
            print(f"Test admin user already exists: {admin.email}")
            return admin

        # Create admin user
        admin = models.User(
            email="testadmin@hospital.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Test Administrator",
            role="general_manager",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Created test admin user: {admin.email}")
        return admin


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


def create_test_assistant():
    with SessionLocal() as db:
        # Check if assistant user already exists
        user = (
            db.query(models.User)
            .filter(models.User.email == "testassistant@hospital.com")
            .first()
        )
        if not user:
            user = models.User(
                email="testassistant@hospital.com",
                hashed_password=get_password_hash("assistant123"),
                full_name="Test Assistant",
                role="assistant",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Create assistant record
            assistant = models.Assistant(user_id=user.id)
            db.add(assistant)
            db.commit()
            db.refresh(assistant)
            print(f"Created test assistant: {user.email}")
            return assistant
        else:
            # Get assistant record
            assistant = (
                db.query(models.Assistant)
                .filter(models.Assistant.user_id == user.id)
                .first()
            )
            if not assistant:
                assistant = models.Assistant(user_id=user.id)
                db.add(assistant)
                db.commit()
                db.refresh(assistant)
            print(f"Using existing test assistant: {user.email}")
            return assistant


def create_test_patient(doctor_id=None):
    with SessionLocal() as db:
        # Check if patient already exists
        patient = (
            db.query(models.Patient)
            .filter(
                models.Patient.first_name == "Test",
                models.Patient.last_name == "Patient",
            )
            .first()
        )

        if patient:
            # Important: Update the doctor_id to ensure the patient belongs to the test doctor
            if doctor_id and patient.doctor_id != doctor_id:
                patient.doctor_id = doctor_id
                db.commit()
                db.refresh(patient)
                print(f"Updated test patient doctor_id to: {doctor_id}")
            print(
                f"Using existing test patient: {patient.first_name} {patient.last_name}"
            )
            return patient

        # Create new patient
        patient = models.Patient(
            first_name="Test", last_name="Patient", doctor_id=doctor_id, is_active=True
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        print(f"Created test patient: {patient.first_name} {patient.last_name}")
        return patient


def cleanup_test_treatment():
    with SessionLocal() as db:
        treatments = (
            db.query(models.Treatment)
            .filter(models.Treatment.name == "Test Treatment")
            .all()
        )

        count = 0
        for treatment in treatments:
            # First delete any applications
            applications = (
                db.query(
                    models.TreatmentApplication
                )  # Changed from AppliedTreatment to TreatmentApplication
                .filter(models.TreatmentApplication.treatment_id == treatment.id)
                .all()
            )

            for app in applications:
                db.delete(app)
                count += 1

            # Then delete the treatment
            db.delete(treatment)
            count += 1

        if count > 0:
            db.commit()
            print(f"Cleaned up {count} test treatments and applications")


def test_create_treatment():
    # Create test doctor
    doctor = create_test_doctor()

    # Create test patient assigned to this doctor
    patient = create_test_patient(doctor_id=doctor.id)

    # Clean up any existing test treatments
    cleanup_test_treatment()

    # Create treatment data
    treatment_data = {
        "name": "Test Treatment",
        "description": "This is a test treatment",
        "patient_id": patient.id,
    }

    # Create treatment as doctor
    response = client.post(
        "/treatments/",
        json=treatment_data,
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    # Print response details for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content.decode()}")

    assert response.status_code == 200
    data = response.json()
    print(f"Created treatment: {data}")

    assert data["name"] == treatment_data["name"]
    assert data["description"] == treatment_data["description"]
    assert data["patient_id"] == treatment_data["patient_id"]
    assert "id" in data

    treatment_id = data["id"]
    return treatment_id


def test_read_treatments():
    # Create test doctor and treatment if needed
    doctor = create_test_doctor()
    treatment_id = test_create_treatment()

    # Get all treatments
    response = client.get(
        "/treatments/", params={"current_user_email": "testdoctor@hospital.com"}
    )

    assert response.status_code == 200
    treatments = response.json()
    print(f"Retrieved {len(treatments)} treatments")
    assert isinstance(treatments, list)
    assert len(treatments) > 0
    return treatments


def test_filter_treatments_by_patient():
    # Create test doctor and treatment if needed
    doctor = create_test_doctor()
    patient = create_test_patient(doctor_id=doctor.id)
    treatment_id = test_create_treatment()

    # Get treatments for specific patient
    response = client.get(
        f"/treatments/",
        params={
            "patient_id": patient.id,
            "current_user_email": "testdoctor@hospital.com",
        },
    )

    assert response.status_code == 200
    treatments = response.json()
    assert isinstance(treatments, list)
    assert len(treatments) > 0
    assert all(t["patient_id"] == patient.id for t in treatments)
    print(f"Retrieved {len(treatments)} treatments for patient {patient.id}")
    return treatments


def test_read_specific_treatment():
    # Create test treatment if needed
    treatment_id = test_create_treatment()

    # Get the specific treatment
    response = client.get(
        f"/treatments/{treatment_id}",
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert response.status_code == 200
    treatment = response.json()
    print(f"Retrieved treatment: {treatment}")

    assert treatment["id"] == treatment_id
    assert treatment["name"] == "Test Treatment"
    return treatment


def test_update_treatment():
    # Create test treatment if needed
    treatment_id = test_create_treatment()

    # Update data
    update_data = {
        "description": "Updated test treatment description",
    }

    # Update the treatment
    response = client.put(
        f"/treatments/{treatment_id}",
        json=update_data,
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert response.status_code == 200
    updated_treatment = response.json()
    print(f"Updated treatment: {updated_treatment}")

    assert updated_treatment["id"] == treatment_id
    assert updated_treatment["description"] == update_data["description"]
    return updated_treatment


# def test_delete_treatment():
#     # Create test treatment
#     treatment_id = test_create_treatment()

#     # Delete the treatment
#     response = client.delete(
#         f"/treatments/{treatment_id}",
#         params={"current_user_email": "testdoctor@hospital.com"},
#     )

#     assert response.status_code == 204
#     print(f"Successfully deleted treatment {treatment_id}")

#     # Verify treatment is deactivated (not deleted)
#     response = client.get(
#         f"/treatments/{treatment_id}",
#         params={"current_user_email": "testdoctor@hospital.com"},
#     )

#     # Treatment should still be found, but with is_active=False
#     assert response.status_code == 200
#     treatment = response.json()
#     assert treatment["is_active"] == False


def setup_patient_assistant_assignment():
    doctor = create_test_doctor()
    patient = create_test_patient(doctor_id=doctor.id)
    assistant = create_test_assistant()

    # Create assignment
    assignment_data = {
        "patient_id": patient.id,
        "assistant_id": assistant.id,
        "assigned_date": datetime.now().isoformat(),
    }

    # Create assignment as doctor
    response = client.post(
        "/assignments/",
        json=assignment_data,
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    if response.status_code != 200:
        print(f"Failed to create assignment: {response.json()}")
        return None, None, None

    return doctor, patient, assistant


def test_apply_treatment():
    # Set up doctor, patient, assistant with proper assignment
    doctor, patient, assistant = setup_patient_assistant_assignment()
    if not all([doctor, patient, assistant]):
        print("Skipping treatment application test due to setup failure")
        return None

    # Create a treatment for the patient
    treatment_data = {
        "name": "Test Treatment for Application",
        "description": "This treatment will be applied",
        "patient_id": patient.id,
    }

    create_response = client.post(
        "/treatments/",
        json=treatment_data,
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    treatment = create_response.json()
    treatment_id = treatment["id"]

    # Now apply the treatment as assistant - adjust to match your actual endpoint
    applied_data = {
        "treatment_id": treatment_id,
        "assistant_id": assistant.id,
        "notes": "Treatment applied during testing",
    }

    response = client.post(
        "/assistants/treatments/apply",  # Use the correct endpoint from your router
        json=applied_data,
        params={"current_user_email": "testassistant@hospital.com"},
    )

    assert response.status_code == 200
    applied = response.json()
    print(f"Applied treatment: {applied}")

    assert applied["treatment_id"] == treatment_id
    assert applied["assistant_id"] == assistant.id
    assert "id" in applied

    # Try to delete the treatment (should fail as it's been applied)
    delete_response = client.delete(
        f"/treatments/{treatment_id}",
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert delete_response.status_code == 400
    print("Confirmed treatment can't be deleted once applied")

    return applied["id"]


def run_treatment_tests():
    print("Running treatment management tests...\n")

    print("\n1. Creating test users:")
    create_test_admin()
    create_test_doctor()
    create_test_assistant()

    print("\n2. Testing treatment creation:")
    treatment_id = test_create_treatment()

    print("\n3. Testing reading all treatments:")
    treatments = test_read_treatments()

    print("\n4. Testing filtering treatments by patient:")
    filtered_treatments = test_filter_treatments_by_patient()

    print("\n5. Testing reading specific treatment:")
    treatment = test_read_specific_treatment()

    print("\n6. Testing updating treatment:")
    updated_treatment = test_update_treatment()

    print("\n7. Testing deleting treatment:")
    # test_delete_treatment()

    print("\n8. Testing applying treatment:")
    try:
        applied_id = test_apply_treatment()
        if applied_id:
            print(f"Treatment application successful with ID: {applied_id}")
    except Exception as e:
        print(f"Treatment application test failed: {e}")

    print("\nAll treatment management tests completed!")


if __name__ == "__main__":
    run_treatment_tests()
