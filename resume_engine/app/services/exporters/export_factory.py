"""Factory for selecting the appropriate exporter by format string."""

from app.core.exceptions import ExportException
from app.core.logging import LoggerFactory
from app.services.exporters.base import BaseExporter
from app.services.exporters.docx_exporter import DOCXExporter
from app.services.exporters.pdf_exporter import PDFExporter
from app.services.templates.template_engine import TemplateEngine

logger = LoggerFactory.get_logger(__name__)


class ExportFactory:
    """Registry-based factory for document exporter instances.

    Maintains a mapping of format strings to exporter instances.
    Exporters are registered once and reused for all subsequent export requests.
    Pre-registers PDF and DOCX exporters on initialization.

    Usage:
        factory = ExportFactory(template_engine)
        exporter = factory.get_exporter("pdf")
        path = await exporter.export(resume_data, "modern_clean", output_path)
    """

    def __init__(self, template_engine: TemplateEngine) -> None:
        self._registry: dict[str, BaseExporter] = {}
        self._template_engine = template_engine
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register the built-in PDF and DOCX exporters."""
        self._registry["pdf"] = PDFExporter(self._template_engine)
        self._registry["docx"] = DOCXExporter()
        logger.debug("Registered default exporters", formats=list(self._registry.keys()))

    def register(self, format_string: str, exporter: BaseExporter) -> None:
        """Register a custom exporter for a given format string.

        Args:
            format_string: Lowercase format identifier, e.g. 'pdf' or 'docx'.
            exporter: An instantiated exporter object to register.
        """
        self._registry[format_string.lower()] = exporter
        logger.info("Registered custom exporter", format=format_string)

    def get_exporter(self, format_string: str) -> BaseExporter:
        """Return the appropriate exporter for the given format string.

        Args:
            format_string: Lowercase format identifier to look up.

        Returns:
            A BaseExporter instance for the given format.

        Raises:
            ExportException: If no exporter is registered for the format.
        """
        fmt = format_string.lower()
        exporter = self._registry.get(fmt)
        if exporter is None:
            supported = list(self._registry.keys())
            raise ExportException(
                f"Unsupported export format '{fmt}'. Supported formats: {supported}",
                details={"format": fmt, "supported_formats": supported},
            )
        return exporter

    def supported_formats(self) -> list[str]:
        """Return all registered format strings.

        Returns:
            List of lowercase format strings.
        """
        return list(self._registry.keys())
