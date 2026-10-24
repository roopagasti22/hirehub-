"""Job web routes."""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required
from app.services.job_service import JobService
from app.services.matching_service import MatchingService
from app.services.application_service import ApplicationService
from app.repositories import CandidateRepository, CompanyRepository
from app.exceptions import JobNotFoundError

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/")
def job_list():
    job_svc = JobService()
    page = int(request.args.get("page", 1))
    keyword = request.args.get("q", "")
    location = request.args.get("location", "")
    work_mode = request.args.get("work_mode", "")
    employment_type = request.args.get("employment_type", "")
    skills_raw = request.args.get("skills", "")
    skills = [s.strip() for s in skills_raw.split(",") if s.strip()] if skills_raw else []

    result = job_svc.search_jobs(
        keyword=keyword,
        skills=skills,
        location=location,
        work_mode=work_mode,
        employment_type=employment_type,
        page=page,
        per_page=10,
    )

    # Enrich with company names
    company_repo = CompanyRepository()
    for job in result["items"]:
        if job.get("company_id"):
            company = company_repo.find_by_id(job["company_id"])
            job["company_name"] = company["name"] if company else "Unknown"
        else:
            job["company_name"] = "Unknown"

    return render_template(
        "jobs/list.html",
        jobs=result["items"],
        pagination=result,
        filters={
            "q": keyword, "location": location, "work_mode": work_mode,
            "employment_type": employment_type, "skills": skills_raw,
        },
    )


@jobs_bp.route("/<job_id>")
def job_detail(job_id):
    job_svc = JobService()
    try:
        job = job_svc.get_job(job_id)
    except JobNotFoundError:
        return render_template("errors/404.html"), 404

    # Fetch company
    company_repo = CompanyRepository()
    company = None
    if job.get("company_id"):
        company = company_repo.find_by_id(job["company_id"])
        if company:
            company["_id"] = str(company["_id"])

    # Match score for logged-in candidates
    match_result = None
    already_applied = False
    is_saved = False
    if session.get("role") == "CANDIDATE":
        user_id = session["user_id"]
        candidate_repo = CandidateRepository()
        candidate = candidate_repo.find_by_id(user_id)
        if candidate:
            matching = MatchingService()
            match_result = matching.calculate(candidate, job)

        app_svc = ApplicationService()
        from app.repositories import ApplicationRepository
        app_repo = ApplicationRepository()
        existing_app = app_repo.find_by_candidate_and_job(user_id, job_id)
        already_applied = existing_app is not None

        if candidate:
            is_saved = job_id in (candidate.get("saved_jobs") or [])

    return render_template(
        "jobs/detail.html",
        job=job,
        company=company,
        match_result=match_result,
        already_applied=already_applied,
        is_saved=is_saved,
    )
