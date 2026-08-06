#!/usr/bin/env python3
"""Run static checks on the leslie-tech-writer skill itself."""

from __future__ import annotations

import ast
from pathlib import Path
import re


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    skill_path = root / "SKILL.md"
    text = skill_path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        errors.append("SKILL.md: missing YAML frontmatter")
    else:
        frontmatter = match.group(1)
        name = re.search(r"^name:\s*(.+)$", frontmatter, re.M)
        description = re.search(r"^description:\s*(.+)$", frontmatter, re.M)
        if not name or name.group(1).strip() != root.name:
            errors.append("SKILL.md: name must match directory")
        if not description or len(description.group(1).strip()) < 80:
            errors.append("SKILL.md: description is missing or not sufficiently specific")
        if description and len(description.group(1).strip()) > 1024:
            errors.append("SKILL.md: description exceeds 1024 characters")

    for relative in sorted(set(re.findall(r"`((?:references|scripts|assets)/[^`]+)`", text))):
        if not (root / relative).exists():
            errors.append(f"SKILL.md: referenced path does not exist: {relative}")

    for path in root.rglob("*"):
        if path.is_symlink():
            errors.append(f"unexpected symlink: {path.relative_to(root)}")
        if path.is_file():
            content = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"sk-ai-v1-[A-Za-z0-9]{20,}", content):
                errors.append(f"possible embedded API key: {path.relative_to(root)}")

    for script in sorted((root / "scripts").glob("*.py")):
        try:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        except SyntaxError as exc:
            errors.append(f"{script.name}: {exc}")

    if errors:
        print("FAIL")
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PASS: skill structure, references, scripts, and secret scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
