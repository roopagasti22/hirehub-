"""Pytest configuration and fixtures for HireHub tests."""
import pytest
import os
os.environ["FLASK_ENV"] = "testing"
os.environ["MONGO_DATABASE"] = "hirehub_test"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["UPLOAD_FOLDER"] = "app/uploads/test_resumes"

from app import create_app
from app.config import TestingConfig
from app.extensions import MongoDB


@pytest.fixture(scope="session")
def app():
    """Create test Flask app."""
    application = create_app(TestingConfig)
    application.config["TESTING"] = True
    yield application
    # Cleanup test database
    try:
        db = MongoDB.get_db()
        for coll in ["users", "companies", "jobs", "applications", "interviews", "resumes", "notifications", "audit_logs"]:
            db[coll].drop()
    except Exception:
        pass


@pytest.fixture(scope="session")
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture(scope="session")
def db(app):
    """Test database."""
    return MongoDB.get_db()


@pytest.fixture
def candidate_data():
    return {
        "name": "Test Candidate",
        "email": "testcandidate@example.com",
        "phone": "9876543210",
        "password": "Test@1234",
        "confirm_password": "Test@1234",
        "role": "CANDIDATE",
    }


@pytest.fixture
def recruiter_data():
    return {
        "name": "Test Recruiter",
        "email": "testrecruiter@example.com",
        "phone": "9876543211",
        "password": "Test@1234",
        "confirm_password": "Test@1234",
        "company_name": "Test Corp",
        "role": "RECRUITER",
    }
