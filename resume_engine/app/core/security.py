"""Security service for authentication and authorization operations.

Handles password hashing, JWT token creation and validation using
passlib and python-jose respectively.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationException
from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class SecurityService:
    """Service for cryptographic security operations.

    Handles password hashing with bcrypt and JWT token lifecycle
    including creation, signing, and validation.

    Attributes:
        _settings: Application settings instance.
        _pwd_context: Passlib CryptContext configured for bcrypt.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash_password(self, plain_password: str) -> str:
        """Hash a plain text password using bcrypt.

        Args:
            plain_password: The raw password to hash.

        Returns:
            The bcrypt hash of the password.
        """
        return self._pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against its bcrypt hash.

        Args:
            plain_password: The raw password to check.
            hashed_password: The stored bcrypt hash to verify against.

        Returns:
            True if password matches, False otherwise.
        """
        return self._pwd_context.verify(plain_password, hashed_password)

    def create_access_token(
        self,
        subject: str | UUID,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        """Create a signed JWT access token.

        Args:
            subject: The token subject (typically user ID or email).
            extra_claims: Optional additional claims to include in the token.

        Returns:
            A signed JWT access token string.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        payload: dict[str, Any] = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(
            payload,
            self._settings.SECRET_KEY,
            algorithm=self._settings.ALGORITHM,
        )

    def create_refresh_token(self, subject: str | UUID) -> str:
        """Create a signed JWT refresh token with a longer TTL.

        Args:
            subject: The token subject (typically user ID).

        Returns:
            A signed JWT refresh token string.
        """
        expire = datetime.now(timezone.utc) + timedelta(
            days=self._settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        payload: dict[str, Any] = {
            "sub": str(subject),
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh",
        }

        return jwt.encode(
            payload,
            self._settings.SECRET_KEY,
            algorithm=self._settings.ALGORITHM,
        )

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT access token.

        Args:
            token: The JWT token string to decode.

        Returns:
            The decoded token payload as a dictionary.

        Raises:
            AuthenticationException: If the token is invalid, expired, or has
                wrong type.
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.SECRET_KEY,
                algorithms=[self._settings.ALGORITHM],
            )
            if payload.get("type") != "access":
                raise AuthenticationException("Invalid token type")
            return payload
        except JWTError as exc:
            logger.warning("JWT decode failed", error=str(exc))
            raise AuthenticationException("Invalid or expired token") from exc

    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        """Decode and validate a JWT refresh token.

        Args:
            token: The JWT refresh token string to decode.

        Returns:
            The decoded token payload as a dictionary.

        Raises:
            AuthenticationException: If the token is invalid, expired, or has
                wrong type.
        """
        try:
            payload = jwt.decode(
                token,
                self._settings.SECRET_KEY,
                algorithms=[self._settings.ALGORITHM],
            )
            if payload.get("type") != "refresh":
                raise AuthenticationException("Invalid token type")
            return payload
        except JWTError as exc:
            logger.warning("Refresh token decode failed", error=str(exc))
            raise AuthenticationException("Invalid or expired refresh token") from exc
