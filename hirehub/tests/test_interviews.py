"""Tests for interview scheduling."""
import pytest


def test_interview_scheduling_requires_recruiter(client, candidate_data):
    """Candidates cannot schedule interviews."""
    client.post("/api/auth/register", json=candidate_data)
    client.post("/api/auth/login", json={"email": candidate_data["email"], "password": candidate_data["password"]})
    res = client.post("/api/interviews/", json={
        "application_id": "000000000000000000000000",
        "date": "2026-12-01",
        "time": "10:00",
    })
    assert res.status_code == 403


def test_list_interviews_authenticated(client, candidate_data):
    """Authenticated users can list their interviews."""
    client.post("/api/auth/login", json={"email": candidate_data["email"], "password": candidate_data["password"]})
    res = client.get("/api/interviews/")
    assert res.status_code == 200
