"""Prompt builder for the job tailoring stage."""

import json

from prompts.system.system_prompt import SystemPrompt


class TailoringPrompt:
    """Builds system and user prompts for the job tailoring stage.

    The tailoring stage aligns a resume to a specific job description by
    performing keyword gap analysis and rewriting summary and bullets
    to highlight the most relevant experience for the target role.
    """

    _TAILORING_SCHEMA: dict = {
        "tailored_summary": "string — 3-5 sentence summary written specifically for this role",
        "tailored_work_experience": [
            {
                "company": "string — unchanged",
                "title": "string — unchanged",
                "start_date": "string — unchanged",
                "end_date": "string — unchanged",
                "optimized_bullets": [
                    "rewritten bullets emphasizing relevance to the target role"
                ],
            }
        ],
        "tailored_skills": {
            "technical": ["skills most relevant to this role listed first"],
            "soft": ["soft skills most relevant to this role"],
            "tools": ["tools and platforms matching JD requirements"],
        },
        "keyword_gap_analysis": {
            "missing_required": ["required JD keywords not found in resume"],
            "missing_preferred": ["preferred JD keywords not found in resume"],
            "present_keywords": ["JD keywords already present in resume"],
            "recommended_additions": ["top keywords to naturally incorporate"],
        },
        "match_score": "float 0-100 — alignment score before tailoring adjustments",
        "tailoring_notes": [
            "list of notes describing what was changed and why for this specific role"
        ],
    }

    @staticmethod
    def build(
        resume_data: dict, job_title: str, job_description: str
    ) -> tuple[str, str]:
        """Build the tailoring system and user prompts.

        Args:
            resume_data: Structured resume data (extracted or optimized).
            job_title: The target job title.
            job_description: Full text of the job description.

        Returns:
            A tuple of (system_prompt, user_prompt) strings for the Claude API.
        """
        schema_str = json.dumps(TailoringPrompt._TAILORING_SCHEMA, indent=2)
        resume_str = json.dumps(resume_data, indent=2, default=str)

        system_prompt = f"""{SystemPrompt.get()}

YOUR TASK FOR THIS REQUEST: Tailor the provided resume to a specific job description.
Analyze the job description for required and preferred keywords, required experience,
key responsibilities, and must-have skills. Then rewrite the resume summary and bullets
to maximize alignment with this specific role.

Rules:
1. DO NOT fabricate experience, titles, companies, dates, or skills.
2. DO reorder and rephrase existing bullets to highlight the most relevant achievements.
3. DO naturally incorporate keywords from the JD where they genuinely match the candidate's experience.
4. DO write the tailored summary to speak directly to this role and company context.
5. Score the match_score based on how well the ORIGINAL resume (before tailoring) aligns
   with the JD — be honest and calibrated.
6. List keyword gaps clearly to help the candidate understand what's missing.

Return ONLY a valid JSON object matching this schema:
{schema_str}"""

        user_prompt = f"""Tailor this resume for the following job.

JOB TITLE: {job_title}

JOB DESCRIPTION:
---
{job_description[:8000]}
---

CANDIDATE'S RESUME DATA:
---
{resume_str}
---

Return ONLY the tailoring JSON object. Be honest about the match score."""

        return system_prompt, user_prompt
