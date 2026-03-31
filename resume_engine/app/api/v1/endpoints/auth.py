"""Authentication endpoints: register, login, refresh, logout."""

from fastapi import APIRouter, Depends, status

from app.api.v1.dependencies.services import get_user_service
from app.core.config import Settings, get_settings
from app.core.exceptions import AuthenticationException
from app.core.security import SecurityService
from app.schemas.user import RefreshTokenRequest, TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user account.

    Validates the email for uniqueness, hashes the password with bcrypt,
    and persists the new user. Returns the created user profile.

    Args:
        user_create: Registration payload with email, password, and optional name.
        user_service: User management service (injected).

    Returns:
        The newly created user's profile.
    """
    user = await user_service.create_user(user_create)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain JWT tokens",
)
async def login(
    user_login: UserLogin,
    user_service: UserService = Depends(get_user_service),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Authenticate with email and password.

    Returns access and refresh JWT tokens on success.

    Args:
        user_login: Login payload with email and password.
        user_service: User management service (injected).
        settings: Application settings for token TTL (injected).

    Returns:
        TokenResponse containing access_token, refresh_token, and TTL.
    """
    user = await user_service.authenticate_user(user_login.email, user_login.password)
    if user is None:
        raise AuthenticationException("Invalid email or password")

    security = SecurityService(settings)
    access_token = security.create_access_token(subject=str(user.id))
    refresh_token = security.create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange a refresh token for new access and refresh tokens",
)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    """Refresh access tokens using a valid refresh token.

    Decodes the refresh token, verifies the user still exists and is active,
    then issues a new token pair.

    Args:
        refresh_request: Payload containing the refresh token.
        user_service: User management service (injected).
        settings: Application settings (injected).

    Returns:
        New TokenResponse with fresh access and refresh tokens.
    """
    security = SecurityService(settings)
    payload = security.decode_refresh_token(refresh_request.refresh_token)

    import uuid
    user_id = uuid.UUID(payload["sub"])
    user = await user_service.get_user_by_id(user_id)

    if not user.is_active:
        raise AuthenticationException("Account is deactivated")

    new_access = security.create_access_token(subject=str(user.id))
    new_refresh = security.create_refresh_token(subject=str(user.id))

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout (client-side token invalidation)",
)
async def logout() -> None:
    """Logout the current user.

    Since JWT tokens are stateless, logout is handled client-side by
    discarding the tokens. This endpoint returns 204 as a semantic
    confirmation. Server-side token blacklisting can be added via Redis.
    """
    return None
