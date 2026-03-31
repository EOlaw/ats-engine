"""Resume and ResumeJob ORM model definitions."""

import enum
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.export import ResumeExport
    from app.models.user import User


class ResumeStatus(str, enum.Enum):
    """Processing status for a resume through the AI pipeline."""

    PENDING = "pending"
    PARSING = "parsing"
    PARSED = "parsed"
    SCORING = "scoring"
    SCORED = "scored"
    OPTIMIZING = "optimizing"
    OPTIMIZED = "optimized"
    ERROR = "error"


class FileType(str, enum.Enum):
    """Supported resume file types."""

    PDF = "pdf"
    DOCX = "docx"


class Resume(Base, UUIDMixin, TimestampMixin):
    """ORM model representing an uploaded resume.

    Stores the original file reference, raw extracted text, and all
    AI-generated analysis data as JSONB columns for flexible schema evolution.
    """

    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )
    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType, name="file_type_enum"),
        nullable=False,
    )
    status: Mapped[ResumeStatus] = mapped_column(
        Enum(ResumeStatus, name="resume_status_enum"),
        default=ResumeStatus.PENDING,
        nullable=False,
        index=True,
    )
    raw_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    extracted_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    ats_analysis: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    optimized_content: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    ats_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="resumes")
    jobs: Mapped[list["ResumeJob"]] = relationship(
        "ResumeJob",
        back_populates="resume",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    exports: Mapped[list["ResumeExport"]] = relationship(
        "ResumeExport",
        back_populates="resume",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"<Resume id={self.id} "
            f"filename={self.original_filename!r} "
            f"status={self.status}>"
        )


class ResumeJob(Base, UUIDMixin, TimestampMixin):
    """ORM model representing a job tailoring request for a resume.

    Links a resume to a specific job description and stores the
    AI-generated tailored content and match score.
    """

    __tablename__ = "resume_jobs"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    job_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    tailored_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    match_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    # Relationships
    resume: Mapped["Resume"] = relationship("Resume", back_populates="jobs")
    exports: Mapped[list["ResumeExport"]] = relationship(
        "ResumeExport",
        back_populates="job",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<ResumeJob id={self.id} "
            f"resume_id={self.resume_id} "
            f"job_title={self.job_title!r} "
            f"match_score={self.match_score}>"
        )
