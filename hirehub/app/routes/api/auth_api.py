"""Authentication REST API endpoints."""
from flask import Blueprint, request, session
from app.services.auth_service import AuthService
from app.utils.helpers import make_success_response, make_error_response
from app.utils.decorators import api_login_required
from app.exceptions import (
    UserAlreadyExistsError, InvalidCredentialsError, ValidationError,
)

auth_api_bp = Blueprint("auth_api", __name__)
_svc = AuthService()


@auth_api_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True) or {}
    role = data.get("role", "CANDIDATE").upper()
    try:
        if role == "CANDIDATE":
            result = _svc.register_candidate(data)
        elif role == "RECRUITER":
            result = _svc.register_recruiter(data)
        else:
            return make_error_response("Invalid role. Choose CANDIDATE or RECRUITER.", "INVALID_ROLE", 400)
        result["_id"] = str(result.get("_id", ""))
        result.pop("password_hash", None)
        return make_success_response("Registration successful.", result, 201)
    except UserAlreadyExistsError as e:
        return make_error_response(str(e), e.error_code, e.status_code)
    except ValidationError as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@auth_api_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")
    try:
        user = _svc.login(email, password)
        return make_success_response("Login successful.", user)
    except InvalidCredentialsError as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@auth_api_bp.route("/logout", methods=["POST"])
def logout():
    _svc.logout()
    return make_success_response("Logged out successfully.")


@auth_api_bp.route("/me", methods=["GET"])
@api_login_required
def me():
    user = _svc.get_current_user()
    if not user:
        return make_error_response("User not found.", "USER_NOT_FOUND", 404)
    return make_success_response(data=user)
