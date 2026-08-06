#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a portable Leslie web-research package.")
    parser.add_argument("--output", required=True)
    parser.add_argument("--subject", required=True)
    args = parser.parse_args()
    output = Path(args.output).expanduser().resolve(strict=False)
    if output.exists() and any(output.iterdir()):
        parser.error(f"refusing non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    (output / "archive").mkdir(exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    project = {
        "format_version": 1,
        "subject": args.subject,
        "created_at": now,
        "status": "draft",
        "workflow": "discover-verify-package-handoff",
        "native_web_tools_only": True,
    }
    (output / "project.json").write_text(json.dumps(project, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "claims.json").write_text("[]\n", encoding="utf-8")
    (output / "source-ledger.json").write_text("[]\n", encoding="utf-8")
    (output / "research-brief.md").write_text(
        f"# {args.subject}\n\n## Decision or question\n\n## Audience\n\n## Scope\n\n## Freshness requirement\n\n## Exclusions\n",
        encoding="utf-8",
    )
    (output / "research-summary.md").write_text(
        "# Research summary\n\n## Verified evidence\n\n## Inferences\n\n## Uncertainty\n\n## Conflicts\n\n## Open questions\n",
        encoding="utf-8",
    )
    (output / "handoff.md").write_text(
        "# Handoff\n\n## Intended angle\n\n## Verified facts and source IDs\n\n## Disputed points\n\n## Suggested visuals\n",
        encoding="utf-8",
    )
    (output / "archive" / "README.md").write_text(
        "# Archive\n\nNo URL is downloaded automatically. Put explicitly requested and permitted local source copies here.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "initialized", "output": str(output)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

