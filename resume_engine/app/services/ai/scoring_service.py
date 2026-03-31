"""AI service for ATS scoring and analysis of resume data."""

from typing import Any

import anthropic
from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import ScoringException
from app.core.logging import LoggerFactory
from app.schemas.resume import ATSAnalysis
from app.services.ai.base import BaseAIService
from prompts.scoring.scoring_prompt import ScoringPrompt

logger = LoggerFactory.get_logger(__name__)


class ATSScoringService(BaseAIService):
    """AI service that produces ATS compatibility scoring and analysis.

    Analyzes the structured resume data plus the raw resume text to produce
    a comprehensive ATS analysis including score, strengths, weaknesses,
    keyword gaps, formatting issues, and prioritized recommendations.
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
        resume_text: str,
        **kwargs: Any,
    ) -> ATSAnalysis:
        """Score the resume for ATS compatibility.

        Args:
            extracted_data: Structured data from ExtractionService.
            resume_text: Raw plain text of the resume for additional context.

        Returns:
            A fully populated ATSAnalysis Pydantic model.

        Raises:
            ScoringException: If the AI call fails or the response cannot
                be parsed into an ATSAnalysis model.
        """
        logger.info("Starting ATS scoring", data_keys=list(extracted_data.keys()))

        system_prompt, user_prompt = ScoringPrompt.build(extracted_data, resume_text)

        try:
            response_text = await self._call_claude(
                system=system_prompt,
                user=user_prompt,
                max_tokens=4096,
            )
        except Exception as exc:
            raise ScoringException(
                f"Claude API call failed during ATS scoring: {exc}"
            ) from exc

        try:
            raw_data = self._extract_json_from_response(response_text)
        except Exception as exc:
            raise ScoringException(
                f"Failed to parse ATS scoring response as JSON: {exc}",
                details={"response_preview": response_text[:300]},
            ) from exc

        try:
            analysis = ATSAnalysis.model_validate(raw_data)
        except ValidationError as exc:
            logger.warning(
                "Pydantic validation failed for scoring response, attempting partial",
                errors=exc.errors(),
            )
            # Graceful degradation: construct what we can
            score_val = raw_data.get("score_estimate", 0.0)
            try:
                score_val = float(score_val)
            except (TypeError, ValueError):
                score_val = 0.0

            analysis = ATSAnalysis(
                score_estimate=min(100.0, max(0.0, score_val)),
                strengths=raw_data.get("strengths", []),
                weaknesses=raw_data.get("weaknesses", []),
                critical_fixes=raw_data.get("critical_fixes", []),
                keyword_gaps=raw_data.get("keyword_gaps", []),
                format_issues=raw_data.get("format_issues", []),
                recommendations=raw_data.get("recommendations", []),
            )

        logger.info(
            "ATS scoring completed",
            score=analysis.score_estimate,
            keyword_gaps=len(analysis.keyword_gaps),
            critical_fixes=len(analysis.critical_fixes),
        )

        return analysis
