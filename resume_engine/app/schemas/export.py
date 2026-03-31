"""Pydantic v2 schemas for resume export requests and responses."""

import enum
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TemplateEnum(str, enum.Enum):
    """Available resume templates."""

    MODERN_CLEAN = "modern_clean"
    EXECUTIVE_CLASSIC = "executive_classic"
    TECH_MINIMAL = "tech_minimal"
    CREATIVE_BOLD = "creative_bold"
    ATS_OPTIMIZED = "ats_optimized"
    ACADEMIC = "academic"


class ExportFormat(str, enum.Enum):
    """Supported export formats."""

    PDF = "pdf"
    DOCX = "docx"


class ExportRequest(BaseModel):
    """Request body for generating a resume export."""

    model_config = ConfigDict(str_strip_whitespace=True)

    resume_id: uuid.UUID = Field(description="ID of the resume to export")
    template_name: TemplateEnum = Field(
        default=TemplateEnum.ATS_OPTIMIZED,
        description="Template to use for rendering",
    )
    format: ExportFormat = Field(
        default=ExportFormat.PDF,
        description="Output file format",
    )
    job_id: uuid.UUID | None = Field(
        default=None,
        description="Optional job ID to use tailored content instead of base resume",
    )
    use_optimized: bool = Field(
        default=True,
        description="Use AI-optimized content if available",
    )


class ExportResponse(BaseModel):
    """Response returned after a resume export is generated."""

    model_config = ConfigDict(from_attributes=True)

    export_id: uuid.UUID
    resume_id: uuid.UUID
    template_name: str
    format: ExportFormat
    download_url: str = Field(description="URL to download the exported file")
    file_path: str
    created_at: datetime
