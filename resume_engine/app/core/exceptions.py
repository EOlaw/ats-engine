"""Custom exception hierarchy for the ATS Engine application.

All exceptions inherit from ATSEngineException and carry structured
error information including HTTP status codes and machine-readable error codes.
"""

from http import HTTPStatus


class ATSEngineException(Exception):
    """Base exception for all ATS Engine application errors.

    All application-specific exceptions must inherit from this class.
    Carries structured error information suitable for API error responses.
    """

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR.value,
        error_code: str = "INTERNAL_ERROR",
        details: dict | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r})"
        )


class DocumentParseException(ATSEngineException):
    """Raised when document parsing fails.

    Covers both PDF and DOCX parsing failures, including corrupt files,
    unsupported formats, and extraction errors.
    """

    def __init__(
        self,
        message: str,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
            error_code="DOCUMENT_PARSE_ERROR",
            details=details,
        )


class AIServiceException(ATSEngineException):
    """Base exception for all AI service failures.

    Parent class for specific AI pipeline stage failures.
    """

    def __init__(
        self,
        message: str,
        status_code: int = HTTPStatus.SERVICE_UNAVAILABLE.value,
        error_code: str = "AI_SERVICE_ERROR",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status_code,
            error_code=error_code,
            details=details,
        )


class ExtractionException(AIServiceException):
    """Raised when resume data extraction from AI fails."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
            error_code="EXTRACTION_ERROR",
            details=details,
        )


class ScoringException(AIServiceException):
    """Raised when ATS scoring analysis fails."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE.value,
            error_code="SCORING_ERROR",
            details=details,
        )


class OptimizationException(AIServiceException):
    """Raised when resume optimization fails."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE.value,
            error_code="OPTIMIZATION_ERROR",
            details=details,
        )


class TailoringException(AIServiceException):
    """Raised when job-specific resume tailoring fails."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.SERVICE_UNAVAILABLE.value,
            error_code="TAILORING_ERROR",
            details=details,
        )


class ValidationException(ATSEngineException):
    """Raised when request or data validation fails.

    Used for both API input validation and internal data consistency errors.
    """

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY.value,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class ExportException(ATSEngineException):
    """Raised when document export (PDF/DOCX) fails."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            error_code="EXPORT_ERROR",
            details=details,
        )


class AuthenticationException(ATSEngineException):
    """Raised when authentication fails (invalid credentials, expired token, etc.)."""

    def __init__(self, message: str = "Authentication failed", details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.UNAUTHORIZED.value,
            error_code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationException(ATSEngineException):
    """Raised when an authenticated user lacks permission for a resource or action."""

    def __init__(self, message: str = "Access denied", details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.FORBIDDEN.value,
            error_code="AUTHORIZATION_ERROR",
            details=details,
        )


class ResourceNotFoundException(ATSEngineException):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        resource_type: str,
        resource_id: str | None = None,
        details: dict | None = None,
    ) -> None:
        message = (
            f"{resource_type} not found"
            if resource_id is None
            else f"{resource_type} with id '{resource_id}' not found"
        )
        super().__init__(
            message=message,
            status_code=HTTPStatus.NOT_FOUND.value,
            error_code="RESOURCE_NOT_FOUND",
            details=details or {"resource_type": resource_type, "resource_id": resource_id},
        )


class StorageException(ATSEngineException):
    """Raised when file storage operations fail (read, write, delete)."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(
            message=message,
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR.value,
            error_code="STORAGE_ERROR",
            details=details,
        )
