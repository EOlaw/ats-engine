"""Prompt builder for the resume extraction stage."""

import json

from prompts.system.system_prompt import SystemPrompt


class ExtractionPrompt:
    """Builds system and user prompts for the resume extraction stage.

    The extraction stage converts raw resume text into a fully structured
    JSON object matching the ExtractedResume schema. The prompt embeds the
    target JSON schema directly to ensure Claude returns conformant output.
    """

    _EXTRACTION_SCHEMA: dict = {
        "personal_info": {
            "full_name": "string | null",
            "email": "string | null",
            "phone": "string | null",
            "location": "string | null",
            "linkedin_url": "string | null",
            "github_url": "string | null",
            "portfolio_url": "string | null",
            "summary": "string | null — the professional summary if present in the document",
        },
        "skills": {
            "technical": ["list of technical/hard skills"],
            "soft": ["list of soft skills"],
            "languages": ["programming or spoken languages"],
            "tools": ["tools, platforms, frameworks"],
            "certifications_mentioned": ["certifications mentioned within skills section"],
        },
        "work_experience": [
            {
                "company": "string | null",
                "title": "string | null",
                "location": "string | null",
                "start_date": "string | null — YYYY-MM or free text",
                "end_date": "string | null — YYYY-MM, 'Present', or free text",
                "is_current": "boolean",
                "bullets": ["list of accomplishment/responsibility bullet strings"],
                "technologies": ["technologies used in this role"],
            }
        ],
        "education": [
            {
                "institution": "string | null",
                "degree": "string | null",
                "field_of_study": "string | null",
                "start_date": "string | null",
                "end_date": "string | null",
                "gpa": "string | null",
                "honors": ["list of honors, awards, relevant coursework"],
            }
        ],
        "certifications": [
            {
                "name": "string | null",
                "issuer": "string | null",
                "date_earned": "string | null",
                "expiry_date": "string | null",
                "credential_id": "string | null",
            }
        ],
        "projects": [
            {
                "name": "string | null",
                "description": "string | null",
                "technologies": ["list"],
                "url": "string | null",
                "date": "string | null",
                "highlights": ["list of key accomplishments"],
            }
        ],
        "volunteer_experience": [],
        "publications": [],
        "awards": ["list of award strings"],
        "languages": [{"language": "string", "proficiency": "string | null"}],
        "extraction_confidence": "float 0.0-1.0 — your confidence in the extraction quality",
        "raw_sections_found": ["list of section names detected in the document"],
    }

    @staticmethod
    def build(resume_text: str) -> tuple[str, str]:
        """Build the extraction system and user prompts.

        Args:
            resume_text: Raw plain text content of the resume document.

        Returns:
            A tuple of (system_prompt, user_prompt) strings for the Claude API.
        """
        schema_str = json.dumps(ExtractionPrompt._EXTRACTION_SCHEMA, indent=2)

        system_prompt = f"""{SystemPrompt.get()}

YOUR TASK FOR THIS REQUEST: Extract all structured information from the provided resume text.
Return ONLY a valid JSON object matching the schema below. Do not include any text outside the JSON.
If a field is not present in the resume, use null for strings or [] for arrays.
Never invent or infer information not explicitly stated in the resume text.

TARGET JSON SCHEMA:
{schema_str}"""

        user_prompt = f"""Extract all structured resume data from the following resume text.
Return a single valid JSON object matching the schema. Set extraction_confidence based on how
clearly structured and complete the resume is (1.0 = very clear and complete, 0.4 = ambiguous or sparse).

RESUME TEXT:
---
{resume_text}
---

Respond with ONLY the JSON object, no additional text."""

        return system_prompt, user_prompt
