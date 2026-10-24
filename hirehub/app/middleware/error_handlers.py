"""Centralised error handlers — returns HTML for web, JSON for API."""
from flask import Flask, request, render_template, jsonify
from app.exceptions import HireHubException


def _is_api(req) -> bool:
    return req.path.startswith("/api/")


def register_error_handlers(app: Flask) -> None:
    """Register all error handlers on the Flask app."""

    @app.errorhandler(HireHubException)
    def handle_hirehub_error(error: HireHubException):
        if _is_api(request):
            return jsonify({
                "success": False,
                "message": error.message,
                "error_code": error.error_code,
            }), error.status_code
        return render_template("errors/generic.html", error=error), error.status_code

    @app.errorhandler(404)
    def not_found(error):
        if _is_api(request):
            return jsonify({"success": False, "message": "Not found.", "error_code": "NOT_FOUND"}), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(error):
        if _is_api(request):
            return jsonify({"success": False, "message": "Forbidden.", "error_code": "FORBIDDEN"}), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(error):
        if _is_api(request):
            return jsonify({"success": False, "message": "Internal server error.", "error_code": "SERVER_ERROR"}), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(413)
    def request_too_large(error):
        if _is_api(request):
            return jsonify({"success": False, "message": "File too large.", "error_code": "FILE_TOO_LARGE"}), 413
        return render_template("errors/generic.html", error=type("E", (), {"message": "File too large (max 5 MB).", "status_code": 413})()), 413
