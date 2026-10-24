"""Tests for job applications."""
import pytest


def _register_and_login(client, data):
    client.post("/api/auth/register", json=data)
    client.post("/api/auth/login", json={"email": data["email"], "password": data["password"]})


def test_apply_to_job(client, candidate_data, recruiter_data):
    # Create a job as recruiter
    _register_and_login(client, recruiter_data)
    r = client.post("/api/jobs/", json={
        "title": "Test Apply Job",
        "description": "Test",
        "skills": ["python"],
        "location": "Remote",
        "work_mode": "REMOTE",
        "employment_type": "FULL_TIME",
        "experience_min": 0,
        "experience_max": 2,
    })
    assert r.status_code == 201
    job_id = r.get_json()["data"]["_id"]

    # Login as candidate and apply
    _register_and_login(client, candidate_data)
    res = client.post(f"/api/jobs/{job_id}/apply")
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True


def test_duplicate_application(client, candidate_data, recruiter_data):
    # Create job
    _register_and_login(client, recruiter_data)
    r = client.post("/api/jobs/", json={
        "title": "Duplicate Test Job",
        "description": "Test",
        "skills": ["java"],
        "location": "Mumbai",
        "work_mode": "ONSITE",
        "employment_type": "FULL_TIME",
        "experience_min": 0,
        "experience_max": 5,
    })
    job_id = r.get_json()["data"]["_id"]

    # Apply once
    _register_and_login(client, candidate_data)
    client.post(f"/api/jobs/{job_id}/apply")

    # Apply again — should fail
    res = client.post(f"/api/jobs/{job_id}/apply")
    assert res.status_code == 409
    assert res.get_json()["error_code"] == "DUPLICATE_APPLICATION"


def test_list_applications(client, candidate_data):
    _register_and_login(client, candidate_data)
    res = client.get("/api/applications/")
    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data["data"]


def test_candidate_applications_page_renders(client, candidate_data):
    _register_and_login(client, candidate_data)

    res = client.get("/candidate/applications")

    assert res.status_code == 200
    assert b"My Applications" in res.data
