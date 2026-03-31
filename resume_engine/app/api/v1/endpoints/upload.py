"""Resume upload endpoint."""

from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.services import get_resume_service
from app.core.config import Settings, get_settings
from app.core.exceptions import ValidationException
from app.models.user import User
from app.schemas.resume import ResumeUploadResponse
from app.services.ai.prompt_chain import ProcessingMode
from app.services.resume_service import ResumeService
from app.utils.file_utils import FileUtils

router = APIRouter(tags=["Upload"])

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_EXTENSIONS = {"pdf", "docx"}


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a resume file and start AI processing",
)
async def upload_resume(
    file: UploadFile = File(description="Resume file (PDF or DOCX, max 10 MB)"),
    mode: ProcessingMode = Query(
        default=ProcessingMode.FULL_OPTIMIZATION,
        description="AI processing depth: extract_only, extract_and_analyze, or full_optimization",
    ),
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
    settings: Settings = Depends(get_settings),
) -> ResumeUploadResponse:
    """Upload a resume file and trigger asynchronous AI processing.

    Validates file type and size, then passes the file to ResumeService
    for parsing and AI pipeline execution. Returns immediately with the
    resume ID and initial status.

    Args:
        file: The uploaded UploadFile (PDF or DOCX).
        mode: Controls how many AI pipeline stages are executed.
        current_user: Authenticated user (injected via JWT).
        resume_service: Resume processing orchestrator (injected).
        settings: Application settings for size limits (injected).

    Returns:
        ResumeUploadResponse with resume_id and initial status.

    Raises:
        ValidationException: If file type is unsupported or file exceeds size limit.
    """
    # Validate file type
    filename = file.filename or ""
    ext = FileUtils.get_file_extension(filename).lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationException(
            f"Unsupported file type '.{ext}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
            details={"filename": filename, "extension": ext},
        )

    # Read file to check size (UploadFile doesn't expose size directly before read)
    file_bytes = await file.read()
    file_size = len(file_bytes)

    if not FileUtils.validate_file_size(file_size, settings.MAX_UPLOAD_SIZE_MB):
        raise ValidationException(
            f"File size {file_size / (1024*1024):.1f} MB exceeds the "
            f"{settings.MAX_UPLOAD_SIZE_MB} MB limit",
            details={
                "file_size_bytes": file_size,
                "max_size_mb": settings.MAX_UPLOAD_SIZE_MB,
            },
        )

    # Reset file position for downstream reading
    import io
    file.file = io.BytesIO(file_bytes)

    resume = await resume_service.upload_and_process(
        file=file,
        user_id=current_user.id,
        mode=mode,
    )

    return ResumeUploadResponse(
        resume_id=resume.id,
        status=resume.status,
        original_filename=resume.original_filename,
        message=f"Resume uploaded and processed with mode '{mode.value}'",
    )
