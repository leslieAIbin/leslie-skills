#!/usr/bin/env python3

from __future__ import annotations

import binascii
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib


SKILL = Path(__file__).resolve().parent.parent
VALIDATE = SKILL / "scripts" / "validate_article_package.py"
INIT = SKILL / "scripts" / "init_article_project.py"
FINALIZE = SKILL / "scripts" / "finalize_article_package.py"
NATURALNESS = SKILL / "scripts" / "check_naturalness.py"
STATIC = SKILL / "scripts" / "validate_skill.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        text=True,
        capture_output=True,
        check=False,
    )


def png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)


def write_png(path: Path, width: int = 160, height: int = 90) -> None:
    raw = b"".join(b"\x00" + (b"\xff\xfa\xf0" * width) for _ in range(height))
    png = b"\x89PNG\r\n\x1a\n"
    png += png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += png_chunk(b"IDAT", zlib.compress(raw))
    png += png_chunk(b"IEND", b"")
    path.write_bytes(png)


def write_valid_package(project: Path) -> None:
    work = project / ".writer-work"
    assets = project / "illustrations" / "kv-cache-boundary"
    (work / "candidates").mkdir(parents=True)
    (work / "sources").mkdir()
    (assets / "prompts").mkdir(parents=True)
    (work / "project.json").write_text(
        json.dumps({"format_version": 2, "title": "KV Cache 到底在缓存什么", "slug": "kv-cache-boundary", "mode": "full-production"}, ensure_ascii=False),
        encoding="utf-8",
    )
    (work / "brief.md").write_text(
        "# KV Cache brief\n\n- Mode: full-production\n- Primary archetype: architecture deep dive\n"
        "- Target reader: 推理工程师\n- Reader promise: 理解缓存边界\n- Thesis: KV Cache 用空间换解码计算\n"
        "\n## Scope\n推理解码路径。\n\n## Non-goals\n不讨论训练。\n",
        encoding="utf-8",
    )
    (work / "evidence.md").write_text(
        "# Evidence ledger\n\n"
        "| ID | Claim | Type | Status | Source/artifact | Accessed/tested | Permission/notes |\n"
        "|---|---|---|---|---|---|---|\n"
        "| E01 | KV Cache 保存注意力键值状态 | source | verified | 官方技术文档 | 2026-08-06 | 可引用 |\n",
        encoding="utf-8",
    )
    (work / "outline.md").write_text(
        "# Outline\n\n## 问题\n- Question: 为什么解码慢\n- Evidence: E01\n"
        "- Takeaway: 找到重复计算\n- Visual: V01\n",
        encoding="utf-8",
    )
    (work / "visual-plan.md").write_text(
        "# Visual plan\n\nPreset: `warm-paper-tech`\n\n"
        "| ID | Filename | Section | Reader question | Visual thesis | Evidence/exact text | Layout | Leslie skill | Status | QA |\n"
        "|---|---|---|---|---|---|---|---|---|---|\n"
        "| V01 | ../illustrations/kv-cache-boundary/01-cache.png | 机制 | 缓存什么 | 缓存避免重复计算 | E01; KV Cache | structural breakdown | leslie-infographic | accepted | PASS |\n",
        encoding="utf-8",
    )
    (work / "article.md").write_text(
        "# KV Cache 到底在缓存什么\n\nKV Cache 用空间换取解码阶段的重复计算。\n\n"
        "## 缓存边界\n\n![缓存结构](../illustrations/kv-cache-boundary/01-cache.png)\n\n证据见 E01。\n",
        encoding="utf-8",
    )
    (work / "qa-report.md").write_text(
        "# QA report\n\n- Stage: release\n- Validator result: PASS\n\n"
        "## Gate 1 — Evidence and truth\nStatus: PASS\n证据可追溯。\n\n"
        "## Gate 2 — Argument and reader value\nStatus: PASS\n主线明确。\n\n"
        "## Gate 3 — Technical and visual correctness\nStatus: PASS\n文字和数据一致。\n\n"
        "## Gate 4 — Voice, naturalness, and publication readiness\nStatus: PASS\n移动端可读。\n\n"
        "### Naturalness audit\n- Result: REVIEWED\n- Findings reviewed: none\n",
        encoding="utf-8",
    )
    (work / "article.html").write_text("<h1>KV Cache 到底在缓存什么</h1>", encoding="utf-8")
    (assets / "prompts" / "01-cache.md").write_text("# Prompt\n\nKV Cache mechanism illustration.\n", encoding="utf-8")
    write_png(assets / "01-cache.png")


class ValidatorTests(unittest.TestCase):
    def test_skill_static_validation(self) -> None:
        result = run(str(STATIC))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_initialized_skeleton_fails_until_completed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            created = run(str(INIT), str(project), "--title", "测试文章", "--slug", "test-article")
            self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
            checked = run(str(VALIDATE), str(project), "--stage", "planning")
            self.assertEqual(checked.returncode, 1)
            self.assertIn("unresolved markers", checked.stdout)

    def test_valid_release_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            write_valid_package(project)
            result = run(str(VALIDATE), str(project), "--stage", "release", "--require-html")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Result: PASS", result.stdout)

    def test_release_rejects_pending_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            write_valid_package(project)
            evidence = (project / ".writer-work" / "evidence.md").read_text(encoding="utf-8").replace("verified", "pending")
            (project / ".writer-work" / "evidence.md").write_text(evidence, encoding="utf-8")
            result = run(str(VALIDATE), str(project), "--stage", "release")
            self.assertEqual(result.returncode, 1)
            self.assertIn("pending evidence blocks release", result.stdout)

    def test_release_rejects_unaccepted_or_wrong_aspect_visual(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            write_valid_package(project)
            plan = (project / ".writer-work" / "visual-plan.md").read_text(encoding="utf-8").replace("accepted | PASS", "regenerate | FAIL")
            (project / ".writer-work" / "visual-plan.md").write_text(plan, encoding="utf-8")
            write_png(project / "illustrations" / "kv-cache-boundary" / "01-cache.png", 100, 100)
            result = run(str(VALIDATE), str(project), "--stage", "release")
            self.assertEqual(result.returncode, 1)
            self.assertIn("status regenerate blocks release", result.stdout)
            self.assertIn("is not 16:9", result.stdout)

    def test_release_rejects_failed_qualitative_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            write_valid_package(project)
            qa = (project / ".writer-work" / "qa-report.md").read_text(encoding="utf-8").replace("Status: PASS", "Status: FAIL", 1)
            (project / ".writer-work" / "qa-report.md").write_text(qa, encoding="utf-8")
            result = run(str(VALIDATE), str(project), "--stage", "release")
            self.assertEqual(result.returncode, 1)
            self.assertIn("qualitative gate is marked FAIL", result.stdout)

    def test_finalizer_keeps_only_article_prompts_and_accepted_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            write_valid_package(project)
            result = run(str(FINALIZE), str(project), "--confirm-delete-work", "--filename", "KV Cache全景拆解")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertFalse((project / ".writer-work").exists())
            self.assertTrue((project / "KV Cache全景拆解.md").is_file())
            checked = run(str(VALIDATE), str(project), "--stage", "final")
            self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)

    def test_finalizer_preserves_work_when_release_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            write_valid_package(project)
            evidence = (project / ".writer-work" / "evidence.md").read_text(encoding="utf-8").replace("verified", "pending")
            (project / ".writer-work" / "evidence.md").write_text(evidence, encoding="utf-8")
            result = run(str(FINALIZE), str(project), "--confirm-delete-work")
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((project / ".writer-work").is_dir())

    def test_finalizer_requires_explicit_cleanup_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "article"
            write_valid_package(project)
            result = run(str(FINALIZE), str(project))
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue((project / ".writer-work").is_dir())

    def test_naturalness_scan_is_advisory_and_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            article = Path(tmp) / "draft.md"
            original = "# 测试\n\n你以为缓存只影响吞吐，其实它也影响首字延迟。\n"
            article.write_text(original, encoding="utf-8")
            result = run(str(NATURALNESS), str(article))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("performative-reversal", result.stdout)
            self.assertEqual(article.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
