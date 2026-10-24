"""Notification domain model."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Notification:
    """User notification with read/unread state."""

    TYPES = (
        "REGISTRATION", "APPLICATION_SUBMITTED", "APPLICATION_SHORTLISTED",
        "APPLICATION_REJECTED", "INTERVIEW_SCHEDULED", "INTERVIEW_CANCELLED",
        "CANDIDATE_SELECTED", "GENERAL",
    )

    def __init__(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "GENERAL",
        is_read: bool = False,
        resource_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        _id=None,
        created_at: Optional[datetime] = None,
    ) -> None:
        self._id = _id or ObjectId()
        self.user_id = str(user_id)
        self.title = title
        self.message = message
        self.notification_type = notification_type.upper()
        self.is_read = is_read
        self.resource_id = resource_id
        self.resource_type = resource_type
        self.created_at = created_at or datetime.utcnow()

    @property
    def id(self) -> str:
        return str(self._id)

    def mark_read(self) -> None:
        self.is_read = True

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "user_id": self.user_id,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "is_read": self.is_read,
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "created_at": self.created_at,
        }

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d["_id"] = str(d["_id"])
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        return cls(
            user_id=data["user_id"],
            title=data["title"],
            message=data["message"],
            notification_type=data.get("notification_type", "GENERAL"),
            is_read=data.get("is_read", False),
            resource_id=data.get("resource_id"),
            resource_type=data.get("resource_type"),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
        )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user={self.user_id} read={self.is_read}>"
