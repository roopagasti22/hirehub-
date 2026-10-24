"""Report service — generates CSV-ready data."""
from __future__ import annotations
import csv
import io
from datetime import datetime
from app.extensions import get_db
from app.utils.helpers import serialize_doc


class ReportService:
    """Generates filterable reports and CSV exports."""

    def __init__(self) -> None:
        self._db = get_db()

    # ── Candidate report ─────────────────────────────────────────────────
    def candidate_report(self, filters: dict = None) -> list[dict]:
        query = {"role": "CANDIDATE"}
        self._apply_date_filter(query, "created_at", filters)
        docs = list(self._db["users"].find(query).sort("created_at", -1).limit(500))
        result = []
        for d in docs:
            result.append({
                "id": str(d["_id"]),
                "name": d.get("name", ""),
                "email": d.get("email", ""),
                "phone": d.get("phone", ""),
                "location": d.get("location", ""),
                "skills": ", ".join(d.get("skills", [])),
                "status": d.get("status", ""),
                "registered": d.get("created_at", ""),
            })
        return result

    # ── Job report ───────────────────────────────────────────────────────
    def job_report(self, filters: dict = None) -> list[dict]:
        query = {}
        if filters:
            if filters.get("status"):
                query["status"] = filters["status"].upper()
            if filters.get("location"):
                query["location"] = {"$regex": filters["location"], "$options": "i"}
            if filters.get("company_id"):
                query["company_id"] = filters["company_id"]
        self._apply_date_filter(query, "created_at", filters)
        docs = list(self._db["jobs"].find(query).sort("posted_date", -1).limit(500))
        result = []
        for d in docs:
            result.append({
                "id": str(d["_id"]),
                "title": d.get("title", ""),
                "company_id": d.get("company_id", ""),
                "location": d.get("location", ""),
                "work_mode": d.get("work_mode", ""),
                "employment_type": d.get("employment_type", ""),
                "status": d.get("status", ""),
                "posted_date": d.get("posted_date", ""),
                "skills": ", ".join(d.get("skills", [])),
            })
        return result

    # ── Application report ───────────────────────────────────────────────
    def application_report(self, filters: dict = None) -> list[dict]:
        query = {}
        if filters:
            if filters.get("status"):
                query["status"] = filters["status"].upper()
            if filters.get("job_id"):
                query["job_id"] = filters["job_id"]
        self._apply_date_filter(query, "applied_at", filters)
        docs = list(self._db["applications"].find(query).sort("applied_at", -1).limit(500))
        result = []
        for d in docs:
            result.append({
                "id": str(d["_id"]),
                "candidate_id": d.get("candidate_id", ""),
                "job_id": d.get("job_id", ""),
                "status": d.get("status", ""),
                "applied_at": d.get("applied_at", ""),
                "updated_at": d.get("updated_at", ""),
            })
        return result

    # ── CSV generation ───────────────────────────────────────────────────
    def to_csv(self, data: list[dict]) -> str:
        """Convert a list of dicts to a CSV string."""
        if not data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            # Convert datetime objects to strings
            clean_row = {k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in row.items()}
            writer.writerow(clean_row)
        return output.getvalue()

    @staticmethod
    def _apply_date_filter(query: dict, field: str, filters: dict) -> None:
        if not filters:
            return
        date_filter = {}
        if filters.get("date_from"):
            try:
                date_filter["$gte"] = datetime.strptime(filters["date_from"], "%Y-%m-%d")
            except ValueError:
                pass
        if filters.get("date_to"):
            try:
                date_filter["$lte"] = datetime.strptime(filters["date_to"], "%Y-%m-%d")
            except ValueError:
                pass
        if date_filter:
            query[field] = date_filter
