"""Base User domain model demonstrating OOP concepts."""
from __future__ import annotations
from datetime import datetime
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional


class User:
    """
    Base user class.

    Demonstrates:
    - Constructor / instance variables
    - Instance methods
    - Class variables
    - Class methods
    - Static methods
    - Properties
    - Encapsulation
    """

    # Class variables
    ROLES = ("CANDIDATE", "RECRUITER", "ADMIN")
    STATUSES = ("ACTIVE", "INACTIVE", "SUSPENDED")

    def __init__(
        self,
        name: str,
        email: str,
        phone: str,
        role: str,
        password_hash: str = "",
        status: str = "ACTIVE",
        _id=None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        self._id = _id or ObjectId()
        self.name = name
        self._email = email.lower().strip()
        self.phone = phone
        self.role = role.upper()
        self._password_hash = password_hash
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    # ── Properties (encapsulation) ───────────────────────────────────────
    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        self._email = value.lower().strip()

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    # ── Password management ──────────────────────────────────────────────
    def set_password(self, plain_password: str) -> None:
        """Hash and store the password. Never stores plain text."""
        self._password_hash = generate_password_hash(plain_password)

    def check_password(self, plain_password: str) -> bool:
        """Return True if plain_password matches the stored hash."""
        return check_password_hash(self._password_hash, plain_password)

    # ── Instance methods ─────────────────────────────────────────────────
    def to_dict(self) -> dict:
        """Serialise to a MongoDB-ready dictionary."""
        return {
            "_id": self._id,
            "name": self.name,
            "email": self._email,
            "phone": self.phone,
            "role": self.role,
            "password_hash": self._password_hash,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_public_dict(self) -> dict:
        """Serialise without sensitive fields."""
        d = self.to_dict()
        d.pop("password_hash", None)
        d["_id"] = str(d["_id"])
        return d

    def touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        self.status = "INACTIVE"
        self.touch()

    def activate(self) -> None:
        self.status = "ACTIVE"
        self.touch()

    # ── Class methods ────────────────────────────────────────────────────
    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Reconstruct a User from a MongoDB document."""
        return cls(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            role=data["role"],
            password_hash=data.get("password_hash", ""),
            status=data.get("status", "ACTIVE"),
            _id=data.get("_id"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    # ── Static methods ───────────────────────────────────────────────────
    @staticmethod
    def is_valid_role(role: str) -> bool:
        return role.upper() in User.ROLES

    # ── Dunder methods ───────────────────────────────────────────────────
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self._email} role={self.role}>"
