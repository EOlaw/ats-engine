"""AI service for optimizing resume content based on ATS analysis."""

from typing import Any

import anthropic
from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import OptimizationException
from app.core.logging import LoggerFactory
from app.schemas.resume import OptimizedContent
from app.services.ai.base import BaseAIService
from prompts.optimization.optimization_prompt import OptimizationPrompt

logger = LoggerFactory.get_logger(__name__)


class OptimizationService(BaseAIService):
    """AI service that optimizes resume content using ATS analysis gaps.

    Takes the structured extraction data and ATS analysis as context,
    then rewrites the professional summary, work experience bullets,
    and reorganizes skills to address identified weaknesses and keyword gaps.
    """

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        model: str,
        settings: Settings | None = None,
    ) -> None:
        super().__init__(client, model, settings)

    async def execute(
        self,
        extracted_data: dict[str, Any],
        ats_analysis: dict[str, Any],
        **kwargs: Any,
    ) -> OptimizedContent:
        """Optimize resume content based on ATS analysis.

        Args:
            extracted_data: Structured data from ExtractionService.
            ats_analysis: ATS analysis output from ATSScoringService.

        Returns:
            A fully populated OptimizedContent Pydantic model with
            rewritten summary, bullets, and reorganized skills.

        Raises:
            OptimizationException: If the AI call fails or response
                cannot be parsed.
        """
        logger.info(
            "Starting resume optimization",
            score_before=ats_analysis.get("score_estimate"),
        )

        system_prompt, user_prompt = OptimizationPrompt.build(extracted_data, ats_analysis)

        try:
            response_text = await self._call_claude(
                system=system_prompt,
                user=user_prompt,
                max_tokens=6000,
            )
        except Exception as exc:
            raise OptimizationException(
                f"Claude API call failed during optimization: {exc}"
            ) from exc

        try:
            raw_data = self._extract_json_from_response(response_text)
        except Exception as exc:
            raise OptimizationException(
                f"Failed to parse optimization response as JSON: {exc}",
                details={"response_preview": response_text[:300]},
            ) from exc

        try:
            optimized = OptimizedContent.model_validate(raw_data)
        except ValidationError as exc:
            logger.warning(
                "Pydantic validation failed for optimization, using partial data",
                errors=exc.errors(),
            )
            optimized = OptimizedContent(
                professional_summary=raw_data.get("professional_summary"),
                work_experience=raw_data.get("work_experience", []),
                skills_grouping=raw_data.get("skills_grouping", {}),
                added_keywords=raw_data.get("added_keywords", []),
                optimization_notes=raw_data.get("optimization_notes", []),
            )

        logger.info(
            "Optimization completed",
            added_keywords=len(optimized.added_keywords),
            experience_entries=len(optimized.work_experience),
        )

        return optimized
