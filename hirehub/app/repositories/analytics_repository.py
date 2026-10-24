"""Analytics repository — uses MongoDB aggregation pipelines."""
from __future__ import annotations
from datetime import datetime
from app.extensions import get_db


class AnalyticsRepository:
    """All analytics queries using MongoDB aggregation pipelines."""

    def __init__(self) -> None:
        self._db = get_db()

    # ── Job analytics ────────────────────────────────────────────────────
    def jobs_by_skill(self) -> list[dict]:
        return list(self._db["jobs"].aggregate([
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 20},
        ]))

    def jobs_by_location(self) -> list[dict]:
        return list(self._db["jobs"].aggregate([
            {"$group": {"_id": "$location", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 15},
        ]))

    def jobs_by_work_mode(self) -> list[dict]:
        return list(self._db["jobs"].aggregate([
            {"$group": {"_id": "$work_mode", "count": {"$sum": 1}}},
        ]))

    def jobs_by_employment_type(self) -> list[dict]:
        return list(self._db["jobs"].aggregate([
            {"$group": {"_id": "$employment_type", "count": {"$sum": 1}}},
        ]))

    # ── Application analytics ────────────────────────────────────────────
    def applications_by_status(self) -> list[dict]:
        return list(self._db["applications"].aggregate([
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]))

    def applications_by_job(self, limit: int = 10) -> list[dict]:
        return list(self._db["applications"].aggregate([
            {"$group": {"_id": "$job_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]))

    def monthly_applications(self) -> list[dict]:
        return list(self._db["applications"].aggregate([
            {"$group": {
                "_id": {
                    "year": {"$year": "$applied_at"},
                    "month": {"$month": "$applied_at"},
                },
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
            {"$limit": 12},
        ]))

    # ── User analytics ───────────────────────────────────────────────────
    def monthly_registrations(self) -> list[dict]:
        return list(self._db["users"].aggregate([
            {"$group": {
                "_id": {
                    "year": {"$year": "$created_at"},
                    "month": {"$month": "$created_at"},
                },
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
            {"$limit": 12},
        ]))

    def user_counts_by_role(self) -> dict:
        pipeline = [
            {"$group": {"_id": "$role", "count": {"$sum": 1}}},
        ]
        result = list(self._db["users"].aggregate(pipeline))
        return {r["_id"]: r["count"] for r in result}

    # ── Recruiter-specific ───────────────────────────────────────────────
    def recruiter_stats(self, recruiter_id: str) -> dict:
        job_ids = [
            str(j["_id"])
            for j in self._db["jobs"].find({"recruiter_id": str(recruiter_id)}, {"_id": 1})
        ]
        total_jobs = len(job_ids)
        active_jobs = self._db["jobs"].count_documents({
            "recruiter_id": str(recruiter_id), "status": "OPEN"
        })
        total_applications = self._db["applications"].count_documents(
            {"job_id": {"$in": job_ids}}
        )
        shortlisted = self._db["applications"].count_documents(
            {"job_id": {"$in": job_ids}, "status": "SHORTLISTED"}
        )
        selected = self._db["applications"].count_documents(
            {"job_id": {"$in": job_ids}, "status": "SELECTED"}
        )
        interviews = self._db["interviews"].count_documents(
            {"recruiter_id": str(recruiter_id)}
        )
        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_applications,
            "shortlisted": shortlisted,
            "selected": selected,
            "interviews": interviews,
        }

    # ── Candidate-specific ───────────────────────────────────────────────
    def candidate_stats(self, candidate_id: str) -> dict:
        total = self._db["applications"].count_documents({"candidate_id": str(candidate_id)})
        shortlisted = self._db["applications"].count_documents(
            {"candidate_id": str(candidate_id), "status": "SHORTLISTED"}
        )
        interviews = self._db["interviews"].count_documents(
            {"candidate_id": str(candidate_id)}
        )
        selected = self._db["applications"].count_documents(
            {"candidate_id": str(candidate_id), "status": "SELECTED"}
        )
        return {
            "total_applications": total,
            "shortlisted": shortlisted,
            "interviews": interviews,
            "selected": selected,
        }

    # ── Admin-level ──────────────────────────────────────────────────────
    def platform_overview(self) -> dict:
        db = self._db
        return {
            "total_users": db["users"].count_documents({}),
            "candidates": db["users"].count_documents({"role": "CANDIDATE"}),
            "recruiters": db["users"].count_documents({"role": "RECRUITER"}),
            "companies": db["companies"].count_documents({}),
            "total_jobs": db["jobs"].count_documents({}),
            "open_jobs": db["jobs"].count_documents({"status": "OPEN"}),
            "total_applications": db["applications"].count_documents({}),
            "total_interviews": db["interviews"].count_documents({}),
            "selected": db["applications"].count_documents({"status": "SELECTED"}),
        }

    def top_skills(self, limit: int = 15) -> list[dict]:
        return list(self._db["jobs"].aggregate([
            {"$unwind": "$skills"},
            {"$group": {"_id": "$skills", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]))
