"""Authentication service — registration, login, logout, audit."""
from __future__ import annotations
from datetime import datetime
from flask import session
from app.models import Candidate, Recruiter, Admin
from app.repositories import UserRepository, CompanyRepository
from app.exceptions import (
    UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError,
)
from app.utils.validators import validate_email, validate_phone, validate_password
from app.exceptions import ValidationError
from .notification_service import NotificationService


class AuthService:
    """Handles registration, login, and session management."""

    def __init__(self) -> None:
        self._user_repo = UserRepository()
        self._company_repo = CompanyRepository()
        self._notification_svc = NotificationService()

    # ── Registration ─────────────────────────────────────────────────────
    def register_candidate(self, data: dict) -> dict:
        """Validate and register a new candidate. Returns the created document."""
        self._validate_registration_data(data)

        email = data["email"].lower().strip()
        if self._user_repo.email_exists(email):
            raise UserAlreadyExistsError(f"Email '{email}' is already registered.")

        candidate = Candidate(
            name=data["name"].strip(),
            email=email,
            phone=data["phone"].strip(),
        )
        candidate.set_password(data["password"])
        doc = candidate.to_dict()
        inserted_id = self._user_repo.insert_one(doc)
        doc["_id"] = inserted_id

        self._log_audit(inserted_id, "USER_REGISTERED", "user", inserted_id)
        self._notification_svc.create(
            user_id=inserted_id,
            title="Welcome to HireHub!",
            message=f"Hi {candidate.name}, your candidate account has been created.",
            notification_type="REGISTRATION",
        )
        return doc

    def register_recruiter(self, data: dict) -> dict:
        """Validate and register a new recruiter + company."""
        self._validate_registration_data(data)

        email = data["email"].lower().strip()
        if self._user_repo.email_exists(email):
            raise UserAlreadyExistsError(f"Email '{email}' is already registered.")

        recruiter = Recruiter(
            name=data["name"].strip(),
            email=email,
            phone=data["phone"].strip(),
            company_name=data.get("company_name", "").strip(),
        )
        recruiter.set_password(data["password"])
        doc = recruiter.to_dict()
        inserted_id = self._user_repo.insert_one(doc)

        # Create company record
        from app.models import Company
        company = Company(
            name=data.get("company_name", "").strip(),
            recruiter_id=inserted_id,
        )
        company_doc = company.to_dict()
        company_id = self._company_repo.insert_one(company_doc)

        # Link company to recruiter
        self._user_repo.update_one(inserted_id, {"company_id": company_id})

        self._log_audit(inserted_id, "USER_REGISTERED", "user", inserted_id)
        self._notification_svc.create(
            user_id=inserted_id,
            title="Welcome to HireHub!",
            message=f"Hi {recruiter.name}, your recruiter account has been created.",
            notification_type="REGISTRATION",
        )
        doc["_id"] = inserted_id
        return doc

    # ── Login / Logout ───────────────────────────────────────────────────
    def login(self, email: str, password: str) -> dict:
        """Authenticate and set session. Returns public user dict."""
        email = email.lower().strip()
        user_doc = self._user_repo.find_by_email(email)
        if not user_doc:
            raise InvalidCredentialsError()

        if user_doc.get("status") != "ACTIVE":
            raise InvalidCredentialsError("Your account has been deactivated.")

        # Verify password
        from werkzeug.security import check_password_hash
        if not check_password_hash(user_doc["password_hash"], password):
            raise InvalidCredentialsError()

        # Set session
        session.permanent = True
        session["user_id"] = str(user_doc["_id"])
        session["email"] = user_doc["email"]
        session["name"] = user_doc["name"]
        session["role"] = user_doc["role"]

        self._log_audit(str(user_doc["_id"]), "USER_LOGIN", "user", str(user_doc["_id"]))
        doc = {k: v for k, v in user_doc.items() if k != "password_hash"}
        doc["_id"] = str(doc["_id"])
        return doc

    def logout(self) -> None:
        user_id = session.get("user_id")
        if user_id:
            self._log_audit(user_id, "USER_LOGOUT", "user", user_id)
        session.clear()

    # ── Current user ─────────────────────────────────────────────────────
    def get_current_user(self) -> dict | None:
        user_id = session.get("user_id")
        if not user_id:
            return None
        doc = self._user_repo.find_by_id(user_id)
        if not doc:
            return None
        doc = {k: v for k, v in doc.items() if k != "password_hash"}
        doc["_id"] = str(doc["_id"])
        return doc

    # ── Internal helpers ─────────────────────────────────────────────────
    def _validate_registration_data(self, data: dict) -> None:
        required = ["name", "email", "phone", "password", "confirm_password"]
        for field in required:
            if not data.get(field, "").strip():
                raise ValidationError(f"'{field}' is required.")

        if not validate_email(data["email"]):
            raise ValidationError("Invalid email address.")

        if not validate_phone(data["phone"]):
            raise ValidationError("Invalid phone number.")

        valid_pwd, msg = validate_password(data["password"])
        if not valid_pwd:
            raise ValidationError(msg)

        if data["password"] != data["confirm_password"]:
            raise ValidationError("Passwords do not match.")

    def _log_audit(
        self, user_id: str, action: str, resource: str, resource_id: str, metadata: dict = None
    ) -> None:
        log = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "timestamp": datetime.utcnow(),
            "metadata": metadata or {},
        }
        self._user_repo.log_audit(log)
