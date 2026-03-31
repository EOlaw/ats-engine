"""Orchestrator for the multi-stage AI prompt chain pipeline."""

import enum
from typing import Any

from app.core.exceptions import AIServiceException
from app.core.logging import LoggerFactory
from app.services.ai.extraction_service import ExtractionService
from app.services.ai.optimization_service import OptimizationService
from app.services.ai.scoring_service import ATSScoringService
from app.services.ai.tailoring_service import TailoringService
from app.services.ai.validation_service import ValidationService

logger = LoggerFactory.get_logger(__name__)


class ProcessingMode(str, enum.Enum):
    """Controls which stages of the AI pipeline are executed."""

    EXTRACT_ONLY = "extract_only"
    EXTRACT_AND_ANALYZE = "extract_and_analyze"
    FULL_OPTIMIZATION = "full_optimization"


class PromptChainOrchestrator:
    """Orchestrates the multi-stage AI processing pipeline.

    Coordinates extraction, validation, scoring, and optimization services,
    passing the output of each stage as input to the next. The processing
    depth is controlled by the ProcessingMode enum.

    Attributes:
        _extraction: Service for extracting structured data from raw text.
        _validation: Service for validating and correcting extracted data.
        _scoring: Service for ATS compatibility scoring.
        _optimization: Service for content optimization.
        _tailoring: Service for job-specific tailoring.
    """

    def __init__(
        self,
        extraction: ExtractionService,
        validation: ValidationService,
        scoring: ATSScoringService,
        optimization: OptimizationService,
        tailoring: TailoringService,
    ) -> None:
        self._extraction = extraction
        self._validation = validation
        self._scoring = scoring
        self._optimization = optimization
        self._tailoring = tailoring

    async def run_full_pipeline(
        self,
        resume_text: str,
        mode: ProcessingMode = ProcessingMode.FULL_OPTIMIZATION,
    ) -> dict[str, Any]:
        """Run the full AI processing pipeline on raw resume text.

        Pipeline stages executed based on mode:
        - EXTRACT_ONLY: extraction → validation
        - EXTRACT_AND_ANALYZE: extraction → validation → scoring
        - FULL_OPTIMIZATION: extraction → validation → scoring → optimization

        Each stage's output is fed as input to the next stage.

        Args:
            resume_text: Raw plain text content of the resume.
            mode: Controls how many pipeline stages are executed.

        Returns:
            A dictionary containing all stage outputs:
                - extracted_data: dict from extraction (validated)
                - ats_analysis: dict from scoring (if executed)
                - optimized_content: dict from optimization (if executed)
                - ats_score: float from scoring (if executed)

        Raises:
            AIServiceException: If any pipeline stage fails.
        """
        result: dict[str, Any] = {
            "extracted_data": None,
            "ats_analysis": None,
            "optimized_content": None,
            "ats_score": None,
        }

        # Stage 1: Extraction
        logger.info("Pipeline stage 1: extraction", mode=mode.value)
        extracted = await self._extraction.execute(resume_text=resume_text)
        extracted_dict = extracted.model_dump()

        # Stage 2: Validation
        logger.info("Pipeline stage 2: validation")
        validation_result = await self._validation.execute(extracted_data=extracted_dict)
        validated_data = validation_result.get("corrected_data", extracted_dict)
        result["extracted_data"] = validated_data

        if mode == ProcessingMode.EXTRACT_ONLY:
            return result

        # Stage 3: ATS Scoring
        logger.info("Pipeline stage 3: ATS scoring")
        ats_analysis = await self._scoring.execute(
            extracted_data=validated_data,
            resume_text=resume_text,
        )
        ats_analysis_dict = ats_analysis.model_dump()
        result["ats_analysis"] = ats_analysis_dict
        result["ats_score"] = ats_analysis.score_estimate

        if mode == ProcessingMode.EXTRACT_AND_ANALYZE:
            return result

        # Stage 4: Optimization
        logger.info("Pipeline stage 4: optimization")
        optimized = await self._optimization.execute(
            extracted_data=validated_data,
            ats_analysis=ats_analysis_dict,
        )
        result["optimized_content"] = optimized.model_dump()

        logger.info(
            "Full pipeline completed",
            ats_score=result["ats_score"],
        )
        return result

    async def run_tailoring_pipeline(
        self,
        resume_data: dict[str, Any],
        job_title: str,
        job_description: str,
    ) -> dict[str, Any]:
        """Run the job tailoring pipeline on existing resume data.

        Does not re-run extraction or scoring. Uses already-processed
        resume data as the base for job-specific tailoring.

        Args:
            resume_data: Previously extracted (and optionally optimized) resume data.
            job_title: Target job title.
            job_description: Full job description text.

        Returns:
            The output dictionary from TailoringService containing
            tailored content and keyword gap analysis.

        Raises:
            AIServiceException: If the tailoring stage fails.
        """
        logger.info("Running tailoring pipeline", job_title=job_title)
        tailored = await self._tailoring.execute(
            resume_data=resume_data,
            job_title=job_title,
            job_description=job_description,
        )
        logger.info("Tailoring pipeline completed", match_score=tailored.get("match_score"))
        return tailored
