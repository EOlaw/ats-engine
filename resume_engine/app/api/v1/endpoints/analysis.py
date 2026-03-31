"""Resume analysis and job tailoring endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.services import get_resume_service
from app.core.exceptions import ResourceNotFoundException
from app.db.session import get_db
from app.models.resume import ResumeJob
from app.models.user import User
from app.schemas.job import JobTailoringRequest, TailoredResumeResponse
from app.services.resume_service import ResumeService

router = APIRouter(tags=["Analysis"])


@router.get(
    "/resumes/{resume_id}/analysis",
    response_model=dict[str, Any],
    summary="Get the ATS analysis for a resume",
)
async def get_analysis(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> dict[str, Any]:
    """Retrieve the ATS analysis results for a resume.

    Returns the full ats_analysis JSON including score breakdown, keyword gaps,
    strengths, weaknesses, and recommendations.

    Args:
        resume_id: UUID of the resume.
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).

    Returns:
        The ats_analysis dictionary or an empty dict if not yet analyzed.
    """
    resume = await resume_service.get_resume(resume_id, current_user.id)
    return resume.ats_analysis or {}


@router.post(
    "/resumes/{resume_id}/tailor",
    response_model=TailoredResumeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tailor a resume to a specific job description",
)
async def tailor_resume(
    resume_id: uuid.UUID,
    job_request: JobTailoringRequest,
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> TailoredResumeResponse:
    """Tailor a resume to a specific job posting using AI.

    Runs the full tailoring pipeline: keyword gap analysis, summary rewrite,
    bullet point optimization, and skills reorganization for the target role.

    Args:
        resume_id: UUID of the resume to tailor.
        job_request: Job tailoring request with title and description.
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).

    Returns:
        TailoredResumeResponse with job_id, tailored_data, and match_score.
    """
    job = await resume_service.tailor_resume(resume_id, current_user.id, job_request)
    return TailoredResumeResponse.model_validate(job)


@router.get(
    "/resumes/{resume_id}/tailoring/{job_id}",
    response_model=TailoredResumeResponse,
    summary="Retrieve a specific job tailoring result",
)
async def get_tailoring(
    resume_id: uuid.UUID,
    job_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
    db: AsyncSession = Depends(get_db),
) -> TailoredResumeResponse:
    """Retrieve a previously generated job tailoring result.

    Validates that the resume belongs to the current user before
    returning the tailored content.

    Args:
        resume_id: UUID of the resume.
        job_id: UUID of the ResumeJob tailoring record.
        current_user: Authenticated user (injected).
        resume_service: Resume service for ownership check (injected).
        db: Database session (injected).

    Returns:
        TailoredResumeResponse with the stored tailored data.

    Raises:
        ResourceNotFoundException: If the job or resume does not exist.
    """
    # Verify resume ownership
    await resume_service.get_resume(resume_id, current_user.id)

    result = await db.execute(
        select(ResumeJob).where(
            ResumeJob.id == job_id,
            ResumeJob.resume_id == resume_id,
        )
    )
    job = result.scalar_one_or_none()
    if job is None:
        raise ResourceNotFoundException("ResumeJob", str(job_id))

    return TailoredResumeResponse.model_validate(job)
