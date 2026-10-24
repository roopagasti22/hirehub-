"""Company domain model."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Company:
    """
    Represents a company in HireHub.

    Demonstrates:
    - Standalone domain class (composition with Recruiter)
    - Class variables, static methods, properties
    """

    VERIFICATION_STATUSES = ("PENDING", "VERIFIED", "REJECTED")

    def __init__(
        self,
        name: str,
        recruiter_id: str,
        industry: str = "",
        website: str = "",
        description: str = "",
        location: str = "",
        size: str = "",
        logo_url: str = "",
        verification_status: str = "PENDING",
        _id=None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = _id or ObjectId()
        self.name = name
        self.recruiter_id = str(recruiter_id)
        self.industry = industry
        self.website = website
        self.description = description
        self.location = location
        self.size = size
        self.logo_url = logo_url
        self.verification_status = verification_status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def is_verified(self) -> bool:
        return self.verification_status == "VERIFIED"

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "name": self.name,
            "recruiter_id": self.recruiter_id,
            "industry": self.industry,
            "website": self.website,
            "description": self.description,
            "location": self.location,
            "size": self.size,
            "logo_url": self.logo_url,
            "verification_status": self.verification_status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d["_id"] = str(d["_id"])
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Company":
        return cls(
            name=data["name"],
            recruiter_id=data.get("recruiter_id", ""),
            industry=data.get("industry", ""),
            website=data.get("website", ""),
            description=data.get("description", ""),
            location=data.get("location", ""),
            size=data.get("size", ""),
            logo_url=data.get("logo_url", ""),
            verification_status=data.get("verification_status", "PENDING"),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def is_valid_verification_status(status: str) -> bool:
        return status in Company.VERIFICATION_STATUSES

    def verify(self) -> None:
        self.verification_status = "VERIFIED"
        self.updated_at = datetime.utcnow()

    def reject(self) -> None:
        self.verification_status = "REJECTED"
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name}>"
