"""Recruiter repository."""
from __future__ import annotations
from typing import Optional
from bson import ObjectId
from .base_repository import BaseRepository
from app.extensions import get_db


class RecruiterRepository(BaseRepository):

    def __init__(self) -> None:
        super().__init__(get_db()["users"])

    def find_by_id(self, recruiter_id: str) -> Optional[dict]:
        try:
            return self._collection.find_one({"_id": ObjectId(recruiter_id), "role": "RECRUITER"})
        except Exception:
            return None

    def find_by_email(self, email: str) -> Optional[dict]:
        return self._collection.find_one({"email": email.lower(), "role": "RECRUITER"})

    def find_all(self, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many(
            {"role": "RECRUITER"},
            sort=[("created_at", -1)],
            skip=skip,
            limit=limit,
        )

    def count_all(self) -> int:
        return self.count({"role": "RECRUITER"})

    def update_profile(self, recruiter_id: str, data: dict) -> bool:
        return self.update_one(recruiter_id, data)

    def get_notifications(self, user_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
        db = get_db()
        return list(
            db["notifications"]
            .find({"user_id": user_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
