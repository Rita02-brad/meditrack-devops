"""
MediTrack - Test Suite
Tests for the core API endpoints using pytest and Flask's test client.
"""

import pytest
from app import app, patients, next_id


@pytest.fixture(autouse=True)
def reset_patients():
    """
    Reset the in-memory patient store before each test so tests are isolated.
    We restore the original 3 sample records and reset the ID counter.
    """
    import app as app_module

    # Save original state
    original_patients = app_module.patients.copy()
    original_next_id = app_module.next_id

    yield  # run the test

    # Restore original state after each test
    app_module.patients.clear()
    app_module.patients.extend(original_patients)
    app_module.next_id = original_next_id


@pytest.fixture
def client():
    """Create a Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

def test_health_returns_200_and_healthy_status(client):
    """GET /health should return 200 with the expected JSON body."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data == {"status": "healthy", "service": "meditrack-api"}


# ---------------------------------------------------------------------------
# GET /patients
# ---------------------------------------------------------------------------

def test_get_patients_returns_200_and_list(client):
    """GET /patients should return 200 and a JSON list."""
    response = client.get("/patients")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    # The store is pre-populated with 3 sample records
    assert len(data) == 3


# ---------------------------------------------------------------------------
# POST /patients
# ---------------------------------------------------------------------------

def test_create_patient_returns_201_and_new_patient(client):
    """POST /patients with valid data should return 201 and the created record."""
    new_patient = {
        "name": "David Lee",
        "age": 50,
        "gender": "Male",
        "diagnosis": "Pneumonia",
        "ward": "Respiratory",
        "admitted_on": "2026-03-28"
    }
    response = client.post("/patients", json=new_patient)
    assert response.status_code == 201

    data = response.get_json()
    assert data["name"] == "David Lee"
    assert data["diagnosis"] == "Pneumonia"
    assert "id" in data  # ID should be auto-generated


def test_create_patient_missing_fields_returns_400(client):
    """POST /patients with missing fields should return 400."""
    response = client.post("/patients", json={"name": "Incomplete Record"})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /patients/<id>
# ---------------------------------------------------------------------------

def test_get_patient_by_valid_id_returns_200(client):
    """GET /patients/<id> with a valid ID should return 200 and the patient."""
    response = client.get("/patients/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert "name" in data


def test_get_patient_by_invalid_id_returns_404(client):
    """GET /patients/<id> with a non-existent ID should return 404."""
    response = client.get("/patients/9999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


# ---------------------------------------------------------------------------
# PUT /patients/<id>
# ---------------------------------------------------------------------------

def test_update_patient_returns_200_and_updated_record(client):
    """PUT /patients/<id> should update the record and return it."""
    response = client.put("/patients/1", json={"diagnosis": "Hypertension Stage 2"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["diagnosis"] == "Hypertension Stage 2"


def test_update_nonexistent_patient_returns_404(client):
    """PUT /patients/<id> for a missing patient should return 404."""
    response = client.put("/patients/9999", json={"diagnosis": "Unknown"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /patients/<id>
# ---------------------------------------------------------------------------

def test_delete_patient_returns_200_and_success_message(client):
    """DELETE /patients/<id> should remove the patient and return a success message."""
    response = client.delete("/patients/1")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data

    # Confirm the patient is gone
    follow_up = client.get("/patients/1")
    assert follow_up.status_code == 404


def test_delete_nonexistent_patient_returns_404(client):
    """DELETE /patients/<id> for a missing patient should return 404."""
    response = client.delete("/patients/9999")
    assert response.status_code == 404
