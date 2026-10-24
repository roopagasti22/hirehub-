"""Resume upload, download, and deletion service."""
from __future__ import annotations
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from bson import ObjectId
from app.models import Resume
from app.extensions import get_db
from app.exceptions import ResumeUploadError, UnauthorizedError, ValidationError
from app.utils.helpers import serialize_doc


class ResumeService:
    """Handles file operations and resume metadata."""

    MAX_SIZE = 5 * 1024 * 1024  # 5 MB

    def __init__(self, upload_folder: str) -> None:
        self._upload_folder = upload_folder
        self._db = get_db()
        os.makedirs(upload_folder, exist_ok=True)

    def upload(self, file: FileStorage, candidate_id: str) -> dict:
        """Validate and save a resume file."""
        if not file or not file.filename:
            raise ResumeUploadError("No file provided.")

        original_name = secure_filename(file.filename)

        if not Resume.is_allowed_extension(original_name):
            raise ResumeUploadError("Only PDF, DOC, and DOCX files are allowed.")

        # Read content for size check
        content = file.read()
        if len(content) > self.MAX_SIZE:
            raise ResumeUploadError("File size exceeds the 5 MB limit.")
        file.seek(0)

        mime = file.content_type or ""
        if mime and not Resume.is_allowed_mimetype(mime):
            raise ResumeUploadError("Invalid file MIME type.")

        # Generate unique stored filename
        ext = original_name.rsplit(".", 1)[-1].lower()
        stored_name = f"{uuid.uuid4().hex}.{ext}"
        file_path = os.path.join(self._upload_folder, stored_name)
        file.save(file_path)

        # Remove old resume if exists
        existing = self._db["resumes"].find_one({"candidate_id": str(candidate_id)})
        if existing:
            self._delete_file(existing.get("stored_filename", ""))
            self._db["resumes"].delete_one({"_id": existing["_id"]})

        resume = Resume(
            candidate_id=candidate_id,
            original_filename=original_name,
            stored_filename=stored_name,
            file_size=len(content),
            mime_type=mime,
        )
        doc = resume.to_dict()
        result = self._db["resumes"].insert_one(doc)
        resume_id = str(result.inserted_id)

        # Update candidate record
        self._db["users"].update_one(
            {"_id": ObjectId(candidate_id)},
            {"$set": {"resume_id": resume_id, "updated_at": datetime.utcnow()}},
        )

        doc["_id"] = resume_id
        return serialize_doc(doc)

    def get_metadata(self, resume_id: str) -> dict | None:
        doc = self._db["resumes"].find_one({"_id": ObjectId(resume_id)})
        if doc:
            return serialize_doc(doc)
        return None

    def get_by_candidate(self, candidate_id: str) -> dict | None:
        doc = self._db["resumes"].find_one({"candidate_id": str(candidate_id)})
        if doc:
            return serialize_doc(doc)
        return None

    def get_file_path(self, resume_id: str, requesting_user_id: str, requesting_role: str) -> str:
        """Return the absolute file path after authorisation check."""
        doc = self._db["resumes"].find_one({"_id": ObjectId(resume_id)})
        if not doc:
            raise FileNotFoundError("Resume not found.")

        # Authorisation: candidate owns it OR recruiter/admin
        if requesting_role == "CANDIDATE" and str(doc["candidate_id"]) != str(requesting_user_id):
            raise UnauthorizedError("You cannot access this resume.")

        file_path = os.path.join(self._upload_folder, doc["stored_filename"])
        if not os.path.exists(file_path):
            raise FileNotFoundError("Resume file not found on server.")
        return file_path, doc["original_filename"]

    def delete(self, resume_id: str, candidate_id: str) -> bool:
        doc = self._db["resumes"].find_one({"_id": ObjectId(resume_id)})
        if not doc:
            return False
        if str(doc["candidate_id"]) != str(candidate_id):
            raise UnauthorizedError()
        self._delete_file(doc.get("stored_filename", ""))
        self._db["resumes"].delete_one({"_id": ObjectId(resume_id)})
        self._db["users"].update_one(
            {"_id": ObjectId(candidate_id)},
            {"$set": {"resume_id": None, "updated_at": datetime.utcnow()}},
        )
        return True

    def _delete_file(self, stored_filename: str) -> None:
        if stored_filename:
            path = os.path.join(self._upload_folder, stored_filename)
            if os.path.exists(path):
                os.remove(path)
