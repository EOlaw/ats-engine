"""PDF resume exporter using WeasyPrint."""

import asyncio
from functools import partial
from pathlib import Path
from typing import Any

from weasyprint import CSS, HTML

from app.core.exceptions import ExportException
from app.core.logging import LoggerFactory
from app.services.exporters.base import BaseExporter
from app.services.templates.template_engine import TemplateEngine
from app.services.templates.template_registry import TemplateRegistry

logger = LoggerFactory.get_logger(__name__)


class PDFExporter(BaseExporter):
    """Exports resumes to PDF using WeasyPrint HTML-to-PDF rendering.

    Renders the resume data as HTML using the TemplateEngine, then converts
    the HTML to PDF using WeasyPrint. WeasyPrint is synchronous so the
    conversion is offloaded to a thread pool executor.

    Attributes:
        _template_engine: Engine for rendering HTML from resume data and template.
    """

    def __init__(self, template_engine: TemplateEngine) -> None:
        self._template_engine = template_engine

    def supported_format(self) -> str:
        """Return the format string for PDF exports."""
        return "pdf"

    async def export(
        self,
        resume_data: dict[str, Any],
        template_name: str,
        output_path: Path,
    ) -> Path:
        """Export resume data to a PDF file.

        Renders the HTML template and then converts it to PDF using WeasyPrint.
        The conversion is run in a thread executor to avoid blocking the event loop.

        Args:
            resume_data: Structured resume data dictionary.
            template_name: Name of the visual template to use.
            output_path: Path where the PDF file should be written.

        Returns:
            Path to the created PDF file.

        Raises:
            ExportException: If HTML rendering or PDF conversion fails.
        """
        logger.info("Starting PDF export", template=template_name, output=str(output_path))

        try:
            html_content = self._template_engine.render_html(resume_data, template_name)
        except Exception as exc:
            raise ExportException(
                f"HTML rendering failed for PDF export: {exc}",
                details={"template": template_name},
            ) from exc

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                partial(self._render_pdf, html_content, output_path),
            )
        except ExportException:
            raise
        except Exception as exc:
            raise ExportException(
                f"WeasyPrint PDF conversion failed: {exc}",
                details={"output_path": str(output_path)},
            ) from exc

        logger.info("PDF export completed", path=str(output_path))
        return output_path

    def _render_pdf(self, html_content: str, output_path: Path) -> None:
        """Synchronous WeasyPrint rendering (called in executor).

        Args:
            html_content: Full HTML string to render.
            output_path: Destination path for the PDF file.

        Raises:
            ExportException: If WeasyPrint raises any error.
        """
        try:
            base_css = CSS(string=self._get_base_css())
            html = HTML(string=html_content)
            html.write_pdf(
                str(output_path),
                stylesheets=[base_css],
                presentational_hints=True,
            )
        except Exception as exc:
            raise ExportException(f"PDF rendering error: {exc}") from exc

    def _get_base_css(self) -> str:
        """Return base CSS for PDF rendering.

        Provides page size, margins, and font setup for WeasyPrint.

        Returns:
            CSS string for WeasyPrint.
        """
        return """
            @page {
                size: Letter;
                margin: 0.75in 0.75in 0.75in 0.75in;
            }
            body {
                font-family: Arial, Helvetica, sans-serif;
                font-size: 10pt;
                line-height: 1.4;
                color: #1a1a1a;
            }
            h1 { font-size: 18pt; margin-bottom: 2pt; }
            h2 { font-size: 12pt; margin-top: 8pt; margin-bottom: 3pt; border-bottom: 1pt solid #333; }
            h3 { font-size: 10pt; font-weight: bold; margin-top: 4pt; margin-bottom: 1pt; }
            ul { margin: 2pt 0; padding-left: 14pt; }
            li { margin-bottom: 1pt; }
            .contact-info { font-size: 9pt; color: #444; }
            .date-range { font-size: 9pt; color: #555; float: right; }
            .section { margin-bottom: 8pt; }
            .clearfix::after { content: ""; display: table; clear: both; }
        """
