"""AI service for validating and correcting extracted resume data."""

from typing import Any

import anthropic

from app.core.config import Settings
from app.core.exceptions import ExtractionException
from app.core.logging import LoggerFactory
from app.services.ai.base import BaseAIService
from prompts.validation.validation_prompt import ValidationPrompt

logger = LoggerFactory.get_logger(__name__)


class ValidationService(BaseAIService):
    """AI service that validates and corrects extracted resume JSON.

    Reviews the structured output from ExtractionService for logical
    consistency issues including date conflicts, duplicate entries,
    missing required fields, and ambiguous sections. Returns a validation
    report with optional corrections applied.
    """

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        model: str,
        settings: Settings | None = None,
    ) -> None:
        super().__init__(client, model, settings)

    async def execute(self, extracted_data: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """Validate extracted resume data and return a corrected version.

        Args:
            extracted_data: The raw dict output from ExtractionService.

        Returns:
            A dictionary with keys:
                - is_valid (bool): Whether the data passed all checks.
                - issues (list[str]): Descriptions of found issues.
                - corrected_data (dict): Corrected resume data dictionary.
                - validation_score (float): 0-1 quality score.

        Raises:
            ExtractionException: If the validation call or response parsing fails.
        """
        logger.info("Starting resume data validation")

        system_prompt, user_prompt = ValidationPrompt.build(extracted_data)

        try:
            response_text = await self._call_claude(
                system=system_prompt,
                user=user_prompt,
                max_tokens=4096,
            )
        except Exception as exc:
            raise ExtractionException(
                f"Claude API call failed during validation: {exc}"
            ) from exc

        try:
            validation_result = self._extract_json_from_response(response_text)
        except Exception as exc:
            # Validation failure is not fatal — return the original data as-is
            logger.warning("Failed to parse validation response, using original data", error=str(exc))
            return {
                "is_valid": True,
                "issues": ["Validation service returned unparseable response"],
                "corrected_data": extracted_data,
                "validation_score": 0.5,
            }

        # Ensure corrected_data is present; fall back to original if not
        if "corrected_data" not in validation_result or not validation_result["corrected_data"]:
            validation_result["corrected_data"] = extracted_data

        # Normalize expected keys
        validation_result.setdefault("is_valid", True)
        validation_result.setdefault("issues", [])
        validation_result.setdefault("validation_score", 1.0 if validation_result["is_valid"] else 0.5)

        logger.info(
            "Validation completed",
            is_valid=validation_result.get("is_valid"),
            issues_count=len(validation_result.get("issues", [])),
        )

        return validation_result
