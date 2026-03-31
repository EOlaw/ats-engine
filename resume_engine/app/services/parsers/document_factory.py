"""Factory for selecting the appropriate document parser by file extension."""

from pathlib import Path
from typing import ClassVar

from app.core.exceptions import DocumentParseException
from app.core.logging import LoggerFactory
from app.services.parsers.base import BaseDocumentParser
from app.services.parsers.docx_parser import DOCXParser
from app.services.parsers.pdf_parser import PDFParser

logger = LoggerFactory.get_logger(__name__)


class DocumentParserFactory:
    """Registry-based factory for document parser instances.

    Maintains a mapping of file extensions to parser instances.
    Parsers are registered once and reused for all subsequent parse requests.
    Pre-registers PDF and DOCX parsers on initialization.

    Usage:
        factory = DocumentParserFactory()
        parser = factory.get_parser(Path("resume.pdf"))
        text = await parser.parse(Path("resume.pdf"))
    """

    _default_parsers: ClassVar[dict[str, type[BaseDocumentParser]]] = {
        "pdf": PDFParser,
        "docx": DOCXParser,
    }

    def __init__(self) -> None:
        self._registry: dict[str, BaseDocumentParser] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the built-in PDF and DOCX parsers."""
        for ext, parser_class in self._default_parsers.items():
            instance = parser_class()
            self._registry[ext.lower()] = instance
            logger.debug("Registered parser", extension=ext, parser=parser_class.__name__)

    def register(self, extension: str, parser_class: type[BaseDocumentParser]) -> None:
        """Register a new parser for a given file extension.

        If a parser is already registered for the extension, it is replaced.

        Args:
            extension: Lowercase file extension without leading dot (e.g., 'pdf').
            parser_class: The parser class to instantiate and register.
        """
        ext = extension.lower().lstrip(".")
        instance = parser_class()
        self._registry[ext] = instance
        logger.info("Registered custom parser", extension=ext, parser=parser_class.__name__)

    def get_parser(self, file_path: Path) -> BaseDocumentParser:
        """Return the appropriate parser for the given file path.

        Args:
            file_path: Path to the document file. The extension is used
                to select the parser.

        Returns:
            A BaseDocumentParser instance for the file's extension.

        Raises:
            DocumentParseException: If no parser is registered for the
                file's extension.
        """
        ext = file_path.suffix.lower().lstrip(".")
        if not ext:
            raise DocumentParseException(
                f"File has no extension: {file_path.name}",
                details={"filename": file_path.name},
            )

        parser = self._registry.get(ext)
        if parser is None:
            supported = list(self._registry.keys())
            raise DocumentParseException(
                f"Unsupported file type '.{ext}'. Supported types: {supported}",
                details={"extension": ext, "supported_extensions": supported},
            )

        return parser

    def supported_extensions(self) -> list[str]:
        """Return all registered file extensions.

        Returns:
            List of lowercase extension strings without leading dots.
        """
        return list(self._registry.keys())

    def is_supported(self, file_path: Path) -> bool:
        """Check if a file's extension has a registered parser.

        Args:
            file_path: Path to check.

        Returns:
            True if the extension is supported, False otherwise.
        """
        ext = file_path.suffix.lower().lstrip(".")
        return ext in self._registry
