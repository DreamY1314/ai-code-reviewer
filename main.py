"""
AI Code Reviewer - Multi-Agent Code Review & Auto-Fix Pipeline
Entry point for the application.
"""

import argparse
import sys
from pathlib import Path
from pipeline import CodeReviewPipeline
from utils.logger import setup_logger
from utils.report import generate_html_report

logger = setup_logger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI-powered multi-agent code review and auto-fix pipeline"
    )
    parser.add_argument("target", help="File or directory to review")
    parser.add_argument("--fix", action="store_true", help="Automatically apply suggested fixes")
    parser.add_argument("--report", type=str, default=None, help="Output path for HTML report")
    parser.add_argument("--lang", type=str, default="python",
        choices=["python", "javascript", "typescript", "java", "go"])
    return parser.parse_args()


def collect_files(target: str, lang: str) -> list:
    extensions = {
        "python": [".py"], "javascript": [".js", ".jsx"],
        "typescript": [".ts", ".tsx"], "java": [".java"], "go": [".go"],
    }
    exts = extensions.get(lang, [".py"])
    path = Path(target)
    if path.is_file():
        return [path]
    elif path.is_dir():
        files = []
        for ext in exts:
            files.extend(path.rglob(f"*{ext}"))
        return [f for f in files if ".git" not in str(f)]
    else:
        logger.error(f"Target path not found: {target}")
        sys.exit(1)


def main():
    args = parse_args()
    files = collect_files(args.target, args.lang)
    if not files:
        logger.warning("No files found to review.")
        sys.exit(0)
    logger.info(f"Found {len(files)} file(s) to review.")
    pipeline = CodeReviewPipeline(language=args.lang, auto_fix=args.fix)
    results = pipeline.run(files)
    pipeline.print_summary(results)
    if args.report:
        generate_html_report(results, output_path=args.report)
        logger.info(f"HTML report saved to: {args.report}")


if __name__ == "__main__":
    main()
