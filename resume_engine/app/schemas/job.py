"""Pydantic v2 schemas for job tailoring requests and responses."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class JobTailoringRequest(BaseModel):
    """Request body for tailoring a resume to a specific job posting."""

    model_config = ConfigDict(str_strip_whitespace=True)

    resume_id: uuid.UUID = Field(description="ID of the resume to tailor")
    job_title: str = Field(
        description="Job title being applied for",
        min_length=2,
        max_length=200,
    )
    job_description: str = Field(
        description="Full job description text",
        min_length=50,
        max_length=20000,
    )


class KeywordGapAnalysis(BaseModel):
    """Analysis of keyword gaps between a resume and job description."""

    missing_required: list[str] = Field(
        default_factory=list,
        description="Required keywords from JD not found in resume",
    )
    missing_preferred: list[str] = Field(
        default_factory=list,
        description="Preferred/nice-to-have keywords not found in resume",
    )
    present_keywords: list[str] = Field(
        default_factory=list,
        description="Keywords from JD already present in resume",
    )
    recommended_additions: list[str] = Field(
        default_factory=list,
        description="Top keywords to naturally incorporate",
    )


class JobMatchAnalysis(BaseModel):
    """Analysis of how well a resume matches a specific job posting."""

    match_score: float = Field(
        ge=0.0, le=100.0, description="Overall match percentage 0-100"
    )
    keyword_gap_analysis: KeywordGapAnalysis = Field(
        default_factory=KeywordGapAnalysis
    )
    experience_alignment: str = Field(
        default="", description="Assessment of experience alignment with role requirements"
    )
    skills_alignment: str = Field(
        default="", description="Assessment of skills alignment"
    )
    education_alignment: str = Field(
        default="", description="Assessment of education requirements match"
    )
    strengths_for_role: list[str] = Field(
        default_factory=list,
        description="Candidate's strengths most relevant to this role",
    )
    gaps_for_role: list[str] = Field(
        default_factory=list,
        description="Notable gaps relative to the role requirements",
    )
    tailoring_recommendations: list[str] = Field(
        default_factory=list,
        description="Specific recommendations for tailoring the resume",
    )


class TailoredResumeResponse(BaseModel):
    """Response containing the tailored resume data and analysis."""

    model_config = ConfigDict(from_attributes=True)

    job_id: uuid.UUID
    resume_id: uuid.UUID
    job_title: str
    match_score: float | None = None
    tailored_data: dict | None = None
    created_at: datetime
    updated_at: datetime
