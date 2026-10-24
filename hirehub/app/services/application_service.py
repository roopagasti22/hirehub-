"""Application service — apply, withdraw, status management."""
from __future__ import annotations
from datetime import datetime
from app.models import Application
from app.repositories import ApplicationRepository, JobRepository
from app.exceptions import (
    ApplicationNotFoundError, DuplicateApplicationError,
    JobNotFoundError, JobClosedError, InvalidApplicationStatusError,
    UnauthorizedError,
)
from app.utils.helpers import serialize_doc
from .notification_service import NotificationService


class ApplicationService:
    """Business logic for job applications."""

    def __init__(self) -> None:
        self._app_repo = ApplicationRepository()
        self._job_repo = JobRepository()
        self._notification_svc = NotificationService()

    def apply(self, candidate_id: str, job_id: str) -> dict:
        """Submit a new application."""
        # Validate job
        job_doc = self._job_repo.find_by_id(job_id)
        if not job_doc:
            raise JobNotFoundError()

        if job_doc.get("status") != "OPEN":
            raise JobClosedError()

        if job_doc.get("deadline"):
            deadline = job_doc["deadline"]
            if isinstance(deadline, str):
                deadline = datetime.fromisoformat(deadline)
            if datetime.utcnow() > deadline:
                raise JobClosedError("The application deadline for this job has passed.")

        # Check for duplicate
        existing = self._app_repo.find_by_candidate_and_job(candidate_id, job_id)
        if existing:
            raise DuplicateApplicationError()

        app = Application(candidate_id=candidate_id, job_id=job_id)
        doc = app.to_dict()
        app_id = self._app_repo.insert_one(doc)

        # Notify candidate
        self._notification_svc.create(
            user_id=candidate_id,
            title="Application Submitted",
            message=f"Your application for '{job_doc.get('title', 'the job')}' has been submitted.",
            notification_type="APPLICATION_SUBMITTED",
            resource_id=app_id,
            resource_type="application",
        )

        doc["_id"] = app_id
        return serialize_doc(doc)

    def withdraw(self, application_id: str, candidate_id: str) -> dict:
        doc = self._app_repo.find_by_id(application_id)
        if not doc:
            raise ApplicationNotFoundError()
        if str(doc["candidate_id"]) != str(candidate_id):
            raise UnauthorizedError("You can only withdraw your own applications.")
        app = Application.from_dict(doc)
        if not app.can_withdraw:
            raise InvalidApplicationStatusError("Application cannot be withdrawn at this stage.")
        self._app_repo.update_status(application_id, "WITHDRAWN")
        return self.get_application(application_id)

    def update_status(
        self, application_id: str, new_status: str, recruiter_id: str, notes: str = ""
    ) -> dict:
        doc = self._app_repo.find_by_id(application_id)
        if not doc:
            raise ApplicationNotFoundError()

        # Verify recruiter owns the job
        job_doc = self._job_repo.find_by_id(doc["job_id"])
        if not job_doc or str(job_doc.get("recruiter_id")) != str(recruiter_id):
            raise UnauthorizedError("You can only manage applications for your own jobs.")

        app = Application.from_dict(doc)
        if not app.can_transition_to(new_status):
            raise InvalidApplicationStatusError(
                f"Cannot transition from {app.status} to {new_status}."
            )

        self._app_repo.update_status(application_id, new_status, notes)

        # Send notification to candidate
        notification_map = {
            "SHORTLISTED": ("Application Shortlisted", "Congratulations! Your application has been shortlisted.", "APPLICATION_SHORTLISTED"),
            "REJECTED": ("Application Update", "Your application has been reviewed and was not selected at this time.", "APPLICATION_REJECTED"),
            "SELECTED": ("Offer Extended!", "Congratulations! You have been selected for the position.", "CANDIDATE_SELECTED"),
        }
        if new_status in notification_map:
            title, message, n_type = notification_map[new_status]
            self._notification_svc.create(
                user_id=doc["candidate_id"],
                title=title,
                message=message,
                notification_type=n_type,
                resource_id=application_id,
                resource_type="application",
            )

        return self.get_application(application_id)

    def get_application(self, application_id: str) -> dict:
        doc = self._app_repo.find_by_id(application_id)
        if not doc:
            raise ApplicationNotFoundError()
        return serialize_doc(doc)

    def get_candidate_applications(self, candidate_id: str, page: int = 1, per_page: int = 10) -> dict:
        skip = (page - 1) * per_page
        docs = self._app_repo.find_by_candidate(candidate_id, skip=skip, limit=per_page)
        total = self._app_repo.count_by_candidate(candidate_id)
        return {
            "items": [serialize_doc(d) for d in docs],
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(1, (total + per_page - 1) // per_page),
        }

    def get_job_applications(self, job_id: str, page: int = 1, per_page: int = 20) -> dict:
        skip = (page - 1) * per_page
        docs = self._app_repo.find_by_job(job_id, skip=skip, limit=per_page)
        total = self._app_repo.count_by_job(job_id)
        return {
            "items": [serialize_doc(d) for d in docs],
            "total": total,
            "page": page,
        }

    def get_all_applications(self, page: int = 1, per_page: int = 50) -> dict:
        skip = (page - 1) * per_page
        docs = self._app_repo.find_all(skip=skip, limit=per_page)
        total = self._app_repo.count_all()
        return {"items": [serialize_doc(d) for d in docs], "total": total}
