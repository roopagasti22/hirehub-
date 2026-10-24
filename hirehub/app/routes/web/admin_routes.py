"""Admin web routes."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import role_required
from app.services.analytics_service import AnalyticsService
from app.services.report_service import ReportService
from app.services.company_service import CompanyService
from app.services.job_service import JobService
from app.repositories import UserRepository, CandidateRepository, RecruiterRepository
from flask import make_response

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/users")
@role_required("ADMIN")
def users():
    user_repo = UserRepository()
    page = int(request.args.get("page", 1))
    per_page = 20
    skip = (page - 1) * per_page
    role_filter = request.args.get("role", "")

    if role_filter:
        docs = user_repo.find_by_role(role_filter, skip=skip, limit=per_page)
        total = user_repo.count({"role": role_filter.upper()})
    else:
        docs = user_repo.find_all(skip=skip, limit=per_page)
        total = user_repo.count({})

    for d in docs:
        d["_id"] = str(d["_id"])
        d.pop("password_hash", None)

    pages = max(1, (total + per_page - 1) // per_page)
    return render_template(
        "admin/users.html",
        users=docs,
        total=total,
        page=page,
        pages=pages,
        role_filter=role_filter,
    )


@admin_bp.route("/users/<user_id>/toggle", methods=["POST"])
@role_required("ADMIN")
def toggle_user(user_id):
    user_repo = UserRepository()
    user = user_repo.find_by_id(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("web.admin.users"))
    new_status = "INACTIVE" if user.get("status") == "ACTIVE" else "ACTIVE"
    user_repo.update_status(user_id, new_status)
    action = "USER_DEACTIVATED" if new_status == "INACTIVE" else "USER_ACTIVATED"
    user_repo.log_audit({
        "user_id": session["user_id"],
        "action": action,
        "resource": "user",
        "resource_id": user_id,
        "timestamp": __import__("datetime").datetime.utcnow(),
        "metadata": {},
    })
    flash(f"User status updated to {new_status}.", "success")
    return redirect(url_for("web.admin.users"))


@admin_bp.route("/companies")
@role_required("ADMIN")
def companies():
    company_svc = CompanyService()
    page = int(request.args.get("page", 1))
    result = company_svc.get_all(page=page)
    return render_template("admin/companies.html", companies=result["items"], pagination=result)


@admin_bp.route("/companies/<company_id>/verify", methods=["POST"])
@role_required("ADMIN")
def verify_company(company_id):
    company_svc = CompanyService()
    company_svc.verify_company(company_id)
    flash("Company verified.", "success")
    return redirect(url_for("web.admin.companies"))


@admin_bp.route("/companies/<company_id>/reject", methods=["POST"])
@role_required("ADMIN")
def reject_company(company_id):
    company_svc = CompanyService()
    company_svc.reject_company(company_id)
    flash("Company verification rejected.", "warning")
    return redirect(url_for("web.admin.companies"))


@admin_bp.route("/jobs")
@role_required("ADMIN")
def jobs():
    job_svc = JobService()
    page = int(request.args.get("page", 1))
    status_filter = request.args.get("status", "")
    result = job_svc.get_all_jobs(page=page, per_page=20, status=status_filter or None)
    return render_template("admin/jobs.html", jobs=result["items"], pagination=result, status_filter=status_filter)


@admin_bp.route("/analytics")
@role_required("ADMIN")
def analytics():
    analytics_svc = AnalyticsService()
    data = analytics_svc.get_admin_analytics()
    return render_template("admin/analytics.html", analytics=data)


@admin_bp.route("/reports")
@role_required("ADMIN")
def reports():
    return render_template("admin/reports.html")


@admin_bp.route("/reports/candidates")
@role_required("ADMIN")
def report_candidates():
    report_svc = ReportService()
    filters = {
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
    }
    data = report_svc.candidate_report(filters)
    if request.args.get("format") == "csv":
        csv_content = report_svc.to_csv(data)
        response = make_response(csv_content)
        response.headers["Content-Disposition"] = "attachment; filename=candidates.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    return render_template("admin/report_view.html", title="Candidate Report", data=data, report_type="candidates")


@admin_bp.route("/reports/jobs")
@role_required("ADMIN")
def report_jobs():
    report_svc = ReportService()
    filters = {
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "status": request.args.get("status", ""),
        "location": request.args.get("location", ""),
    }
    data = report_svc.job_report(filters)
    if request.args.get("format") == "csv":
        csv_content = report_svc.to_csv(data)
        response = make_response(csv_content)
        response.headers["Content-Disposition"] = "attachment; filename=jobs.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    return render_template("admin/report_view.html", title="Job Report", data=data, report_type="jobs")


@admin_bp.route("/reports/applications")
@role_required("ADMIN")
def report_applications():
    report_svc = ReportService()
    filters = {
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "status": request.args.get("status", ""),
    }
    data = report_svc.application_report(filters)
    if request.args.get("format") == "csv":
        csv_content = report_svc.to_csv(data)
        response = make_response(csv_content)
        response.headers["Content-Disposition"] = "attachment; filename=applications.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    return render_template("admin/report_view.html", title="Application Report", data=data, report_type="applications")


@admin_bp.route("/audit-logs")
@role_required("ADMIN")
def audit_logs():
    user_repo = UserRepository()
    page = int(request.args.get("page", 1))
    per_page = 30
    skip = (page - 1) * per_page
    logs = user_repo.get_audit_logs(skip=skip, limit=per_page)
    total = user_repo.count_audit_logs()
    pages = max(1, (total + per_page - 1) // per_page)
    from app.utils.helpers import serialize_doc
    logs = [serialize_doc(log) for log in logs]
    return render_template(
        "admin/audit_logs.html",
        logs=logs,
        page=page,
        pages=pages,
        total=total,
    )
