"""Custom application exceptions for HireHub."""


class HireHubException(Exception):
    """Base exception for all HireHub errors."""
    status_code: int = 400
    error_code: str = "HIREHUB_ERROR"

    def __init__(self, message: str = "An error occurred.") -> None:
        super().__init__(message)
        self.message = message


class UserAlreadyExistsError(HireHubException):
    status_code = 409
    error_code = "USER_ALREADY_EXISTS"

    def __init__(self, message: str = "A user with this email already exists.") -> None:
        super().__init__(message)


class InvalidCredentialsError(HireHubException):
    status_code = 401
    error_code = "INVALID_CREDENTIALS"

    def __init__(self, message: str = "Invalid email or password.") -> None:
        super().__init__(message)


class UserNotFoundError(HireHubException):
    status_code = 404
    error_code = "USER_NOT_FOUND"

    def __init__(self, message: str = "User not found.") -> None:
        super().__init__(message)


class UnauthorizedError(HireHubException):
    status_code = 403
    error_code = "UNAUTHORIZED"

    def __init__(self, message: str = "You are not authorized to perform this action.") -> None:
        super().__init__(message)


class JobNotFoundError(HireHubException):
    status_code = 404
    error_code = "JOB_NOT_FOUND"

    def __init__(self, message: str = "Job not found.") -> None:
        super().__init__(message)


class JobClosedError(HireHubException):
    status_code = 400
    error_code = "JOB_CLOSED"

    def __init__(self, message: str = "This job is no longer accepting applications.") -> None:
        super().__init__(message)


class DuplicateApplicationError(HireHubException):
    status_code = 409
    error_code = "DUPLICATE_APPLICATION"

    def __init__(self, message: str = "You have already applied for this job.") -> None:
        super().__init__(message)


class ApplicationNotFoundError(HireHubException):
    status_code = 404
    error_code = "APPLICATION_NOT_FOUND"

    def __init__(self, message: str = "Application not found.") -> None:
        super().__init__(message)


class InvalidApplicationStatusError(HireHubException):
    status_code = 400
    error_code = "INVALID_APPLICATION_STATUS"

    def __init__(self, message: str = "Invalid application status transition.") -> None:
        super().__init__(message)


class ResumeUploadError(HireHubException):
    status_code = 400
    error_code = "RESUME_UPLOAD_ERROR"

    def __init__(self, message: str = "Failed to upload resume.") -> None:
        super().__init__(message)


class ValidationError(HireHubException):
    status_code = 422
    error_code = "VALIDATION_ERROR"

    def __init__(self, message: str = "Validation failed.") -> None:
        super().__init__(message)


class CompanyNotFoundError(HireHubException):
    status_code = 404
    error_code = "COMPANY_NOT_FOUND"

    def __init__(self, message: str = "Company not found.") -> None:
        super().__init__(message)


class InterviewNotFoundError(HireHubException):
    status_code = 404
    error_code = "INTERVIEW_NOT_FOUND"

    def __init__(self, message: str = "Interview not found.") -> None:
        super().__init__(message)
