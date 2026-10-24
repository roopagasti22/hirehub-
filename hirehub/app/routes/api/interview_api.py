"""Interview REST API endpoints."""
from flask import Blueprint, request, session
from app.services.interview_service import InterviewService
from app.utils.helpers import make_success_response, make_error_response
from app.utils.decorators import api_login_required, role_required
from app.exceptions import InterviewNotFoundError, UnauthorizedError, ValidationError

interview_api_bp = Blueprint("interview_api", __name__)
_svc = InterviewService()


@interview_api_bp.route("/", methods=["POST"])
@role_required("RECRUITER")
def schedule():
    data = request.get_json(force=True) or {}
    try:
        interview = _svc.schedule(data, session["user_id"])
        return make_success_response("Interview scheduled.", interview, 201)
    except (ValidationError, UnauthorizedError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@interview_api_bp.route("/", methods=["GET"])
@api_login_required
def list_interviews():
    user_id = session["user_id"]
    role = session.get("role")
    if role == "CANDIDATE":
        items = _svc.get_candidate_interviews(user_id)
    else:
        items = _svc.get_recruiter_interviews(user_id)
    return make_success_response(data={"items": items})


@interview_api_bp.route("/<interview_id>", methods=["PUT"])
@role_required("RECRUITER")
def update_interview(interview_id):
    data = request.get_json(force=True) or {}
    try:
        interview = _svc.update_interview(interview_id, data, session["user_id"])
        return make_success_response("Interview updated.", interview)
    except (InterviewNotFoundError, UnauthorizedError, ValidationError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)
