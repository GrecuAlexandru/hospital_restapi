from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.database import SessionLocal
from app import models, crud, schemas

# Create test client
client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    print(f"Health check response: {response.json()}")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_user():
    # Clean up any existing test user first
    with SessionLocal() as db:
        existing_user = (
            db.query(models.User)
            .filter(models.User.email == "test@example.com")
            .first()
        )
        if existing_user:
            db.delete(existing_user)
            db.commit()
            print(f"Deleted existing test user: {existing_user.email}")

    # Create new test user
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "password123",
        "role": "doctor",
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    print(f"Created user: {data}")
    assert data["email"] == user_data["email"]
    assert "id" in data

    user_id = data["id"]
    return user_id


def test_read_users():
    response = client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    print(f"All users: {users}")
    assert isinstance(users, list)
    return users


def test_read_specific_user():
    # First create a user to ensure we have something to read
    user_id = test_create_user()

    # Now read that specific user
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    user = response.json()
    print(f"Retrieved user: {user}")
    assert user["id"] == user_id
    assert user["email"] == "test@example.com"
    return user


def create_admin_user():
    with SessionLocal() as db:
        # Check if admin already exists
        admin = (
            db.query(models.User)
            .filter(models.User.email == "admin@hospital.com")
            .first()
        )
        if admin:
            print("Admin user already exists")
            return admin

        from app.auth_utils import get_password_hash

        # Create admin user
        admin = models.User(
            email="admin@hospital.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Hospital Admin",
            role="general_manager",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print(f"Created admin user: {admin.email}")
        return admin


def test_create_doctor():
    # Check if doctor already exists
    with SessionLocal() as db:
        existing_doctor = (
            db.query(models.User)
            .filter(models.User.email == "doctor@hospital.com")
            .first()
        )
        if existing_doctor:
            print(f"Doctor already exists: {existing_doctor.email}")
            # Get doctor profile
            doctor_profile = (
                db.query(models.Doctor)
                .filter(models.Doctor.user_id == existing_doctor.id)
                .first()
            )
            if doctor_profile:
                print(f"Doctor profile found with id: {doctor_profile.id}")
                return doctor_profile.id

    # Create doctor data
    doctor_data = {
        "email": "doctor@hospital.com",
        "full_name": "Dr. Test Doctor",
        "password": "doctor123",
        "role": "doctor",
        "specialization": "General Medicine",
        "experience": 5,
    }

    # Create doctor as admin
    response = client.post(
        "/doctors/",
        json=doctor_data,
        params={"current_user_email": "admin@hospital.com"},
    )

    assert response.status_code == 200
    data = response.json()
    print(f"Created doctor: {data}")
    assert data["user"]["email"] == doctor_data["email"]

    doctor_id = data["id"]
    return doctor_id


def test_read_doctors():
    response = client.get(
        "/doctors/", params={"current_user_email": "admin@hospital.com"}
    )

    assert response.status_code == 200
    doctors = response.json()
    print(f"All doctors: {doctors}")
    assert isinstance(doctors, list)
    return doctors


def run_tests():
    print("Running tests on production database...")

    print("\n1. Testing health check:")
    test_health_check()

    print("\n2. Creating admin user:")
    create_admin_user()

    print("\n3. Testing user creation:")
    user_id = test_create_user()

    print("\n4. Testing doctor creation:")
    doctor_id = test_create_doctor()

    print("\n5. Testing reading all doctors:")
    doctors = test_read_doctors()

    print("\nAll tests passed successfully!")


if __name__ == "__main__":
    run_tests()
