"""Job repository with filtering, sorting, and pagination."""
from __future__ import annotations
from typing import Optional
from bson import ObjectId
from pymongo import DESCENDING
from .base_repository import BaseRepository
from app.extensions import get_db


class JobRepository(BaseRepository):

    def __init__(self) -> None:
        super().__init__(get_db()["jobs"])

    def find_by_id(self, job_id: str) -> Optional[dict]:
        try:
            return self._collection.find_one({"_id": ObjectId(job_id)})
        except Exception:
            return None

    def insert_job(self, doc: dict) -> str:
        return self.insert_one(doc)

    def update_job(self, job_id: str, data: dict) -> bool:
        return self.update_one(job_id, data)

    def find_by_recruiter(self, recruiter_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many(
            {"recruiter_id": str(recruiter_id)},
            sort=[("created_at", -1)],
            skip=skip,
            limit=limit,
        )

    def count_by_recruiter(self, recruiter_id: str) -> int:
        return self.count({"recruiter_id": str(recruiter_id)})

    def search(
        self,
        keyword: str = "",
        skills: list = None,
        location: str = "",
        salary_min: int = None,
        salary_max: int = None,
        experience_min: int = None,
        work_mode: str = "",
        employment_type: str = "",
        company_id: str = "",
        status: str = "OPEN",
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[dict], int]:
        """Build a dynamic query and return (results, total_count)."""
        query: dict = {}

        if status:
            query["status"] = status.upper()

        if keyword:
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"description": {"$regex": keyword, "$options": "i"}},
            ]

        if skills:
            normalised = [s.strip().lower() for s in skills if s.strip()]
            if normalised:
                query["skills"] = {"$in": normalised}

        if location:
            query["location"] = {"$regex": location, "$options": "i"}

        if work_mode:
            query["work_mode"] = work_mode.upper()

        if employment_type:
            query["employment_type"] = employment_type.upper()

        if company_id:
            query["company_id"] = company_id

        if salary_min is not None:
            query.setdefault("salary_max", {})["$gte"] = salary_min

        if salary_max is not None:
            query.setdefault("salary_min", {})["$lte"] = salary_max

        if experience_min is not None:
            query["experience_max"] = {"$gte": experience_min}

        total = self._collection.count_documents(query)
        cursor = (
            self._collection.find(query)
            .sort("posted_date", DESCENDING)
            .skip(skip)
            .limit(limit)
        )
        return list(cursor), total

    def find_all(self, skip: int = 0, limit: int = 20, status: str = None) -> list[dict]:
        query = {}
        if status:
            query["status"] = status.upper()
        return self.find_many(query, sort=[("posted_date", -1)], skip=skip, limit=limit)

    def count_all(self, status: str = None) -> int:
        query = {}
        if status:
            query["status"] = status.upper()
        return self.count(query)
