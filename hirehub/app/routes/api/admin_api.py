"""Admin REST API endpoints."""
from flask import Blueprint, request, session
from app.repositories import UserRepository
from app.utils.helpers import make_success_response, make_error_response, serialize_doc
from app.utils.decorators import role_required

admin_api_bp = Blueprint("admin_api", __name__)


@admin_api_bp.route("/users", methods=["GET"])
@role_required("ADMIN")
def list_users():
    user_repo = UserRepository()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    skip = (page - 1) * per_page
    role_filter = request.args.get("role", "")

    if role_filter:
        docs = user_repo.find_by_role(role_filter, skip=skip, limit=per_page)
        total = user_repo.count({"role": role_filter.upper()})
    else:
        docs = user_repo.find_all(skip=skip, limit=per_page)
        total = user_repo.count({})

    serialised = []
    for d in docs:
        d.pop("password_hash", None)
        serialised.append(serialize_doc(d))

    return make_success_response(data={"items": serialised, "total": total, "page": page})


@admin_api_bp.route("/users/<user_id>/status", methods=["PUT"])
@role_required("ADMIN")
def update_user_status(user_id):
    data = request.get_json(force=True) or {}
    status = data.get("status", "")
    if status not in ("ACTIVE", "INACTIVE", "SUSPENDED"):
        return make_error_response("Invalid status.", "INVALID_STATUS", 400)
    user_repo = UserRepository()
    user_repo.update_status(user_id, status)
    return make_success_response("User status updated.")


@admin_api_bp.route("/audit-logs", methods=["GET"])
@role_required("ADMIN")
def audit_logs():
    user_repo = UserRepository()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 30))
    skip = (page - 1) * per_page
    logs = user_repo.get_audit_logs(skip=skip, limit=per_page)
    total = user_repo.count_audit_logs()
    return make_success_response(data={
        "items": [serialize_doc(l) for l in logs],
        "total": total,
        "page": page,
    })
