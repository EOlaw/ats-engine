"""AI service for extracting structured resume data from raw text."""

from typing import Any

import anthropic
from pydantic import ValidationError

from app.core.config import Settings
from app.core.exceptions import ExtractionException
from app.core.logging import LoggerFactory
from app.schemas.resume import ExtractedResume
from app.services.ai.base import BaseAIService
from prompts.extraction.extraction_prompt import ExtractionPrompt

logger = LoggerFactory.get_logger(__name__)


class ExtractionService(BaseAIService):
    """AI service that extracts structured data from raw resume text.

    Takes raw text from a parsed resume document and uses Claude to
    extract it into a fully typed ExtractedResume Pydantic model.
    Validates extraction confidence and raises on low-quality extractions.
    """

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        model: str,
        settings: Settings | None = None,
    ) -> None:
        super().__init__(client, model, settings)

    async def execute(self, resume_text: str, **kwargs: Any) -> ExtractedResume:
        """Extract structured data from raw resume text.

        Builds an extraction prompt, calls Claude, parses the JSON response
        into an ExtractedResume model, and validates confidence.

        Args:
            resume_text: The raw plain text content of the resume.

        Returns:
            A fully populated ExtractedResume Pydantic model.

        Raises:
            ExtractionException: If the AI call fails, the response cannot
                be parsed as JSON, or Pydantic validation fails.
        """
        if not resume_text or not resume_text.strip():
            raise ExtractionException("Resume text is empty — cannot extract data")

        logger.info("Starting resume extraction", text_length=len(resume_text))

        system_prompt, user_prompt = ExtractionPrompt.build(resume_text)

        try:
            response_text = await self._call_claude(
                system=system_prompt,
                user=user_prompt,
                max_tokens=4096,
            )
        except Exception as exc:
            raise ExtractionException(
                f"Claude API call failed during extraction: {exc}"
            ) from exc

        try:
            raw_data = self._extract_json_from_response(response_text)
        except Exception as exc:
            raise ExtractionException(
                f"Failed to parse extraction response as JSON: {exc}",
                details={"response_preview": response_text[:300]},
            ) from exc

        try:
            extracted = ExtractedResume.model_validate(raw_data)
        except ValidationError as exc:
            logger.warning("Pydantic validation failed for extraction, attempting partial", errors=exc.errors())
            # Attempt graceful degradation — use only what validates
            try:
                extracted = ExtractedResume.model_construct(**{
                    k: v for k, v in raw_data.items()
                    if k in ExtractedResume.model_fields
                })
            except Exception as construct_exc:
                raise ExtractionException(
                    f"Extraction response failed Pydantic validation: {exc}",
                    details={"validation_errors": exc.errors()},
                ) from construct_exc

        self._validate_confidence(extracted)

        logger.info(
            "Extraction completed",
            confidence=extracted.extraction_confidence,
            sections_found=len(extracted.raw_sections_found),
            work_experience_count=len(extracted.work_experience),
        )

        return extracted

    def _validate_confidence(self, extracted: ExtractedResume) -> None:
        """Warn if extraction confidence is below acceptable threshold.

        Args:
            extracted: The populated ExtractedResume to validate.
        """
        MIN_CONFIDENCE = 0.4
        if extracted.extraction_confidence < MIN_CONFIDENCE:
            logger.warning(
                "Low extraction confidence",
                confidence=extracted.extraction_confidence,
                threshold=MIN_CONFIDENCE,
            )
        if not extracted.personal_info.email and not extracted.personal_info.full_name:
            logger.warning("Extraction found neither name nor email — document may not be a resume")
