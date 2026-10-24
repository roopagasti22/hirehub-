"""Recruiter profile service."""
from __future__ import annotations
from app.repositories import RecruiterRepository
from app.exceptions import UserNotFoundError, UnauthorizedError, ValidationError
from app.utils.validators import validate_phone


class RecruiterService:
    """Manages recruiter profile operations."""

    def __init__(self) -> None:
        self._repo = RecruiterRepository()

    def get_profile(self, recruiter_id: str) -> dict:
        doc = self._repo.find_by_id(recruiter_id)
        if not doc:
            raise UserNotFoundError()
        doc["_id"] = str(doc["_id"])
        doc.pop("password_hash", None)
        return doc

    def update_profile(self, recruiter_id: str, data: dict, requesting_user_id: str) -> dict:
        if recruiter_id != requesting_user_id:
            raise UnauthorizedError("You can only edit your own profile.")
        allowed = ["name", "phone", "designation"]
        update = {k: v for k, v in data.items() if k in allowed}
        if "phone" in update and not validate_phone(update["phone"]):
            raise ValidationError("Invalid phone number.")
        self._repo.update_profile(recruiter_id, update)
        return self.get_profile(recruiter_id)

    def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        skip = (page - 1) * per_page
        docs = self._repo.find_all(skip=skip, limit=per_page)
        total = self._repo.count_all()
        for d in docs:
            d["_id"] = str(d["_id"])
            d.pop("password_hash", None)
        return {"items": docs, "total": total, "page": page, "per_page": per_page}
