"""AI service for tailoring resume content to a specific job description."""

from typing import Any

import anthropic

from app.core.config import Settings
from app.core.exceptions import TailoringException
from app.core.logging import LoggerFactory
from app.services.ai.base import BaseAIService
from prompts.tailoring.tailoring_prompt import TailoringPrompt

logger = LoggerFactory.get_logger(__name__)


class TailoringService(BaseAIService):
    """AI service that tailors a resume to a specific job posting.

    Compares the structured resume data against a job description, identifies
    keyword and skills gaps, then rewrites the professional summary and
    work experience bullets to maximize alignment with the target role.
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
        resume_data: dict[str, Any],
        job_title: str,
        job_description: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Tailor resume content to a specific job description.

        Args:
            resume_data: Structured resume data (from extraction or optimization).
            job_title: The target job title.
            job_description: The full job description text.

        Returns:
            A dictionary containing:
                - tailored_summary (str): Job-specific professional summary.
                - tailored_work_experience (list): Rewritten work experience bullets.
                - tailored_skills (dict): Reorganized/filtered skills.
                - keyword_gap_analysis (dict): Missing and present keywords.
                - match_score (float): 0-100 alignment score.
                - tailoring_notes (list[str]): Summary of changes made.

        Raises:
            TailoringException: If the AI call fails or response cannot be parsed.
        """
        logger.info("Starting resume tailoring", job_title=job_title)

        system_prompt, user_prompt = TailoringPrompt.build(
            resume_data, job_title, job_description
        )

        try:
            response_text = await self._call_claude(
                system=system_prompt,
                user=user_prompt,
                max_tokens=6000,
            )
        except Exception as exc:
            raise TailoringException(
                f"Claude API call failed during tailoring: {exc}"
            ) from exc

        try:
            tailored_data = self._extract_json_from_response(response_text)
        except Exception as exc:
            raise TailoringException(
                f"Failed to parse tailoring response as JSON: {exc}",
                details={"response_preview": response_text[:300]},
            ) from exc

        # Ensure required keys are present
        tailored_data.setdefault("tailored_summary", "")
        tailored_data.setdefault("tailored_work_experience", [])
        tailored_data.setdefault("tailored_skills", {})
        tailored_data.setdefault("keyword_gap_analysis", {})
        tailored_data.setdefault("match_score", 0.0)
        tailored_data.setdefault("tailoring_notes", [])

        # Normalize match_score to float 0-100
        try:
            score = float(tailored_data["match_score"])
            tailored_data["match_score"] = min(100.0, max(0.0, score))
        except (TypeError, ValueError):
            tailored_data["match_score"] = 0.0

        logger.info(
            "Tailoring completed",
            job_title=job_title,
            match_score=tailored_data.get("match_score"),
        )

        return tailored_data
