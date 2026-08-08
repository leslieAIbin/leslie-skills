#!/usr/bin/env python3
"""Create a Leslie technical article package from bundled templates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import sys


TEMPLATE_FILES = (
    "brief.md",
    "evidence.md",
    "outline.md",
    "visual-plan.md",
    "article.md",
    "qa-report.md",
)
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, help="New article project directory")
    parser.add_argument("--title", required=True, help="Working article title")
    parser.add_argument(
        "--slug",
        required=True,
        help="Semantic lowercase English kebab-case asset directory name",
    )
    parser.add_argument(
        "--mode",
        default="full-production",
        choices=("full-production", "collaborative", "edit", "review"),
    )
    parser.add_argument(
        "--archetype",
        default="source-code-or-architecture-deep-dive",
        help="Primary archetype slug or short label",
    )
    parser.add_argument("--reader", default="有工程经验的中文技术读者")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    if not SLUG.fullmatch(args.slug):
        print("ERROR: --slug must be semantic lowercase ASCII kebab-case", file=sys.stderr)
        return 2
    if project.exists():
        if not project.is_dir():
            print(f"ERROR: target exists and is not a directory: {project}", file=sys.stderr)
            return 2
        if any(project.iterdir()):
            print(f"ERROR: target is not empty: {project}", file=sys.stderr)
            return 2

    templates = Path(__file__).resolve().parent.parent / "assets" / "templates"
    missing = [name for name in TEMPLATE_FILES if not (templates / name).is_file()]
    if missing:
        print(f"ERROR: missing templates: {', '.join(missing)}", file=sys.stderr)
        return 2

    work = project / ".writer-work"
    illustrations = project / "illustrations" / args.slug
    work.mkdir(parents=True, exist_ok=True)
    (work / "candidates").mkdir()
    (work / "sources").mkdir()
    (illustrations / "prompts").mkdir(parents=True)

    metadata = {
        "format_version": 2,
        "title": args.title,
        "slug": args.slug,
        "mode": args.mode,
    }
    (work / "project.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    replacements = {
        "{{TITLE}}": args.title,
        "{{SLUG}}": args.slug,
        "{{MODE}}": args.mode,
        "{{ARCHETYPE}}": args.archetype,
        "{{READER}}": args.reader,
    }
    for name in TEMPLATE_FILES:
        text = (templates / name).read_text(encoding="utf-8")
        for token, value in replacements.items():
            text = text.replace(token, value)
        (work / name).write_text(text, encoding="utf-8")

    shutil.copyfile(templates / "image-prompt.md", work / "PROMPT-TEMPLATE.md")
    print(f"Created article package: {project}")
    print(f"Working files: {work}")
    print(f"Durable illustrations: {illustrations}")
    print("Next: complete the planning files, then run the planning validator.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
