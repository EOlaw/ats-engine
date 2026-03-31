"""Application configuration module using pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file.

    Uses pydantic-settings for automatic env var parsing and validation.
    All fields are typed and have sensible defaults where appropriate.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/ats_engine",
        description="Async PostgreSQL connection string",
    )

    # Security
    SECRET_KEY: str = Field(
        default="change-me-in-production-must-be-at-least-32-characters-long",
        description="JWT signing secret key",
        min_length=32,
    )
    ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, description="Access token TTL in minutes", ge=1
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token TTL in days", ge=1
    )

    # Anthropic
    ANTHROPIC_API_KEY: str = Field(
        default="", description="Anthropic API key for Claude"
    )
    CLAUDE_MODEL: str = Field(
        default="claude-sonnet-4-6", description="Claude model identifier"
    )

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = Field(
        default=10, description="Maximum upload file size in megabytes", ge=1, le=100
    )

    # CORS
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        description="Comma-separated list of allowed CORS origins",
    )

    # Application
    ENVIRONMENT: Literal["development", "staging", "production"] = Field(
        default="development", description="Deployment environment"
    )
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", description="Redis connection URL"
    )

    # Upload directory
    UPLOAD_DIR: str = Field(
        default="/tmp/ats_engine/uploads", description="Directory for uploaded files"
    )
    EXPORT_DIR: str = Field(
        default="/tmp/ats_engine/exports", description="Directory for exported files"
    )

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def parse_allowed_origins(cls, v: str) -> str:
        """Ensure ALLOWED_ORIGINS is a valid comma-separated string."""
        origins = [o.strip() for o in v.split(",") if o.strip()]
        if not origins:
            raise ValueError("ALLOWED_ORIGINS must contain at least one origin")
        return v

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return ALLOWED_ORIGINS as a list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def max_upload_size_bytes(self) -> int:
        """Return max upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton Settings instance.

    Uses lru_cache to ensure a single Settings object is created
    and reused across the application lifetime.
    """
    return Settings()
