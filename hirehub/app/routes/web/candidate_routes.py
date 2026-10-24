"""Candidate web routes."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app, send_file
from app.utils.decorators import login_required, role_required
from app.services.candidate_service import CandidateService
from app.services.resume_service import ResumeService
from app.services.application_service import ApplicationService
from app.services.interview_service import InterviewService
from app.services.notification_service import NotificationService
from app.services.recommendation_service import RecommendationService
from app.exceptions import (
    UserNotFoundError, UnauthorizedError, ResumeUploadError, ValidationError
)

candidate_bp = Blueprint("candidate", __name__)


@candidate_bp.route("/profile")
@role_required("CANDIDATE")
def profile():
    user_id = session["user_id"]
    svc = CandidateService()
    profile_data = svc.get_profile(user_id)

    resume_svc = ResumeService(current_app.config["UPLOAD_FOLDER"])
    resume = resume_svc.get_by_candidate(user_id)

    return render_template("candidate/profile.html", profile=profile_data, resume=resume)


@candidate_bp.route("/profile/edit", methods=["GET", "POST"])
@role_required("CANDIDATE")
def edit_profile():
    user_id = session["user_id"]
    svc = CandidateService()
    if request.method == "POST":
        try:
            data = {
                "name": request.form.get("name", ""),
                "phone": request.form.get("phone", ""),
                "location": request.form.get("location", ""),
                "skills": request.form.get("skills", ""),
                "expected_salary": request.form.get("expected_salary") or None,
                "notice_period": request.form.get("notice_period") or None,
            }
            # Handle education/experience as JSON-like form fields
            svc.update_profile(user_id, data, user_id)
            flash("Profile updated successfully.", "success")
            return redirect(url_for("web.candidate.profile"))
        except (ValidationError, UnauthorizedError) as e:
            flash(str(e), "danger")

    profile_data = svc.get_profile(user_id)
    return render_template("candidate/edit_profile.html", profile=profile_data)


@candidate_bp.route("/resume/upload", methods=["POST"])
@role_required("CANDIDATE")
def upload_resume():
    user_id = session["user_id"]
    resume_svc = ResumeService(current_app.config["UPLOAD_FOLDER"])
    try:
        file = request.files.get("resume")
        resume_svc.upload(file, user_id)
        flash("Resume uploaded successfully.", "success")
    except ResumeUploadError as e:
        flash(str(e), "danger")
    return redirect(url_for("web.candidate.profile"))


@candidate_bp.route("/resume/download/<resume_id>")
@login_required
def download_resume(resume_id):
    user_id = session["user_id"]
    role = session.get("role")
    resume_svc = ResumeService(current_app.config["UPLOAD_FOLDER"])
    try:
        file_path, original_name = resume_svc.get_file_path(resume_id, user_id, role)
        return send_file(file_path, as_attachment=True, download_name=original_name)
    except (FileNotFoundError, UnauthorizedError) as e:
        flash(str(e), "danger")
        return redirect(url_for("web.candidate.profile"))


@candidate_bp.route("/applications")
@role_required("CANDIDATE")
def applications():
    user_id = session["user_id"]
    page = int(request.args.get("page", 1))
    app_svc = ApplicationService()
    result = app_svc.get_candidate_applications(user_id, page=page)

    # Enrich with job titles
    from app.repositories import JobRepository
    job_repo = JobRepository()
    applications_list = result["items"]
    for application in applications_list:
        job = job_repo.find_by_id(application.get("job_id", ""))
        application["job_title"]    = job["title"]            if job else "Unknown"
        application["job_location"] = job.get("location", "") if job else ""

    return render_template(
        "candidate/applications.html",
        applications=applications_list,
        total=result["total"],
        page=result["page"],
        pages=result["pages"],
    )


@candidate_bp.route("/interviews")
@role_required("CANDIDATE")
def interviews():
    user_id = session["user_id"]
    interview_svc = InterviewService()
    interviews_list = interview_svc.get_candidate_interviews(user_id)

    # Enrich with job titles
    from app.repositories import ApplicationRepository, JobRepository
    app_repo = ApplicationRepository()
    job_repo = JobRepository()
    for iv in interviews_list:
        app_doc = app_repo.find_by_id(iv.get("application_id", ""))
        if app_doc:
            job = job_repo.find_by_id(app_doc.get("job_id", ""))
            iv["job_title"] = job["title"] if job else "Unknown"
        else:
            iv["job_title"] = "Unknown"

    return render_template("candidate/interviews.html", interviews=interviews_list)


@candidate_bp.route("/notifications")
@role_required("CANDIDATE")
def notifications():
    user_id = session["user_id"]
    notification_svc = NotificationService()
    items = notification_svc.get_for_user(user_id, limit=50)
    notification_svc.mark_all_read(user_id)
    return render_template("candidate/notifications.html", notifications=items)


@candidate_bp.route("/saved-jobs")
@role_required("CANDIDATE")
def saved_jobs():
    user_id = session["user_id"]
    svc = CandidateService()
    job_ids = svc.get_saved_jobs(user_id)
    from app.repositories import JobRepository
    job_repo = JobRepository()
    jobs = []
    for jid in job_ids:
        job = job_repo.find_by_id(jid)
        if job:
            from app.utils.helpers import serialize_doc
            jobs.append(serialize_doc(job))
    return render_template("candidate/saved_jobs.html", jobs=jobs)


@candidate_bp.route("/recommendations")
@role_required("CANDIDATE")
def recommendations():
    user_id = session["user_id"]
    recommendation_svc = RecommendationService()
    recs = recommendation_svc.get_recommendations(user_id, limit=10)
    return render_template("candidate/recommendations.html", recommendations=recs)
