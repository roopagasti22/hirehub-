"""User repository — handles users collection."""
from __future__ import annotations
from typing import Optional
from bson import ObjectId
from .base_repository import BaseRepository
from app.extensions import get_db


class UserRepository(BaseRepository):
    """CRUD operations for the users collection."""

    def __init__(self) -> None:
        super().__init__(get_db()["users"])

    def find_by_id(self, user_id: str) -> Optional[dict]:
        try:
            return self._collection.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    def find_by_email(self, email: str) -> Optional[dict]:
        return self._collection.find_one({"email": email.lower().strip()})

    def find_all(self, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many({}, sort=[("created_at", -1)], skip=skip, limit=limit)

    def find_by_role(self, role: str, skip: int = 0, limit: int = 20) -> list[dict]:
        return self.find_many(
            {"role": role.upper()},
            sort=[("created_at", -1)],
            skip=skip,
            limit=limit,
        )

    def email_exists(self, email: str) -> bool:
        return self._collection.count_documents({"email": email.lower().strip()}) > 0

    def update_status(self, user_id: str, status: str) -> bool:
        return self.update_one(user_id, {"status": status})

    def log_audit(self, log_doc: dict) -> str:
        """Insert an audit log entry into the audit_logs collection."""
        db = get_db()
        result = db["audit_logs"].insert_one(log_doc)
        return str(result.inserted_id)

    def get_audit_logs(
        self,
        query: dict = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        db = get_db()
        cursor = db["audit_logs"].find(query or {}).sort("timestamp", -1).skip(skip).limit(limit)
        return list(cursor)

    def count_audit_logs(self, query: dict = None) -> int:
        db = get_db()
        return db["audit_logs"].count_documents(query or {})
