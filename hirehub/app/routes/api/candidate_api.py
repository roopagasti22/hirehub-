"""Candidate REST API endpoints."""
from flask import Blueprint, request, session
from app.services.candidate_service import CandidateService
from app.utils.helpers import make_success_response, make_error_response
from app.utils.decorators import api_login_required, role_required
from app.exceptions import UserNotFoundError, UnauthorizedError, ValidationError

candidate_api_bp = Blueprint("candidate_api", __name__)
_svc = CandidateService()


@candidate_api_bp.route("/<candidate_id>", methods=["GET"])
@api_login_required
def get_candidate(candidate_id):
    try:
        profile = _svc.get_profile(candidate_id)
        return make_success_response(data=profile)
    except UserNotFoundError as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@candidate_api_bp.route("/<candidate_id>", methods=["PUT"])
@role_required("CANDIDATE")
def update_candidate(candidate_id):
    data = request.get_json(force=True) or {}
    try:
        profile = _svc.update_profile(candidate_id, data, session["user_id"])
        return make_success_response("Profile updated.", profile)
    except (UserNotFoundError, UnauthorizedError, ValidationError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)
