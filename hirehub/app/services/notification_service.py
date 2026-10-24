"""Notification service."""
from __future__ import annotations
from datetime import datetime
from bson import ObjectId
from app.extensions import get_db


class NotificationService:
    """Create and manage user notifications."""

    def __init__(self) -> None:
        self._db = get_db()

    def create(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str = "GENERAL",
        resource_id: str = None,
        resource_type: str = None,
    ) -> str:
        doc = {
            "user_id": str(user_id),
            "title": title,
            "message": message,
            "notification_type": notification_type.upper(),
            "is_read": False,
            "resource_id": resource_id,
            "resource_type": resource_type,
            "created_at": datetime.utcnow(),
        }
        result = self._db["notifications"].insert_one(doc)
        return str(result.inserted_id)

    def get_for_user(self, user_id: str, skip: int = 0, limit: int = 20) -> list[dict]:
        docs = list(
            self._db["notifications"]
            .find({"user_id": str(user_id)})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        for d in docs:
            d["_id"] = str(d["_id"])
            if isinstance(d.get("created_at"), datetime):
                d["created_at"] = d["created_at"].isoformat()
        return docs

    def count_unread(self, user_id: str) -> int:
        return self._db["notifications"].count_documents(
            {"user_id": str(user_id), "is_read": False}
        )

    def mark_read(self, notification_id: str, user_id: str) -> bool:
        result = self._db["notifications"].update_one(
            {"_id": ObjectId(notification_id), "user_id": str(user_id)},
            {"$set": {"is_read": True}},
        )
        return result.modified_count > 0

    def mark_all_read(self, user_id: str) -> int:
        result = self._db["notifications"].update_many(
            {"user_id": str(user_id), "is_read": False},
            {"$set": {"is_read": True}},
        )
        return result.modified_count
