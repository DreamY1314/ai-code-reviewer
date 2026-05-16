"""
AnalysisAgent — Stage 2
Performs deep, long-chain reasoning to identify root causes.
"""

import json
from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are a senior software architect performing deep root-cause analysis.
Given source code and a list of detected issues, you must:
1. Trace each issue back to its architectural or logical root cause
2. Identify dependency chains between issues
3. Assess blast radius: what can go wrong if each issue is left unfixed
4. Prioritize the order in which issues should be fixed

Respond ONLY with a valid JSON object (no markdown, no preamble):
{
  "root_causes": [
    {
      "issue_ids": ["unique-id-001"],
      "root_cause": "Description of the underlying root cause",
      "reasoning_chain": ["Step 1 of reasoning", "Step 2", "..."],
      "blast_radius": "Description of potential impact",
      "fix_priority": 1
    }
  ],
  "fix_order": ["unique-id-001", "unique-id-002"],
  "summary": "Overall assessment of the codebase health"
}
"""


class AnalysisAgent(BaseAgent):
    def __init__(self, language: str = "python"):
        super().__init__(name="AnalysisAgent", language=language)

    def run(self, code: str, issues: list, file_name: str) -> dict:
        issues_json = json.dumps(issues, indent=2, ensure_ascii=False)

        user_prompt = f"""Perform deep root-cause analysis on the following {self.language} code.

File: {file_name}

```{self.language}
{code}
