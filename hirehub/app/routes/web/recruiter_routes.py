"""Recruiter web routes."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, send_file
from app.utils.decorators import login_required, role_required
from app.services.recruiter_service import RecruiterService
from app.services.company_service import CompanyService
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.services.interview_service import InterviewService
from app.services.notification_service import NotificationService
from app.exceptions import (
    UnauthorizedError, ValidationError, JobNotFoundError,
    ApplicationNotFoundError, InvalidApplicationStatusError,
)

recruiter_bp = Blueprint("recruiter", __name__)


@recruiter_bp.route("/profile")
@role_required("RECRUITER")
def profile():
    user_id = session["user_id"]
    recruiter_svc = RecruiterService()
    company_svc = CompanyService()
    profile_data = recruiter_svc.get_profile(user_id)
    company = company_svc.get_by_recruiter(user_id)
    return render_template("recruiter/profile.html", profile=profile_data, company=company)


@recruiter_bp.route("/profile/edit", methods=["GET", "POST"])
@role_required("RECRUITER")
def edit_profile():
    user_id = session["user_id"]
    recruiter_svc = RecruiterService()
    company_svc = CompanyService()
    if request.method == "POST":
        try:
            data = {
                "name": request.form.get("name", ""),
                "phone": request.form.get("phone", ""),
                "designation": request.form.get("designation", ""),
            }
            recruiter_svc.update_profile(user_id, data, user_id)

            company = company_svc.get_by_recruiter(user_id)
            if company:
                company_data = {
                    "name": request.form.get("company_name", ""),
                    "industry": request.form.get("industry", ""),
                    "website": request.form.get("website", ""),
                    "description": request.form.get("company_description", ""),
                    "location": request.form.get("company_location", ""),
                    "size": request.form.get("company_size", ""),
                }
                company_svc.update_company(company["_id"], company_data, user_id)

            flash("Profile updated successfully.", "success")
            return redirect(url_for("web.recruiter.profile"))
        except (ValidationError, UnauthorizedError) as e:
            flash(str(e), "danger")

    profile_data = recruiter_svc.get_profile(user_id)
    company = company_svc.get_by_recruiter(user_id)
    return render_template("recruiter/edit_profile.html", profile=profile_data, company=company)


@recruiter_bp.route("/jobs")
@role_required("RECRUITER")
def my_jobs():
    user_id = session["user_id"]
    job_svc = JobService()
    page = int(request.args.get("page", 1))
    result = job_svc.get_recruiter_jobs(user_id, page=page)
    return render_template("recruiter/my_jobs.html", jobs=result["items"], pagination=result)


@recruiter_bp.route("/jobs/create", methods=["GET", "POST"])
@role_required("RECRUITER")
def create_job():
    user_id = session["user_id"]
    if request.method == "POST":
        try:
            data = {
                "title": request.form.get("title", ""),
                "description": request.form.get("description", ""),
                "skills": request.form.get("skills", ""),
                "location": request.form.get("location", ""),
                "work_mode": request.form.get("work_mode", "ONSITE"),
                "employment_type": request.form.get("employment_type", "FULL_TIME"),
                "experience_min": request.form.get("experience_min", 0),
                "experience_max": request.form.get("experience_max", 0),
                "salary_min": request.form.get("salary_min") or None,
                "salary_max": request.form.get("salary_max") or None,
                "deadline": request.form.get("deadline") or None,
            }
            job_svc = JobService()
            job_svc.create_job(data, user_id)
            flash("Job posted successfully!", "success")
            return redirect(url_for("web.recruiter.my_jobs"))
        except (ValidationError, UnauthorizedError) as e:
            flash(str(e), "danger")

    return render_template("recruiter/create_job.html")


@recruiter_bp.route("/jobs/<job_id>/edit", methods=["GET", "POST"])
@role_required("RECRUITER")
def edit_job(job_id):
    user_id = session["user_id"]
    job_svc = JobService()
    try:
        job = job_svc.get_job(job_id)
    except JobNotFoundError:
        flash("Job not found.", "danger")
        return redirect(url_for("web.recruiter.my_jobs"))

    if request.method == "POST":
        try:
            data = {k: v for k, v in request.form.items()}
            job_svc.update_job(job_id, data, user_id)
            flash("Job updated.", "success")
            return redirect(url_for("web.recruiter.my_jobs"))
        except (ValidationError, UnauthorizedError) as e:
            flash(str(e), "danger")

    return render_template("recruiter/edit_job.html", job=job)


@recruiter_bp.route("/jobs/<job_id>/close", methods=["POST"])
@role_required("RECRUITER")
def close_job(job_id):
    user_id = session["user_id"]
    try:
        job_svc = JobService()
        job_svc.close_job(job_id, user_id)
        flash("Job closed.", "success")
    except (JobNotFoundError, UnauthorizedError) as e:
        flash(str(e), "danger")
    return redirect(url_for("web.recruiter.my_jobs"))


@recruiter_bp.route("/jobs/<job_id>/applicants")
@role_required("RECRUITER")
def applicants(job_id):
    user_id = session["user_id"]
    job_svc = JobService()
    try:
        job = job_svc.get_job(job_id)
    except JobNotFoundError:
        flash("Job not found.", "danger")
        return redirect(url_for("web.recruiter.my_jobs"))

    if str(job.get("recruiter_id")) != str(user_id):
        flash("Unauthorized.", "danger")
        return redirect(url_for("web.recruiter.my_jobs"))

    page = int(request.args.get("page", 1))
    app_svc = ApplicationService()
    result = app_svc.get_job_applications(job_id, page=page)

    from app.repositories import CandidateRepository
    candidate_repo = CandidateRepository()
    applicants_list = result["items"]
    for application in applicants_list:
        c = candidate_repo.find_by_id(application.get("candidate_id", ""))
        application["candidate_name"]   = c["name"]              if c else "Unknown"
        application["candidate_email"]  = c["email"]             if c else ""
        application["candidate_skills"] = c.get("skills", [])    if c else []

    return render_template(
        "recruiter/applicants.html",
        job=job,
        applicants=applicants_list,
        total=result["total"],
        page=page,
        pages=result.get("pages", 1),
    )


@recruiter_bp.route("/applications/<app_id>/status", methods=["POST"])
@role_required("RECRUITER")
def update_application_status(app_id):
    user_id = session["user_id"]
    new_status = request.form.get("status", "")
    notes = request.form.get("notes", "")
    try:
        app_svc = ApplicationService()
        app_svc.update_status(app_id, new_status, user_id, notes)
        flash(f"Application status updated to {new_status}.", "success")
    except (ApplicationNotFoundError, InvalidApplicationStatusError, UnauthorizedError) as e:
        flash(str(e), "danger")

    # Redirect back to applicants page
    from app.repositories import ApplicationRepository
    app_repo = ApplicationRepository()
    doc = app_repo.find_by_id(app_id)
    if doc:
        return redirect(url_for("web.recruiter.applicants", job_id=doc["job_id"]))
    return redirect(url_for("web.recruiter.my_jobs"))


@recruiter_bp.route("/interviews/schedule", methods=["GET", "POST"])
@role_required("RECRUITER")
def schedule_interview():
    user_id = session["user_id"]
    app_id = request.args.get("application_id") or request.form.get("application_id")
    if request.method == "POST":
        try:
            data = {
                "application_id": request.form.get("application_id"),
                "date": request.form.get("date"),
                "time": request.form.get("time"),
                "interview_type": request.form.get("interview_type", "ONLINE"),
                "meeting_link": request.form.get("meeting_link", ""),
            }
            interview_svc = InterviewService()
            interview_svc.schedule(data, user_id)
            flash("Interview scheduled successfully!", "success")
            return redirect(url_for("web.recruiter.interviews"))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("recruiter/schedule_interview.html", application_id=app_id)


@recruiter_bp.route("/interviews")
@role_required("RECRUITER")
def interviews():
    user_id = session["user_id"]
    interview_svc = InterviewService()
    items = interview_svc.get_recruiter_interviews(user_id)

    from app.repositories import ApplicationRepository, JobRepository, CandidateRepository
    app_repo = ApplicationRepository()
    job_repo = JobRepository()
    candidate_repo = CandidateRepository()
    for iv in items:
        app_doc = app_repo.find_by_id(iv.get("application_id", ""))
        if app_doc:
            job = job_repo.find_by_id(app_doc.get("job_id", ""))
            iv["job_title"] = job["title"] if job else "Unknown"
        else:
            iv["job_title"] = "Unknown"
        candidate = candidate_repo.find_by_id(iv.get("candidate_id", ""))
        iv["candidate_name"] = candidate["name"] if candidate else "Unknown"

    return render_template("recruiter/interviews.html", interviews=items)


@recruiter_bp.route("/notifications")
@role_required("RECRUITER")
def notifications():
    user_id = session["user_id"]
    notification_svc = NotificationService()
    items = notification_svc.get_for_user(user_id, limit=50)
    notification_svc.mark_all_read(user_id)
    return render_template("recruiter/notifications.html", notifications=items)


@recruiter_bp.route("/resume/<resume_id>/download")
@role_required("RECRUITER")
def download_resume(resume_id):
    user_id = session["user_id"]
    from app.services.resume_service import ResumeService
    resume_svc = ResumeService(current_app.config["UPLOAD_FOLDER"])
    try:
        file_path, original_name = resume_svc.get_file_path(resume_id, user_id, "RECRUITER")
        return send_file(file_path, as_attachment=True, download_name=original_name)
    except (FileNotFoundError, UnauthorizedError) as e:
        flash(str(e), "danger")
        return redirect(url_for("web.recruiter.my_jobs"))
