"""General helper utilities."""
from __future__ import annotations
from flask import jsonify, request
from bson import ObjectId
from datetime import datetime
from typing import Any


def make_success_response(message: str = "Success", data: Any = None, status_code: int = 200):
    """Return a standardised JSON success response."""
    payload = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status_code


def make_error_response(message: str, error_code: str = "ERROR", status_code: int = 400):
    """Return a standardised JSON error response."""
    payload = {"success": False, "message": message, "error_code": error_code}
    return jsonify(payload), status_code


def paginate(query_result: list, page: int, per_page: int) -> dict:
    """Slice a list for pagination and return metadata."""
    total = len(query_result)
    start = (page - 1) * per_page
    end = start + per_page
    items = query_result[start:end]
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


def serialize_doc(doc) -> Any:
    """Recursively convert a MongoDB document to a JSON-serialisable structure."""
    if isinstance(doc, dict):
        return {k: serialize_doc(v) for k, v in doc.items()}
    if isinstance(doc, list):
        return [serialize_doc(i) for i in doc]
    if isinstance(doc, ObjectId):
        return str(doc)
    if isinstance(doc, datetime):
        return doc.isoformat()
    return doc


def get_pagination_params() -> tuple[int, int]:
    """Extract page and per_page from request query args."""
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        per_page = min(100, max(1, int(request.args.get("per_page", 10))))
    except (ValueError, TypeError):
        per_page = 10
    return page, per_page
