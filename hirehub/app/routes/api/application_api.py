"""Application REST API endpoints."""
from flask import Blueprint, request, session
from app.services.application_service import ApplicationService
from app.utils.helpers import make_success_response, make_error_response
from app.utils.decorators import api_login_required, role_required
from app.exceptions import (
    ApplicationNotFoundError, DuplicateApplicationError,
    InvalidApplicationStatusError, UnauthorizedError,
)

application_api_bp = Blueprint("application_api", __name__)
_svc = ApplicationService()


@application_api_bp.route("/", methods=["GET"])
@api_login_required
def list_applications():
    role = session.get("role")
    user_id = session["user_id"]
    page = int(request.args.get("page", 1))

    if role == "CANDIDATE":
        result = _svc.get_candidate_applications(user_id, page=page)
    elif role in ("RECRUITER", "ADMIN"):
        result = _svc.get_all_applications(page=page)
    else:
        return make_error_response("Unauthorized.", "UNAUTHORIZED", 403)

    return make_success_response(data=result)


@application_api_bp.route("/<app_id>", methods=["GET"])
@api_login_required
def get_application(app_id):
    try:
        app = _svc.get_application(app_id)
        return make_success_response(data=app)
    except ApplicationNotFoundError as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@application_api_bp.route("/<app_id>/status", methods=["PUT"])
@role_required("RECRUITER", "ADMIN")
def update_status(app_id):
    data = request.get_json(force=True) or {}
    new_status = data.get("status", "")
    notes = data.get("notes", "")
    try:
        app = _svc.update_status(app_id, new_status, session["user_id"], notes)
        return make_success_response("Status updated.", app)
    except (ApplicationNotFoundError, InvalidApplicationStatusError, UnauthorizedError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@application_api_bp.route("/<app_id>/withdraw", methods=["POST"])
@role_required("CANDIDATE")
def withdraw(app_id):
    try:
        app = _svc.withdraw(app_id, session["user_id"])
        return make_success_response("Application withdrawn.", app)
    except (ApplicationNotFoundError, UnauthorizedError, InvalidApplicationStatusError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)
