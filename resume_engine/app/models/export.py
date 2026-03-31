"""ResumeExport ORM model definition."""

import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.resume import Resume, ResumeJob


class ExportFormat(str, enum.Enum):
    """Supported export file formats."""

    PDF = "pdf"
    DOCX = "docx"


class ResumeExport(Base, UUIDMixin, TimestampMixin):
    """ORM model representing a generated resume export artifact.

    Tracks each exported file with its template, format, and file path.
    Optionally linked to a specific job tailoring request.
    """

    __tablename__ = "resume_exports"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    template_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    format: Mapped[ExportFormat] = mapped_column(
        Enum(ExportFormat, name="export_format_enum"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    job_id: Mapped[uuid.UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("resume_jobs.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="exports")
    job: Mapped["ResumeJob | None"] = relationship("ResumeJob", back_populates="exports")

    def __repr__(self) -> str:
        return (
            f"<ResumeExport id={self.id} "
            f"resume_id={self.resume_id} "
            f"template={self.template_name!r} "
            f"format={self.format}>"
        )
