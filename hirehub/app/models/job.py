"""Job domain model."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Job:
    """
    Represents a job posting.

    Demonstrates: class variables, properties, static validation methods.
    """

    WORK_MODES = ("REMOTE", "HYBRID", "ONSITE")
    EMPLOYMENT_TYPES = ("FULL_TIME", "PART_TIME", "INTERNSHIP", "CONTRACT")
    STATUSES = ("OPEN", "CLOSED", "EXPIRED")

    def __init__(
        self,
        title: str,
        company_id: str,
        recruiter_id: str,
        description: str = "",
        skills: Optional[list] = None,
        experience_min: int = 0,
        experience_max: int = 0,
        location: str = "",
        work_mode: str = "ONSITE",
        employment_type: str = "FULL_TIME",
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        deadline: Optional[datetime] = None,
        status: str = "OPEN",
        _id=None,
        posted_date: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = _id or ObjectId()
        self.title = title
        self.company_id = str(company_id)
        self.recruiter_id = str(recruiter_id)
        self.description = description
        self.skills: list = skills or []
        self.experience_min = experience_min
        self.experience_max = experience_max
        self.location = location
        self.work_mode = work_mode.upper()
        self.employment_type = employment_type.upper()
        self.salary_min = salary_min
        self.salary_max = salary_max
        self.deadline = deadline
        self.status = status.upper()
        self.posted_date = posted_date or datetime.utcnow()
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def is_open(self) -> bool:
        if self.status != "OPEN":
            return False
        if self.deadline and datetime.utcnow() > self.deadline:
            return False
        return True

    @property
    def is_expired(self) -> bool:
        return self.deadline is not None and datetime.utcnow() > self.deadline

    def close(self) -> None:
        self.status = "CLOSED"
        self.updated_at = datetime.utcnow()

    def expire(self) -> None:
        self.status = "EXPIRED"
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "title": self.title,
            "company_id": self.company_id,
            "recruiter_id": self.recruiter_id,
            "description": self.description,
            "skills": self.skills,
            "experience_min": self.experience_min,
            "experience_max": self.experience_max,
            "location": self.location,
            "work_mode": self.work_mode,
            "employment_type": self.employment_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "deadline": self.deadline,
            "status": self.status,
            "posted_date": self.posted_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d["_id"] = str(d["_id"])
        if d.get("deadline"):
            d["deadline"] = d["deadline"].isoformat()
        if d.get("posted_date"):
            d["posted_date"] = d["posted_date"].isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Job":
        return cls(
            title=data["title"],
            company_id=data.get("company_id", ""),
            recruiter_id=data.get("recruiter_id", ""),
            description=data.get("description", ""),
            skills=data.get("skills", []),
            experience_min=data.get("experience_min", 0),
            experience_max=data.get("experience_max", 0),
            location=data.get("location", ""),
            work_mode=data.get("work_mode", "ONSITE"),
            employment_type=data.get("employment_type", "FULL_TIME"),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            deadline=data.get("deadline"),
            status=data.get("status", "OPEN"),
            _id=data.get("_id"),
            posted_date=data.get("posted_date"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def is_valid_work_mode(mode: str) -> bool:
        return mode.upper() in Job.WORK_MODES

    @staticmethod
    def is_valid_employment_type(etype: str) -> bool:
        return etype.upper() in Job.EMPLOYMENT_TYPES

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title}>"
