"""Pydantic v2 schemas for user authentication and profile data."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.user import SubscriptionTier


class UserCreate(BaseModel):
    """Schema for user registration requests."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(description="User email address")
    password: str = Field(
        description="User password",
        min_length=8,
        max_length=128,
    )
    full_name: str | None = Field(
        default=None,
        description="User's full name",
        max_length=255,
    )

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Validate that the password meets minimum strength requirements."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login requests."""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr = Field(description="User email address")
    password: str = Field(description="User password")


class UserResponse(BaseModel):
    """Schema for user data in API responses.

    Excludes sensitive fields like hashed_password.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    is_active: bool
    is_verified: bool
    subscription_tier: SubscriptionTier
    created_at: datetime
    updated_at: datetime


class TokenResponse(BaseModel):
    """Schema for authentication token responses."""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token TTL in seconds")


class TokenData(BaseModel):
    """Schema for data encoded inside a JWT token."""

    sub: str = Field(description="Token subject (user ID)")
    type: str = Field(description="Token type: access or refresh")
    exp: int | None = Field(default=None, description="Expiration timestamp")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh requests."""

    refresh_token: str = Field(description="A valid JWT refresh token")
