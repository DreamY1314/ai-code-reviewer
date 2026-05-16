"""
FixAgent — Stage 3
Generates fixed code based on detected issues and root-cause analysis.
"""

import json
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are an expert software engineer who writes clean, secure, production-ready code.
Given source code, a list of detected issues, and root-cause analysis, you must:
1. Fix ALL identified issues in the code
2. Preserve the original logic and functionality
3. Add brief inline comments where fixes are non-obvious
4. Produce a human-readable summary of every change made

Respond ONLY with a valid JSON object (no markdown, no preamble):
{
  "fixed_code": "<complete fixed source code as a string>",
  "changes": [
    {
      "issue_id": "unique-id-001",
      "description": "What was changed and why",
      "line_range": "10-15"
    }
  ],
  "unfixed_issues": ["unique-id-XXX"],
  "unfixed_reasons": {"unique-id-XXX": "Reason it cannot be auto-fixed"}
}
"""


class FixAgent(BaseAgent):
    def __init__(self, language: str = "python"):
        super().__init__(name="FixAgent", language=language)

    def run(self, code: str, issues: list, root_causes: list, file_name: str) -> dict:
        issues_json = json.dumps(issues, indent=2, ensure_ascii=False)
        causes_json = json.dumps(root_causes, indent=2, ensure_ascii=False)

        user_prompt = f"""Fix ALL issues in the following {self.language} file.

File: {file_name}

Original code:
```{self.language}
{code}
