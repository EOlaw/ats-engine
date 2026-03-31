"""FastAPI exception handlers for all custom application exceptions."""

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AIServiceException,
    ATSEngineException,
    AuthenticationException,
    AuthorizationException,
    DocumentParseException,
    ExportException,
    ExtractionException,
    OptimizationException,
    ResourceNotFoundException,
    ScoringException,
    StorageException,
    TailoringException,
    ValidationException,
)
from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


def _build_error_response(exc: ATSEngineException, request: Request) -> JSONResponse:
    """Build a structured JSON error response from a custom exception.

    Args:
        exc: The caught ATSEngineException.
        request: The current FastAPI Request (for logging context).

    Returns:
        JSONResponse with error_code, message, and optional details.
    """
    logger.warning(
        "Application exception",
        error_code=exc.error_code,
        message=exc.message,
        path=str(request.url),
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
    )


async def ats_engine_exception_handler(
    request: Request, exc: ATSEngineException
) -> JSONResponse:
    """Catch-all handler for the base ATSEngineException."""
    return _build_error_response(exc, request)


async def authentication_exception_handler(
    request: Request, exc: AuthenticationException
) -> JSONResponse:
    """Handler for authentication failures."""
    return _build_error_response(exc, request)


async def authorization_exception_handler(
    request: Request, exc: AuthorizationException
) -> JSONResponse:
    """Handler for authorization/permission failures."""
    return _build_error_response(exc, request)


async def resource_not_found_exception_handler(
    request: Request, exc: ResourceNotFoundException
) -> JSONResponse:
    """Handler for missing resource lookups."""
    return _build_error_response(exc, request)


async def validation_exception_handler(
    request: Request, exc: ValidationException
) -> JSONResponse:
    """Handler for application-level validation errors."""
    return _build_error_response(exc, request)


async def document_parse_exception_handler(
    request: Request, exc: DocumentParseException
) -> JSONResponse:
    """Handler for document parsing failures."""
    return _build_error_response(exc, request)


async def ai_service_exception_handler(
    request: Request, exc: AIServiceException
) -> JSONResponse:
    """Handler for general AI service failures."""
    return _build_error_response(exc, request)


async def extraction_exception_handler(
    request: Request, exc: ExtractionException
) -> JSONResponse:
    """Handler for extraction stage failures."""
    return _build_error_response(exc, request)


async def scoring_exception_handler(
    request: Request, exc: ScoringException
) -> JSONResponse:
    """Handler for scoring stage failures."""
    return _build_error_response(exc, request)


async def optimization_exception_handler(
    request: Request, exc: OptimizationException
) -> JSONResponse:
    """Handler for optimization stage failures."""
    return _build_error_response(exc, request)


async def tailoring_exception_handler(
    request: Request, exc: TailoringException
) -> JSONResponse:
    """Handler for tailoring stage failures."""
    return _build_error_response(exc, request)


async def export_exception_handler(
    request: Request, exc: ExportException
) -> JSONResponse:
    """Handler for export failures."""
    return _build_error_response(exc, request)


async def storage_exception_handler(
    request: Request, exc: StorageException
) -> JSONResponse:
    """Handler for file storage operation failures."""
    return _build_error_response(exc, request)


def register_exception_handlers(app: "FastAPI") -> None:  # type: ignore[name-defined]  # noqa: F821
    """Register all custom exception handlers on the FastAPI application.

    This function is called once during application startup in the app factory.

    Args:
        app: The FastAPI application instance.
    """
    app.add_exception_handler(AuthenticationException, authentication_exception_handler)
    app.add_exception_handler(AuthorizationException, authorization_exception_handler)
    app.add_exception_handler(ResourceNotFoundException, resource_not_found_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(DocumentParseException, document_parse_exception_handler)
    app.add_exception_handler(ExtractionException, extraction_exception_handler)
    app.add_exception_handler(ScoringException, scoring_exception_handler)
    app.add_exception_handler(OptimizationException, optimization_exception_handler)
    app.add_exception_handler(TailoringException, tailoring_exception_handler)
    app.add_exception_handler(AIServiceException, ai_service_exception_handler)
    app.add_exception_handler(ExportException, export_exception_handler)
    app.add_exception_handler(StorageException, storage_exception_handler)
    # Base handler last — catches anything not matched above
    app.add_exception_handler(ATSEngineException, ats_engine_exception_handler)
