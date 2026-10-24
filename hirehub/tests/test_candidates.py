"""Tests for candidate profile operations."""
import pytest


def _register_and_login(client, data):
    client.post("/api/auth/register", json=data)
    client.post("/api/auth/login", json={"email": data["email"], "password": data["password"]})
    me = client.get("/api/auth/me").get_json()
    return me["data"]["_id"]


def test_get_candidate_profile(client, candidate_data):
    user_id = _register_and_login(client, candidate_data)
    res = client.get(f"/api/candidates/{user_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["data"]["email"] == candidate_data["email"].lower()


def test_update_candidate_profile(client, candidate_data):
    user_id = _register_and_login(client, candidate_data)
    res = client.put(f"/api/candidates/{user_id}", json={
        "location": "Hyderabad",
        "skills": ["python", "django"],
        "expected_salary": 600000,
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["data"]["location"] == "Hyderabad"


def test_update_other_candidate_profile(client, candidate_data):
    """Candidate cannot edit another candidate's profile."""
    _register_and_login(client, candidate_data)
    res = client.put("/api/candidates/000000000000000000000001", json={"location": "Mumbai"})
    assert res.status_code in (403, 404)
