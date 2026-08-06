#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse


SECRET_RE = re.compile(r"(?:\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}\b|-----BEGIN .*PRIVATE KEY-----)")
REQUIRED_MARKDOWN = ("research-brief.md", "research-summary.md", "handoff.md")
SOURCE_TYPES = {"official-docs", "standard", "repository", "paper", "first-party", "news", "analysis", "dataset", "local-file"}


def load_json(path: Path, errors: List[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.name}")
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.name}: {exc}")
    return None


def nonempty_sections(text: str) -> bool:
    chunks = re.split(r"(?m)^##\s+", text)[1:]
    return bool(chunks) and all(len(chunk.splitlines()) > 1 and "\n".join(chunk.splitlines()[1:]).strip() for chunk in chunks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a Leslie web-research package.")
    parser.add_argument("project")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    root = Path(args.project).expanduser().resolve(strict=False)
    errors: List[str] = []
    warnings: List[str] = []
    if not root.is_dir():
        parser.error(f"not a directory: {root}")
    project = load_json(root / "project.json", errors)
    claims = load_json(root / "claims.json", errors)
    sources = load_json(root / "source-ledger.json", errors)
    if project is not None:
        for field in ("format_version", "subject", "created_at", "status"):
            if not project.get(field):
                errors.append(f"project.json missing {field}")
        if args.strict and project.get("status") != "complete":
            errors.append("strict validation requires project status=complete")
    if not isinstance(claims, list):
        errors.append("claims.json must contain a list")
        claims = []
    if not isinstance(sources, list):
        errors.append("source-ledger.json must contain a list")
        sources = []
    source_by_id: Dict[str, Dict[str, Any]] = {}
    urls: Dict[str, str] = {}
    for index, source in enumerate(sources):
        label = f"source[{index}]"
        if not isinstance(source, dict):
            errors.append(label + " must be an object")
            continue
        for field in ("id", "title", "url", "publisher", "source_type", "primary", "accessed_at", "claim_ids", "notes"):
            if field not in source or source[field] in ("", None):
                errors.append(f"{label} missing {field}")
        source_id = str(source.get("id", ""))
        if source_id in source_by_id:
            errors.append(f"duplicate source id: {source_id}")
        source_by_id[source_id] = source
        url = str(source.get("url", ""))
        parsed = urlparse(url)
        if source.get("source_type") != "local-file" and (parsed.scheme not in ("http", "https") or not parsed.netloc):
            errors.append(f"{source_id} has invalid direct URL")
        if "google.com/search" in url or "bing.com/search" in url:
            errors.append(f"{source_id} is a search-result URL, not evidence")
        if url in urls and url:
            errors.append(f"duplicate source URL: {url}")
        urls[url] = source_id
        if source.get("source_type") not in SOURCE_TYPES:
            errors.append(f"{source_id} has unsupported source_type")
        try:
            dt.date.fromisoformat(str(source.get("accessed_at", "")))
        except ValueError:
            errors.append(f"{source_id} accessed_at must be YYYY-MM-DD")
    claim_ids = set()
    for index, claim in enumerate(claims):
        label = f"claim[{index}]"
        if not isinstance(claim, dict):
            errors.append(label + " must be an object")
            continue
        for field in ("id", "text", "importance", "status", "source_ids"):
            if field not in claim or claim[field] in ("", None):
                errors.append(f"{label} missing {field}")
        claim_id = str(claim.get("id", ""))
        if claim_id in claim_ids:
            errors.append(f"duplicate claim id: {claim_id}")
        claim_ids.add(claim_id)
        refs = claim.get("source_ids", [])
        if not isinstance(refs, list):
            errors.append(f"{claim_id} source_ids must be a list")
            continue
        missing = [ref for ref in refs if ref not in source_by_id]
        if missing:
            errors.append(f"{claim_id} references unknown sources: {missing}")
        if claim.get("status") == "verified" and not refs:
            errors.append(f"{claim_id} is verified without a source")
        if claim.get("importance") == "central" and claim.get("status") == "verified":
            primary_count = sum(1 for ref in refs if source_by_id.get(ref, {}).get("primary") is True)
            justification = str(claim.get("single_source_justification", "")).strip()
            if primary_count < 1:
                errors.append(f"central claim {claim_id} has no primary source")
            if len(set(refs)) < 2 and not justification:
                errors.append(f"central claim {claim_id} needs two sources or single_source_justification")
    for source_id, source in source_by_id.items():
        for claim_id in source.get("claim_ids", []):
            if claim_id not in claim_ids:
                errors.append(f"{source_id} references unknown claim: {claim_id}")
    for filename in REQUIRED_MARKDOWN:
        path = root / filename
        if not path.is_file():
            errors.append(f"missing file: {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        if SECRET_RE.search(text):
            errors.append(f"secret-like content in {filename}")
        if args.strict and not nonempty_sections(text):
            errors.append(f"strict validation requires all sections filled in {filename}")
    if not claims:
        warnings.append("no claims recorded")
    if not sources:
        warnings.append("no sources recorded")
    report = {"status": "ok" if not errors else "error", "errors": errors, "warnings": warnings, "claims": len(claims), "sources": len(sources)}
    (root / "validation-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())

