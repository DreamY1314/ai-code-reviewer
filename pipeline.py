"""
Pipeline orchestrator - coordinates all agents in sequence:
  1. ScanAgent      → detect issues
  2. AnalysisAgent  → deep root-cause reasoning
  3. FixAgent       → generate patch / fixed code
  4. ValidationAgent→ verify fix correctness
"""

import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from agents.scan_agent import ScanAgent
from agents.analysis_agent import AnalysisAgent
from agents.fix_agent import FixAgent
from agents.validation_agent import ValidationAgent
from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class FileReviewResult:
    file_path: str
    language: str
    issues: list = field(default_factory=list)
    root_causes: list = field(default_factory=list)
    fix_applied: bool = False
    fixed_code: Optional[str] = None
    validation_passed: Optional[bool] = None
    validation_notes: str = ""
    tokens_used: int = 0
    duration_seconds: float = 0.0
    error: Optional[str] = None


class CodeReviewPipeline:
    def __init__(self, language: str = "python", auto_fix: bool = False):
        self.language = language
        self.auto_fix = auto_fix
        self.scan_agent = ScanAgent(language=language)
        self.analysis_agent = AnalysisAgent(language=language)
        self.fix_agent = FixAgent(language=language)
        self.validation_agent = ValidationAgent(language=language)

    def run(self, files: list) -> list:
        results = []
        total = len(files)
        for idx, file_path in enumerate(files, 1):
            logger.info(f"[{idx}/{total}] Reviewing: {file_path}")
            result = self._review_file(file_path)
            results.append(result)
        return results

    def _review_file(self, file_path: Path) -> FileReviewResult:
        start = time.time()
        result = FileReviewResult(file_path=str(file_path), language=self.language)

        try:
            code = file_path.read_text(encoding="utf-8")
        except Exception as e:
            result.error = f"Could not read file: {e}"
            return result

        total_tokens = 0

        logger.info("  [Agent 1/4] ScanAgent: detecting issues...")
        scan_out = self.scan_agent.run(code=code, file_name=file_path.name)
        result.issues = scan_out.get("issues", [])
        total_tokens += scan_out.get("tokens_used", 0)
        logger.info(f"  → {len(result.issues)} issue(s) found")

        if not result.issues:
            result.tokens_used = total_tokens
            result.duration_seconds = time.time() - start
            return result

        logger.info("  [Agent 2/4] AnalysisAgent: root-cause reasoning...")
        analysis_out = self.analysis_agent.run(
            code=code, issues=result.issues, file_name=file_path.name)
        result.root_causes = analysis_out.get("root_causes", [])
        total_tokens += analysis_out.get("tokens_used", 0)

        logger.info("  [Agent 3/4] FixAgent: generating fixes...")
        fix_out = self.fix_agent.run(
            code=code, issues=result.issues,
            root_causes=result.root_causes, file_name=file_path.name)
        result.fixed_code = fix_out.get("fixed_code")
        total_tokens += fix_out.get("tokens_used", 0)

        if self.auto_fix and result.fixed_code:
            try:
                file_path.write_text(result.fixed_code, encoding="utf-8")
                result.fix_applied = True
                logger.info("  → Fix applied to file")
            except Exception as e:
                logger.warning(f"  → Could not apply fix: {e}")

        logger.info("  [Agent 4/4] ValidationAgent: verifying fix...")
        val_out = self.validation_agent.run(
            original_code=code, fixed_code=result.fixed_code or code,
            issues=result.issues, file_name=file_path.name)
        result.validation_passed = val_out.get("passed")
        result.validation_notes = val_out.get("notes", "")
        total_tokens += val_out.get("tokens_used", 0)

        result.tokens_used = total_tokens
        result.duration_seconds = time.time() - start
        logger.info(f"  ✓ Done — {total_tokens:,} tokens used in {result.duration_seconds:.1f}s")
        return result

    def print_summary(self, results: list):
        total_issues = sum(len(r.issues) for r in results)
        total_tokens = sum(r.tokens_used for r in results)
        files_with_errors = [r for r in results if r.error]
        files_ok = [r for r in results if not r.error]

        print("\n" + "=" * 60)
        print("  AI CODE REVIEWER — SUMMARY")
        print("=" * 60)
        print(f"  Files reviewed : {len(results)}")
        print(f"  Total issues   : {total_issues}")
        print(f"  Total tokens   : {total_tokens:,}")
        print(f"  Errors         : {len(files_with_errors)}")
        print("=" * 60)

        for r in files_ok:
            status = "✓" if (r.validation_passed or not r.issues) else "✗"
            print(f"\n  {status} {r.file_path}")
          for issue in r.issues:
                sev = issue.get("severity", "INFO").upper()
                msg = issue.get("message", "")
                line = issue.get("line", "?")
                print(f"      [{sev}] Line {line}: {msg}")
            if r.fix_applied:
                print("      Fix: applied ✔")
            elif r.fixed_code:
                print("      Fix: generated (use --fix to apply)")
            if r.validation_notes:
                print(f"      Validation: {r.validation_notes}")

        for r in files_with_errors:
            print(f"\n  ✗ {r.file_path}\n      ERROR: {r.error}")
        print()
          
