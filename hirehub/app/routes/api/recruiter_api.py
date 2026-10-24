"""Recruiter REST API endpoints."""
from flask import Blueprint, request, session
from app.services.recruiter_service import RecruiterService
from app.utils.helpers import make_success_response, make_error_response
from app.utils.decorators import api_login_required, role_required
from app.exceptions import UserNotFoundError, UnauthorizedError, ValidationError

recruiter_api_bp = Blueprint("recruiter_api", __name__)
_svc = RecruiterService()


@recruiter_api_bp.route("/<recruiter_id>", methods=["GET"])
@api_login_required
def get_recruiter(recruiter_id):
    try:
        profile = _svc.get_profile(recruiter_id)
        return make_success_response(data=profile)
    except UserNotFoundError as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@recruiter_api_bp.route("/<recruiter_id>", methods=["PUT"])
@role_required("RECRUITER")
def update_recruiter(recruiter_id):
    data = request.get_json(force=True) or {}
    try:
        profile = _svc.update_profile(recruiter_id, data, session["user_id"])
        return make_success_response("Profile updated.", profile)
    except (UserNotFoundError, UnauthorizedError, ValidationError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)
