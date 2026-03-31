"""DOCX document parser using python-docx."""

import asyncio
from functools import partial
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

from app.core.exceptions import DocumentParseException
from app.core.logging import LoggerFactory
from app.services.parsers.base import BaseDocumentParser

logger = LoggerFactory.get_logger(__name__)


class DOCXParser(BaseDocumentParser):
    """Parser for DOCX resume documents using python-docx.

    Extracts text from paragraphs, tables, headers, and footers while
    preserving document section structure. All synchronous python-docx
    operations are wrapped in a thread pool executor for async compatibility.
    """

    def supported_extensions(self) -> list[str]:
        """Return supported file extensions."""
        return ["docx"]

    async def parse(self, file_path: Path) -> str:
        """Parse a DOCX file and return structured plain text.

        Args:
            file_path: Absolute path to the DOCX file.

        Returns:
            Plain text content with section structure preserved.

        Raises:
            DocumentParseException: If the document cannot be opened or read.
        """
        loop = asyncio.get_event_loop()
        try:
            text = await loop.run_in_executor(None, partial(self._extract_text, file_path))
        except DocumentParseException:
            raise
        except Exception as exc:
            logger.error("DOCX parsing failed", file=str(file_path), error=str(exc))
            raise DocumentParseException(
                f"Failed to parse DOCX: {exc}",
                details={"file_path": str(file_path)},
            ) from exc
        return text

    def _extract_text(self, file_path: Path) -> str:
        """Synchronous DOCX text extraction (called in executor).

        Iterates over document body elements in document order,
        preserving section headers and table cell text.

        Args:
            file_path: Path to the DOCX file.

        Returns:
            Structured plain text content.

        Raises:
            DocumentParseException: If the file doesn't exist or is corrupt.
        """
        if not file_path.exists():
            raise DocumentParseException(
                f"DOCX file not found: {file_path}",
                details={"file_path": str(file_path)},
            )

        try:
            doc = Document(str(file_path))
        except Exception as exc:
            raise DocumentParseException(
                f"DOCX file is corrupt or invalid: {exc}",
                details={"file_path": str(file_path)},
            ) from exc

        text_parts: list[str] = []

        # Iterate over document body elements in order (paragraphs and tables)
        for element in doc.element.body:
            tag = element.tag.split("}")[-1] if "}" in element.tag else element.tag

            if tag == "p":
                para = Paragraph(element, doc)
                para_text = para.text.strip()
                if para_text:
                    # Prefix headers with a marker to help AI identify sections
                    if para.style.name.startswith("Heading"):
                        text_parts.append(f"\n### {para_text} ###")
                    else:
                        text_parts.append(para_text)

            elif tag == "tbl":
                table = Table(element, doc)
                table_text = self._extract_table_text(table)
                if table_text:
                    text_parts.append(table_text)

        return "\n".join(text_parts).strip()

    def _extract_table_text(self, table: Table) -> str:
        """Extract text from a table, row by row.

        Args:
            table: A python-docx Table object.

        Returns:
            Tab-separated cell content with newlines between rows.
        """
        rows: list[str] = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                rows.append(" | ".join(cells))
        return "\n".join(rows)

    async def extract_metadata(self, file_path: Path) -> dict:
        """Extract core properties metadata from a DOCX file.

        Args:
            file_path: Absolute path to the DOCX file.

        Returns:
            Dictionary with keys: title, author, created, modified,
            paragraph_count, table_count, file_size_bytes.

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
                f"Failed to extract DOCX metadata: {exc}",
                details={"file_path": str(file_path)},
            ) from exc
        return metadata

    def _extract_metadata_sync(self, file_path: Path) -> dict:
        """Synchronous metadata extraction (called in executor)."""
        if not file_path.exists():
            raise DocumentParseException(
                f"DOCX file not found: {file_path}",
                details={"file_path": str(file_path)},
            )

        doc = Document(str(file_path))
        props = doc.core_properties

        return {
            "title": props.title or "",
            "author": props.author or "",
            "created": str(props.created) if props.created else "",
            "modified": str(props.modified) if props.modified else "",
            "paragraph_count": len(doc.paragraphs),
            "table_count": len(doc.tables),
            "file_size_bytes": file_path.stat().st_size,
        }
