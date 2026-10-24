"""Job service — creation, update, search."""
from __future__ import annotations
from datetime import datetime
from bson import ObjectId
from app.models import Job
from app.repositories import JobRepository, CompanyRepository
from app.exceptions import JobNotFoundError, UnauthorizedError, ValidationError
from app.utils.validators import validate_salary, validate_experience
from app.utils.helpers import serialize_doc


class JobService:
    """Business logic for job management."""

    def __init__(self) -> None:
        self._job_repo = JobRepository()
        self._company_repo = CompanyRepository()

    def create_job(self, data: dict, recruiter_id: str) -> dict:
        """Create a new job posting."""
        self._validate_job_data(data)

        # Resolve company
        company_doc = self._company_repo.find_by_recruiter(recruiter_id)
        company_id = str(company_doc["_id"]) if company_doc else ""

        deadline = None
        if data.get("deadline"):
            try:
                deadline = datetime.strptime(data["deadline"], "%Y-%m-%d")
            except ValueError:
                raise ValidationError("Invalid deadline format. Use YYYY-MM-DD.")

        skills = self._parse_skills(data.get("skills", []))

        job = Job(
            title=data["title"].strip(),
            company_id=company_id,
            recruiter_id=recruiter_id,
            description=data.get("description", "").strip(),
            skills=skills,
            experience_min=int(data.get("experience_min", 0)),
            experience_max=int(data.get("experience_max", 0)),
            location=data.get("location", "").strip(),
            work_mode=data.get("work_mode", "ONSITE"),
            employment_type=data.get("employment_type", "FULL_TIME"),
            salary_min=int(data["salary_min"]) if data.get("salary_min") else None,
            salary_max=int(data["salary_max"]) if data.get("salary_max") else None,
            deadline=deadline,
        )
        doc = job.to_dict()
        job_id = self._job_repo.insert_job(doc)
        doc["_id"] = job_id
        return serialize_doc(doc)

    def update_job(self, job_id: str, data: dict, recruiter_id: str) -> dict:
        job_doc = self._job_repo.find_by_id(job_id)
        if not job_doc:
            raise JobNotFoundError()
        if str(job_doc["recruiter_id"]) != str(recruiter_id):
            raise UnauthorizedError("You can only edit your own jobs.")

        allowed = [
            "title", "description", "skills", "experience_min", "experience_max",
            "location", "work_mode", "employment_type", "salary_min", "salary_max",
            "deadline", "status",
        ]
        update = {k: v for k, v in data.items() if k in allowed}

        if "skills" in update:
            update["skills"] = self._parse_skills(update["skills"])
        if "deadline" in update and update["deadline"]:
            try:
                update["deadline"] = datetime.strptime(update["deadline"], "%Y-%m-%d")
            except ValueError:
                raise ValidationError("Invalid deadline format.")

        self._job_repo.update_job(job_id, update)
        return self.get_job(job_id)

    def close_job(self, job_id: str, recruiter_id: str) -> dict:
        job_doc = self._job_repo.find_by_id(job_id)
        if not job_doc:
            raise JobNotFoundError()
        if str(job_doc["recruiter_id"]) != str(recruiter_id):
            raise UnauthorizedError()
        self._job_repo.update_job(job_id, {"status": "CLOSED"})
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> dict:
        doc = self._job_repo.find_by_id(job_id)
        if not doc:
            raise JobNotFoundError()
        return serialize_doc(doc)

    def search_jobs(
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
        page: int = 1,
        per_page: int = 10,
    ) -> dict:
        skip = (page - 1) * per_page
        results, total = self._job_repo.search(
            keyword=keyword,
            skills=skills or [],
            location=location,
            salary_min=salary_min,
            salary_max=salary_max,
            experience_min=experience_min,
            work_mode=work_mode,
            employment_type=employment_type,
            company_id=company_id,
            status=status,
            skip=skip,
            limit=per_page,
        )
        serialised = [serialize_doc(r) for r in results]
        pages = max(1, (total + per_page - 1) // per_page)
        return {
            "items": serialised,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    def get_recruiter_jobs(self, recruiter_id: str, page: int = 1, per_page: int = 20) -> dict:
        skip = (page - 1) * per_page
        docs = self._job_repo.find_by_recruiter(recruiter_id, skip=skip, limit=per_page)
        total = self._job_repo.count_by_recruiter(recruiter_id)
        return {
            "items": [serialize_doc(d) for d in docs],
            "total": total,
            "page": page,
        }

    def get_all_jobs(self, page: int = 1, per_page: int = 20, status: str = None) -> dict:
        skip = (page - 1) * per_page
        docs = self._job_repo.find_all(skip=skip, limit=per_page, status=status)
        total = self._job_repo.count_all(status=status)
        pages = max(1, (total + per_page - 1) // per_page)
        return {"items": [serialize_doc(d) for d in docs], "total": total, "pages": pages}

    # ── Helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _parse_skills(skills) -> list:
        if isinstance(skills, str):
            return [s.strip().lower() for s in skills.split(",") if s.strip()]
        if isinstance(skills, list):
            return [s.strip().lower() for s in skills if isinstance(s, str) and s.strip()]
        return []

    @staticmethod
    def _validate_job_data(data: dict) -> None:
        if not data.get("title", "").strip():
            raise ValidationError("Job title is required.")
        if not data.get("location", "").strip():
            raise ValidationError("Location is required.")
        if data.get("work_mode") and not Job.is_valid_work_mode(data["work_mode"]):
            raise ValidationError("Invalid work mode.")
        if data.get("employment_type") and not Job.is_valid_employment_type(data["employment_type"]):
            raise ValidationError("Invalid employment type.")
