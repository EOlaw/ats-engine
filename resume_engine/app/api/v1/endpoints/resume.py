"""Resume CRUD and management endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status

from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.services import get_resume_service
from app.models.user import User
from app.schemas.resume import ResumeProcessResponse, ResumeStatusResponse
from app.services.ai.prompt_chain import ProcessingMode
from app.services.resume_service import ResumeService

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get(
    "",
    response_model=list[ResumeProcessResponse],
    summary="List all resumes for the authenticated user",
)
async def list_resumes(
    skip: int = Query(default=0, ge=0, description="Pagination offset"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum results to return"),
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> list[ResumeProcessResponse]:
    """Retrieve a paginated list of the user's uploaded resumes.

    Args:
        skip: Number of records to skip (for pagination).
        limit: Maximum number of records to return.
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).

    Returns:
        List of ResumeProcessResponse objects ordered by creation date.
    """
    resumes = await resume_service.list_resumes(
        user_id=current_user.id, skip=skip, limit=limit
    )
    return [ResumeProcessResponse.model_validate(r) for r in resumes]


@router.get(
    "/{resume_id}",
    response_model=ResumeProcessResponse,
    summary="Get full resume data including AI analysis",
)
async def get_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeProcessResponse:
    """Retrieve a single resume with all extracted and analyzed data.

    Args:
        resume_id: UUID of the resume to retrieve.
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).

    Returns:
        Full ResumeProcessResponse including extracted_data, ats_analysis,
        optimized_content, and ats_score.
    """
    resume = await resume_service.get_resume(resume_id, current_user.id)
    return ResumeProcessResponse.model_validate(resume)


@router.get(
    "/{resume_id}/status",
    response_model=ResumeStatusResponse,
    summary="Check the processing status of a resume",
)
async def get_resume_status(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeStatusResponse:
    """Poll the current processing status of a resume.

    Useful for long-running AI pipeline operations. Returns a lightweight
    status response without the full data payload.

    Args:
        resume_id: UUID of the resume to check.
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).

    Returns:
        ResumeStatusResponse with current status and optional ATS score.
    """
    resume = await resume_service.get_resume(resume_id, current_user.id)
    return ResumeStatusResponse(
        resume_id=resume.id,
        status=resume.status,
        ats_score=resume.ats_score,
        error_message=resume.error_message,
        updated_at=resume.updated_at,
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resume and its associated file",
)
async def delete_resume(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> None:
    """Delete a resume record and remove the stored file.

    Args:
        resume_id: UUID of the resume to delete.
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).
    """
    await resume_service.delete_resume(resume_id, current_user.id)


@router.post(
    "/{resume_id}/reprocess",
    response_model=ResumeProcessResponse,
    summary="Re-run the AI pipeline on an existing resume",
)
async def reprocess_resume(
    resume_id: uuid.UUID,
    mode: ProcessingMode = Query(
        default=ProcessingMode.FULL_OPTIMIZATION,
        description="Processing mode for re-run",
    ),
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ResumeProcessResponse:
    """Re-run the AI processing pipeline on an already-uploaded resume.

    Uses the stored raw_text from the initial parse — the original file
    does not need to be re-uploaded. Useful for re-running with a different
    processing mode or after a pipeline failure.

    Args:
        resume_id: UUID of the resume to reprocess.
        mode: AI pipeline mode for the reprocess run.
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).

    Returns:
        Updated ResumeProcessResponse after reprocessing.
    """
    resume = await resume_service.reprocess_resume(resume_id, current_user.id, mode)
    return ResumeProcessResponse.model_validate(resume)
