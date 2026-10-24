"""Interview scheduling service."""
from __future__ import annotations
from datetime import datetime
from app.models import Interview
from app.repositories import InterviewRepository, ApplicationRepository, JobRepository
from app.exceptions import (
    InterviewNotFoundError, ApplicationNotFoundError,
    UnauthorizedError, ValidationError,
)
from app.utils.helpers import serialize_doc
from .notification_service import NotificationService


class InterviewService:
    """Manages interview scheduling and updates."""

    def __init__(self) -> None:
        self._interview_repo = InterviewRepository()
        self._app_repo = ApplicationRepository()
        self._job_repo = JobRepository()
        self._notification_svc = NotificationService()

    def schedule(self, data: dict, recruiter_id: str) -> dict:
        """Schedule an interview for an application."""
        app_id = data.get("application_id", "")
        app_doc = self._app_repo.find_by_id(app_id)
        if not app_doc:
            raise ApplicationNotFoundError()

        job_doc = self._job_repo.find_by_id(app_doc["job_id"])
        if not job_doc or str(job_doc.get("recruiter_id")) != str(recruiter_id):
            raise UnauthorizedError("You can only schedule interviews for your own jobs.")

        # Parse date
        try:
            date = datetime.strptime(data["date"], "%Y-%m-%d")
        except (ValueError, KeyError):
            raise ValidationError("Invalid or missing date. Use YYYY-MM-DD.")

        interview = Interview(
            application_id=app_id,
            candidate_id=app_doc["candidate_id"],
            recruiter_id=recruiter_id,
            date=date,
            time=data.get("time", ""),
            interview_type=data.get("interview_type", "ONLINE"),
            meeting_link=data.get("meeting_link", ""),
        )
        doc = interview.to_dict()
        interview_id = self._interview_repo.insert_one(doc)

        # Link interview to application and update status
        self._app_repo.set_interview(app_id, interview_id)
        self._app_repo.update_status(app_id, "INTERVIEW_SCHEDULED")

        # Notify candidate
        self._notification_svc.create(
            user_id=app_doc["candidate_id"],
            title="Interview Scheduled",
            message=(
                f"An interview has been scheduled for you on "
                f"{date.strftime('%B %d, %Y')} at {data.get('time', '')}."
            ),
            notification_type="INTERVIEW_SCHEDULED",
            resource_id=interview_id,
            resource_type="interview",
        )

        doc["_id"] = interview_id
        return serialize_doc(doc)

    def update_interview(self, interview_id: str, data: dict, recruiter_id: str) -> dict:
        doc = self._interview_repo.find_by_id(interview_id)
        if not doc:
            raise InterviewNotFoundError()
        if str(doc["recruiter_id"]) != str(recruiter_id):
            raise UnauthorizedError()

        allowed = ["date", "time", "interview_type", "meeting_link", "status", "feedback"]
        update = {k: v for k, v in data.items() if k in allowed}

        if "date" in update and update["date"]:
            try:
                update["date"] = datetime.strptime(update["date"], "%Y-%m-%d")
            except ValueError:
                raise ValidationError("Invalid date format.")

        if update.get("status") == "CANCELLED":
            self._notification_svc.create(
                user_id=doc["candidate_id"],
                title="Interview Cancelled",
                message="Your scheduled interview has been cancelled.",
                notification_type="INTERVIEW_CANCELLED",
                resource_id=interview_id,
                resource_type="interview",
            )

        self._interview_repo.update_interview(interview_id, update)
        return self.get_interview(interview_id)

    def get_interview(self, interview_id: str) -> dict:
        doc = self._interview_repo.find_by_id(interview_id)
        if not doc:
            raise InterviewNotFoundError()
        return serialize_doc(doc)

    def get_candidate_interviews(self, candidate_id: str) -> list:
        docs = self._interview_repo.find_by_candidate(candidate_id)
        return [serialize_doc(d) for d in docs]

    def get_recruiter_interviews(self, recruiter_id: str) -> list:
        docs = self._interview_repo.find_by_recruiter(recruiter_id)
        return [serialize_doc(d) for d in docs]
