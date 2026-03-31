"""Utility class for text processing and cleaning operations."""

import json
import re


class TextUtils:
    """Collection of static utility methods for text manipulation.

    Provides text cleaning for resume content, prompt size management,
    and JSON extraction from AI response strings.
    """

    @staticmethod
    def clean_resume_text(text: str) -> str:
        """Normalize and clean raw resume text for AI processing.

        Removes null bytes, normalizes unicode whitespace, collapses
        excessive blank lines, and strips control characters while
        preserving meaningful newlines that indicate section breaks.

        Args:
            text: Raw text from a document parser.

        Returns:
            Cleaned text ready for AI prompt embedding.
        """
        if not text:
            return ""

        # Remove null bytes and form feeds
        text = text.replace("\x00", "").replace("\x0c", "\n")

        # Normalize unicode whitespace characters
        text = re.sub(r"[\u00a0\u2002\u2003\u2009\u200b]", " ", text)

        # Normalize unicode dashes and bullets
        text = text.replace("\u2022", "-").replace("\u2023", "-").replace("\u25cf", "-")
        text = text.replace("\u2013", "-").replace("\u2014", "--")

        # Remove other non-printable control characters (except tab and newline)
        text = re.sub(r"[\x01-\x08\x0b\x0e-\x1f\x7f]", "", text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Fix hyphenated line breaks from PDF column layouts
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Collapse more than 2 consecutive blank lines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip trailing whitespace from each line, preserve intentional indentation
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    @staticmethod
    def truncate_for_prompt(text: str, max_chars: int = 12000) -> str:
        """Truncate text to fit within a maximum character limit for prompts.

        Truncates at a word boundary to avoid cutting mid-word. Appends
        a notice that content was truncated.

        Args:
            text: The text to potentially truncate.
            max_chars: Maximum number of characters to retain. Defaults to 12000
                which is approximately 3,000-4,000 tokens.

        Returns:
            The original text if under max_chars, otherwise truncated with
            an appended notice.
        """
        if len(text) <= max_chars:
            return text

        truncated = text[:max_chars]
        # Find last word boundary
        last_space = truncated.rfind(" ")
        if last_space > max_chars - 200:
            truncated = truncated[:last_space]

        return truncated + "\n\n[Note: Resume text was truncated for processing. Some content may be omitted.]"

    @staticmethod
    def extract_json_block(text: str) -> str:
        """Strip markdown JSON code fences from a text string.

        Handles both ```json ... ``` and ``` ... ``` fenced blocks.
        If no code fence is detected, returns the text unchanged.

        Args:
            text: A string that may contain a markdown JSON code block.

        Returns:
            The extracted JSON string without surrounding fences,
            or the original text if no fences are found.
        """
        text = text.strip()

        # Match ```json ... ``` or ``` ... ``` blocks
        fence_pattern = re.compile(
            r"^```(?:json)?\s*\n?([\s\S]*?)\n?```\s*$",
            re.IGNORECASE | re.MULTILINE,
        )
        match = fence_pattern.search(text)
        if match:
            return match.group(1).strip()

        # Match inline ```json...``` without newlines
        inline_pattern = re.compile(r"```(?:json)?(.*?)```", re.DOTALL | re.IGNORECASE)
        inline_match = inline_pattern.search(text)
        if inline_match:
            return inline_match.group(1).strip()

        return text

    @staticmethod
    def safe_json_loads(text: str) -> dict:
        """Attempt to parse a string as JSON, extracting from code fences first.

        Args:
            text: A string that may be JSON, possibly wrapped in markdown fences.

        Returns:
            Parsed dictionary if successful.

        Raises:
            ValueError: If the text cannot be parsed as JSON after extraction.
        """
        extracted = TextUtils.extract_json_block(text)
        try:
            return json.loads(extracted)
        except json.JSONDecodeError as exc:
            # Last attempt: find first { and last }
            start = extracted.find("{")
            end = extracted.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(extracted[start: end + 1])
                except json.JSONDecodeError:
                    pass
            raise ValueError(f"Cannot parse as JSON: {exc}") from exc
