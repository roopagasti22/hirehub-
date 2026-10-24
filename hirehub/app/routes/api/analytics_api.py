"""Analytics REST API endpoints."""
from flask import Blueprint, session
from app.services.analytics_service import AnalyticsService
from app.utils.helpers import make_success_response
from app.utils.decorators import role_required

analytics_api_bp = Blueprint("analytics_api", __name__)
_svc = AnalyticsService()


@analytics_api_bp.route("/candidate", methods=["GET"])
@role_required("CANDIDATE")
def candidate_analytics():
    data = _svc.get_candidate_analytics(session["user_id"])
    return make_success_response(data=data)


@analytics_api_bp.route("/recruiter", methods=["GET"])
@role_required("RECRUITER")
def recruiter_analytics():
    data = _svc.get_recruiter_analytics(session["user_id"])
    return make_success_response(data=data)


@analytics_api_bp.route("/admin", methods=["GET"])
@role_required("ADMIN")
def admin_analytics():
    data = _svc.get_admin_analytics()
    return make_success_response(data=data)
