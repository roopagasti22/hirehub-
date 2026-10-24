"""Tests for authentication — registration, login, logout."""
import pytest


def test_candidate_registration(client, candidate_data):
    """Successful candidate registration."""
    res = client.post("/api/auth/register", json=candidate_data)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True


def test_duplicate_registration(client, candidate_data):
    """Duplicate email should return 409."""
    client.post("/api/auth/register", json=candidate_data)
    res = client.post("/api/auth/register", json=candidate_data)
    assert res.status_code == 409
    data = res.get_json()
    assert data["error_code"] == "USER_ALREADY_EXISTS"


def test_login_success(client, candidate_data):
    """Valid credentials should return success."""
    res = client.post("/api/auth/login", json={
        "email": candidate_data["email"],
        "password": candidate_data["password"],
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["email"] == candidate_data["email"].lower()


def test_login_invalid_password(client, candidate_data):
    """Wrong password should return 401."""
    res = client.post("/api/auth/login", json={
        "email": candidate_data["email"],
        "password": "WrongPass99!",
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data["error_code"] == "INVALID_CREDENTIALS"


def test_logout(client, candidate_data):
    """Logout should clear session."""
    client.post("/api/auth/login", json={
        "email": candidate_data["email"],
        "password": candidate_data["password"],
    })
    res = client.post("/api/auth/logout")
    assert res.status_code == 200


def test_me_unauthenticated(client):
    """GET /api/auth/me without session should return 401."""
    with client.session_transaction() as sess:
        sess.clear()
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_recruiter_registration(client, recruiter_data):
    """Successful recruiter registration."""
    res = client.post("/api/auth/register", json=recruiter_data)
    assert res.status_code == 201


def test_registration_invalid_email(client):
    """Invalid email should return 422."""
    res = client.post("/api/auth/register", json={
        "name": "Bad User",
        "email": "not-an-email",
        "phone": "9876543210",
        "password": "Test@1234",
        "confirm_password": "Test@1234",
        "role": "CANDIDATE",
    })
    assert res.status_code == 422


def test_registration_password_mismatch(client):
    """Password mismatch should return 422."""
    res = client.post("/api/auth/register", json={
        "name": "User",
        "email": "mismatch@test.com",
        "phone": "9876543210",
        "password": "Test@1234",
        "confirm_password": "Different@9",
        "role": "CANDIDATE",
    })
    assert res.status_code == 422
