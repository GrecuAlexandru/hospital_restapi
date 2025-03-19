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
            full_name="Test Admin",
            role="general_manager",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Created test admin user: {admin.email}")
        return admin


def cleanup_test_doctor():
    with SessionLocal() as db:
        # Find the doctor by associated user email
        existing_user = (
            db.query(models.User)
            .filter(models.User.email == "testdoctor@hospital.com")
            .first()
        )

        if existing_user:
            # Find and delete doctor record
            existing_doctor = (
                db.query(models.Doctor)
                .filter(models.Doctor.user_id == existing_user.id)
                .first()
            )

            if existing_doctor:
                print(f"Deleting existing test doctor with ID: {existing_doctor.id}")
                db.delete(existing_doctor)
                db.commit()

            # Delete user record
            print(f"Deleting existing test user: {existing_user.email}")
            db.delete(existing_user)
            db.commit()


def test_create_doctor():
    # Clean up any existing test doctor
    cleanup_test_doctor()

    # Create doctor data
    doctor_data = {
        "email": "testdoctor@hospital.com",
        "full_name": "Dr. Test Doctor",
        "password": "doctor123",
        "role": "doctor",
        "specialization": "Dentist",
        "experience": 10,
    }

    # Create doctor as admin
    response = client.post(
        "/doctors/",
        json=doctor_data,
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 200
    data = response.json()
    print(f"Created doctor: {data}")
    assert data["user"]["email"] == doctor_data["email"]
    assert data["user"]["role"] == "doctor"

    doctor_id = data["id"]
    return doctor_id


def test_read_doctors():
    # Ensure admin exists
    create_test_admin()

    response = client.get(
        "/doctors/", params={"current_user_email": "testadmin@hospital.com"}
    )

    assert response.status_code == 200
    doctors = response.json()
    print(f"Retrieved {len(doctors)} doctors")
    assert isinstance(doctors, list)
    return doctors


def test_read_specific_doctor():
    # First create a doctor to ensure we have one to read
    doctor_id = test_create_doctor()

    # Now read that specific doctor
    response = client.get(
        f"/doctors/{doctor_id}", params={"current_user_email": "testadmin@hospital.com"}
    )

    assert response.status_code == 200
    doctor = response.json()
    print(f"Retrieved doctor: {doctor}")
    assert doctor["id"] == doctor_id
    assert doctor["user"]["email"] == "testdoctor@hospital.com"
    return doctor


def test_update_doctor():
    # First create a doctor to update
    doctor_id = test_create_doctor()

    # Update data
    update_data = {"specialization": "Surgeon", "experience": 15}
    # Update the doctor
    response = client.put(
        f"/doctors/{doctor_id}",
        json=update_data,
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 200
    updated_doctor = response.json()
    print(f"Updated doctor: {updated_doctor}")
    assert updated_doctor["id"] == doctor_id
    assert updated_doctor["specialization"] == "Surgeon"
    assert updated_doctor["experience"] == 15


def test_delete_doctor():
    # First create a doctor to delete
    doctor_id = test_create_doctor()

    # Delete the doctor
    response = client.delete(
        f"/doctors/{doctor_id}", params={"current_user_email": "testadmin@hospital.com"}
    )

    assert response.status_code == 204

    # Verify the doctor is deactivated
    response = client.get(
        f"/doctors/{doctor_id}", params={"current_user_email": "testadmin@hospital.com"}
    )

    doctor = response.json()
    print(f"Doctor after deletion: {doctor}")
    assert doctor["user"]["is_active"] == False


def test_unauthorized_access():
    # Create a regular user
    with SessionLocal() as db:
        user = (
            db.query(models.User)
            .filter(models.User.email == "regularuser@hospital.com")
            .first()
        )
        if not user:
            user = models.User(
                email="regularuser@hospital.com",
                hashed_password=get_password_hash("user123"),
                full_name="Regular User",
                role="assistant",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

    # Try to access doctors list
    response = client.get(
        "/doctors/", params={"current_user_email": "regularuser@hospital.com"}
    )

    print(response.json())

    assert response.status_code == 403
    assert "Not enough permissions" in response.json()["detail"]


def run_doctor_tests():
    print("Running doctor management tests...\n")

    print("\n1. Creating test admin:")
    create_test_admin()

    print("\n2. Testing doctor creation:")
    doctor_id = test_create_doctor()

    print("\n3. Testing reading all doctors:")
    doctors = test_read_doctors()

    print("\n4. Testing reading specific doctor:")
    doctor = test_read_specific_doctor()

    print("\n5. Testing updating doctor:")
    test_update_doctor()

    print("\n6. Testing deleting doctor:")
    test_delete_doctor()

    print("\n7. Testing unauthorized access:")
    test_unauthorized_access()

    print("\nAll doctor management tests completed successfully!")


if __name__ == "__main__":
    run_doctor_tests()
