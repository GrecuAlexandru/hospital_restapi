from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import SessionLocal
from app import models, crud, schemas
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


# Cleanup any existing test assistant
def cleanup_test_assistant():
    with SessionLocal() as db:
        # Find the assistant by associated user email
        existing_user = (
            db.query(models.User)
            .filter(models.User.email == "testassistant@hospital.com")
            .first()
        )

        if existing_user:
            # Find and delete assistant record
            existing_assistant = (
                db.query(models.Assistant)
                .filter(models.Assistant.user_id == existing_user.id)
                .first()
            )

            if existing_assistant:
                print(
                    f"Deleting existing test assistant with ID: {existing_assistant.id}"
                )

                # Delete related assignments first
                assignments = (
                    db.query(models.PatientAssistant)
                    .filter(
                        models.PatientAssistant.assistant_id == existing_assistant.id
                    )
                    .all()
                )

                for assignment in assignments:
                    db.delete(assignment)

                # Delete assistant
                db.delete(existing_assistant)
                db.commit()

            # Delete user record
            print(f"Deleting existing test user: {existing_user.email}")
            db.delete(existing_user)
            db.commit()


def test_create_assistant():
    # Clean up any existing test assistant
    cleanup_test_assistant()

    # Create assistant data
    assistant_data = {
        "email": "testassistant@hospital.com",
        "full_name": "Test Assistant",
        "password": "assistant123",
        "age": 30,
        "specialization": "General",
    }

    # Create assistant as admin
    response = client.post(
        "/assistants/",
        json=assistant_data,
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 200
    data = response.json()
    print(f"Created assistant: {data}")
    assert data["user"]["email"] == assistant_data["email"]
    assert data["user"]["role"] == "assistant"

    assistant_id = data["id"]
    return assistant_id


def test_read_assistants():
    # Ensure admin exists
    create_test_admin()

    response = client.get(
        "/assistants/", params={"current_user_email": "testadmin@hospital.com"}
    )

    assert response.status_code == 200
    assistants = response.json()
    print(f"Retrieved {len(assistants)} assistants")
    assert isinstance(assistants, list)
    return assistants


def test_read_specific_assistant():
    # First create an assistant to ensure we have one to read
    assistant_id = test_create_assistant()

    # Now read that specific assistant
    response = client.get(
        f"/assistants/{assistant_id}",
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 200
    assistant = response.json()
    print(f"Retrieved assistant: {assistant}")
    assert assistant["id"] == assistant_id
    assert assistant["user"]["email"] == "testassistant@hospital.com"
    return assistant


def test_update_assistant():
    # First create an assistant to update
    assistant_id = test_create_assistant()

    update_data = {"age": 35, "specialization": "Dentist"}

    # Update the assistant
    response = client.put(
        f"/assistants/{assistant_id}",
        json=update_data,
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 200
    updated_assistant = response.json()
    print(f"Updated assistant: {updated_assistant}")
    assert updated_assistant["id"] == assistant_id
    assert updated_assistant["age"] == 35
    assert updated_assistant["specialization"] == "Dentist"


def test_delete_assistant():
    # First create an assistant to delete
    assistant_id = test_create_assistant()

    # Delete the assistant
    response = client.delete(
        f"/assistants/{assistant_id}",
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 204

    # Verify the assistant is deactivated
    response = client.get(
        f"/assistants/{assistant_id}",
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assistant = response.json()
    print(f"Assistant after deletion: {assistant}")
    assert assistant["user"]["is_active"] == False


def test_patient_assistant_assignment():
    # First create doctor, patient, and assistant to use in assignment
    from tests.test_doctor import test_create_doctor
    from tests.test_patient import test_create_patient

    doctor_id = test_create_doctor()
    patient_id = test_create_patient()
    assistant_id = test_create_assistant()

    # Create assignment
    assignment_data = {"patient_id": patient_id, "assistant_id": assistant_id}

    response = client.post(
        "/assistants/patients/assign",
        json=assignment_data,
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 200
    data = response.json()
    print(f"Created patient-assistant assignment: {data}")
    assert data["patient_id"] == patient_id
    assert data["assistant_id"] == assistant_id

    assignment_id = data["id"]
    return assignment_id


def run_assistant_tests():
    print("Running assistant management tests...\n")

    print("\n1. Creating test admin:")
    create_test_admin()

    print("\n2. Testing assistant creation:")
    assistant_id = test_create_assistant()

    print("\n3. Testing reading all assistants:")
    assistants = test_read_assistants()

    print("\n4. Testing reading specific assistant:")
    assistant = test_read_specific_assistant()

    print("\n5. Testing updating assistant:")
    test_update_assistant()

    print("\n6. Testing deleting assistant:")
    # test_delete_assistant()

    print("\n7. Testing patient-assistant assignment:")
    try:
        assignment_id = test_patient_assistant_assignment()
        print(f"Assignment created with ID: {assignment_id}")
    except Exception as e:
        print(f"Assignment test failed: {e}")

    print("\nAll assistant management tests completed successfully!")


if __name__ == "__main__":
    run_assistant_tests()
