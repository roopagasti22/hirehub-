"""Resume domain model."""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from bson import ObjectId


class Resume:
    """Stores resume metadata; actual file lives on disk."""

    ALLOWED_EXTENSIONS = {"pdf", "doc", "docx"}
    ALLOWED_MIMETYPES = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }

    def __init__(
        self,
        candidate_id: str,
        original_filename: str,
        stored_filename: str,
        file_size: int,
        mime_type: str,
        _id=None,
        uploaded_at: Optional[datetime] = None,
    ) -> None:
        self._id = _id or ObjectId()
        self.candidate_id = str(candidate_id)
        self.original_filename = original_filename
        self.stored_filename = stored_filename
        self.file_size = file_size
        self.mime_type = mime_type
        self.uploaded_at = uploaded_at or datetime.utcnow()

    @property
    def id(self) -> str:
        return str(self._id)

    @property
    def extension(self) -> str:
        return self.original_filename.rsplit(".", 1)[-1].lower() if "." in self.original_filename else ""

    def to_dict(self) -> dict:
        return {
            "_id": self._id,
            "candidate_id": self.candidate_id,
            "original_filename": self.original_filename,
            "stored_filename": self.stored_filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "uploaded_at": self.uploaded_at,
        }

    def to_public_dict(self) -> dict:
        d = self.to_dict()
        d["_id"] = str(d["_id"])
        if isinstance(d.get("uploaded_at"), datetime):
            d["uploaded_at"] = d["uploaded_at"].isoformat()
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Resume":
        return cls(
            candidate_id=data["candidate_id"],
            original_filename=data["original_filename"],
            stored_filename=data["stored_filename"],
            file_size=data.get("file_size", 0),
            mime_type=data.get("mime_type", ""),
            _id=data.get("_id"),
            uploaded_at=data.get("uploaded_at"),
        )

    @staticmethod
    def is_allowed_extension(filename: str) -> bool:
        if "." not in filename:
            return False
        ext = filename.rsplit(".", 1)[-1].lower()
        return ext in Resume.ALLOWED_EXTENSIONS

    @staticmethod
    def is_allowed_mimetype(mime: str) -> bool:
        return mime in Resume.ALLOWED_MIMETYPES

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file={self.original_filename}>"
