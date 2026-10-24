"""Route registration for HireHub."""
from .web import web_bp
from .api import api_bp

__all__ = ["web_bp", "api_bp"]
