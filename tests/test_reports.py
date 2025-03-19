from fastapi.testclient import TestClient
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from tests.test_treatment import (
    create_test_admin,
    create_test_doctor,
    create_test_patient,
    create_test_assistant,
)

# Create test client
client = TestClient(app)


def test_doctor_patient_report():
    # First ensure we have test data
    admin = create_test_admin()
    doctor = create_test_doctor()
    patient = create_test_patient(doctor_id=doctor.id)

    # Try to access the report as general manager
    response = client.get(
        "/reports/doctors-patients",
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert response.status_code == 200
    data = response.json()
    print("Report data:", data)

    # Verify report structure
    assert "doctors" in data
    assert "statistics" in data
    assert isinstance(data["doctors"], list)
    assert len(data["doctors"]) > 0
    assert isinstance(data["statistics"], dict)

    # Verify statistics fields
    stats = data["statistics"]
    assert "total_doctors" in stats
    assert "total_patients" in stats
    assert "avg_patients_per_doctor" in stats
    assert "patients_per_doctor" in stats

    # Try to access as non-manager (should fail)
    non_manager_response = client.get(
        "/reports/doctors-patients",
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert non_manager_response.status_code == 403


def test_patient_treatment_report():
    # First ensure we have test data with treatments and applications
    admin = create_test_admin()
    doctor = create_test_doctor()
    patient = create_test_patient(doctor_id=doctor.id)
    assistant = create_test_assistant()

    # Create test treatment
    treatment_data = {
        "name": "Test Treatment for Report",
        "description": "Treatment for testing the report",
        "patient_id": patient.id,
    }

    # Create treatment as doctor
    treatment_resp = client.post(
        "/treatments/",
        json=treatment_data,
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    treatment_id = treatment_resp.json()["id"]

    # Assign patient to assistant
    assignment_data = {"patient_id": patient.id, "assistant_id": assistant.id}

    client.post(
        "/assistants/patients/assign",
        json=assignment_data,
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    # Apply treatment
    application_data = {
        "treatment_id": treatment_id,
        "notes": "Applied during testing",
    }

    client.post(
        "/assistants/treatments/apply",
        json=application_data,
        params={"current_user_email": "testassistant@hospital.com"},
    )

    # Try to access the report as doctor
    doctor_response = client.get(
        f"/reports/patients/{patient.id}/treatments",
        params={"current_user_email": "testdoctor@hospital.com"},
    )

    assert doctor_response.status_code == 200
    doctor_data = doctor_response.json()
    print("Doctor view of patient treatment report:", doctor_data)

    # Verify report structure from doctor perspective
    assert len(doctor_data) > 0
    assert "id" in doctor_data[0]
    assert "name" in doctor_data[0]
    assert "applications" in doctor_data[0]

    # Try to access as general manager
    gm_response = client.get(
        f"/reports/patients/{patient.id}/treatments",
        params={"current_user_email": "testadmin@hospital.com"},
    )

    assert gm_response.status_code == 200
    gm_data = gm_response.json()
    print("GM view of patient treatment report:", gm_data)


def run_report_tests():
    """Run all report tests"""
    print("\nRunning report tests...")
    test_doctor_patient_report()
    test_patient_treatment_report()
    print("All report tests passed!")


if __name__ == "__main__":
    run_report_tests()
