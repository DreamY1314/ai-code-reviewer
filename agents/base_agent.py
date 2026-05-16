"""
Base agent — shared Claude API call logic for all agents.
"""

import os
import json
import anthropic
from utils.logger import setup_logger

logger = setup_logger(__name__)

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096


class BaseAgent:
    def __init__(self, name: str, language: str = "python"):
        self.name = name
        self.language = language
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set. "
                "Please export your API key before running."
            )
        self.client = anthropic.Anthropic(api_key=api_key)

    def _call(self, system_prompt: str, user_prompt: str) -> tuple:
        """Call Claude API and return (response_text, tokens_used)."""
        try:
            message = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = message.content[0].text
            tokens = message.usage.input_tokens + message.usage.output_tokens
            return content, tokens
        except anthropic.APIError as e:
            logger.error(f"[{self.name}] API error: {e}")
            raise

    def _parse_json(self, text: str) -> dict:
        """Parse JSON from model output, stripping markdown fences."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"[{self.name}] JSON parse error: {e}. Returning raw text.")
            return {"raw": text}
