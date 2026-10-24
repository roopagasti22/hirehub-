"""Resume REST API endpoints."""
from flask import Blueprint, request, session, current_app, send_file
from app.services.resume_service import ResumeService
from app.utils.helpers import make_success_response, make_error_response
from app.utils.decorators import api_login_required, role_required
from app.exceptions import ResumeUploadError, UnauthorizedError

resume_api_bp = Blueprint("resume_api", __name__)


@resume_api_bp.route("/", methods=["POST"])
@role_required("CANDIDATE")
def upload_resume():
    file = request.files.get("resume")
    resume_svc = ResumeService(current_app.config["UPLOAD_FOLDER"])
    try:
        result = resume_svc.upload(file, session["user_id"])
        return make_success_response("Resume uploaded.", result, 201)
    except ResumeUploadError as e:
        return make_error_response(str(e), e.error_code, e.status_code)


@resume_api_bp.route("/<resume_id>", methods=["GET"])
@api_login_required
def download_resume(resume_id):
    resume_svc = ResumeService(current_app.config["UPLOAD_FOLDER"])
    try:
        file_path, original_name = resume_svc.get_file_path(
            resume_id, session["user_id"], session.get("role", "")
        )
        return send_file(file_path, as_attachment=True, download_name=original_name)
    except (FileNotFoundError, UnauthorizedError) as e:
        return make_error_response(str(e), "RESUME_NOT_FOUND", 404)


@resume_api_bp.route("/<resume_id>", methods=["DELETE"])
@role_required("CANDIDATE")
def delete_resume(resume_id):
    resume_svc = ResumeService(current_app.config["UPLOAD_FOLDER"])
    try:
        resume_svc.delete(resume_id, session["user_id"])
        return make_success_response("Resume deleted.")
    except (FileNotFoundError, UnauthorizedError) as e:
        return make_error_response(str(e), "ERROR", 400)
