"""Interview repository."""
from __future__ import annotations
from typing import Optional
from bson import ObjectId
from .base_repository import BaseRepository
from app.extensions import get_db


class InterviewRepository(BaseRepository):

    def __init__(self) -> None:
        super().__init__(get_db()["interviews"])

    def find_by_id(self, interview_id: str) -> Optional[dict]:
        try:
            return self._collection.find_one({"_id": ObjectId(interview_id)})
        except Exception:
            return None

    def find_by_candidate(self, candidate_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many(
            {"candidate_id": str(candidate_id)},
            sort=[("date", -1)],
            skip=skip,
            limit=limit,
        )

    def find_by_recruiter(self, recruiter_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many(
            {"recruiter_id": str(recruiter_id)},
            sort=[("date", -1)],
            skip=skip,
            limit=limit,
        )

    def find_by_application(self, application_id: str) -> Optional[dict]:
        return self._collection.find_one({"application_id": str(application_id)})

    def count_all(self) -> int:
        return self.count({})

    def update_interview(self, interview_id: str, data: dict) -> bool:
        return self.update_one(interview_id, data)
