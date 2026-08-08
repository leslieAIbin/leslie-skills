#!/usr/bin/env python3
"""Finalize an article and delete process files only after release validation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from validate_article_package import safe_title, validate_final_package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument(
        "--filename",
        help="Meaningful final Markdown filename without .md; defaults to project title",
    )
    parser.add_argument(
        "--confirm-delete-work",
        action="store_true",
        help="Required acknowledgement that .writer-work will be deleted",
    )
    return parser.parse_args()


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    if not args.confirm_delete_work:
        return fail("refusing destructive finalization without --confirm-delete-work")
    if not project.is_dir():
        return fail(f"project directory does not exist: {project}")

    work = project / ".writer-work"
    if work.parent != project or not work.is_dir() or work.is_symlink():
        return fail("expected a real .writer-work directory directly under the project")
    article_path = work / "article.md"
    if not article_path.is_file() or article_path.is_symlink():
        return fail("missing real working article: .writer-work/article.md")

    validator = Path(__file__).resolve().with_name("validate_article_package.py")
    release = subprocess.run(
        [sys.executable, str(validator), str(project), "--stage", "release"],
        text=True,
        capture_output=True,
        check=False,
    )
    if release.returncode:
        print(release.stdout, end="")
        print(release.stderr, end="", file=sys.stderr)
        return fail("release validation failed; process files were preserved")

    article = article_path.read_text(encoding="utf-8")
    headings = [match.group(1).strip() for match in re.finditer(r"(?m)^#\s+(.+?)\s*$", article)]
    if len(headings) != 1:
        return fail(f"working article must contain exactly one H1, found {len(headings)}")
    try:
        metadata = json.loads((work / "project.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return fail(f"cannot read project metadata: {error}")
    title = safe_title(args.filename or str(metadata.get("title", "")) or headings[0])
    if not title:
        return fail("article H1 cannot produce a safe filename")
    target = project / f"{title}.md"
    if target.exists():
        return fail(f"final article already exists: {target.name}")

    unexpected = [entry.name for entry in project.iterdir() if entry.name not in {".writer-work", "illustrations"}]
    if unexpected:
        return fail("unexpected root entries block finalization: " + ", ".join(sorted(unexpected)))

    final_article = article.replace("../illustrations/", "illustrations/")
    target.write_text(final_article, encoding="utf-8")
    errors, _ = validate_final_package(project, allow_work=True)
    if errors:
        target.unlink()
        print("Final-layout preflight failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return fail("process files were preserved")

    shutil.rmtree(work)
    errors, _ = validate_final_package(project)
    if errors:
        print("Post-finalization validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 3

    print("Finalization complete")
    print(f"Final article: {target}")
    print(f"Removed process directory: {work}")
    print(f"Retained illustrations: {project / 'illustrations'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
