"""Recommendation service — returns jobs sorted by match score."""
from __future__ import annotations
from app.repositories import JobRepository, CandidateRepository
from .matching_service import MatchingService
from app.utils.helpers import serialize_doc


class RecommendationService:
    """Returns personalised job recommendations for a candidate."""

    def __init__(self) -> None:
        self._job_repo = JobRepository()
        self._candidate_repo = CandidateRepository()
        self._matching = MatchingService()

    def get_recommendations(
        self, candidate_id: str, limit: int = 10
    ) -> list[dict]:
        """Return up to `limit` recommended jobs sorted by match score."""
        candidate_doc = self._candidate_repo.find_by_id(candidate_id)
        if not candidate_doc:
            return []

        # Fetch a pool of open jobs
        jobs, _ = self._job_repo.search(status="OPEN", limit=100)

        scored = []
        for job in jobs:
            result = self._matching.calculate(candidate_doc, job)
            job_serialised = serialize_doc(job)
            job_serialised["match_score"] = result["score"]
            job_serialised["matched_skills"] = result["matched_skills"]
            job_serialised["missing_skills"] = result["missing_skills"]
            scored.append(job_serialised)

        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored[:limit]
