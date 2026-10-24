"""Server-side input validators."""
import re
from bson import ObjectId
from bson.errors import InvalidId


def validate_email(email: str) -> bool:
    """Return True if email matches a basic RFC-5322 pattern."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """Return True for 7–15 digit phone numbers (digits only, optional leading +)."""
    pattern = r"^\+?[0-9]{7,15}$"
    return bool(re.match(pattern, phone.strip()))


def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, error_message).
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    return True, ""


def validate_objectid(value: str) -> bool:
    """Return True if value is a valid MongoDB ObjectId string."""
    try:
        ObjectId(value)
        return True
    except (InvalidId, TypeError):
        return False


def validate_salary(salary_min, salary_max) -> tuple[bool, str]:
    """Validate salary range."""
    try:
        mn = int(salary_min)
        mx = int(salary_max)
    except (TypeError, ValueError):
        return False, "Salary values must be integers."
    if mn < 0 or mx < 0:
        return False, "Salary values must be non-negative."
    if mn > mx:
        return False, "Minimum salary cannot exceed maximum salary."
    return True, ""


def validate_experience(exp_min, exp_max) -> tuple[bool, str]:
    """Validate experience range."""
    try:
        mn = int(exp_min)
        mx = int(exp_max)
    except (TypeError, ValueError):
        return False, "Experience values must be integers."
    if mn < 0 or mx < 0:
        return False, "Experience values must be non-negative."
    if mn > mx:
        return False, "Minimum experience cannot exceed maximum experience."
    return True, ""


def validate_skills(skills) -> tuple[bool, str]:
    """Validate a list of skill strings."""
    if not isinstance(skills, list):
        return False, "Skills must be a list."
    if not all(isinstance(s, str) and s.strip() for s in skills):
        return False, "Each skill must be a non-empty string."
    return True, ""
