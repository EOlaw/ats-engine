"""Prompt builder for the resume data validation stage."""

import json

from prompts.system.system_prompt import SystemPrompt


class ValidationPrompt:
    """Builds system and user prompts for the resume validation stage.

    The validation stage reviews the extracted JSON for logical consistency
    issues and returns a validation report with an optional corrected version.
    """

    @staticmethod
    def build(extracted_json: dict) -> tuple[str, str]:
        """Build the validation system and user prompts.

        Args:
            extracted_json: The structured resume data from the extraction stage.

        Returns:
            A tuple of (system_prompt, user_prompt) strings for the Claude API.
        """
        extracted_str = json.dumps(extracted_json, indent=2, default=str)

        system_prompt = f"""{SystemPrompt.get()}

YOUR TASK FOR THIS REQUEST: Validate the provided extracted resume JSON for logical consistency.
Check for the following types of issues:
1. Date conflicts: overlapping work experience dates, end dates before start dates,
   future start dates for past roles.
2. Missing critical fields: no email, no full name, no work experience for an experienced candidate.
3. Duplicate entries: same company/role appearing twice with slight variations.
4. Unclear sections: items clearly placed in the wrong section (e.g., a certification
   listed under work experience).
5. Inconsistent data: role title mentioned in summary but not in work experience, etc.

Return ONLY a valid JSON object with this structure:
{{
  "is_valid": boolean,
  "issues": ["list of issue descriptions"],
  "corrected_data": {{ ...the full corrected JSON matching the original schema... }},
  "validation_score": float 0.0-1.0
}}

If the data looks correct, set is_valid to true, issues to [], validation_score to 1.0,
and corrected_data to the input unchanged."""

        user_prompt = f"""Validate the following extracted resume JSON for consistency and correctness.
If you find issues, correct them in the corrected_data field.
If everything looks correct, return the data unchanged.

EXTRACTED RESUME JSON:
---
{extracted_str}
---

Return ONLY the validation result JSON object."""

        return system_prompt, user_prompt
