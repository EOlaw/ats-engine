"""PDF document parser using pdfplumber."""

import asyncio
import re
from functools import partial
from pathlib import Path

import pdfplumber

from app.core.exceptions import DocumentParseException
from app.core.logging import LoggerFactory
from app.services.parsers.base import BaseDocumentParser

logger = LoggerFactory.get_logger(__name__)


class PDFParser(BaseDocumentParser):
    """Parser for PDF resume documents using pdfplumber.

    pdfplumber is a synchronous library, so all operations are wrapped in
    asyncio's thread executor to avoid blocking the event loop. Extracted
    text is cleaned to normalize whitespace and remove parsing artifacts.
    """

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return ["pdf"]

    async def parse(self, file_path: Path) -> str:
        """Parse a PDF file and return cleaned plain text.

        Runs pdfplumber extraction in a thread pool executor to prevent
        blocking the async event loop. Text is cleaned of excess whitespace,
        null bytes, and other PDF parsing artifacts.

        Args:
            file_path: Absolute path to the PDF file.

        Returns:
            Cleaned plain text content of the PDF.

        Raises:
            DocumentParseException: If the PDF cannot be opened or read.
        """
        loop = asyncio.get_event_loop()
        try:
            text = await loop.run_in_executor(None, partial(self._extract_text, file_path))
        except DocumentParseException:
            raise
        except Exception as exc:
            logger.error("PDF parsing failed", file=str(file_path), error=str(exc))
            raise DocumentParseException(
                f"Failed to parse PDF: {exc}",
                details={"file_path": str(file_path)},
            ) from exc
        return text

    def _extract_text(self, file_path: Path) -> str:
        """Synchronous PDF text extraction (called in executor).

        Args:
            file_path: Path to the PDF file.

        Returns:
            Cleaned text content from all pages.

        Raises:
            DocumentParseException: If extraction fails.
        """
        if not file_path.exists():
            raise DocumentParseException(
                f"PDF file not found: {file_path}",
                details={"file_path": str(file_path)},
            )

        pages_text: list[str] = []
        with pdfplumber.open(str(file_path)) as pdf:
            if len(pdf.pages) == 0:
                raise DocumentParseException(
                    "PDF contains no pages",
                    details={"file_path": str(file_path)},
                )
            for page_num, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text(x_tolerance=3, y_tolerance=3)
                    if page_text:
                        pages_text.append(page_text)
                except Exception as exc:
                    logger.warning(
                        "Failed to extract page text",
                        page=page_num,
                        error=str(exc),
                    )

        raw_text = "\n\n".join(pages_text)
        return self._clean_text(raw_text)

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted PDF text.

        Removes null bytes, normalizes whitespace, collapses excessive
        blank lines, and strips leading/trailing whitespace per line.

        Args:
            text: Raw text from PDF extraction.

        Returns:
            Normalized text suitable for AI processing.
        """
        # Remove null bytes and other control characters
        text = text.replace("\x00", "").replace("\x0c", "\n")

        # Normalize unicode dashes and bullets
        text = text.replace("\u2022", "-").replace("\u2013", "-").replace("\u2014", "--")

        # Fix hyphenated line breaks (e.g., "devel-\noped" -> "developed")
        text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Collapse more than 2 consecutive newlines to 2
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip trailing whitespace from each line
        lines = [line.rstrip() for line in text.split("\n")]
        text = "\n".join(lines)

        return text.strip()

    async def extract_metadata(self, file_path: Path) -> dict:
        """Extract metadata from a PDF file.

        Args:
            file_path: Absolute path to the PDF file.

        Returns:
            Dictionary with keys: page_count, title, author, creator,
            producer, file_size_bytes.

        Raises:
            DocumentParseException: If metadata extraction fails.
        """
        loop = asyncio.get_event_loop()
        try:
            metadata = await loop.run_in_executor(
                None, partial(self._extract_metadata_sync, file_path)
            )
        except DocumentParseException:
            raise
        except Exception as exc:
            raise DocumentParseException(
                f"Failed to extract PDF metadata: {exc}",
                details={"file_path": str(file_path)},
            ) from exc
        return metadata

    def _extract_metadata_sync(self, file_path: Path) -> dict:
        """Synchronous metadata extraction (called in executor)."""
        if not file_path.exists():
            raise DocumentParseException(
                f"PDF file not found: {file_path}",
                details={"file_path": str(file_path)},
            )

        with pdfplumber.open(str(file_path)) as pdf:
            meta = pdf.metadata or {}
            return {
                "page_count": len(pdf.pages),
                "title": meta.get("Title", ""),
                "author": meta.get("Author", ""),
                "creator": meta.get("Creator", ""),
                "producer": meta.get("Producer", ""),
                "file_size_bytes": file_path.stat().st_size,
            }
