#!/usr/bin/env python3
"""Validate Leslie portable task contracts and Codex /goal adapters."""

from __future__ import annotations

import re
import sys
from pathlib import Path


MARKERS = [
    ("outcome", [r"^结果[:：]", r"^Outcome[:：]", r"^/goal\s+\S"]),
    ("verification", [r"^验证[:：]", r"^Verification[:：]"]),
    ("constraints", [r"^约束[:：]", r"^Constraints[:：]"]),
    ("boundaries", [r"^写入边界[:：]", r"^边界[:：]", r"^Boundaries[:：]"]),
    ("iteration", [r"^迭代策略[:：]", r"^Iteration policy[:：]"]),
    ("completion", [r"^完成条件[:：]", r"^Stop when[:：]"]),
    ("pause", [r"^暂停条件[:：]", r"^Pause if[:：]"]),
]

PLACEHOLDERS = [r"\[[^\]]+\]", r"<[^>]+>", r"\b(?:TBD|TODO)\b", r"待补充", r"待定"]
VAGUE = [r"确保可用", r"make sure it works", r"随便改", r"一直尝试", r"keep trying", r"直到满意"]
EVIDENCE = re.compile(
    r"(运行|测试|构建|检查|日志|截图|文件|链接|接口|API|浏览器|真机|证据|run|test|build|lint|log|screenshot|file|URL|API|browser|evidence)",
    re.IGNORECASE,
)


def field(text: str, patterns: list[str]) -> str | None:
    for pattern in patterns:
        match = re.search(pattern + r"\s*(.*)$", text, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def lint(text: str, source: str) -> list[str]:
    errors: list[str] = []
    if re.search(r"^\s*/目标\b", text, re.MULTILINE):
        errors.append(f"{source}: use /goal, not /目标")
    for label, patterns in MARKERS:
        value = field(text, patterns)
        if value is None:
            errors.append(f"{source}: missing {label}")
        elif len(value) < 12:
            errors.append(f"{source}: {label} is too thin")
    verification = field(text, MARKERS[1][1])
    if verification and not EVIDENCE.search(verification):
        errors.append(f"{source}: verification lacks concrete evidence")
    for pattern in PLACEHOLDERS:
        if re.search(pattern, text, re.IGNORECASE):
            errors.append(f"{source}: unresolved placeholder matched {pattern}")
    for pattern in VAGUE:
        if re.search(pattern, text, re.IGNORECASE):
            errors.append(f"{source}: vague instruction matched {pattern}")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: lint_task_contract.py <file> [<file> ...]", file=sys.stderr)
        return 2
    errors: list[str] = []
    for raw in argv[1:]:
        path = Path(raw)
        try:
            errors.extend(lint(path.read_text(encoding="utf-8"), str(path)))
        except OSError as exc:
            errors.append(f"{path}: cannot read: {exc}")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Task contract lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
