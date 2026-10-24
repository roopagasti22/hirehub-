"""Company repository."""
from __future__ import annotations
from typing import Optional
from bson import ObjectId
from .base_repository import BaseRepository
from app.extensions import get_db


class CompanyRepository(BaseRepository):

    def __init__(self) -> None:
        super().__init__(get_db()["companies"])

    def find_by_id(self, company_id: str) -> Optional[dict]:
        try:
            return self._collection.find_one({"_id": ObjectId(company_id)})
        except Exception:
            return None

    def find_by_recruiter(self, recruiter_id: str) -> Optional[dict]:
        return self._collection.find_one({"recruiter_id": str(recruiter_id)})

    def find_all(self, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many({}, sort=[("created_at", -1)], skip=skip, limit=limit)

    def count_all(self) -> int:
        return self.count({})

    def find_verified(self) -> list[dict]:
        return self.find_many({"verification_status": "VERIFIED"})

    def update_verification(self, company_id: str, status: str) -> bool:
        return self.update_one(company_id, {"verification_status": status})
