"""
ValidationAgent — Stage 4
Verifies that the generated fix resolves issues without regressions.
"""

import json
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are a rigorous QA engineer performing final validation.
Given the original code, the fixed code, and the list of issues, you must:
1. Verify each issue has been properly addressed in the fixed code
2. Check for newly introduced bugs or regressions
3. Verify behavioral equivalence (same functionality, just safer/cleaner)
4. Produce a final pass/fail verdict

Respond ONLY with a valid JSON object (no markdown, no preamble):
{
  "passed": true,
  "score": 95,
  "verified_fixes": ["unique-id-001", "unique-id-002"],
  "unresolved_issues": [],
  "new_issues_introduced": [],
  "behavioral_equivalence": true,
  "notes": "Overall validation summary"
}
"""


class ValidationAgent(BaseAgent):
    def __init__(self, language: str = "python"):
        super().__init__(name="ValidationAgent", language=language)

    def run(self, original_code: str, fixed_code: str, issues: list, file_name: str) -> dict:
        issues_json = json.dumps(issues, indent=2, ensure_ascii=False)

        user_prompt = f"""Validate the fix for the following {self.language} file.

File: {file_name}

Original code:
```{self.language}
{original_code}
