"""Abstract base class for resume document exporters."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseExporter(ABC):
    """Abstract interface for all resume exporters.

    Each exporter converts a structured resume data dictionary and a
    template into a specific output file format (PDF, DOCX, etc.).
    All operations must be async to maintain a non-blocking API.
    """

    @abstractmethod
    async def export(
        self,
        resume_data: dict[str, Any],
        template_name: str,
        output_path: Path,
    ) -> Path:
        """Export resume data to a file using the specified template.

        Args:
            resume_data: Structured resume data dictionary. May contain
                optimized content, tailored content, or base extraction data.
            template_name: Name of the template to use for rendering.
            output_path: Absolute path where the exported file should be saved.
                The file extension must match the exporter's supported format.

        Returns:
            The absolute path of the successfully written output file.

        Raises:
            ExportException: If rendering or file writing fails.
        """
        ...

    @abstractmethod
    def supported_format(self) -> str:
        """Return the file format string this exporter produces.

        Returns:
            Lowercase format string, e.g. 'pdf' or 'docx'.
        """
        ...
