from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INIT = ROOT / "scripts" / "init_research_project.py"
VALIDATE = ROOT / "scripts" / "validate_research_package.py"


class ResearchPackageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="leslie-research-test-")
        self.project = Path(self.temp.name) / "project"
        proc = subprocess.run(
            [sys.executable, str(INIT), "--output", str(self.project), "--subject", "Test subject"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def validate(self, strict: bool = False) -> tuple[int, dict]:
        command = [sys.executable, str(VALIDATE), str(self.project)]
        if strict:
            command.append("--strict")
        proc = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return proc.returncode, json.loads(proc.stdout)

    def fill_markdown(self) -> None:
        for filename in ("research-brief.md", "research-summary.md", "handoff.md"):
            path = self.project / filename
            text = path.read_text(encoding="utf-8")
            lines = []
            for line in text.splitlines():
                lines.append(line)
                if line.startswith("## "):
                    lines.append("Verified content for this section.")
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_strict_package_with_primary_and_corrobating_source(self) -> None:
        project = json.loads((self.project / "project.json").read_text(encoding="utf-8"))
        project["status"] = "complete"
        (self.project / "project.json").write_text(json.dumps(project), encoding="utf-8")
        claims = [{"id": "C1", "text": "Testable claim", "importance": "central", "status": "verified", "source_ids": ["S1", "S2"], "single_source_justification": ""}]
        sources = [
            {"id": "S1", "title": "Official", "url": "https://example.com/docs", "publisher": "Example", "source_type": "official-docs", "primary": True, "published_at": "2026-08-01", "accessed_at": "2026-08-06", "claim_ids": ["C1"], "notes": "Inspected official documentation."},
            {"id": "S2", "title": "Paper", "url": "https://example.org/paper", "publisher": "Example Org", "source_type": "paper", "primary": False, "published_at": "2026-08-02", "accessed_at": "2026-08-06", "claim_ids": ["C1"], "notes": "Independent corroboration."},
        ]
        (self.project / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
        (self.project / "source-ledger.json").write_text(json.dumps(sources), encoding="utf-8")
        self.fill_markdown()
        code, report = self.validate(strict=True)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["status"], "ok")

    def test_central_claim_without_primary_is_blocked(self) -> None:
        claims = [{"id": "C1", "text": "Weak claim", "importance": "central", "status": "verified", "source_ids": ["S1"], "single_source_justification": ""}]
        sources = [{"id": "S1", "title": "Analysis", "url": "https://example.com/post", "publisher": "Example", "source_type": "analysis", "primary": False, "accessed_at": "2026-08-06", "claim_ids": ["C1"], "notes": "Secondary analysis."}]
        (self.project / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
        (self.project / "source-ledger.json").write_text(json.dumps(sources), encoding="utf-8")
        code, report = self.validate()
        self.assertEqual(code, 2)
        self.assertTrue(any("no primary source" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()

