"""Prompt builder for the resume optimization stage."""

import json

from prompts.system.system_prompt import SystemPrompt


class OptimizationPrompt:
    """Builds system and user prompts for the resume content optimization stage.

    The optimization stage rewrites the professional summary, work experience
    bullets, and reorganizes skills to address the gaps and weaknesses
    identified in the ATS analysis. Only content optimization — no fabrication.
    """

    _OPTIMIZATION_SCHEMA: dict = {
        "professional_summary": "string — rewritten 3-5 sentence professional summary optimized for ATS",
        "work_experience": [
            {
                "company": "string — original company name (unchanged)",
                "title": "string — original title (unchanged)",
                "start_date": "string — original start date (unchanged)",
                "end_date": "string — original end date (unchanged)",
                "optimized_bullets": [
                    "list of rewritten bullet points: lead with action verb, include metric/result"
                ],
            }
        ],
        "skills_grouping": {
            "technical": ["reorganized technical skills"],
            "soft": ["reorganized soft skills"],
            "languages": ["programming or spoken languages"],
            "tools": ["tools and platforms"],
            "domain_expertise": ["industry-specific domain knowledge"],
        },
        "added_keywords": ["keywords added during optimization that were missing"],
        "optimization_notes": [
            "list of concise notes describing the changes made and why"
        ],
    }

    @staticmethod
    def build(extracted_json: dict, ats_analysis: dict) -> tuple[str, str]:
        """Build the optimization system and user prompts.

        Args:
            extracted_json: Validated structured resume data.
            ats_analysis: ATS analysis output from the scoring stage.

        Returns:
            A tuple of (system_prompt, user_prompt) strings for the Claude API.
        """
        schema_str = json.dumps(OptimizationPrompt._OPTIMIZATION_SCHEMA, indent=2)
        extracted_str = json.dumps(extracted_json, indent=2, default=str)
        analysis_str = json.dumps(ats_analysis, indent=2, default=str)

        system_prompt = f"""{SystemPrompt.get()}

YOUR TASK FOR THIS REQUEST: Optimize the resume content based on the ATS analysis provided.
Rewrite the professional summary, work experience bullets, and reorganize skills to
address the identified weaknesses and fill keyword gaps.

Critical rules:
1. DO NOT fabricate metrics, companies, titles, dates, or skills not present in the original.
2. DO reorganize and rephrase existing content to be more impactful and ATS-friendly.
3. DO add keywords from the keyword_gaps list if they can be naturally incorporated based
   on existing experience (e.g., if they did a task but didn't name the skill explicitly).
4. DO lead every bullet point with a strong past-tense action verb.
5. DO include quantified metrics where the original mentions scale, volume, or impact.
6. DO NOT change company names, job titles, or employment dates.
7. Maintain original meaning while improving clarity, impact, and keyword density.

Return ONLY a valid JSON object matching this schema:
{schema_str}"""

        user_prompt = f"""Optimize this resume content using the ATS analysis to guide improvements.

CURRENT RESUME DATA:
---
{extracted_str}
---

ATS ANALYSIS (use this to guide optimization):
---
{analysis_str}
---

Rewrite the professional summary and all work experience bullets. Reorganize skills.
Fill in keyword gaps naturally where appropriate based on actual experience.
Return ONLY the optimization JSON object."""

        return system_prompt, user_prompt
