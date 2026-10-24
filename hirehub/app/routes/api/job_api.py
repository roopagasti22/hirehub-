"""Job REST API endpoints."""
from flask import Blueprint, request, session
from app.services.job_service import JobService
from app.utils.helpers import make_success_response, make_error_response
from app.utils.decorators import api_login_required, role_required
from app.exceptions import JobNotFoundError, UnauthorizedError, ValidationError

job_api_bp = Blueprint("job_api", __name__)
_svc = JobService()


@job_api_bp.route("/", methods=["GET"])
def list_jobs():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    skills_raw = request.args.get("skill", "")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
    result = _svc.search_jobs(
        keyword=request.args.get("q", ""),
        skills=skills,
        location=request.args.get("location", ""),
        work_mode=request.args.get("work_mode", ""),
        employment_type=request.args.get("employment_type", ""),
        page=page,
        per_page=per_page,
    )
    return make_success_response(data=result)


@job_api_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    try:
        job = _svc.get_job(job_id)
        return make_success_response(data=job)
    except JobNotFoundError as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@job_api_bp.route("/", methods=["POST"])
@role_required("RECRUITER")
def create_job():
    data = request.get_json(force=True) or {}
    try:
        job = _svc.create_job(data, session["user_id"])
        return make_success_response("Job created.", job, 201)
    except (ValidationError, UnauthorizedError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@job_api_bp.route("/<job_id>", methods=["PUT"])
@role_required("RECRUITER")
def update_job(job_id):
    data = request.get_json(force=True) or {}
    try:
        job = _svc.update_job(job_id, data, session["user_id"])
        return make_success_response("Job updated.", job)
    except (JobNotFoundError, UnauthorizedError, ValidationError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@job_api_bp.route("/<job_id>", methods=["DELETE"])
@role_required("RECRUITER")
def close_job(job_id):
    try:
        job = _svc.close_job(job_id, session["user_id"])
        return make_success_response("Job closed.", job)
    except (JobNotFoundError, UnauthorizedError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@job_api_bp.route("/<job_id>/apply", methods=["POST"])
@role_required("CANDIDATE")
def apply_to_job(job_id):
    from app.services.application_service import ApplicationService
    from app.exceptions import (
        DuplicateApplicationError, JobClosedError, ApplicationNotFoundError,
    )
    app_svc = ApplicationService()
    try:
        result = app_svc.apply(session["user_id"], job_id)
        return make_success_response("Application submitted successfully.", result, 201)
    except (DuplicateApplicationError, JobClosedError, JobNotFoundError) as e:
        return make_error_response(str(e), e.error_code, e.status_code)
