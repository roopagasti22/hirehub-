"""Tests for the MatchingService."""
import pytest
from app.services.matching_service import MatchingService


@pytest.fixture
def matching():
    return MatchingService()


def test_full_skill_match(matching):
    candidate = {"skills": ["python", "sql", "mongodb"], "location": "Bengaluru", "experience": [{"years": 2}]}
    job = {"skills": ["python", "sql", "mongodb"], "location": "Bengaluru", "work_mode": "ONSITE", "experience_min": 1, "experience_max": 3}
    result = matching.calculate(candidate, job)
    assert result["score"] > 70
    assert len(result["matched_skills"]) == 3
    assert len(result["missing_skills"]) == 0


def test_partial_skill_match(matching):
    candidate = {"skills": ["python", "sql"], "location": "", "experience": []}
    job = {"skills": ["python", "sql", "aws"], "location": "", "work_mode": "REMOTE", "experience_min": 0, "experience_max": 5}
    result = matching.calculate(candidate, job)
    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["aws"]
    assert result["score"] < 100


def test_no_skill_match(matching):
    candidate = {"skills": ["java"], "location": "", "experience": []}
    job = {"skills": ["python", "django"], "location": "", "work_mode": "REMOTE", "experience_min": 0, "experience_max": 5}
    result = matching.calculate(candidate, job)
    assert result["matched_skills"] == []
    assert "python" in result["missing_skills"]


def test_remote_job_location_match(matching):
    candidate = {"skills": [], "location": "Mumbai", "experience": []}
    job = {"skills": [], "location": "Bengaluru", "work_mode": "REMOTE", "experience_min": 0, "experience_max": 5}
    result = matching.calculate(candidate, job)
    assert result["breakdown"]["location"]["match"] is True


def test_experience_outside_range(matching):
    candidate = {"skills": [], "location": "", "experience": [{"years": 0}]}
    job = {"skills": [], "location": "", "work_mode": "REMOTE", "experience_min": 5, "experience_max": 10}
    result = matching.calculate(candidate, job)
    assert result["breakdown"]["experience"]["score"] < 15


def test_salary_match_accepts_string_values(matching):
    candidate = {
        "skills": [],
        "location": "",
        "experience": [],
        "expected_salary": "600000",
    }
    job = {
        "skills": [],
        "location": "",
        "work_mode": "REMOTE",
        "experience_min": 0,
        "experience_max": 5,
        "salary_min": "500000",
        "salary_max": "800000",
    }

    result = matching.calculate(candidate, job)

    assert result["breakdown"]["salary"]["score"] == 10


def test_invalid_salary_values_do_not_break_matching(matching):
    candidate = {"skills": [], "location": "", "experience": [], "expected_salary": "unknown"}
    job = {
        "skills": [],
        "location": "",
        "work_mode": "REMOTE",
        "experience_min": 0,
        "experience_max": 5,
        "salary_min": None,
        "salary_max": "unknown",
    }

    result = matching.calculate(candidate, job)

    assert result["breakdown"]["salary"]["score"] == 10
