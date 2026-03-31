"""Prompt builder for AI-assisted template rendering."""

import json

from prompts.system.system_prompt import SystemPrompt


class TemplatePrompt:
    """Builds system and user prompts for AI-assisted template rendering.

    Used when AI assistance is needed to intelligently arrange or summarize
    resume content for a specific template layout beyond what the deterministic
    TemplateEngine provides.
    """

    @staticmethod
    def build(optimized_data: dict, template_name: str) -> tuple[str, str]:
        """Build the template rendering system and user prompts.

        Args:
            optimized_data: The fully optimized resume data dictionary.
            template_name: The name of the template to render for.

        Returns:
            A tuple of (system_prompt, user_prompt) strings for the Claude API.
        """
        data_str = json.dumps(optimized_data, indent=2, default=str)

        template_styles: dict[str, str] = {
            "modern_clean": "minimalist single-column, Calibri font, blue accents",
            "executive_classic": "traditional serif single-column, Georgia font, black",
            "tech_minimal": "clean sans-serif, skills before experience, dark theme",
            "creative_bold": "two-column layout with bold typographic hierarchy, purple accents",
            "ats_optimized": "plain single-column, Arial, no formatting, maximum ATS compatibility",
            "academic": "comprehensive CV format with all sections, Times New Roman",
        }
        style_desc = template_styles.get(template_name, "professional single-column layout")

        system_prompt = f"""{SystemPrompt.get()}

YOUR TASK FOR THIS REQUEST: Prepare the resume data for rendering with the '{template_name}' template.
Template style: {style_desc}.

Review the provided optimized resume data and return a final rendering-ready JSON object.
If the template is 'ats_optimized', ensure all content is plain text with no special characters.
If the template is 'two_column', suggest which sections go in the left vs right column.
If the template is 'academic', ensure all publications, awards, and volunteer work are included.

Return ONLY a valid JSON object with the rendering-ready resume data."""

        user_prompt = f"""Prepare this resume data for the '{template_name}' template.
Return the final rendering-ready JSON, making any template-specific adjustments needed.

OPTIMIZED RESUME DATA:
---
{data_str}
---

Template: {template_name} ({style_desc})

Return ONLY the rendering-ready JSON object."""

        return system_prompt, user_prompt
