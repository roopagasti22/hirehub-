"""Candidate profile and saved-jobs service."""
from __future__ import annotations
from flask import session
from app.repositories import CandidateRepository
from app.exceptions import UserNotFoundError, UnauthorizedError, ValidationError
from app.utils.validators import validate_phone


class CandidateService:
    """Manages candidate profile operations."""

    def __init__(self) -> None:
        self._repo = CandidateRepository()

    def get_profile(self, candidate_id: str) -> dict:
        doc = self._repo.find_by_id(candidate_id)
        if not doc:
            raise UserNotFoundError()
        doc["_id"] = str(doc["_id"])
        doc.pop("password_hash", None)
        return doc

    def update_profile(self, candidate_id: str, data: dict, requesting_user_id: str) -> dict:
        """Update profile — only the owner may update."""
        if candidate_id != requesting_user_id:
            raise UnauthorizedError("You can only edit your own profile.")

        allowed = [
            "name", "phone", "location", "skills",
            "education", "experience", "expected_salary", "notice_period",
        ]
        update = {k: v for k, v in data.items() if k in allowed}

        if "phone" in update and not validate_phone(update["phone"]):
            raise ValidationError("Invalid phone number.")

        if "skills" in update:
            if not isinstance(update["skills"], list):
                update["skills"] = [s.strip().lower() for s in update["skills"].split(",") if s.strip()]
            else:
                update["skills"] = [s.strip().lower() for s in update["skills"] if s.strip()]

        self._repo.update_profile(candidate_id, update)

        # Refresh session name if changed
        if "name" in update:
            session["name"] = update["name"]

        return self.get_profile(candidate_id)

    def save_job(self, candidate_id: str, job_id: str) -> None:
        doc = self._repo.find_by_id(candidate_id)
        if not doc:
            raise UserNotFoundError()
        saved = doc.get("saved_jobs", [])
        if job_id not in saved:
            saved.append(job_id)
            self._repo.update_profile(candidate_id, {"saved_jobs": saved})

    def unsave_job(self, candidate_id: str, job_id: str) -> None:
        doc = self._repo.find_by_id(candidate_id)
        if not doc:
            raise UserNotFoundError()
        saved = doc.get("saved_jobs", [])
        if job_id in saved:
            saved.remove(job_id)
            self._repo.update_profile(candidate_id, {"saved_jobs": saved})

    def get_saved_jobs(self, candidate_id: str) -> list:
        doc = self._repo.find_by_id(candidate_id)
        if not doc:
            return []
        return doc.get("saved_jobs", [])

    def search_candidates(self, skills: list, page: int = 1, per_page: int = 10) -> dict:
        skip = (page - 1) * per_page
        docs = self._repo.search_by_skills(skills, skip=skip, limit=per_page)
        for d in docs:
            d["_id"] = str(d["_id"])
            d.pop("password_hash", None)
        return {"items": docs, "page": page, "per_page": per_page}
