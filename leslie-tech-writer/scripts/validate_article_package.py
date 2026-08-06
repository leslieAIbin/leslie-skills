#!/usr/bin/env python3
"""Validate a Leslie technical article package at planning, draft, or release."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import struct


STAGE_FILES = {
    "planning": ("brief.md", "evidence.md", "outline.md", "visual-plan.md"),
    "draft": (
        "brief.md",
        "evidence.md",
        "outline.md",
        "visual-plan.md",
        "article.md",
        "qa-report.md",
    ),
    "release": (
        "brief.md",
        "evidence.md",
        "outline.md",
        "visual-plan.md",
        "article.md",
        "qa-report.md",
    ),
}
MARKERS = (
    re.compile(r"\[待填写[^\]]*\]"),
    re.compile(r"\b(?:TODO|TBD|FIXME)\b", re.I),
    re.compile(r"\{\{[^}]+\}\}"),
)
EVIDENCE_ID = re.compile(r"\bE\d{2,}\b")
VISUAL_ID = re.compile(r"\bV\d{2,}\b")
IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--stage", choices=tuple(STAGE_FILES), default="draft")
    parser.add_argument("--require-html", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def read(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        errors.append(f"{path.name}: must be UTF-8")
        return ""


def markdown_table(text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = [cell.strip().lower() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) == len(headers):
            rows.append(dict(zip(headers, cells)))
    return rows


def marker_hits(text: str) -> list[str]:
    hits: list[str] = []
    for pattern in MARKERS:
        hits.extend(match.group(0) for match in pattern.finditer(text))
    return hits


def bitmap_dimensions(path: Path) -> tuple[int, int] | None:
    """Return PNG dimensions without requiring third-party image libraries."""
    if path.suffix.lower() != ".png":
        return None
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def check_required_files(project: Path, stage: str, errors: list[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for name in STAGE_FILES[stage]:
        path = project / name
        if not path.is_file():
            errors.append(f"missing required file: {name}")
            continue
        if path.stat().st_size < 20:
            errors.append(f"required file is too small: {name}")
        texts[name] = read(path, errors)
        hits = marker_hits(texts[name])
        if hits:
            errors.append(f"{name}: unresolved markers: {', '.join(sorted(set(hits)))}")
    return texts


def check_evidence(texts: dict[str, str], stage: str, errors: list[str], warnings: list[str]) -> set[str]:
    text = texts.get("evidence.md", "")
    rows = markdown_table(text)
    if not rows:
        errors.append("evidence.md: missing readable Markdown ledger table")
        return set()
    required = {"id", "claim", "type", "status", "source/artifact"}
    if not required.issubset(rows[0]):
        errors.append("evidence.md: ledger headers do not match the output contract")
    ids: set[str] = set()
    allowed_types = {"experience", "experiment", "source", "opinion", "inference", "unusable"}
    allowed_status = {"verified", "pending", "opinion", "unusable"}
    for index, row in enumerate(rows, start=1):
        evidence_id = row.get("id", "")
        if not re.fullmatch(r"E\d{2,}", evidence_id):
            errors.append(f"evidence.md row {index}: invalid evidence ID {evidence_id!r}")
        elif evidence_id in ids:
            errors.append(f"evidence.md: duplicate evidence ID {evidence_id}")
        ids.add(evidence_id)
        if row.get("type", "").lower() not in allowed_types:
            errors.append(f"evidence.md {evidence_id}: invalid evidence type")
        status = row.get("status", "").lower()
        if status not in allowed_status:
            errors.append(f"evidence.md {evidence_id}: invalid status")
        if stage == "release" and status in {"pending", "unusable"}:
            errors.append(f"evidence.md {evidence_id}: {status} evidence blocks release")
        elif status in {"pending", "unusable"}:
            warnings.append(f"evidence.md {evidence_id}: status is {status}")
    return ids


def check_evidence_references(texts: dict[str, str], evidence_ids: set[str], errors: list[str]) -> None:
    for name in ("outline.md", "visual-plan.md", "article.md"):
        for evidence_id in EVIDENCE_ID.findall(texts.get(name, "")):
            if evidence_id not in evidence_ids:
                errors.append(f"{name}: references undefined evidence {evidence_id}")


def check_visuals(project: Path, texts: dict[str, str], stage: str, errors: list[str], warnings: list[str]) -> None:
    rows = markdown_table(texts.get("visual-plan.md", ""))
    if not rows:
        errors.append("visual-plan.md: missing readable Markdown table")
        return
    required = {"id", "filename", "status", "qa"}
    if not required.issubset(rows[0]):
        errors.append("visual-plan.md: headers do not match the output contract")
    statuses: dict[str, str] = {}
    seen_ids: set[str] = set()
    allowed = {"planned", "prompted", "generated", "accepted", "regenerate", "replace-with-svg", "omit"}
    for index, row in enumerate(rows, start=1):
        visual_id = row.get("id", "")
        if not VISUAL_ID.fullmatch(visual_id):
            errors.append(f"visual-plan.md row {index}: invalid visual ID {visual_id!r}")
        elif visual_id in seen_ids:
            errors.append(f"visual-plan.md: duplicate visual ID {visual_id}")
        seen_ids.add(visual_id)
        filename = row.get("filename", "").strip("`")
        status = row.get("status", "").lower()
        if status not in allowed:
            errors.append(f"visual-plan.md {visual_id}: invalid status {status!r}")
        if filename:
            statuses[filename] = status
            statuses[Path(filename).name] = status
        qa = row.get("qa", "").lower()
        if stage == "release" and status not in {"accepted", "omit"}:
            errors.append(f"visual-plan.md {visual_id}: status {status} blocks release")
        if stage == "release" and status == "accepted" and qa not in {"pass", "passed", "accepted"}:
            errors.append(f"visual-plan.md {visual_id}: accepted asset requires PASS QA")
        elif status == "regenerate":
            warnings.append(f"visual-plan.md {visual_id}: requires regeneration")

    article = texts.get("article.md", "")
    for raw_link in IMAGE_LINK.findall(article):
        if re.match(r"https?://", raw_link):
            continue
        clean = raw_link.split("#", 1)[0]
        asset = (project / clean).resolve()
        try:
            asset.relative_to(project.resolve())
        except ValueError:
            errors.append(f"article.md: image escapes project directory: {raw_link}")
            continue
        if not asset.is_file():
            errors.append(f"article.md: linked image does not exist: {raw_link}")
        elif asset.suffix.lower() == ".png":
            dimensions = bitmap_dimensions(asset)
            if dimensions is None:
                errors.append(f"article.md: linked PNG is invalid: {raw_link}")
            elif "warm-paper-tech" in texts.get("visual-plan.md", ""):
                width, height = dimensions
                if not 1.75 <= width / height <= 1.84:
                    message = f"article.md: warm-paper-tech PNG is not 16:9: {raw_link} ({width}x{height})"
                    if stage == "release":
                        errors.append(message)
                    else:
                        warnings.append(message)
        elif asset.suffix.lower() == ".svg":
            if "<svg" not in read(asset, errors)[:1000].lower():
                errors.append(f"article.md: linked SVG is invalid: {raw_link}")
        status = statuses.get(clean, statuses.get(Path(clean).name))
        if stage == "release" and status != "accepted":
            errors.append(f"article.md: linked image is not accepted in visual-plan.md: {raw_link}")
        elif status and status != "accepted":
            warnings.append(f"article.md: linked image status is {status}: {raw_link}")


def check_article(texts: dict[str, str], stage: str, errors: list[str], warnings: list[str]) -> None:
    article = texts.get("article.md", "")
    if not article:
        return
    h1_count = sum(1 for line in article.splitlines() if re.match(r"^#\s+\S", line))
    if h1_count != 1:
        errors.append(f"article.md: expected exactly one H1, found {h1_count}")


def check_qa(texts: dict[str, str], stage: str, errors: list[str]) -> None:
    qa = texts.get("qa-report.md", "")
    if not qa:
        return
    for gate in range(1, 5):
        if not re.search(rf"Gate\s+{gate}\b", qa, re.I):
            errors.append(f"qa-report.md: missing Gate {gate}")
    if stage == "release" and re.search(r"Status:\s*FAIL\b", qa, re.I):
        errors.append("qa-report.md: a qualitative gate is marked FAIL")


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not project.is_dir():
        errors.append(f"project directory does not exist: {project}")
        texts: dict[str, str] = {}
    else:
        texts = check_required_files(project, args.stage, errors)
        evidence_ids = check_evidence(texts, args.stage, errors, warnings)
        check_evidence_references(texts, evidence_ids, errors)
        check_visuals(project, texts, args.stage, errors, warnings)
        check_article(texts, args.stage, errors, warnings)
        check_qa(texts, args.stage, errors)
        if args.require_html and not (project / "article.html").is_file():
            errors.append("missing required file: article.html")

    result = {
        "project": str(project),
        "stage": args.stage,
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Stage: {args.stage}")
        print(f"Result: {'PASS' if not errors else 'FAIL'}")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN: {item}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
