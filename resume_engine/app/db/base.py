"""SQLAlchemy declarative base and shared model mixins.

Provides the Base class for all ORM models plus reusable mixins
for UUID primary keys and automatic timestamp management.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """SQLAlchemy declarative base class for all ORM models.

    All model classes must inherit from this base to participate in
    SQLAlchemy's ORM mapping and migration tracking.
    """

    pass


class UUIDMixin:
    """Mixin that provides a UUID primary key column.

    Uses PostgreSQL's native UUID type for efficient storage and indexing.
    The default is auto-generated using uuid4 at the Python level before
    the row is inserted, ensuring the ID is available immediately.
    """

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )


class TimestampMixin:
    """Mixin that provides automatic created_at and updated_at timestamp columns.

    created_at is set once at insert time. updated_at is updated automatically
    on every row modification via SQLAlchemy's onupdate mechanism.
    Both columns are timezone-aware UTC datetimes.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
