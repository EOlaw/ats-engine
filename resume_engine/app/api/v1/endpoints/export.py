"""Resume export endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import get_current_active_user
from app.api.v1.dependencies.services import get_resume_service
from app.core.exceptions import ResourceNotFoundException, StorageException
from app.db.session import get_db
from app.models.export import ExportFormat, ResumeExport
from app.models.user import User
from app.schemas.export import ExportRequest, ExportResponse
from app.services.resume_service import ResumeService

router = APIRouter(tags=["Export"])

_MIME_MAP: dict[str, str] = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post(
    "/export",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a PDF or DOCX export of a resume",
)
async def create_export(
    export_request: ExportRequest,
    current_user: User = Depends(get_current_active_user),
    resume_service: ResumeService = Depends(get_resume_service),
) -> ExportResponse:
    """Generate a resume export in the specified format and template.

    Creates the export file and returns metadata including the download URL.
    Use GET /exports/{export_id}/download to retrieve the file.

    Args:
        export_request: Export configuration (resume_id, template, format, optional job_id).
        current_user: Authenticated user (injected).
        resume_service: Resume service (injected).

    Returns:
        ExportResponse with export_id, file_path, and download_url.
    """
    export_record = await resume_service.export_resume(export_request, current_user.id)

    return ExportResponse(
        export_id=export_record.id,
        resume_id=export_record.resume_id,
        template_name=export_record.template_name,
        format=export_record.format,
        download_url=f"/api/v1/exports/{export_record.id}/download",
        file_path=export_record.file_path,
        created_at=export_record.created_at,
    )


@router.get(
    "/exports/{export_id}/download",
    summary="Download an exported resume file",
    response_class=FileResponse,
)
async def download_export(
    export_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Stream an exported resume file for download.

    Verifies that the export belongs to the current user (via the related
    resume's user_id) before serving the file.

    Args:
        export_id: UUID of the ResumeExport record.
        current_user: Authenticated user (injected).
        db: Database session (injected).

    Returns:
        FileResponse streaming the exported PDF or DOCX file.

    Raises:
        ResourceNotFoundException: If the export record does not exist.
        StorageException: If the exported file is no longer present on disk.
    """
    from sqlalchemy.orm import joinedload

    result = await db.execute(
        select(ResumeExport)
        .options(joinedload(ResumeExport.resume))
        .where(ResumeExport.id == export_id)
    )
    export_record = result.scalar_one_or_none()

    if export_record is None:
        raise ResourceNotFoundException("ResumeExport", str(export_id))

    if export_record.resume.user_id != current_user.id:
        from app.core.exceptions import AuthorizationException
        raise AuthorizationException("You do not have access to this export")

    file_path = Path(export_record.file_path)
    if not file_path.exists():
        raise StorageException(
            f"Export file not found on disk: {file_path.name}",
            details={"export_id": str(export_id)},
        )

    fmt = export_record.format.value if isinstance(export_record.format, ExportFormat) else export_record.format
    media_type = _MIME_MAP.get(fmt, "application/octet-stream")
    download_name = f"resume_{export_record.resume_id}.{fmt}"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=download_name,
    )
