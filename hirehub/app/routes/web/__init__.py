"""Web blueprint aggregation."""
from flask import Blueprint

web_bp = Blueprint("web", __name__)

from .auth_routes import auth_bp
from .candidate_routes import candidate_bp
from .recruiter_routes import recruiter_bp
from .admin_routes import admin_bp
from .job_routes import jobs_bp
from .dashboard_routes import dashboard_bp

web_bp.register_blueprint(auth_bp, url_prefix="/auth")
web_bp.register_blueprint(candidate_bp, url_prefix="/candidate")
web_bp.register_blueprint(recruiter_bp, url_prefix="/recruiter")
web_bp.register_blueprint(admin_bp, url_prefix="/admin")
web_bp.register_blueprint(jobs_bp, url_prefix="/jobs")
web_bp.register_blueprint(dashboard_bp, url_prefix="/dashboard")
