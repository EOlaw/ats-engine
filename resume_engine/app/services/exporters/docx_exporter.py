"""DOCX resume exporter using python-docx."""

import asyncio
from functools import partial
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from app.core.exceptions import ExportException
from app.core.logging import LoggerFactory
from app.services.exporters.base import BaseExporter

logger = LoggerFactory.get_logger(__name__)


class DOCXExporter(BaseExporter):
    """Exports resumes to DOCX format using python-docx.

    Builds a properly formatted Word document with styled headings,
    consistent fonts, bullet points, and professional section ordering.
    All operations are wrapped in a thread executor for async compatibility.
    """

    def supported_format(self) -> str:
        """Return the format string for DOCX exports."""
        return "docx"

    async def export(
        self,
        resume_data: dict[str, Any],
        template_name: str,
        output_path: Path,
    ) -> Path:
        """Export resume data to a DOCX file.

        Args:
            resume_data: Structured resume data dictionary.
            template_name: Name of the template (used for color scheme selection).
            output_path: Path where the DOCX file should be written.

        Returns:
            Path to the created DOCX file.

        Raises:
            ExportException: If document building or writing fails.
        """
        logger.info("Starting DOCX export", template=template_name, output=str(output_path))

        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                partial(self._build_document, resume_data, template_name, output_path),
            )
        except ExportException:
            raise
        except Exception as exc:
            raise ExportException(
                f"DOCX export failed: {exc}",
                details={"output_path": str(output_path), "template": template_name},
            ) from exc

        logger.info("DOCX export completed", path=str(output_path))
        return output_path

    def _build_document(
        self,
        resume_data: dict[str, Any],
        template_name: str,
        output_path: Path,
    ) -> None:
        """Build and save the DOCX document (runs in executor).

        Args:
            resume_data: Resume data dictionary.
            template_name: Template name for style selection.
            output_path: Destination file path.
        """
        doc = Document()
        self._configure_document(doc)

        personal_info = resume_data.get("personal_info", {})
        self._add_header(doc, personal_info)

        # Professional summary
        summary = (
            resume_data.get("optimized_content", {}).get("professional_summary")
            or personal_info.get("summary")
        )
        if summary:
            self._add_section_heading(doc, "PROFESSIONAL SUMMARY")
            doc.add_paragraph(summary)

        # Work experience
        work_experience = (
            resume_data.get("optimized_content", {}).get("work_experience")
            or resume_data.get("work_experience", [])
        )
        if work_experience:
            self._add_section_heading(doc, "EXPERIENCE")
            for job in work_experience:
                self._add_work_experience(doc, job)

        # Education
        education = resume_data.get("education", [])
        if education:
            self._add_section_heading(doc, "EDUCATION")
            for edu in education:
                self._add_education(doc, edu)

        # Skills
        skills_grouping = (
            resume_data.get("optimized_content", {}).get("skills_grouping")
            or self._flatten_skills(resume_data.get("skills", {}))
        )
        if skills_grouping:
            self._add_section_heading(doc, "SKILLS")
            self._add_skills(doc, skills_grouping)

        # Certifications
        certifications = resume_data.get("certifications", [])
        if certifications:
            self._add_section_heading(doc, "CERTIFICATIONS")
            for cert in certifications:
                self._add_certification(doc, cert)

        # Projects
        projects = resume_data.get("projects", [])
        if projects:
            self._add_section_heading(doc, "PROJECTS")
            for project in projects:
                self._add_project(doc, project)

        try:
            doc.save(str(output_path))
        except Exception as exc:
            raise ExportException(f"Failed to save DOCX file: {exc}") from exc

    def _configure_document(self, doc: Document) -> None:
        """Set document-level page margins and default styles."""
        section = doc.sections[0]
        section.page_width = Inches(8.5)
        section.page_height = Inches(11)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)

        # Set default paragraph font
        normal_style = doc.styles["Normal"]
        normal_style.font.name = "Calibri"
        normal_style.font.size = Pt(10)

    def _add_header(self, doc: Document, personal_info: dict[str, Any]) -> None:
        """Add the candidate name and contact info header."""
        name = personal_info.get("full_name", "")
        if name:
            name_para = doc.add_paragraph()
            name_run = name_para.add_run(name.upper())
            name_run.bold = True
            name_run.font.size = Pt(18)
            name_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            name_para.space_after = Pt(2)

        contact_parts = []
        for field in ["email", "phone", "location", "linkedin_url"]:
            value = personal_info.get(field)
            if value:
                contact_parts.append(value)

        if contact_parts:
            contact_para = doc.add_paragraph(" | ".join(contact_parts))
            contact_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in contact_para.runs:
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0x44, 0x44, 0x44)
            contact_para.space_after = Pt(6)

    def _add_section_heading(self, doc: Document, title: str) -> None:
        """Add a styled section heading with a horizontal rule effect."""
        heading = doc.add_paragraph()
        run = heading.add_run(title)
        run.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x1a, 0x1a, 0x1a)

        # Add bottom border to simulate rule under heading
        pPr = heading._p.get_or_add_pPr()
        pBdr = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "6")
        bottom.set(qn("w:space"), "1")
        bottom.set(qn("w:color"), "333333")
        pBdr.append(bottom)
        pPr.append(pBdr)

        heading.space_before = Pt(8)
        heading.space_after = Pt(3)

    def _add_work_experience(self, doc: Document, job: dict[str, Any]) -> None:
        """Add a single work experience entry."""
        title = job.get("title", "") or job.get("optimized_title", "")
        company = job.get("company", "")
        start = job.get("start_date", "")
        end = job.get("end_date", "Present") if job.get("is_current") else job.get("end_date", "")

        # Title and company on one line, dates right-aligned
        header_para = doc.add_paragraph()
        title_run = header_para.add_run(f"{title}")
        title_run.bold = True
        title_run.font.size = Pt(10)

        if company:
            header_para.add_run(f" — {company}")

        if start or end:
            date_str = f"{start} – {end}" if end else start
            tab_run = header_para.add_run(f"\t{date_str}")
            tab_run.font.size = Pt(9)
            tab_run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

        # Bullet points
        bullets = job.get("bullets", []) or job.get("optimized_bullets", [])
        for bullet in bullets:
            if bullet:
                bullet_para = doc.add_paragraph(style="List Bullet")
                bullet_para.add_run(bullet)
                bullet_para.paragraph_format.left_indent = Inches(0.25)

    def _add_education(self, doc: Document, edu: dict[str, Any]) -> None:
        """Add a single education entry."""
        institution = edu.get("institution", "")
        degree = edu.get("degree", "")
        field = edu.get("field_of_study", "")
        end_date = edu.get("end_date", "")

        degree_str = f"{degree} in {field}" if degree and field else degree or field

        header_para = doc.add_paragraph()
        inst_run = header_para.add_run(institution)
        inst_run.bold = True
        if end_date:
            header_para.add_run(f"\t{end_date}").font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        if degree_str:
            doc.add_paragraph(degree_str)
        if edu.get("gpa"):
            doc.add_paragraph(f"GPA: {edu['gpa']}")
        for honor in edu.get("honors", []):
            doc.add_paragraph(honor, style="List Bullet")

    def _add_skills(self, doc: Document, skills: dict[str, Any]) -> None:
        """Add skills section organized by category."""
        for category, skill_list in skills.items():
            if skill_list:
                skill_str = ", ".join(str(s) for s in skill_list)
                para = doc.add_paragraph()
                para.add_run(f"{category.replace('_', ' ').title()}: ").bold = True
                para.add_run(skill_str)

    def _add_certification(self, doc: Document, cert: dict[str, Any]) -> None:
        """Add a single certification entry."""
        name = cert.get("name", "")
        issuer = cert.get("issuer", "")
        date = cert.get("date_earned", "")
        text = name
        if issuer:
            text += f" — {issuer}"
        if date:
            text += f" ({date})"
        doc.add_paragraph(text, style="List Bullet")

    def _add_project(self, doc: Document, project: dict[str, Any]) -> None:
        """Add a single project entry."""
        name = project.get("name", "")
        description = project.get("description", "")
        technologies = project.get("technologies", [])

        header_para = doc.add_paragraph()
        if name:
            header_para.add_run(name).bold = True
        if description:
            doc.add_paragraph(description)
        if technologies:
            doc.add_paragraph(f"Technologies: {', '.join(technologies)}")
        for highlight in project.get("highlights", []):
            doc.add_paragraph(highlight, style="List Bullet")

    def _flatten_skills(self, skills: dict[str, Any]) -> dict[str, list[str]]:
        """Convert a Skills schema dict to a simple category -> list mapping."""
        result: dict[str, list[str]] = {}
        for key, value in skills.items():
            if isinstance(value, list) and value:
                result[key] = [str(v) for v in value]
        return result
