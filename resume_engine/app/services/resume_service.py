"""Top-level resume service orchestrating upload, processing, tailoring, and export."""

import uuid
from pathlib import Path
from typing import Any

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    AuthorizationException,
    ExportException,
    ResourceNotFoundException,
    StorageException,
)
from app.core.logging import LoggerFactory
from app.models.export import ResumeExport
from app.models.resume import FileType, Resume, ResumeJob, ResumeStatus
from app.schemas.export import ExportRequest
from app.schemas.job import JobTailoringRequest
from app.services.ai.prompt_chain import ProcessingMode, PromptChainOrchestrator
from app.services.exporters.export_factory import ExportFactory
from app.services.parsers.document_factory import DocumentParserFactory
from app.services.templates.template_engine import TemplateEngine
from app.utils.file_utils import FileUtils

logger = LoggerFactory.get_logger(__name__)


class ResumeService:
    """Top-level orchestrator for all resume operations.

    Coordinates file upload, AI pipeline execution, job tailoring,
    and document export. Injected into API endpoints as a FastAPI dependency.

    Attributes:
        _db: Async SQLAlchemy session.
        _parser_factory: Factory for selecting document parsers.
        _prompt_chain: AI pipeline orchestrator.
        _export_factory: Factory for selecting document exporters.
        _template_engine: HTML/text template renderer.
        _settings: Application settings.
    """

    def __init__(
        self,
        db: AsyncSession,
        parser_factory: DocumentParserFactory,
        prompt_chain: PromptChainOrchestrator,
        export_factory: ExportFactory,
        template_engine: TemplateEngine,
        settings: Settings | None = None,
    ) -> None:
        self._db = db
        self._parser_factory = parser_factory
        self._prompt_chain = prompt_chain
        self._export_factory = export_factory
        self._template_engine = template_engine
        self._settings = settings or get_settings()

    async def upload_and_process(
        self,
        file: UploadFile,
        user_id: uuid.UUID,
        mode: ProcessingMode = ProcessingMode.FULL_OPTIMIZATION,
    ) -> Resume:
        """Upload a resume file and run the AI processing pipeline.

        Saves the uploaded file, creates a Resume record, parses the document
        to raw text, then runs the AI pipeline according to the specified mode.
        Status is updated at each pipeline stage.

        Args:
            file: The uploaded file from FastAPI.
            user_id: ID of the authenticated user.
            mode: Controls pipeline depth (extract only, analyze, or full optimization).

        Returns:
            The updated Resume ORM model after processing.

        Raises:
            StorageException: If file save fails.
            DocumentParseException: If the document cannot be parsed.
            AIServiceException: If any AI pipeline stage fails.
        """
        upload_dir = Path(self._settings.UPLOAD_DIR) / str(user_id)
        file_path = await FileUtils.save_upload(file, upload_dir)
        logger.info("File saved", path=str(file_path), user_id=str(user_id))

        ext = FileUtils.get_file_extension(file.filename or "")
        file_type = FileType.PDF if ext == "pdf" else FileType.DOCX

        resume = Resume(
            user_id=user_id,
            original_filename=file.filename or "resume",
            file_path=str(file_path),
            file_type=file_type,
            status=ResumeStatus.PARSING,
        )
        self._db.add(resume)
        await self._db.flush()
        logger.info("Resume record created", resume_id=str(resume.id))

        # Parse document to raw text
        try:
            parser = self._parser_factory.get_parser(file_path)
            raw_text = await parser.parse(file_path)
            resume.raw_text = raw_text
            resume.status = ResumeStatus.PARSED
            await self._db.flush()
        except Exception as exc:
            resume.status = ResumeStatus.ERROR
            resume.error_message = f"Parsing failed: {exc}"
            await self._db.flush()
            raise

        # Run AI pipeline
        try:
            resume.status = ResumeStatus.SCORING
            await self._db.flush()

            pipeline_result = await self._prompt_chain.run_full_pipeline(
                resume_text=raw_text, mode=mode
            )

            resume.extracted_data = pipeline_result.get("extracted_data")
            resume.ats_analysis = pipeline_result.get("ats_analysis")
            resume.optimized_content = pipeline_result.get("optimized_content")
            resume.ats_score = pipeline_result.get("ats_score")

            if mode == ProcessingMode.EXTRACT_ONLY:
                resume.status = ResumeStatus.PARSED
            elif mode == ProcessingMode.EXTRACT_AND_ANALYZE:
                resume.status = ResumeStatus.SCORED
            else:
                resume.status = ResumeStatus.OPTIMIZED

            await self._db.flush()
        except Exception as exc:
            resume.status = ResumeStatus.ERROR
            resume.error_message = f"AI processing failed: {exc}"
            await self._db.flush()
            raise

        logger.info(
            "Resume processing complete",
            resume_id=str(resume.id),
            status=resume.status,
            ats_score=resume.ats_score,
        )
        return resume

    async def get_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> Resume:
        """Retrieve a resume by ID, ensuring ownership.

        Args:
            resume_id: UUID of the resume to retrieve.
            user_id: UUID of the authenticated user (for ownership check).

        Returns:
            The Resume ORM model.

        Raises:
            ResourceNotFoundException: If the resume does not exist.
            AuthorizationException: If the resume belongs to another user.
        """
        result = await self._db.execute(
            select(Resume).where(Resume.id == resume_id)
        )
        resume = result.scalar_one_or_none()
        if resume is None:
            raise ResourceNotFoundException("Resume", str(resume_id))
        if resume.user_id != user_id:
            raise AuthorizationException("You do not have access to this resume")
        return resume

    async def list_resumes(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Resume]:
        """List all resumes for the authenticated user with pagination.

        Args:
            user_id: UUID of the authenticated user.
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.

        Returns:
            List of Resume ORM models ordered by creation date descending.
        """
        result = await self._db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_resume(self, resume_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Delete a resume and its associated file.

        Args:
            resume_id: UUID of the resume to delete.
            user_id: UUID of the authenticated user.

        Raises:
            ResourceNotFoundException: If the resume does not exist.
            AuthorizationException: If the resume belongs to another user.
        """
        resume = await self.get_resume(resume_id, user_id)
        file_path = Path(resume.file_path)
        await FileUtils.delete_file(file_path)
        await self._db.delete(resume)
        await self._db.flush()
        logger.info("Resume deleted", resume_id=str(resume_id))

    async def reprocess_resume(
        self,
        resume_id: uuid.UUID,
        user_id: uuid.UUID,
        mode: ProcessingMode = ProcessingMode.FULL_OPTIMIZATION,
    ) -> Resume:
        """Re-run the AI pipeline on an already-uploaded resume.

        Uses the existing raw_text without re-parsing the file.

        Args:
            resume_id: UUID of the resume to reprocess.
            user_id: UUID of the authenticated user.
            mode: Pipeline mode to use for reprocessing.

        Returns:
            The updated Resume ORM model.

        Raises:
            ResourceNotFoundException: If the resume does not exist.
            AuthorizationException: If the resume belongs to another user.
        """
        resume = await self.get_resume(resume_id, user_id)
        if not resume.raw_text:
            raise ExportException(
                "Cannot reprocess resume: no raw text available. "
                "The original file may have been lost."
            )

        resume.status = ResumeStatus.SCORING
        await self._db.flush()

        try:
            pipeline_result = await self._prompt_chain.run_full_pipeline(
                resume_text=resume.raw_text, mode=mode
            )
            resume.extracted_data = pipeline_result.get("extracted_data")
            resume.ats_analysis = pipeline_result.get("ats_analysis")
            resume.optimized_content = pipeline_result.get("optimized_content")
            resume.ats_score = pipeline_result.get("ats_score")
            resume.status = ResumeStatus.OPTIMIZED
            resume.error_message = None
            await self._db.flush()
        except Exception as exc:
            resume.status = ResumeStatus.ERROR
            resume.error_message = f"Reprocessing failed: {exc}"
            await self._db.flush()
            raise

        return resume

    async def tailor_resume(
        self,
        resume_id: uuid.UUID,
        user_id: uuid.UUID,
        job_request: JobTailoringRequest,
    ) -> ResumeJob:
        """Tailor a resume to a specific job description.

        Args:
            resume_id: UUID of the resume to tailor.
            user_id: UUID of the authenticated user.
            job_request: Job tailoring request containing title and description.

        Returns:
            A ResumeJob ORM model with tailored content and match score.

        Raises:
            ResourceNotFoundException: If the resume does not exist.
            AuthorizationException: If the resume belongs to another user.
            TailoringException: If the AI tailoring pipeline fails.
        """
        resume = await self.get_resume(resume_id, user_id)

        resume_data: dict[str, Any] = {}
        if resume.optimized_content:
            resume_data.update(resume.optimized_content)
        if resume.extracted_data:
            # Merge extracted as base, optimized overrides
            base = dict(resume.extracted_data)
            base.update(resume_data)
            resume_data = base

        tailored = await self._prompt_chain.run_tailoring_pipeline(
            resume_data=resume_data,
            job_title=job_request.job_title,
            job_description=job_request.job_description,
        )

        job = ResumeJob(
            resume_id=resume_id,
            job_title=job_request.job_title,
            job_description=job_request.job_description,
            tailored_data=tailored,
            match_score=tailored.get("match_score"),
        )
        self._db.add(job)
        await self._db.flush()
        logger.info(
            "Tailoring complete",
            resume_id=str(resume_id),
            job_id=str(job.id),
            match_score=job.match_score,
        )
        return job

    async def export_resume(
        self,
        export_request: ExportRequest,
        user_id: uuid.UUID,
    ) -> ResumeExport:
        """Export a resume to a file (PDF or DOCX).

        Merges extracted, optimized, and optionally tailored content, then
        renders using the selected template and format.

        Args:
            export_request: Export configuration including template and format.
            user_id: UUID of the authenticated user.

        Returns:
            A ResumeExport ORM model with the output file path.

        Raises:
            ResourceNotFoundException: If the resume or job does not exist.
            AuthorizationException: If ownership check fails.
            ExportException: If rendering or file writing fails.
        """
        resume = await self.get_resume(export_request.resume_id, user_id)

        # Build the data payload for rendering
        render_data: dict[str, Any] = {}
        if resume.extracted_data:
            render_data.update(resume.extracted_data)
        if export_request.use_optimized and resume.optimized_content:
            render_data["optimized_content"] = resume.optimized_content

        # Layer in tailored content if job_id provided
        if export_request.job_id:
            result = await self._db.execute(
                select(ResumeJob).where(ResumeJob.id == export_request.job_id)
            )
            job = result.scalar_one_or_none()
            if job is None:
                raise ResourceNotFoundException("ResumeJob", str(export_request.job_id))
            if job.tailored_data:
                render_data["optimized_content"] = job.tailored_data

        export_dir = Path(self._settings.EXPORT_DIR) / str(user_id)
        export_dir.mkdir(parents=True, exist_ok=True)
        output_filename = f"resume_{resume.id}_{export_request.template_name}.{export_request.format.value}"
        output_path = export_dir / output_filename

        exporter = self._export_factory.get_exporter(export_request.format.value)
        final_path = await exporter.export(
            resume_data=render_data,
            template_name=export_request.template_name.value,
            output_path=output_path,
        )

        export_record = ResumeExport(
            resume_id=resume.id,
            template_name=export_request.template_name.value,
            format=export_request.format,
            file_path=str(final_path),
            job_id=export_request.job_id,
        )
        self._db.add(export_record)
        await self._db.flush()
        logger.info(
            "Export complete",
            export_id=str(export_record.id),
            format=export_request.format.value,
        )
        return export_record
