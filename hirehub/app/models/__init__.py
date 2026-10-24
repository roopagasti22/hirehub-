"""Domain model classes for HireHub."""
from .user import User
from .candidate import Candidate
from .recruiter import Recruiter
from .admin import Admin
from .company import Company
from .job import Job
from .application import Application
from .interview import Interview
from .resume import Resume
from .notification import Notification

__all__ = [
    "User", "Candidate", "Recruiter", "Admin",
    "Company", "Job", "Application", "Interview",
    "Resume", "Notification",
]
