"""Analytics service — aggregates and formats chart data."""
from __future__ import annotations
from app.repositories import AnalyticsRepository


class AnalyticsService:
    """Wraps AnalyticsRepository and shapes data for Chart.js."""

    def __init__(self) -> None:
        self._repo = AnalyticsRepository()

    def get_admin_analytics(self) -> dict:
        return {
            "overview": self._repo.platform_overview(),
            "jobs_by_skill": self._format_label_value(self._repo.jobs_by_skill()),
            "jobs_by_location": self._format_label_value(self._repo.jobs_by_location()),
            "jobs_by_work_mode": self._format_label_value(self._repo.jobs_by_work_mode()),
            "jobs_by_employment_type": self._format_label_value(self._repo.jobs_by_employment_type()),
            "applications_by_status": self._format_label_value(self._repo.applications_by_status()),
            "monthly_applications": self._format_monthly(self._repo.monthly_applications()),
            "monthly_registrations": self._format_monthly(self._repo.monthly_registrations()),
            "top_skills": self._format_label_value(self._repo.top_skills()),
        }

    def get_recruiter_analytics(self, recruiter_id: str) -> dict:
        return self._repo.recruiter_stats(recruiter_id)

    def get_candidate_analytics(self, candidate_id: str) -> dict:
        return self._repo.candidate_stats(candidate_id)

    @staticmethod
    def _format_label_value(raw: list) -> dict:
        return {
            "labels": [r["_id"] or "Unknown" for r in raw],
            "values": [r["count"] for r in raw],
        }

    @staticmethod
    def _format_monthly(raw: list) -> dict:
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        labels = []
        values = []
        for r in raw:
            y = r["_id"].get("year", "")
            m = r["_id"].get("month", 1)
            labels.append(f"{months[m - 1]} {y}")
            values.append(r["count"])
        return {"labels": labels, "values": values}
