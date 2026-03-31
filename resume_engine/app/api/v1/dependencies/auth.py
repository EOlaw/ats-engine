"""FastAPI authentication dependencies."""

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import AuthenticationException
from app.core.logging import LoggerFactory
from app.core.security import SecurityService
from app.db.session import AsyncSession, get_db
from app.models.user import User
from app.services.user_service import UserService

logger = LoggerFactory.get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency that decodes a JWT and returns the current user.

    Extracts the Bearer token from the Authorization header, decodes it,
    and loads the corresponding User from the database.

    Args:
        credentials: HTTP Bearer credentials from the Authorization header.
        db: Async database session.

    Returns:
        The authenticated User ORM model.

    Raises:
        AuthenticationException: If no token is provided, the token is invalid,
            or the user no longer exists in the database.
    """
    if credentials is None:
        raise AuthenticationException("Authorization header is required")

    security = SecurityService()
    payload = security.decode_access_token(credentials.credentials)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException("Token subject is missing")

    user_service = UserService(db)
    try:
        import uuid
        user_id = uuid.UUID(user_id_str)
        user = await user_service.get_user_by_id(user_id)
    except (ValueError, TypeError) as exc:
        raise AuthenticationException("Invalid user ID in token") from exc
    except Exception as exc:
        raise AuthenticationException(f"User not found: {exc}") from exc

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """FastAPI dependency that ensures the current user is active.

    Wraps get_current_user with an additional is_active check.

    Args:
        current_user: The authenticated user from get_current_user.

    Returns:
        The active User ORM model.

    Raises:
        AuthenticationException: If the user account is deactivated.
    """
    if not current_user.is_active:
        raise AuthenticationException("This account has been deactivated")
    return current_user
