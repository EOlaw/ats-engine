"""Application factory and entry point for the ATS Engine FastAPI application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.exception_handlers import register_exception_handlers
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.logging import LoggerFactory
from app.db.session import sessionmanager

logger = LoggerFactory.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """FastAPI lifespan context manager for startup and shutdown logic.

    Handles database session manager initialization on startup and
    graceful cleanup on shutdown.

    Args:
        app: The FastAPI application instance.
    """
    settings = get_settings()
    logger.info(
        "Starting ATS Engine",
        environment=settings.ENVIRONMENT,
        version="1.0.0",
    )

    # Initialize database connection pool
    sessionmanager.initialize()
    logger.info("Database connection pool initialized")

    yield  # Application is running

    # Shutdown: release database connections
    await sessionmanager.close()
    logger.info("ATS Engine shutdown complete")


def create_application() -> FastAPI:
    """Application factory that creates and configures the FastAPI instance.

    Registers all routers, middleware, exception handlers, and the lifespan
    context manager. Returns a fully configured application ready to serve.

    Returns:
        A configured FastAPI application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="ATS Engine API",
        description=(
            "AI-powered resume parsing, ATS scoring, optimization, and export service. "
            "Uses Claude claude-sonnet-4-6 for intelligent resume analysis and tailoring."
        ),
        version="1.0.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # CORS middleware — must be added before routers
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
    )

    # Trusted host middleware (restrict to known hosts in production)
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*"],  # Replace with actual domains in production
        )

    # Register custom exception handlers
    register_exception_handlers(app)

    # Include versioned API router
    app.include_router(api_router)

    # Health check endpoint (outside versioned prefix)
    @app.get("/health", tags=["Health"], include_in_schema=False)
    async def health_check() -> dict:
        """Health check endpoint for load balancer and monitoring probes."""
        return {"status": "healthy", "version": "1.0.0", "environment": settings.ENVIRONMENT}

    @app.get("/", tags=["Root"], include_in_schema=False)
    async def root() -> dict:
        """Root endpoint returning basic API information."""
        return {
            "name": "ATS Engine API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }

    logger.info("ATS Engine application created", environment=settings.ENVIRONMENT)
    return app


# Module-level application instance for Uvicorn
app = create_application()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
        workers=1 if settings.is_development else 4,
    )
