"""API blueprint aggregation."""
from flask import Blueprint

api_bp = Blueprint("api", __name__)

from .auth_api import auth_api_bp
from .job_api import job_api_bp
from .candidate_api import candidate_api_bp
from .application_api import application_api_bp
from .interview_api import interview_api_bp
from .resume_api import resume_api_bp
from .analytics_api import analytics_api_bp
from .admin_api import admin_api_bp
from .recruiter_api import recruiter_api_bp

api_bp.register_blueprint(auth_api_bp, url_prefix="/auth")
api_bp.register_blueprint(job_api_bp, url_prefix="/jobs")
api_bp.register_blueprint(candidate_api_bp, url_prefix="/candidates")
api_bp.register_blueprint(application_api_bp, url_prefix="/applications")
api_bp.register_blueprint(interview_api_bp, url_prefix="/interviews")
api_bp.register_blueprint(resume_api_bp, url_prefix="/resumes")
api_bp.register_blueprint(analytics_api_bp, url_prefix="/analytics")
api_bp.register_blueprint(admin_api_bp, url_prefix="/admin")
api_bp.register_blueprint(recruiter_api_bp, url_prefix="/recruiters")
