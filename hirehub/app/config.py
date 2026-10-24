"""Application configuration — reads all values from the .env file."""
import os
from pathlib import Path
from dotenv import load_dotenv

# ── Always load .env from the project root, no matter where Python is run ──
BASE_DIR = Path(__file__).resolve().parent.parent   # hirehub/
ENV_FILE = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_FILE, override=True)


class Config:
    """Base configuration — every value comes from .env."""

    # Flask
    SECRET_KEY: str        = os.getenv("SECRET_KEY", "change-this-in-production")
    FLASK_ENV: str         = os.getenv("FLASK_ENV", "development")

    # ── MongoDB (read from .env) ──────────────────────────────────────────
    MONGO_URI: str         = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DATABASE: str    = os.getenv("MONGO_DATABASE", "hirehub")

    # File uploads
    UPLOAD_FOLDER: str     = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "app" / "uploads" / "resumes"))
    MAX_CONTENT_LENGTH: int = int(os.getenv("MAX_CONTENT_LENGTH", 5242880))   # 5 MB default
    ALLOWED_EXTENSIONS: set = {"pdf", "doc", "docx"}

    # Session / cookie
    SESSION_COOKIE_HTTPONLY: bool = os.getenv("SESSION_COOKIE_HTTPONLY", "True") == "True"
    SESSION_COOKIE_SAMESITE: str  = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE: bool   = os.getenv("SESSION_COOKIE_SECURE", "False") == "True"
    PERMANENT_SESSION_LIFETIME: int = 86400   # 24 h

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10

    @classmethod
    def log(cls) -> None:
        """Print active MongoDB config (safe — no secrets)."""
        print(f"  [Config] MONGO_URI      = {cls.MONGO_URI}")
        print(f"  [Config] MONGO_DATABASE = {cls.MONGO_DATABASE}")
        print(f"  [Config] FLASK_ENV      = {cls.FLASK_ENV}")
        print(f"  [Config] UPLOAD_FOLDER  = {cls.UPLOAD_FOLDER}")


class DevelopmentConfig(Config):
    """Development — debug on, cookies not marked Secure."""
    DEBUG: bool = True
    SESSION_COOKIE_SECURE: bool = False


class ProductionConfig(Config):
    """Production — debug off, cookies Secure."""
    DEBUG: bool = False
    SESSION_COOKIE_SECURE: bool = True


class TestingConfig(Config):
    """Testing — separate database, no CSRF."""
    TESTING: bool = True
    MONGO_DATABASE: str = os.getenv("TEST_MONGO_DATABASE", "hirehub_test")
    SESSION_COOKIE_SECURE: bool = False


_config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}


def get_config():
    """Return the correct config class based on FLASK_ENV in .env."""
    env = os.getenv("FLASK_ENV", "development").lower()
    return _config_map.get(env, DevelopmentConfig)
