"""Abstract base class for document parsers."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseDocumentParser(ABC):
    """Abstract interface for all document parsers.

    Every parser implementation must support async parsing to raw text,
    report which file extensions it handles, and extract document metadata.
    Implementations wrap synchronous libraries in thread executors to
    maintain a fully async interface.
    """

    @abstractmethod
    async def parse(self, file_path: Path) -> str:
        """Parse a document and return its full text content.

        Args:
            file_path: Absolute path to the document file.

        Returns:
            The extracted plain text content of the document.

        Raises:
            DocumentParseException: If the document cannot be parsed.
        """
        ...

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """Return the list of file extensions this parser supports.

        Returns:
            A list of lowercase extension strings without leading dots,
            e.g. ['pdf'] or ['docx', 'doc'].
        """
        ...

    @abstractmethod
    async def extract_metadata(self, file_path: Path) -> dict:
        """Extract metadata from a document without full text parsing.

        Args:
            file_path: Absolute path to the document file.

        Returns:
            A dictionary of metadata fields. Common keys include:
            'page_count', 'title', 'author', 'created_date', 'file_size'.

        Raises:
            DocumentParseException: If metadata extraction fails.
        """
        ...
