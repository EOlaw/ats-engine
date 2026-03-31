"""User management service for registration, authentication, and lookup."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException, ResourceNotFoundException, ValidationException
from app.core.logging import LoggerFactory
from app.core.security import SecurityService
from app.models.user import User
from app.schemas.user import UserCreate

logger = LoggerFactory.get_logger(__name__)


class UserService:
    """Service handling user lifecycle operations.

    Provides user creation with password hashing, credential-based
    authentication, and user lookup by ID or email.

    Attributes:
        _db: Async SQLAlchemy session.
        _security: Security service for password hashing and verification.
    """

    def __init__(self, db: AsyncSession, security: SecurityService | None = None) -> None:
        self._db = db
        self._security = security or SecurityService()

    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user account.

        Checks for duplicate email before creating, then hashes the password
        and persists the new User record.

        Args:
            user_create: Validated user registration data.

        Returns:
            The newly created User ORM model.

        Raises:
            ValidationException: If a user with the given email already exists.
        """
        existing = await self.get_user_by_email(user_create.email)
        if existing is not None:
            raise ValidationException(
                f"A user with email '{user_create.email}' already exists.",
                details={"field": "email"},
            )

        hashed_password = self._security.hash_password(user_create.password)
        user = User(
            email=user_create.email.lower().strip(),
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=True,
            is_verified=False,
        )
        self._db.add(user)
        await self._db.flush()
        logger.info("User created", user_id=str(user.id), email=user.email)
        return user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password.

        Returns the User if credentials are valid, or None if no user is found.
        Raises AuthenticationException if the password does not match.

        Args:
            email: The user's email address.
            password: The plain text password to verify.

        Returns:
            The authenticated User model, or None if email not found.

        Raises:
            AuthenticationException: If the password is incorrect.
        """
        user = await self.get_user_by_email(email)
        if user is None:
            # Use consistent timing to prevent user enumeration
            self._security.hash_password("dummy_timing_prevention")
            return None

        if not self._security.verify_password(password, user.hashed_password):
            logger.warning("Failed login attempt", email=email)
            raise AuthenticationException("Invalid email or password")

        if not user.is_active:
            raise AuthenticationException("This account has been deactivated")

        logger.info("User authenticated", user_id=str(user.id))
        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> User:
        """Retrieve a user by their UUID primary key.

        Args:
            user_id: The UUID of the user to retrieve.

        Returns:
            The User ORM model.

        Raises:
            ResourceNotFoundException: If no user with the given ID exists.
        """
        result = await self._db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise ResourceNotFoundException("User", str(user_id))
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by their email address.

        Args:
            email: The email address to look up (case-insensitive).

        Returns:
            The User ORM model if found, or None.
        """
        result = await self._db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def update_user_active_status(
        self, user_id: uuid.UUID, is_active: bool
    ) -> User:
        """Activate or deactivate a user account.

        Args:
            user_id: UUID of the user to update.
            is_active: New active status.

        Returns:
            The updated User ORM model.

        Raises:
            ResourceNotFoundException: If the user does not exist.
        """
        user = await self.get_user_by_id(user_id)
        user.is_active = is_active
        await self._db.flush()
        logger.info("User active status updated", user_id=str(user_id), is_active=is_active)
        return user
