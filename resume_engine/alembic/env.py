"""Alembic migration environment configuration for async SQLAlchemy."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# Import Base and all models to ensure they are registered with SQLAlchemy metadata
from app.db.base import Base
from app.models.user import User  # noqa: F401 — registers User model
from app.models.resume import Resume, ResumeJob  # noqa: F401 — registers Resume models
from app.models.export import ResumeExport  # noqa: F401 — registers Export model
from app.core.config import get_settings

# Alembic Config object providing access to alembic.ini values
config = context.config

# Override sqlalchemy.url from application settings so alembic uses the same URL
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configure logging from alembic.ini if present
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData object for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL without creating an engine.
    Calls to context.execute() emit SQL to the script output directly.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations using an existing synchronous connection.

    Args:
        connection: An active synchronous database connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations asynchronously.

    Uses the async engine from the alembic config but runs migrations
    synchronously via run_sync() to satisfy Alembic's synchronous API.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an async engine.

    Creates an event loop and runs the async migration function.
    This is the standard entry point for Alembic when a live connection
    is required.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
