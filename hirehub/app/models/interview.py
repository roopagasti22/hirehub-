"""Interview domain model."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Interview:
    """Represents a scheduled interview."""

    TYPES = ("ONLINE", "PHONE", "IN_PERSON")
    STATUSES = ("SCHEDULED", "COMPLETED", "CANCELLED")

    def __init__(
        self,
        application_id: str,
        candidate_id: str,
        recruiter_id: str,
        date: datetime,
        time: str,
        interview_type: str = "ONLINE",
        meeting_link: str = "",
        status: str = "SCHEDULED",
        feedback: str = "",
        _id=None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = _id or ObjectId()
        self.application_id = str(application_id)
        self.candidate_id = str(candidate_id)
        self.recruiter_id = str(recruiter_id)
        self.date = date
        self.time = time
        self.interview_type = interview_type.upper()
        self.meeting_link = meeting_link
        self.status = status.upper()
        self.feedback = feedback
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> str:
        return str(self._id)

    def complete(self, feedback: str = "") -> None:
        self.status = "COMPLETED"
        self.feedback = feedback
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        self.status = "CANCELLED"
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "application_id": self.application_id,
            "candidate_id": self.candidate_id,
            "recruiter_id": self.recruiter_id,
            "date": self.date,
            "time": self.time,
            "interview_type": self.interview_type,
            "meeting_link": self.meeting_link,
            "status": self.status,
            "feedback": self.feedback,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d["_id"] = str(d["_id"])
        if isinstance(d.get("date"), datetime):
            d["date"] = d["date"].isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Interview":
        return cls(
            application_id=data["application_id"],
            candidate_id=data["candidate_id"],
            recruiter_id=data["recruiter_id"],
            date=data["date"],
            time=data.get("time", ""),
            interview_type=data.get("interview_type", "ONLINE"),
            meeting_link=data.get("meeting_link", ""),
            status=data.get("status", "SCHEDULED"),
            feedback=data.get("feedback", ""),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def is_valid_type(t: str) -> bool:
        return t.upper() in Interview.TYPES

    def __repr__(self) -> str:
        return f"<Interview id={self.id} status={self.status}>"
