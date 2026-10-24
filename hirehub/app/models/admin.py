"""Admin domain model (inherits from User)."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from .user import User


class Admin(User):
    """Admin user — not publicly registerable."""

    def __init__(
        self,
        name: str,
        email: str,
        phone: str = "",
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
            role="ADMIN",
            password_hash=password_hash,
            status=status,
            _id=_id,
            created_at=created_at,
            updated_at=updated_at,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Admin":
        return cls(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            password_hash=data.get("password_hash", ""),
            status=data.get("status", "ACTIVE"),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        return f"<Admin id={self.id} email={self.email}>"
