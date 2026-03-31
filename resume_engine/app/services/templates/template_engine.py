"""Template engine for rendering resume data to HTML and plain text."""

from typing import Any

from app.core.exceptions import ExportException
from app.core.logging import LoggerFactory
from app.services.templates.template_registry import TemplateConfig, TemplateRegistry

logger = LoggerFactory.get_logger(__name__)


class TemplateEngine:
    """Renders resume data into HTML and plain text using template configurations.

    Uses the TemplateRegistry to look up template styles and applies
    them when generating HTML output for PDF rendering or plain text
    for ATS submission. Pure Python string-based rendering without
    external template dependencies to avoid unnecessary complexity.

    Attributes:
        _registry: The template configuration registry.
    """

    def __init__(self, registry: TemplateRegistry) -> None:
        self._registry = registry

    def render_html(self, resume_data: dict[str, Any], template_name: str) -> str:
        """Render resume data as a complete HTML document.

        Args:
            resume_data: Structured resume data dictionary. May include
                personal_info, work_experience, skills, education, etc.
                as well as optimized_content overrides.
            template_name: Name of the visual template to apply.

        Returns:
            A complete HTML document string ready for WeasyPrint.

        Raises:
            ExportException: If the template is not found or rendering fails.
        """
        try:
            config = self._registry.get(template_name)
        except Exception as exc:
            raise ExportException(f"Template '{template_name}' not found") from exc

        try:
            sections_html = self._render_sections(resume_data, config)
            return self._wrap_html(sections_html, config)
        except ExportException:
            raise
        except Exception as exc:
            raise ExportException(
                f"HTML rendering failed: {exc}",
                details={"template": template_name},
            ) from exc

    def render_text(self, resume_data: dict[str, Any], template_name: str) -> str:
        """Render resume data as plain text for ATS submission.

        Produces a clean plain-text version of the resume with consistent
        section headers and minimal formatting artifacts.

        Args:
            resume_data: Structured resume data dictionary.
            template_name: Template name (used for section ordering).

        Returns:
            Plain text representation of the resume.

        Raises:
            ExportException: If the template is not found.
        """
        try:
            config = self._registry.get(template_name)
        except Exception as exc:
            raise ExportException(f"Template '{template_name}' not found") from exc

        parts: list[str] = []
        personal = resume_data.get("personal_info", {})

        if personal.get("full_name"):
            parts.append(personal["full_name"].upper())

        contact = " | ".join(
            filter(None, [
                personal.get("email"),
                personal.get("phone"),
                personal.get("location"),
                personal.get("linkedin_url"),
            ])
        )
        if contact:
            parts.append(contact)
        parts.append("")

        summary = (
            resume_data.get("optimized_content", {}).get("professional_summary")
            or personal.get("summary")
        )
        if summary:
            parts.extend(["PROFESSIONAL SUMMARY", "-" * 40, summary, ""])

        work_exp = (
            resume_data.get("optimized_content", {}).get("work_experience")
            or resume_data.get("work_experience", [])
        )
        if work_exp:
            parts.append("EXPERIENCE")
            parts.append("-" * 40)
            for job in work_exp:
                title = job.get("title", "")
                company = job.get("company", "")
                start = job.get("start_date", "")
                end = job.get("end_date", "Present") if job.get("is_current") else job.get("end_date", "")
                date_str = f"{start} - {end}" if start else end
                parts.append(f"{title} | {company} | {date_str}".strip(" |"))
                for bullet in job.get("bullets", []) or job.get("optimized_bullets", []):
                    parts.append(f"  * {bullet}")
                parts.append("")

        education = resume_data.get("education", [])
        if education:
            parts.append("EDUCATION")
            parts.append("-" * 40)
            for edu in education:
                inst = edu.get("institution", "")
                degree = edu.get("degree", "")
                field = edu.get("field_of_study", "")
                end_date = edu.get("end_date", "")
                parts.append(f"{inst} | {degree} {field} | {end_date}".strip(" |"))
            parts.append("")

        skills = (
            resume_data.get("optimized_content", {}).get("skills_grouping")
            or {}
        )
        if not skills:
            raw_skills = resume_data.get("skills", {})
            for key, val in raw_skills.items():
                if isinstance(val, list) and val:
                    skills[key] = val

        if skills:
            parts.append("SKILLS")
            parts.append("-" * 40)
            for category, skill_list in skills.items():
                if skill_list:
                    parts.append(f"{category.replace('_', ' ').title()}: {', '.join(str(s) for s in skill_list)}")
            parts.append("")

        return "\n".join(parts)

    def _render_sections(
        self, resume_data: dict[str, Any], config: TemplateConfig
    ) -> str:
        """Render all resume sections as HTML fragments.

        Args:
            resume_data: Resume data dictionary.
            config: Template configuration.

        Returns:
            Concatenated HTML for all non-empty sections.
        """
        html_parts: list[str] = []

        personal = resume_data.get("personal_info", {})
        html_parts.append(self._render_header_html(personal, config))

        summary = (
            resume_data.get("optimized_content", {}).get("professional_summary")
            or personal.get("summary")
        )
        if summary:
            html_parts.append(self._render_summary_html(summary))

        work_exp = (
            resume_data.get("optimized_content", {}).get("work_experience")
            or resume_data.get("work_experience", [])
        )
        if work_exp:
            html_parts.append(self._render_experience_html(work_exp, config))

        education = resume_data.get("education", [])
        if education:
            html_parts.append(self._render_education_html(education, config))

        skills = (
            resume_data.get("optimized_content", {}).get("skills_grouping")
            or self._extract_skills_dict(resume_data.get("skills", {}))
        )
        if skills:
            html_parts.append(self._render_skills_html(skills, config))

        certs = resume_data.get("certifications", [])
        if certs:
            html_parts.append(self._render_certifications_html(certs, config))

        projects = resume_data.get("projects", [])
        if projects:
            html_parts.append(self._render_projects_html(projects, config))

        return "\n".join(html_parts)

    def _wrap_html(self, body: str, config: TemplateConfig) -> str:
        """Wrap rendered section HTML in a full HTML document with inline styles."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body {{
    font-family: {config.font_family}, Arial, sans-serif;
    font-size: {config.font_size}pt;
    color: #1a1a1a;
    line-height: 1.4;
    margin: 0;
    padding: 0;
  }}
  h1 {{ font-size: 18pt; margin: 0 0 2pt 0; color: {config.accent_color}; }}
  h2 {{
    font-size: 11pt;
    margin: 8pt 0 3pt 0;
    color: {config.accent_color};
    border-bottom: 1pt solid {config.accent_color};
    padding-bottom: 1pt;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
  }}
  h3 {{ font-size: 10pt; font-weight: bold; margin: 4pt 0 1pt 0; }}
  .contact {{ font-size: 9pt; color: #555; margin-bottom: 6pt; }}
  .date {{ font-size: 9pt; color: #666; float: right; }}
  .company {{ font-style: italic; font-size: 10pt; }}
  ul {{ margin: 2pt 0; padding-left: 14pt; }}
  li {{ margin-bottom: 1pt; }}
  .section {{ margin-bottom: 8pt; overflow: hidden; }}
  .skill-category {{ margin-bottom: 2pt; }}
  .skill-label {{ font-weight: bold; }}
</style>
</head>
<body>
{body}
</body>
</html>"""

    def _render_header_html(self, personal: dict[str, Any], config: TemplateConfig) -> str:
        name = personal.get("full_name", "")
        contact_parts = filter(None, [
            personal.get("email"),
            personal.get("phone"),
            personal.get("location"),
            personal.get("linkedin_url"),
            personal.get("github_url"),
        ])
        contact_str = " &nbsp;|&nbsp; ".join(contact_parts)
        return f"""<div style="text-align:center; margin-bottom:8pt;">
  <h1>{name}</h1>
  <div class="contact">{contact_str}</div>
</div>"""

    def _render_summary_html(self, summary: str) -> str:
        return f"""<div class="section">
  <h2>Professional Summary</h2>
  <p>{summary}</p>
</div>"""

    def _render_experience_html(
        self, work_exp: list[dict[str, Any]], config: TemplateConfig
    ) -> str:
        items = []
        for job in work_exp:
            title = job.get("title", "")
            company = job.get("company", "")
            start = job.get("start_date", "")
            end = (
                "Present"
                if job.get("is_current")
                else job.get("end_date", "")
            )
            date_str = f"{start} – {end}" if start else end
            bullets = job.get("bullets", []) or job.get("optimized_bullets", [])
            bullets_html = "".join(f"<li>{b}</li>" for b in bullets if b)
            items.append(f"""<div style="margin-bottom:6pt;">
  <div class="clearfix">
    <h3 style="display:inline;">{title}</h3>
    <span class="date">{date_str}</span>
  </div>
  <div class="company">{company}</div>
  <ul>{bullets_html}</ul>
</div>""")
        return f'<div class="section"><h2>Experience</h2>{"".join(items)}</div>'

    def _render_education_html(
        self, education: list[dict[str, Any]], config: TemplateConfig
    ) -> str:
        items = []
        for edu in education:
            inst = edu.get("institution", "")
            degree = edu.get("degree", "")
            field = edu.get("field_of_study", "")
            end_date = edu.get("end_date", "")
            degree_str = f"{degree} in {field}" if degree and field else degree or field
            items.append(f"""<div style="margin-bottom:4pt;">
  <div class="clearfix">
    <h3 style="display:inline;">{inst}</h3>
    <span class="date">{end_date}</span>
  </div>
  <div>{degree_str}</div>
</div>""")
        return f'<div class="section"><h2>Education</h2>{"".join(items)}</div>'

    def _render_skills_html(
        self, skills: dict[str, Any], config: TemplateConfig
    ) -> str:
        rows = []
        for category, skill_list in skills.items():
            if skill_list:
                label = category.replace("_", " ").title()
                skill_str = ", ".join(str(s) for s in skill_list)
                rows.append(
                    f'<div class="skill-category">'
                    f'<span class="skill-label">{label}:</span> {skill_str}'
                    f"</div>"
                )
        return f'<div class="section"><h2>Skills</h2>{"".join(rows)}</div>'

    def _render_certifications_html(
        self, certs: list[dict[str, Any]], config: TemplateConfig
    ) -> str:
        items = []
        for cert in certs:
            name = cert.get("name", "")
            issuer = cert.get("issuer", "")
            date = cert.get("date_earned", "")
            text = f"{name}"
            if issuer:
                text += f" — {issuer}"
            if date:
                text += f" ({date})"
            items.append(f"<li>{text}</li>")
        return f'<div class="section"><h2>Certifications</h2><ul>{"".join(items)}</ul></div>'

    def _render_projects_html(
        self, projects: list[dict[str, Any]], config: TemplateConfig
    ) -> str:
        items = []
        for project in projects:
            name = project.get("name", "")
            description = project.get("description", "")
            technologies = ", ".join(project.get("technologies", []))
            highlights = "".join(
                f"<li>{h}</li>" for h in project.get("highlights", [])
            )
            tech_str = f"<div><em>Technologies: {technologies}</em></div>" if technologies else ""
            items.append(f"""<div style="margin-bottom:4pt;">
  <h3>{name}</h3>
  <div>{description}</div>
  {tech_str}
  <ul>{highlights}</ul>
</div>""")
        return f'<div class="section"><h2>Projects</h2>{"".join(items)}</div>'

    def _extract_skills_dict(self, skills: dict[str, Any]) -> dict[str, list[str]]:
        """Convert skills schema dict to simple category -> list mapping."""
        result: dict[str, list[str]] = {}
        for key, value in skills.items():
            if isinstance(value, list) and value:
                result[key] = [str(v) for v in value]
        return result
