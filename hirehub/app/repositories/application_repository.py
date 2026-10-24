"""Application repository."""
from __future__ import annotations
from typing import Optional
from bson import ObjectId
from .base_repository import BaseRepository
from app.extensions import get_db


class ApplicationRepository(BaseRepository):

    def __init__(self) -> None:
        super().__init__(get_db()["applications"])

    def find_by_id(self, app_id: str) -> Optional[dict]:
        try:
            return self._collection.find_one({"_id": ObjectId(app_id)})
        except Exception:
            return None

    def find_by_candidate(self, candidate_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many(
            {"candidate_id": str(candidate_id)},
            sort=[("applied_at", -1)],
            skip=skip,
            limit=limit,
        )

    def find_by_job(self, job_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many(
            {"job_id": str(job_id)},
            sort=[("applied_at", -1)],
            skip=skip,
            limit=limit,
        )

    def find_by_candidate_and_job(self, candidate_id: str, job_id: str) -> Optional[dict]:
        return self._collection.find_one({
            "candidate_id": str(candidate_id),
            "job_id": str(job_id),
        })

    def count_by_candidate(self, candidate_id: str) -> int:
        return self.count({"candidate_id": str(candidate_id)})

    def count_by_job(self, job_id: str) -> int:
        return self.count({"job_id": str(job_id)})

    def count_all(self) -> int:
        return self.count({})

    def find_for_recruiter_jobs(
        self, job_ids: list, skip: int = 0, limit: int = 20
    ) -> list[dict]:
        return self.find_many(
            {"job_id": {"$in": [str(jid) for jid in job_ids]}},
            sort=[("applied_at", -1)],
            skip=skip,
            limit=limit,
        )

    def update_status(self, app_id: str, status: str, notes: str = "") -> bool:
        data = {"status": status.upper()}
        if notes:
            data["recruiter_notes"] = notes
        return self.update_one(app_id, data)

    def set_interview(self, app_id: str, interview_id: str) -> bool:
        return self.update_one(app_id, {"interview_id": interview_id})

    def find_all(self, skip: int = 0, limit: int = 50) -> list[dict]:
        return self.find_many({}, sort=[("applied_at", -1)], skip=skip, limit=limit)
