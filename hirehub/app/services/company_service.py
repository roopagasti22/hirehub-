"""Company service."""
from __future__ import annotations
from app.repositories import CompanyRepository
from app.exceptions import CompanyNotFoundError, UnauthorizedError


class CompanyService:
    """Manages company profile operations."""

    def __init__(self) -> None:
        self._repo = CompanyRepository()

    def get_company(self, company_id: str) -> dict:
        doc = self._repo.find_by_id(company_id)
        if not doc:
            raise CompanyNotFoundError()
        doc["_id"] = str(doc["_id"])
        return doc

    def get_by_recruiter(self, recruiter_id: str) -> dict | None:
        doc = self._repo.find_by_recruiter(recruiter_id)
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    def update_company(self, company_id: str, data: dict, recruiter_id: str) -> dict:
        doc = self._repo.find_by_id(company_id)
        if not doc:
            raise CompanyNotFoundError()
        if str(doc.get("recruiter_id")) != str(recruiter_id):
            raise UnauthorizedError("You can only edit your own company.")
        allowed = ["name", "industry", "website", "description", "location", "size"]
        update = {k: v for k, v in data.items() if k in allowed}
        self._repo.update_one(company_id, update)
        return self.get_company(company_id)

    def verify_company(self, company_id: str) -> dict:
        doc = self._repo.find_by_id(company_id)
        if not doc:
            raise CompanyNotFoundError()
        self._repo.update_verification(company_id, "VERIFIED")
        return self.get_company(company_id)

    def reject_company(self, company_id: str) -> dict:
        doc = self._repo.find_by_id(company_id)
        if not doc:
            raise CompanyNotFoundError()
        self._repo.update_verification(company_id, "REJECTED")
        return self.get_company(company_id)

    def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        skip = (page - 1) * per_page
        docs = self._repo.find_all(skip=skip, limit=per_page)
        total = self._repo.count_all()
        for d in docs:
            d["_id"] = str(d["_id"])
        return {"items": docs, "total": total, "page": page, "per_page": per_page}
