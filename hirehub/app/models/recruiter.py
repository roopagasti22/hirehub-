"""Recruiter domain model (inherits from User)."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from .user import User


class Recruiter(User):
    """
    Recruiter user type.

    Demonstrates:
    - Inheritance, method overriding
    - Composition with company_id
    """

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        company_id: Optional[str] = None,
        company_name: str = "",
        designation: str = "",
        password_hash: str = "",
        status: str = "ACTIVE",
        _id=None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(
            name=name,
            email=email,
            phone=phone,
            role="RECRUITER",
            password_hash=password_hash,
            status=status,
            _id=_id,
            created_at=created_at,
            updated_at=updated_at,
        )
        self.company_id = company_id
        self.company_name = company_name
        self.designation = designation

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            "company_id": self.company_id,
            "company_name": self.company_name,
            "designation": self.designation,
        })
        return base

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d.pop("password_hash", None)
        d["_id"] = str(d["_id"])
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Recruiter":
        return cls(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            company_id=data.get("company_id"),
            company_name=data.get("company_name", ""),
            designation=data.get("designation", ""),
            password_hash=data.get("password_hash", ""),
            status=data.get("status", "ACTIVE"),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return f"<Recruiter id={self.id} email={self.email}>"
