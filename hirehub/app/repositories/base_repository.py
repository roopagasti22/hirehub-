"""Abstract base repository — defines the repository contract."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Optional
from pymongo.collection import Collection
from bson import ObjectId
from datetime import datetime


class BaseRepository(ABC):
    """
    Abstract base class for all repositories.

    Demonstrates:
    - Abstraction
    - Template method pattern
    - Concrete CRUD helpers shared by subclasses
    """

    def __init__(self, collection: Collection) -> None:
        self._collection = collection

    # ── Abstract interface ───────────────────────────────────────────────
    @abstractmethod
    def find_by_id(self, doc_id: str) -> Optional[dict]:
        ...

    # ── Concrete helpers ─────────────────────────────────────────────────
    def insert_one(self, document: dict) -> str:
        """Insert a document and return its string id."""
        result = self._collection.insert_one(document)
        return str(result.inserted_id)

    def find_one(self, query: dict) -> Optional[dict]:
        return self._collection.find_one(query)

    def find_many(
        self,
        query: dict,
        sort: Optional[list] = None,
        skip: int = 0,
        limit: int = 0,
    ) -> list[dict]:
        cursor = self._collection.find(query)
        if sort:
            cursor = cursor.sort(sort)
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_one(self, doc_id: str, update_data: dict) -> bool:
        update_data["updated_at"] = datetime.utcnow()
        result = self._collection.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": update_data},
        )
        return result.modified_count > 0

    def delete_one(self, doc_id: str) -> bool:
        result = self._collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0

    def count(self, query: dict) -> int:
        return self._collection.count_documents(query)

    @staticmethod
    def to_object_id(value: str) -> ObjectId:
        return ObjectId(value)
