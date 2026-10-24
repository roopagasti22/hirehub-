"""Application domain model."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Application:
    """Represents a candidate's job application."""

    STATUSES = (
        "APPLIED", "UNDER_REVIEW", "SHORTLISTED",
        "INTERVIEW_SCHEDULED", "SELECTED", "REJECTED", "WITHDRAWN",
    )

    # Valid status transitions
    TRANSITIONS: dict = {
        "APPLIED": ["UNDER_REVIEW", "SHORTLISTED", "REJECTED", "WITHDRAWN"],
        "UNDER_REVIEW": ["SHORTLISTED", "REJECTED"],
        "SHORTLISTED": ["INTERVIEW_SCHEDULED", "REJECTED"],
        "INTERVIEW_SCHEDULED": ["SELECTED", "REJECTED"],
        "SELECTED": [],
        "REJECTED": [],
        "WITHDRAWN": [],
    }

    def __init__(
        self,
        candidate_id: str,
        job_id: str,
        status: str = "APPLIED",
        recruiter_notes: str = "",
        interview_id: Optional[str] = None,
        _id=None,
        applied_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = _id or ObjectId()
        self.candidate_id = str(candidate_id)
        self.job_id = str(job_id)
        self.status = status.upper()
        self.recruiter_notes = recruiter_notes
        self.interview_id = interview_id
        self.applied_at = applied_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def can_withdraw(self) -> bool:
        return self.status in ("APPLIED", "UNDER_REVIEW", "SHORTLISTED")

    def can_transition_to(self, new_status: str) -> bool:
        """Check if a transition to new_status is allowed."""
        return new_status in self.TRANSITIONS.get(self.status, [])

    def update_status(self, new_status: str) -> None:
        if not self.can_transition_to(new_status):
            raise ValueError(
                f"Invalid transition from {self.status} to {new_status}"
            )
        self.status = new_status
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "status": self.status,
            "recruiter_notes": self.recruiter_notes,
            "interview_id": self.interview_id,
            "applied_at": self.applied_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d["_id"] = str(d["_id"])
        if d.get("applied_at"):
            d["applied_at"] = d["applied_at"].isoformat()
        if d.get("updated_at"):
            d["updated_at"] = d["updated_at"].isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Application":
        return cls(
            candidate_id=data["candidate_id"],
            job_id=data["job_id"],
            status=data.get("status", "APPLIED"),
            recruiter_notes=data.get("recruiter_notes", ""),
            interview_id=data.get("interview_id"),
            _id=data.get("_id"),
            applied_at=data.get("applied_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def is_valid_status(status: str) -> bool:
        return status.upper() in Application.STATUSES

    def __repr__(self) -> str:
        return f"<Application id={self.id} job={self.job_id} candidate={self.candidate_id}>"
