"""Authentication and authorization decorators."""
from __future__ import annotations
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from app.exceptions import UnauthorizedError


def _is_api_request() -> bool:
    """Return True if the request expects a JSON response."""
    return (
        request.path.startswith("/api/")
        or request.accept_mimetypes.best == "application/json"
    )


def login_required(f):
    """Decorator: redirect to login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            if _is_api_request():
                return jsonify({
                    "success": False,
                    "message": "Authentication required.",
                    "error_code": "UNAUTHENTICATED",
                }), 401
            return redirect(url_for("web.auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """Decorator: allow access only to users with one of the given roles."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                if _is_api_request():
                    return jsonify({
                        "success": False,
                        "message": "Authentication required.",
                        "error_code": "UNAUTHENTICATED",
                    }), 401
                return redirect(url_for("web.auth.login"))
            user_role = session.get("role", "")
            if user_role not in [r.upper() for r in roles]:
                if _is_api_request():
                    return jsonify({
                        "success": False,
                        "message": "You are not authorized to access this resource.",
                        "error_code": "UNAUTHORIZED",
                    }), 403
                return redirect(url_for("web.auth.login"))
            return f(*args, **kwargs)
        return decorated
    return decorator


def api_login_required(f):
    """Decorator for API endpoints that always returns JSON."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({
                "success": False,
                "message": "Authentication required.",
                "error_code": "UNAUTHENTICATED",
            }), 401
        return f(*args, **kwargs)
    return decorated
