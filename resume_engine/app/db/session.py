"""Async SQLAlchemy session management.

Provides a DatabaseSessionManager class that manages the async engine and
session factory lifecycle. Exposes a FastAPI dependency for obtaining
database sessions in request handlers.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.exceptions import ATSEngineException
from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class DatabaseSessionManager:
    """Manages the async SQLAlchemy engine and session factory.

    Handles engine initialization and teardown, and provides an async
    context manager for obtaining database sessions. Designed to be
    instantiated once at module level and reused across the application.

    Attributes:
        _db_url: The database connection URL.
        _engine: The SQLAlchemy async engine (None until initialized).
        _session_maker: The async session factory (None until initialized).
    """

    def __init__(self, db_url: str) -> None:
        self._db_url = db_url
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    def initialize(self) -> None:
        """Initialize the async engine and session factory.

        Creates the engine with connection pooling configuration appropriate
        for production use. Must be called before any sessions are requested.
        """
        self._engine = create_async_engine(
            self._db_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        logger.info("Database session manager initialized", db_url=self._db_url.split("@")[-1])

    async def close(self) -> None:
        """Dispose the engine and release all connections.

        Should be called during application shutdown to cleanly release
        all database connections back to the pool.
        """
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None
        self._session_maker = None
        logger.info("Database session manager closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager that provides a database session.

        Yields an AsyncSession, committing on success and rolling back
        on any exception. Always closes the session when done.

        Raises:
            ATSEngineException: If the session manager has not been initialized.
        """
        if self._session_maker is None:
            raise ATSEngineException(
                "Database session manager is not initialized. Call initialize() first.",
                error_code="DB_NOT_INITIALIZED",
            )
        session = self._session_maker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncConnection, None]:
        """Async context manager that provides a raw database connection.

        Used by Alembic migrations and other low-level operations.

        Raises:
            ATSEngineException: If the engine has not been initialized.
        """
        if self._engine is None:
            raise ATSEngineException(
                "Database engine is not initialized.",
                error_code="DB_NOT_INITIALIZED",
            )
        async with self._engine.begin() as connection:
            yield connection


# Module-level singleton — initialized once during application startup
sessionmanager = DatabaseSessionManager(get_settings().DATABASE_URL)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    Use this as a dependency in FastAPI route handlers to obtain a
    transactional database session that is automatically committed
    or rolled back based on whether the request succeeds.

    Yields:
        An AsyncSession bound to the current request.
    """
    async with sessionmanager.get_session() as session:
        yield session
