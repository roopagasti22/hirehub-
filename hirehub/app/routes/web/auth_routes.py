"""Authentication web routes."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import AuthService
from app.exceptions import (
    UserAlreadyExistsError, InvalidCredentialsError, ValidationError,
)

auth_bp = Blueprint("auth", __name__)
_auth_service = AuthService()


@auth_bp.route("/register", methods=["GET"])
def register():
    if "user_id" in session:
        return redirect(url_for("web.dashboard.index"))
    return render_template("auth/register.html")


@auth_bp.route("/register/candidate", methods=["POST"])
def register_candidate():
    try:
        data = {
            "name": request.form.get("name", ""),
            "email": request.form.get("email", ""),
            "phone": request.form.get("phone", ""),
            "password": request.form.get("password", ""),
            "confirm_password": request.form.get("confirm_password", ""),
        }
        _auth_service.register_candidate(data)
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("web.auth.login"))
    except (UserAlreadyExistsError, ValidationError) as e:
        flash(str(e), "danger")
        return render_template("auth/register.html", role="candidate", form_data=request.form)


@auth_bp.route("/register/recruiter", methods=["POST"])
def register_recruiter():
    try:
        data = {
            "name": request.form.get("name", ""),
            "email": request.form.get("email", ""),
            "phone": request.form.get("phone", ""),
            "password": request.form.get("password", ""),
            "confirm_password": request.form.get("confirm_password", ""),
            "company_name": request.form.get("company_name", ""),
        }
        _auth_service.register_recruiter(data)
        flash("Recruiter account created successfully! Please log in.", "success")
        return redirect(url_for("web.auth.login"))
    except (UserAlreadyExistsError, ValidationError) as e:
        flash(str(e), "danger")
        return render_template("auth/register.html", role="recruiter", form_data=request.form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("web.dashboard.index"))
    if request.method == "POST":
        try:
            email = request.form.get("email", "")
            password = request.form.get("password", "")
            _auth_service.login(email, password)
            flash("Welcome back!", "success")
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            return redirect(url_for("web.dashboard.index"))
        except InvalidCredentialsError as e:
            flash(str(e), "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    _auth_service.logout()
    flash("You have been logged out.", "info")
    return redirect(url_for("web.auth.login"))
