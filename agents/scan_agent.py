"""
ScanAgent — Stage 1
Scans code for security vulnerabilities, performance bottlenecks,
style violations, and potential bugs.
"""

from .base_agent import BaseAgent

SYSTEM_PROMPT = """You are an expert code security and quality scanner.
Your job is to scan source code and identify ALL issues across these categories:
- security: SQL injection, XSS, hardcoded secrets, insecure dependencies, etc.
- performance: N+1 queries, inefficient loops, memory leaks, blocking I/O, etc.
- style: naming conventions, dead code, overly complex functions, etc.
- bug: logic errors, off-by-one, null dereference, race conditions, etc.

Respond ONLY with a valid JSON object (no markdown, no preamble):
{
  "issues": [
    {
      "id": "unique-id-001",
      "category": "security|performance|style|bug",
      "severity": "critical|high|medium|low",
      "line": <line number or null>,
      "message": "Short description of the issue",
      "detail": "Detailed explanation of why this is a problem"
    }
  ]
}

If no issues are found, return: {"issues": []}
"""


class ScanAgent(BaseAgent):
    def __init__(self, language: str = "python"):
        super().__init__(name="ScanAgent", language=language)

    def run(self, code: str, file_name: str) -> dict:
        user_prompt = f"""Please scan the following {self.language} file for issues.

File: {file_name}

```{self.language}
{code}
