"""Flask application factory for HireHub.

Environment variables are read from the .env file located at the project root.
MongoDB connection details (MONGO_URI, MONGO_DATABASE) come from that file
via app/config.py → app/extensions.py.
"""
from __future__ import annotations
import os
from datetime import timedelta
from flask import Flask, session
from app.config import get_config
from app.extensions import MongoDB
from app.middleware import register_error_handlers


def create_app(config_class=None) -> Flask:
    """Create and configure the Flask application."""

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ── Load config (reads .env via config.py) ────────────────────────────
    cfg = config_class or get_config()
    app.config.from_object(cfg)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(
        seconds=cfg.PERMANENT_SESSION_LIFETIME
    )

    # Print active config so you can confirm .env was read correctly
    print("\n── HireHub starting ────────────────────────────────────────────")
    cfg.log()
    print("────────────────────────────────────────────────────────────────\n")

    # Ensure upload folder exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ── Connect to MongoDB (uses MONGO_URI + MONGO_DATABASE from .env) ────
    MongoDB.init_app(app)

    # ── Centralised error handlers ────────────────────────────────────────
    register_error_handlers(app)

    # ── Register blueprints ───────────────────────────────────────────────
    from app.routes.web import web_bp
    from app.routes.api import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    # ── Home route ────────────────────────────────────────────────────────
    from flask import render_template
    from app.repositories import JobRepository, CompanyRepository
    from app.utils.helpers import serialize_doc

    @app.route("/")
    def home():
        job_repo     = JobRepository()
        company_repo = CompanyRepository()
        recent_jobs, _ = job_repo.search(status="OPEN", limit=6)
        companies      = company_repo.find_verified()[:6]

        recent_jobs = [serialize_doc(j) for j in recent_jobs]
        companies   = [serialize_doc(c) for c in companies]

        company_map = {str(c["_id"]): c["name"] for c in companies}
        for job in recent_jobs:
            job["company_name"] = company_map.get(job.get("company_id", ""), "")

        return render_template(
            "home.html",
            recent_jobs=recent_jobs,
            companies=companies,
            user=session.get("user_id"),
        )

    # ── Context processor — inject session data into every template ────────
    @app.context_processor
    def inject_user():
        from app.services.notification_service import NotificationService
        user_id     = session.get("user_id")
        unread_count = 0
        if user_id:
            try:
                unread_count = NotificationService().count_unread(user_id)
            except Exception:
                pass
        return {
            "current_user_id":    user_id,
            "current_user_name":  session.get("name", ""),
            "current_user_role":  session.get("role", ""),
            "unread_notifications": unread_count,
        }

    return app
