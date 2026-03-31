"""Pydantic v2 schemas for resume data structures.

Covers the full JSON schema for AI extraction output, ATS analysis,
optimized content, and API request/response shapes.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.resume import FileType, ResumeStatus


# ---------------------------------------------------------------------------
# Extracted resume data schemas
# ---------------------------------------------------------------------------


class PersonalInfo(BaseModel):
    """Personal and contact information extracted from a resume."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, description="Candidate's full name")
    email: str | None = Field(default=None, description="Primary email address")
    phone: str | None = Field(default=None, description="Primary phone number")
    location: str | None = Field(default=None, description="City, state or full address")
    linkedin_url: str | None = Field(default=None, description="LinkedIn profile URL")
    github_url: str | None = Field(default=None, description="GitHub profile URL")
    portfolio_url: str | None = Field(default=None, description="Portfolio or personal site URL")
    summary: str | None = Field(default=None, description="Professional summary or objective")


class Skills(BaseModel):
    """Categorized skills section extracted from a resume."""

    technical: list[str] = Field(default_factory=list, description="Technical/hard skills")
    soft: list[str] = Field(default_factory=list, description="Soft skills and competencies")
    languages: list[str] = Field(default_factory=list, description="Programming or spoken languages")
    tools: list[str] = Field(default_factory=list, description="Tools, platforms, and frameworks")
    certifications_mentioned: list[str] = Field(
        default_factory=list, description="Certifications mentioned within skills section"
    )


class WorkExperience(BaseModel):
    """A single work experience entry extracted from a resume."""

    company: str | None = Field(default=None, description="Company or organization name")
    title: str | None = Field(default=None, description="Job title or role")
    location: str | None = Field(default=None, description="Work location")
    start_date: str | None = Field(default=None, description="Start date (YYYY-MM or free text)")
    end_date: str | None = Field(default=None, description="End date or 'Present'")
    is_current: bool = Field(default=False, description="Whether this is the current role")
    bullets: list[str] = Field(default_factory=list, description="Accomplishment and responsibility bullets")
    technologies: list[str] = Field(
        default_factory=list, description="Technologies or tools used in this role"
    )


class Education(BaseModel):
    """A single education entry extracted from a resume."""

    institution: str | None = Field(default=None, description="School or university name")
    degree: str | None = Field(default=None, description="Degree type (BS, MS, PhD, etc.)")
    field_of_study: str | None = Field(default=None, description="Major or field of study")
    start_date: str | None = Field(default=None, description="Start date")
    end_date: str | None = Field(default=None, description="Graduation date or 'Present'")
    gpa: str | None = Field(default=None, description="GPA if listed")
    honors: list[str] = Field(default_factory=list, description="Honors, awards, relevant coursework")


class Certification(BaseModel):
    """A professional certification extracted from a resume."""

    name: str | None = Field(default=None, description="Certification name")
    issuer: str | None = Field(default=None, description="Issuing organization")
    date_earned: str | None = Field(default=None, description="Date earned")
    expiry_date: str | None = Field(default=None, description="Expiration date if applicable")
    credential_id: str | None = Field(default=None, description="Credential ID if listed")


class Project(BaseModel):
    """A project entry extracted from a resume."""

    name: str | None = Field(default=None, description="Project name")
    description: str | None = Field(default=None, description="Brief project description")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")
    url: str | None = Field(default=None, description="Project URL or link")
    date: str | None = Field(default=None, description="Project date or date range")
    highlights: list[str] = Field(default_factory=list, description="Key achievements or highlights")


class ExtractedResume(BaseModel):
    """Full structured extraction of a resume document.

    This is the canonical output of the ExtractionService and serves as
    input to all downstream AI pipeline stages.
    """

    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    skills: Skills = Field(default_factory=Skills)
    work_experience: list[WorkExperience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    volunteer_experience: list[dict[str, Any]] = Field(default_factory=list)
    publications: list[dict[str, Any]] = Field(default_factory=list)
    awards: list[str] = Field(default_factory=list)
    languages: list[dict[str, Any]] = Field(default_factory=list)
    extraction_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="AI confidence score for the extraction (0-1)",
    )
    raw_sections_found: list[str] = Field(
        default_factory=list, description="List of section names detected in the document"
    )


# ---------------------------------------------------------------------------
# ATS analysis schemas
# ---------------------------------------------------------------------------


class KeywordMatch(BaseModel):
    """A keyword found or missing in the resume."""

    keyword: str
    found: bool
    context: str | None = None
    importance: str | None = Field(
        default=None, description="high/medium/low importance rating"
    )


class ATSAnalysis(BaseModel):
    """Full ATS analysis output from the scoring stage.

    Contains a numeric score with detailed breakdown, identified strengths
    and weaknesses, and actionable improvement suggestions.
    """

    score_estimate: float = Field(
        ge=0.0, le=100.0, description="Overall ATS compatibility score 0-100"
    )
    score_breakdown: dict[str, float] = Field(
        default_factory=dict,
        description="Per-category scores: format, keywords, experience, education, skills",
    )
    strengths: list[str] = Field(default_factory=list, description="Identified resume strengths")
    weaknesses: list[str] = Field(default_factory=list, description="Identified resume weaknesses")
    critical_fixes: list[str] = Field(
        default_factory=list,
        description="High-priority fixes that will most improve ATS score",
    )
    keyword_gaps: list[str] = Field(
        default_factory=list,
        description="Important keywords typically expected but not found",
    )
    keyword_matches: list[KeywordMatch] = Field(
        default_factory=list, description="Detailed keyword analysis"
    )
    format_issues: list[str] = Field(
        default_factory=list, description="Formatting problems that may cause ATS parsing failures"
    )
    quantification_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Score for use of quantified achievements",
    )
    action_verb_score: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Score for use of strong action verbs",
    )
    recommendations: list[str] = Field(
        default_factory=list, description="Prioritized actionable recommendations"
    )


# ---------------------------------------------------------------------------
# Optimized content schemas
# ---------------------------------------------------------------------------


class OptimizedWorkExperience(BaseModel):
    """Optimized work experience entry with rewritten bullets."""

    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    optimized_bullets: list[str] = Field(default_factory=list)


class OptimizedContent(BaseModel):
    """Output of the optimization stage — rewritten resume content.

    Contains AI-improved professional summary, work experience bullets,
    and reorganized skills sections based on ATS analysis gaps.
    """

    professional_summary: str | None = Field(
        default=None, description="Rewritten professional summary optimized for ATS"
    )
    work_experience: list[OptimizedWorkExperience] = Field(
        default_factory=list, description="Work experience entries with optimized bullets"
    )
    skills_grouping: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Reorganized skills by category: technical, soft, tools, etc.",
    )
    added_keywords: list[str] = Field(
        default_factory=list, description="Keywords added during optimization"
    )
    optimization_notes: list[str] = Field(
        default_factory=list, description="Summary of changes made during optimization"
    )


# ---------------------------------------------------------------------------
# API request / response schemas
# ---------------------------------------------------------------------------


class ResumeUploadResponse(BaseModel):
    """Response returned after a successful resume upload."""

    resume_id: uuid.UUID
    status: ResumeStatus
    original_filename: str
    message: str = "Resume uploaded and processing started"


class ResumeStatusResponse(BaseModel):
    """Response for resume status polling."""

    resume_id: uuid.UUID
    status: ResumeStatus
    ats_score: float | None = None
    error_message: str | None = None
    updated_at: datetime


class ResumeProcessResponse(BaseModel):
    """Full resume data response including all AI pipeline outputs."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    file_type: FileType
    status: ResumeStatus
    ats_score: float | None = None
    extracted_data: dict[str, Any] | None = None
    ats_analysis: dict[str, Any] | None = None
    optimized_content: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
