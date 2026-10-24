"""Candidate domain model (inherits from User)."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bson import ObjectId
from .user import User


class Candidate(User):
    """
    Candidate user type.

    Demonstrates:
    - Inheritance from User
    - Method overriding (to_dict, from_dict)
    - Composition (resume metadata embedded)
    - Additional instance variables
    """

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        password_hash: str = "",
        location: str = "",
        skills: Optional[list] = None,
        education: Optional[list] = None,
        experience: Optional[list] = None,
        expected_salary: Optional[int] = None,
        notice_period: Optional[int] = None,
        resume_id: Optional[str] = None,
        saved_jobs: Optional[list] = None,
        profile_complete: int = 0,
        status: str = "ACTIVE",
        _id=None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            name=name,
            email=email,
            phone=phone,
            role="CANDIDATE",
            password_hash=password_hash,
            status=status,
            _id=_id,
            created_at=created_at,
            updated_at=updated_at,
        )
        self.location = location
        self.skills: list = skills or []
        self.education: list = education or []
        self.experience: list = experience or []
        self.expected_salary = expected_salary
        self.notice_period = notice_period  # days
        self.resume_id = resume_id
        self.saved_jobs: list = saved_jobs or []
        self._profile_complete = profile_complete

    # ── Property ─────────────────────────────────────────────────────────
    @property
    def profile_complete(self) -> int:
        """Calculate profile completion percentage."""
        fields = [
            self.name, self.phone, self.location,
            self.skills, self.education, self.experience,
            self.expected_salary, self.resume_id,
        ]
        filled = sum(1 for f in fields if f)
        return int((filled / len(fields)) * 100)

    # ── Method overriding ────────────────────────────────────────────────
    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "location": self.location,
            "skills": self.skills,
            "education": self.education,
            "experience": self.experience,
            "expected_salary": self.expected_salary,
            "notice_period": self.notice_period,
            "resume_id": self.resume_id,
            "saved_jobs": self.saved_jobs,
            "profile_complete": self.profile_complete,
        })
        return base

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d.pop("password_hash", None)
        d["_id"] = str(d["_id"])
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Candidate":
        return cls(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            password_hash=data.get("password_hash", ""),
            location=data.get("location", ""),
            skills=data.get("skills", []),
            education=data.get("education", []),
            experience=data.get("experience", []),
            expected_salary=data.get("expected_salary"),
            notice_period=data.get("notice_period"),
            resume_id=data.get("resume_id"),
            saved_jobs=data.get("saved_jobs", []),
            profile_complete=data.get("profile_complete", 0),
            status=data.get("status", "ACTIVE"),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    # ── Instance methods ─────────────────────────────────────────────────
    def add_skill(self, skill: str) -> None:
        if skill not in self.skills:
            self.skills.append(skill)
            self.touch()

    def save_job(self, job_id: str) -> None:
        if job_id not in self.saved_jobs:
            self.saved_jobs.append(job_id)

    def unsave_job(self, job_id: str) -> None:
        if job_id in self.saved_jobs:
            self.saved_jobs.remove(job_id)

    def __repr__(self) -> str:
        return f"<Candidate id={self.id} email={self.email}>"
