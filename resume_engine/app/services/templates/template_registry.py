"""Template registry for resume visual templates."""

from dataclasses import dataclass, field

from app.core.exceptions import ResourceNotFoundException
from app.core.logging import LoggerFactory

logger = LoggerFactory.get_logger(__name__)


@dataclass
class TemplateConfig:
    """Configuration dataclass for a single resume template.

    Attributes:
        name: Unique template identifier slug.
        style: Human-readable style description.
        section_order: Ordered list of section keys to render.
        font_family: Primary font family name.
        font_size: Base font size in points.
        accent_color: Hex color string for headings and accents.
        column_layout: Layout style: 'single' or 'two_column'.
    """

    name: str
    style: str
    section_order: list[str] = field(default_factory=list)
    font_family: str = "Arial"
    font_size: int = 10
    accent_color: str = "#1a1a1a"
    column_layout: str = "single"


class TemplateRegistry:
    """Registry of available resume templates.

    Stores TemplateConfig instances by name. Provides registration,
    lookup, and enumeration operations. Pre-registers all 6 built-in
    resume templates on initialization.
    """

    _STANDARD_SECTION_ORDER = [
        "personal_info",
        "professional_summary",
        "work_experience",
        "education",
        "skills",
        "certifications",
        "projects",
    ]

    def __init__(self) -> None:
        self._registry: dict[str, TemplateConfig] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register all 6 built-in resume templates."""
        templates = [
            TemplateConfig(
                name="modern_clean",
                style="Modern Clean — minimalist with subtle color accents",
                section_order=self._STANDARD_SECTION_ORDER,
                font_family="Calibri",
                font_size=10,
                accent_color="#2563EB",
                column_layout="single",
            ),
            TemplateConfig(
                name="executive_classic",
                style="Executive Classic — traditional serif layout for senior roles",
                section_order=[
                    "personal_info",
                    "professional_summary",
                    "work_experience",
                    "education",
                    "certifications",
                    "skills",
                    "projects",
                ],
                font_family="Georgia",
                font_size=11,
                accent_color="#1a1a1a",
                column_layout="single",
            ),
            TemplateConfig(
                name="tech_minimal",
                style="Tech Minimal — clean sans-serif optimized for tech roles",
                section_order=[
                    "personal_info",
                    "skills",
                    "work_experience",
                    "projects",
                    "education",
                    "certifications",
                ],
                font_family="Inter",
                font_size=10,
                accent_color="#0F172A",
                column_layout="single",
            ),
            TemplateConfig(
                name="creative_bold",
                style="Creative Bold — two-column layout with bold typographic hierarchy",
                section_order=[
                    "personal_info",
                    "professional_summary",
                    "skills",
                    "work_experience",
                    "projects",
                    "education",
                    "certifications",
                ],
                font_family="Montserrat",
                font_size=10,
                accent_color="#7C3AED",
                column_layout="two_column",
            ),
            TemplateConfig(
                name="ats_optimized",
                style="ATS Optimized — plain single-column layout maximizing ATS parse rate",
                section_order=self._STANDARD_SECTION_ORDER,
                font_family="Arial",
                font_size=11,
                accent_color="#1a1a1a",
                column_layout="single",
            ),
            TemplateConfig(
                name="academic",
                style="Academic CV — comprehensive layout for academic and research positions",
                section_order=[
                    "personal_info",
                    "professional_summary",
                    "education",
                    "work_experience",
                    "projects",
                    "certifications",
                    "skills",
                    "awards",
                    "publications",
                ],
                font_family="Times New Roman",
                font_size=11,
                accent_color="#1a1a1a",
                column_layout="single",
            ),
        ]

        for template in templates:
            self._registry[template.name] = template
            logger.debug("Registered template", name=template.name)

    def register(self, config: TemplateConfig) -> None:
        """Register a new template or replace an existing one.

        Args:
            config: The TemplateConfig dataclass to register.
        """
        self._registry[config.name] = config
        logger.info("Registered custom template", name=config.name)

    def get(self, name: str) -> TemplateConfig:
        """Retrieve a template by name.

        Args:
            name: The template name slug.

        Returns:
            The TemplateConfig for the given name.

        Raises:
            ResourceNotFoundException: If no template with the given name exists.
        """
        config = self._registry.get(name)
        if config is None:
            raise ResourceNotFoundException(
                resource_type="Template",
                resource_id=name,
                details={"available_templates": list(self._registry.keys())},
            )
        return config

    def list_all(self) -> list[TemplateConfig]:
        """Return all registered template configurations.

        Returns:
            List of all TemplateConfig instances sorted by name.
        """
        return sorted(self._registry.values(), key=lambda t: t.name)

    def exists(self, name: str) -> bool:
        """Check whether a template name is registered.

        Args:
            name: Template name slug to check.

        Returns:
            True if the template exists, False otherwise.
        """
        return name in self._registry
