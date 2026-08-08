#!/usr/bin/env python3
"""Validate a Leslie technical article package from planning through final."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import struct
from urllib.parse import unquote


WORK_STAGE_FILES = {
    "planning": ("brief.md", "evidence.md", "outline.md", "visual-plan.md"),
    "draft": ("brief.md", "evidence.md", "outline.md", "visual-plan.md", "article.md", "qa-report.md"),
    "release": ("brief.md", "evidence.md", "outline.md", "visual-plan.md", "article.md", "qa-report.md"),
}
STAGES = (*WORK_STAGE_FILES, "final")
MARKERS = (
    re.compile(r"\[待填写[^\]]*\]"),
    re.compile(r"\b(?:TODO|TBD|FIXME)\b", re.I),
    re.compile(r"\{\{[^}]+\}\}"),
)
EVIDENCE_ID = re.compile(r"\bE\d{2,}\b")
VISUAL_ID = re.compile(r"\bV\d{2,}\b")
IMAGE_LINK = re.compile(r"!\[[^\]]*\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
OBSIDIAN_IMAGE = re.compile(r"!\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
IMAGE_SUFFIXES = {".webp", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".avif"}
GENERIC_ARTICLE = re.compile(r"(?i)^(?:article|draft|final|\d{2}-(?:draft|final|outline|article-review|publish-check))\.md$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--stage", choices=STAGES, default="draft")
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
    if path.suffix.lower() != ".png":
        return None
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def valid_image(path: Path) -> bool:
    suffix = path.suffix.lower()
    head = path.read_bytes()[:32]
    if suffix == ".png":
        return bitmap_dimensions(path) is not None
    if suffix in {".jpg", ".jpeg"}:
        return head.startswith(b"\xff\xd8\xff")
    if suffix == ".webp":
        return len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if suffix == ".gif":
        return head.startswith((b"GIF87a", b"GIF89a"))
    if suffix == ".avif":
        return b"ftypavif" in head or b"ftypavis" in head
    if suffix == ".svg":
        return "<svg" in path.read_text(encoding="utf-8", errors="ignore")[:2000].lower()
    return False


def image_links(text: str) -> list[str]:
    return IMAGE_LINK.findall(text) + OBSIDIAN_IMAGE.findall(text)


def safe_title(title: str) -> str:
    return re.sub(r"[\x00/]", "／", title.strip()).rstrip(". ")


def check_required_files(work: Path, stage: str, errors: list[str]) -> dict[str, str]:
    texts: dict[str, str] = {}
    for name in WORK_STAGE_FILES[stage]:
        path = work / name
        if not path.is_file():
            errors.append(f"missing required file: .writer-work/{name}")
            continue
        if path.stat().st_size < 20:
            errors.append(f"required file is too small: .writer-work/{name}")
        texts[name] = read(path, errors)
        hits = marker_hits(texts[name])
        if hits:
            errors.append(f"{name}: unresolved markers: {', '.join(sorted(set(hits)))}")
    return texts


def check_metadata(project: Path, work: Path, errors: list[str]) -> str:
    path = work / "project.json"
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        errors.append(f".writer-work/project.json: unreadable metadata: {error}")
        return ""
    slug = str(metadata.get("slug", ""))
    if metadata.get("format_version") != 2:
        errors.append(".writer-work/project.json: format_version must be 2")
    if not SLUG.fullmatch(slug):
        errors.append(".writer-work/project.json: slug must be lowercase ASCII kebab-case")
    expected = project / "illustrations" / slug
    if slug and not expected.is_dir():
        errors.append(f"missing illustration directory: illustrations/{slug}")
    if slug and not (expected / "prompts").is_dir():
        errors.append(f"missing prompt directory: illustrations/{slug}/prompts")
    return slug


def check_evidence(texts: dict[str, str], stage: str, errors: list[str], warnings: list[str]) -> set[str]:
    rows = markdown_table(texts.get("evidence.md", ""))
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


def check_visuals(project: Path, work: Path, texts: dict[str, str], stage: str, errors: list[str], warnings: list[str]) -> None:
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
        filename = unquote(row.get("filename", "").strip("`"))
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
    for raw_link in image_links(article):
        if re.match(r"https?://", raw_link):
            continue
        clean = unquote(raw_link.split("#", 1)[0])
        asset = (work / clean).resolve()
        try:
            asset.relative_to(project.resolve())
        except ValueError:
            errors.append(f"article.md: image escapes project directory: {raw_link}")
            continue
        if not asset.is_file():
            errors.append(f"article.md: linked image does not exist: {raw_link}")
        elif asset.suffix.lower() not in IMAGE_SUFFIXES or not valid_image(asset):
            errors.append(f"article.md: linked image is invalid or unsupported: {raw_link}")
        elif asset.suffix.lower() == ".png" and "warm-paper-tech" in texts.get("visual-plan.md", ""):
            dimensions = bitmap_dimensions(asset)
            if dimensions:
                width, height = dimensions
                if not 1.75 <= width / height <= 1.84:
                    message = f"article.md: warm-paper-tech PNG is not 16:9: {raw_link} ({width}x{height})"
                    (errors if stage == "release" else warnings).append(message)
        status = statuses.get(clean, statuses.get(Path(clean).name))
        if stage == "release" and status != "accepted":
            errors.append(f"article.md: linked image is not accepted in visual-plan.md: {raw_link}")
        elif status and status != "accepted":
            warnings.append(f"article.md: linked image status is {status}: {raw_link}")


def check_article(texts: dict[str, str], errors: list[str]) -> None:
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
    if stage == "release":
        if not re.search(r"Naturalness audit", qa, re.I):
            errors.append("qa-report.md: missing naturalness audit")
        if re.search(r"Naturalness audit[\s\S]{0,500}Result:\s*(?:NOT RUN|PENDING)", qa, re.I):
            errors.append("qa-report.md: naturalness audit was not reviewed")


def validate_final_package(project: Path, allow_work: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    work = project / ".writer-work"
    if work.exists() and not allow_work:
        errors.append("final package still contains .writer-work")

    root_entries = [entry for entry in project.iterdir() if entry.name != ".writer-work"]
    root_articles = [entry for entry in root_entries if entry.is_file() and entry.suffix.lower() == ".md"]
    if len(root_articles) != 1:
        errors.append(f"final package requires exactly one root Markdown article, found {len(root_articles)}")
    allowed_roots = {"illustrations"}
    if root_articles:
        allowed_roots.add(root_articles[0].name)
    for entry in root_entries:
        if entry.name not in allowed_roots:
            errors.append(f"unexpected final root entry: {entry.name}")
        if entry.is_symlink():
            errors.append(f"symlink is not allowed in final package: {entry.name}")

    illustrations = project / "illustrations"
    if not illustrations.is_dir():
        errors.append("final package is missing illustrations/")
        slug_dirs: list[Path] = []
    else:
        slug_dirs = [entry for entry in illustrations.iterdir() if entry.is_dir()]
        non_dirs = [entry.name for entry in illustrations.iterdir() if not entry.is_dir()]
        for name in non_dirs:
            errors.append(f"unexpected file directly under illustrations/: {name}")
        if len(slug_dirs) != 1:
            errors.append(f"final package requires exactly one semantic illustration directory, found {len(slug_dirs)}")

    asset_root = slug_dirs[0] if len(slug_dirs) == 1 else None
    if asset_root:
        if not SLUG.fullmatch(asset_root.name):
            errors.append(f"illustration directory is not semantic kebab-case: {asset_root.name}")
        prompts = asset_root / "prompts"
        if not prompts.is_dir():
            errors.append(f"missing prompt directory: illustrations/{asset_root.name}/prompts")
        for path in asset_root.rglob("*"):
            if path.is_symlink():
                errors.append(f"symlink is not allowed in final package: {path.relative_to(project)}")
                continue
            if path.is_dir():
                if path != prompts:
                    errors.append(f"unexpected nested directory: {path.relative_to(project)}")
                continue
            if prompts in path.parents:
                if path.suffix.lower() != ".md":
                    errors.append(f"prompt artifact must be Markdown: {path.relative_to(project)}")
            elif path.parent != asset_root:
                errors.append(f"accepted image must be directly under the semantic slug: {path.relative_to(project)}")
            elif path.suffix.lower() not in IMAGE_SUFFIXES or not valid_image(path):
                errors.append(f"invalid or unsupported final image: {path.relative_to(project)}")

    if root_articles:
        article_path = root_articles[0]
        article = read(article_path, errors)
        hits = marker_hits(article)
        if hits:
            errors.append(f"final article has unresolved markers: {', '.join(sorted(set(hits)))}")
        if GENERIC_ARTICLE.fullmatch(article_path.name):
            errors.append(f"final article uses a generic process filename: {article_path.name}")
        h1 = [match.group(1).strip() for match in re.finditer(r"(?m)^#\s+(.+?)\s*$", article)]
        if len(h1) > 1:
            errors.append(f"final article contains multiple H1 headings: {len(h1)}")
        elif not h1:
            warnings.append("final article has no H1; preserved for legacy compatibility")
        for raw_link in image_links(article):
            if re.match(r"https?://", raw_link):
                continue
            clean = unquote(raw_link.split("#", 1)[0])
            asset = (article_path.parent / clean).resolve()
            if asset_root:
                try:
                    asset.relative_to(asset_root.resolve())
                except ValueError:
                    errors.append(f"final article image must live under illustrations/{asset_root.name}: {raw_link}")
                    continue
            if not asset.is_file():
                errors.append(f"final article linked image does not exist: {raw_link}")
    return errors, warnings


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not project.is_dir():
        errors.append(f"project directory does not exist: {project}")
    elif args.stage == "final":
        errors, warnings = validate_final_package(project)
    else:
        work = project / ".writer-work"
        if not work.is_dir():
            errors.append("missing working directory: .writer-work")
        else:
            check_metadata(project, work, errors)
            texts = check_required_files(work, args.stage, errors)
            evidence_ids = check_evidence(texts, args.stage, errors, warnings)
            check_evidence_references(texts, evidence_ids, errors)
            check_visuals(project, work, texts, args.stage, errors, warnings)
            check_article(texts, errors)
            check_qa(texts, args.stage, errors)
            if args.require_html and not (work / "article.html").is_file():
                errors.append("missing required file: .writer-work/article.html")

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
