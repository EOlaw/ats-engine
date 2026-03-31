"""Prompt builder for the ATS scoring stage."""

import json

from prompts.system.system_prompt import SystemPrompt


class ScoringPrompt:
    """Builds system and user prompts for the ATS scoring and analysis stage.

    The scoring stage produces a comprehensive ATS compatibility analysis
    including a numeric score, per-category breakdown, keyword gaps,
    strengths, weaknesses, and prioritized recommendations.
    """

    _SCORING_SCHEMA: dict = {
        "score_estimate": "float 0-100 — overall ATS compatibility score",
        "score_breakdown": {
            "format_and_structure": "float 0-100",
            "keyword_density": "float 0-100",
            "work_experience_quality": "float 0-100",
            "education_and_credentials": "float 0-100",
            "skills_section": "float 0-100",
            "contact_information": "float 0-100",
        },
        "strengths": ["list of specific resume strengths"],
        "weaknesses": ["list of specific resume weaknesses"],
        "critical_fixes": [
            "list of high-priority improvements that will most improve ATS score"
        ],
        "keyword_gaps": ["important keywords typically expected but not found"],
        "keyword_matches": [
            {
                "keyword": "string",
                "found": "boolean",
                "context": "string | null — sentence where keyword appears",
                "importance": "high | medium | low",
            }
        ],
        "format_issues": [
            "list of formatting problems that may cause ATS parsing failures"
        ],
        "quantification_score": "float 0-100 — score for use of quantified achievements",
        "action_verb_score": "float 0-100 — score for use of strong action verbs",
        "recommendations": [
            "list of prioritized actionable recommendations, most impactful first"
        ],
    }

    @staticmethod
    def build(extracted_json: dict, resume_text: str) -> tuple[str, str]:
        """Build the scoring system and user prompts.

        Args:
            extracted_json: Validated structured resume data from extraction stage.
            resume_text: Original raw resume text for additional context.

        Returns:
            A tuple of (system_prompt, user_prompt) strings for the Claude API.
        """
        schema_str = json.dumps(ScoringPrompt._SCORING_SCHEMA, indent=2)
        extracted_str = json.dumps(extracted_json, indent=2, default=str)

        system_prompt = f"""{SystemPrompt.get()}

YOUR TASK FOR THIS REQUEST: Perform a comprehensive ATS compatibility analysis on the provided
resume data. Score the resume from 0-100 on overall ATS compatibility and provide detailed
per-category scores, keyword analysis, identified issues, and ranked recommendations.

Scoring criteria:
- format_and_structure (20%): Single-column layout, standard section names, no tables/graphics,
  clean whitespace, readable fonts.
- keyword_density (25%): Presence of role-appropriate technical and soft skill keywords,
  industry terminology, job title alignment.
- work_experience_quality (25%): Quantified achievements, strong action verbs, scope/impact clarity,
  reverse chronological order, date completeness.
- education_and_credentials (15%): Degree level, relevant field, certifications, GPA if strong.
- skills_section (10%): Organized, comprehensive, no vague soft skills without context.
- contact_information (5%): Email, phone, location, LinkedIn at minimum.

Return ONLY a valid JSON object matching the schema below:
{schema_str}"""

        user_prompt = f"""Analyze this resume for ATS compatibility. Score it 0-100 and provide
the full analysis breakdown.

STRUCTURED RESUME DATA:
---
{extracted_str}
---

ORIGINAL RESUME TEXT (for additional context):
---
{resume_text[:6000]}
---

Return ONLY the ATS analysis JSON object."""

        return system_prompt, user_prompt
