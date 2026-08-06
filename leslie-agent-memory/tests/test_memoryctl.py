from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "memoryctl.py"


class MemoryCtlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="leslie-memory-test-")
        self.home = Path(self.temp.name) / "home"
        self.run_cli("init")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def run_cli(self, *args: str, expected: int = 0) -> dict:
        proc = subprocess.run(
            [sys.executable, str(CLI), "--home", str(self.home), "--json", *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(proc.returncode, expected, proc.stdout + proc.stderr)
        return json.loads(proc.stdout)

    def make_memory(self) -> Path:
        created = self.run_cli(
            "new",
            "--title",
            "发布约束",
            "--memory-type",
            "decision",
            "--project-id",
            "demo",
        )
        path = Path(created["path"])
        text = path.read_text(encoding="utf-8").replace(
            "Replace this line with the verified durable fact.",
            "部署必须先通过灰度环境验证。",
        )
        path.write_text(text, encoding="utf-8")
        return path

    def test_search_prewrite_claim_closeout_all_hosts(self) -> None:
        path = self.make_memory()
        indexed = self.run_cli("index")
        self.assertEqual(indexed["indexed"], 1)
        found = self.run_cli("search", "灰度环境", "--actor", "codex")
        self.assertEqual(found["results"][0]["title"], "发布约束")
        noop = self.run_cli("prewrite", "部署必须先通过灰度环境验证", "--actor", "claude")
        self.assertEqual(noop["action"], "NOOP")
        for actor in ("claude", "codex", "opencode"):
            text = path.read_text(encoding="utf-8").replace(
                "## Consequences\n\n- Add what future agents should do differently.",
                f"## Consequences\n\n- Validated by {actor}.",
            )
            path.write_text(text, encoding="utf-8")
            self.run_cli("claim", "--actor", actor, "--session-id", actor + "-session", "--file", str(path))
            ready = self.run_cli("closeout", "--actor", actor, "--session-id", actor + "-session", "--dry-run")
            self.assertEqual(ready["status"], "ready")
            closed = self.run_cli("closeout", "--actor", actor, "--session-id", actor + "-session")
            self.assertEqual(closed["status"], "closed")

    def test_secret_is_rejected(self) -> None:
        result = self.run_cli("prewrite", "API key = sk-example12345678901234567890")
        self.assertEqual(result["action"], "ASK_USER")

    def test_portability_and_feature_boundaries(self) -> None:
        paths = self.run_cli("paths")
        self.assertFalse(paths["program_removal_affects_data"])
        config = json.loads((self.home / "leslie-memory.json").read_text(encoding="utf-8"))
        self.assertFalse(config["features"]["vector"])
        self.assertFalse(config["features"]["automatic_hooks"])
        names = {path.name for path in (ROOT / "scripts").iterdir()}
        self.assertFalse(any("hook" in name or "zvec" in name or "vector" in name for name in names))


if __name__ == "__main__":
    unittest.main()

