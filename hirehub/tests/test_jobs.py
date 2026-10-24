"""Tests for job creation, search, and filtering."""
import pytest


def _login_recruiter(client, recruiter_data):
    client.post("/api/auth/register", json=recruiter_data)
    client.post("/api/auth/login", json={
        "email": recruiter_data["email"],
        "password": recruiter_data["password"],
    })


def _login_candidate(client, candidate_data):
    client.post("/api/auth/register", json=candidate_data)
    client.post("/api/auth/login", json={
        "email": candidate_data["email"],
        "password": candidate_data["password"],
    })


JOB_DATA = {
    "title": "Python Developer",
    "description": "Build backend APIs using Python and Flask.",
    "skills": ["python", "flask", "mongodb"],
    "location": "Bengaluru",
    "work_mode": "HYBRID",
    "employment_type": "FULL_TIME",
    "experience_min": 1,
    "experience_max": 3,
    "salary_min": 500000,
    "salary_max": 800000,
}


def test_create_job(client, recruiter_data):
    _login_recruiter(client, recruiter_data)
    res = client.post("/api/jobs/", json=JOB_DATA)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["title"] == "Python Developer"


def test_create_job_unauthorized(client, candidate_data):
    _login_candidate(client, candidate_data)
    res = client.post("/api/jobs/", json=JOB_DATA)
    assert res.status_code == 403


def test_list_jobs(client):
    res = client.get("/api/jobs/")
    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data["data"]


def test_search_jobs_by_skill(client):
    res = client.get("/api/jobs/?skill=python")
    assert res.status_code == 200


def test_search_jobs_by_location(client):
    res = client.get("/api/jobs/?location=Bengaluru")
    assert res.status_code == 200


def test_get_job_not_found(client):
    res = client.get("/api/jobs/000000000000000000000000")
    assert res.status_code == 404
