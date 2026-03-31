"""Abstract base class for all AI service components."""

import json
import re
from abc import ABC, abstractmethod
from typing import Any

import anthropic
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import Settings, get_settings
from app.core.exceptions import AIServiceException
from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


class BaseAIService(ABC):
    """Abstract base for all AI pipeline service classes.

    Provides a shared Anthropic client, retry logic via tenacity, and
    JSON extraction utilities. Subclasses implement the execute() method
    specific to their pipeline stage.

    Attributes:
        _client: Async Anthropic client instance.
        _model: Claude model identifier to use for API calls.
        _settings: Application settings instance.
    """

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        model: str,
        settings: Settings | None = None,
    ) -> None:
        self._client = client
        self._model = model
        self._settings = settings or get_settings()

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute this AI service stage.

        Args:
            **kwargs: Stage-specific keyword arguments.

        Returns:
            Stage-specific output, typically a Pydantic model instance.

        Raises:
            AIServiceException: If the AI call fails after all retries.
        """
        ...

    async def _call_claude(
        self,
        system: str,
        user: str,
        max_tokens: int = 4096,
    ) -> str:
        """Call the Claude API with retry logic and return the response text.

        Uses tenacity for exponential backoff on transient API errors.
        Retries up to 3 times with 1–10 second exponential backoff.

        Args:
            system: The system prompt.
            user: The user message content.
            max_tokens: Maximum tokens in the response.

        Returns:
            The assistant's response text.

        Raises:
            AIServiceException: If all retry attempts are exhausted or a
                non-retriable error occurs.
        """
        return await self._call_claude_with_retry(system=system, user=user, max_tokens=max_tokens)

    @retry(
        retry=retry_if_exception_type((anthropic.APITimeoutError, anthropic.RateLimitError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=False,
    )
    async def _call_claude_with_retry(
        self,
        system: str,
        user: str,
        max_tokens: int,
    ) -> str:
        """Internal method with tenacity retry decorator applied.

        Args:
            system: System prompt.
            user: User message.
            max_tokens: Max response tokens.

        Returns:
            Raw response text from Claude.

        Raises:
            AIServiceException: On non-retriable errors or final retry failure.
        """
        try:
            message = await self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            response_text = message.content[0].text
            logger.debug(
                "Claude API call succeeded",
                model=self._model,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )
            return response_text
        except (anthropic.APITimeoutError, anthropic.RateLimitError):
            logger.warning("Claude API transient error, will retry")
            raise
        except anthropic.APIError as exc:
            logger.error("Claude API error", error=str(exc), status_code=exc.status_code)
            raise AIServiceException(
                f"Claude API error: {exc.message}",
                details={"status_code": exc.status_code},
            ) from exc
        except Exception as exc:
            logger.error("Unexpected error calling Claude", error=str(exc))
            raise AIServiceException(
                f"Unexpected error calling Claude API: {exc}"
            ) from exc

    def _extract_json_from_response(self, response: str) -> dict[str, Any]:
        """Safely extract a JSON object from a Claude response.

        Handles cases where the JSON is wrapped in markdown code fences
        (```json ... ``` or ``` ... ```), or returned as bare JSON.

        Args:
            response: Raw response text from Claude.

        Returns:
            Parsed Python dictionary from the JSON content.

        Raises:
            AIServiceException: If no valid JSON object can be extracted.
        """
        text = response.strip()

        # Try to strip markdown code fences if present
        code_block_pattern = re.compile(
            r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE
        )
        match = code_block_pattern.search(text)
        if match:
            text = match.group(1).strip()

        # Attempt direct JSON parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find a JSON object by locating first { and last }
        brace_start = text.find("{")
        brace_end = text.rfind("}")
        if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
            candidate = text[brace_start: brace_end + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        logger.error("Failed to extract JSON from Claude response", response_preview=text[:200])
        raise AIServiceException(
            "Claude response did not contain valid JSON",
            details={"response_preview": text[:500]},
        )
