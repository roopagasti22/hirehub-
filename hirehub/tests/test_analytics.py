"""Tests for analytics endpoints."""
import pytest


def _login_candidate(client, data):
    client.post("/api/auth/register", json=data)
    client.post("/api/auth/login", json={"email": data["email"], "password": data["password"]})


def test_candidate_analytics(client, candidate_data):
    _login_candidate(client, candidate_data)
    res = client.get("/api/analytics/candidate")
    assert res.status_code == 200
    data = res.get_json()
    assert "total_applications" in data["data"]


def test_recruiter_analytics_forbidden_for_candidate(client, candidate_data):
    _login_candidate(client, candidate_data)
    res = client.get("/api/analytics/recruiter")
    assert res.status_code == 403


def test_admin_analytics_forbidden_for_candidate(client, candidate_data):
    _login_candidate(client, candidate_data)
    res = client.get("/api/analytics/admin")
    assert res.status_code == 403
