"""Dashboard web routes."""
from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.decorators import login_required
from app.services.analytics_service import AnalyticsService
from app.services.notification_service import NotificationService
from app.services.recommendation_service import RecommendationService
from app.services.application_service import ApplicationService
from app.services.job_service import JobService
from app.services.interview_service import InterviewService
from app.repositories import CandidateRepository, RecruiterRepository

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    role = session.get("role")
    if role == "CANDIDATE":
        return redirect(url_for("web.dashboard.candidate_dashboard"))
    elif role == "RECRUITER":
        return redirect(url_for("web.dashboard.recruiter_dashboard"))
    elif role == "ADMIN":
        return redirect(url_for("web.dashboard.admin_dashboard"))
    return redirect(url_for("web.auth.login"))


@dashboard_bp.route("/candidate")
@login_required
def candidate_dashboard():
    user_id = session["user_id"]
    if session.get("role") != "CANDIDATE":
        return redirect(url_for("web.dashboard.index"))

    analytics_svc = AnalyticsService()
    notification_svc = NotificationService()
    recommendation_svc = RecommendationService()
    app_svc = ApplicationService()
    interview_svc = InterviewService()

    stats = analytics_svc.get_candidate_analytics(user_id)
    notifications = notification_svc.get_for_user(user_id, limit=5)
    unread_count = notification_svc.count_unread(user_id)
    recommendations = recommendation_svc.get_recommendations(user_id, limit=5)
    recent_apps = app_svc.get_candidate_applications(user_id, per_page=5)
    interviews = interview_svc.get_candidate_interviews(user_id)

    # Profile completion
    candidate_repo = CandidateRepository()
    profile = candidate_repo.find_by_id(user_id)
    profile_complete = 0
    if profile:
        fields = [profile.get("phone"), profile.get("location"), profile.get("skills"),
                  profile.get("education"), profile.get("experience"), profile.get("resume_id")]
        filled = sum(1 for f in fields if f)
        profile_complete = int((filled / len(fields)) * 100)

    return render_template(
        "dashboard/candidate.html",
        stats=stats,
        notifications=notifications,
        unread_count=unread_count,
        recommendations=recommendations,
        recent_apps=recent_apps["items"],
        interviews=interviews[:3],
        profile_complete=profile_complete,
    )


@dashboard_bp.route("/recruiter")
@login_required
def recruiter_dashboard():
    user_id = session["user_id"]
    if session.get("role") != "RECRUITER":
        return redirect(url_for("web.dashboard.index"))

    analytics_svc = AnalyticsService()
    notification_svc = NotificationService()
    job_svc = JobService()
    app_svc = ApplicationService()
    interview_svc = InterviewService()

    stats = analytics_svc.get_recruiter_analytics(user_id)
    notifications = notification_svc.get_for_user(user_id, limit=5)
    unread_count = notification_svc.count_unread(user_id)
    jobs = job_svc.get_recruiter_jobs(user_id, per_page=5)

    # Gather recent applications across recruiter's jobs
    from app.repositories import JobRepository, ApplicationRepository
    job_repo = JobRepository()
    app_repo = ApplicationRepository()
    job_ids = [j["_id"] for j in jobs["items"]]
    recent_apps = app_repo.find_for_recruiter_jobs(job_ids, limit=5)
    from app.utils.helpers import serialize_doc
    recent_apps = [serialize_doc(a) for a in recent_apps]

    interviews = interview_svc.get_recruiter_interviews(user_id)

    return render_template(
        "dashboard/recruiter.html",
        stats=stats,
        notifications=notifications,
        unread_count=unread_count,
        jobs=jobs["items"],
        recent_apps=recent_apps,
        interviews=interviews[:3],
    )


@dashboard_bp.route("/admin")
@login_required
def admin_dashboard():
    if session.get("role") != "ADMIN":
        return redirect(url_for("web.dashboard.index"))

    analytics_svc = AnalyticsService()
    notification_svc = NotificationService()

    stats = analytics_svc.get_admin_analytics()
    unread_count = notification_svc.count_unread(session["user_id"])

    return render_template(
        "dashboard/admin.html",
        stats=stats,
        unread_count=unread_count,
    )
