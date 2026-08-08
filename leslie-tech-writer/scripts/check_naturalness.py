#!/usr/bin/env python3
"""Advisory scan for repetitive, performative Chinese prose shapes.

This checker is intentionally read-only and never decides whether prose is
human. Findings require contextual editorial judgment.
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path
import re
import sys


ROAD_SIGNS = (
    "更微妙的是",
    "更深层次的是",
    "还有一层",
    "值得注意的是",
    "需要指出的是",
    "从某种意义上说",
    "归根结底",
    "换句话说",
    "这意味着",
)
OPENERS = (
    "其实",
    "不过",
    "当然",
    "所以",
    "但是",
    "后来",
    "问题是",
    "更重要的是",
    "说到这里",
)
CONJUNCTIONS = ("因为", "所以", "但是", "然而", "同时", "此外", "而且", "并且", "因此")
PIVOTS = (
    re.compile(r"(?:并)?不是[^。！？\n]{0,90}而是"),
    re.compile(r"并非[^。！？\n]{0,90}而是"),
    re.compile(r"你以为[^。！？\n]{0,90}(?:其实|实际|却)"),
    re.compile(r"看似[^。！？\n]{0,90}(?:其实|实际|实则)"),
    re.compile(r"表面(?:上)?[^。！？\n]{0,90}(?:其实|实际|实则)"),
)
NOMINALIZATIONS = (
    re.compile(r"进行(?:了|一次|一场|着)?[^。，！？\n]{0,10}(?:调整|优化|升级|分析|讨论|梳理|复盘|迭代|探索|规划)"),
    re.compile(r"实现了?[^。，！？\n]{0,14}的?[^。，！？\n]{0,6}(?:提升|增长|突破|转变|落地)"),
    re.compile(r"起到了?[^。，！？\n]{0,12}的?作用"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="UTF-8 Markdown or text file")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def mask_non_prose(text: str) -> str:
    def mask(match: re.Match[str]) -> str:
        return "".join("\n" if char == "\n" else " " for char in match.group())

    for pattern in (
        re.compile(r"\A---\s*\n.*?\n---\s*(?:\n|\Z)", re.S),
        re.compile(r"```.*?```", re.S),
        re.compile(r"`[^`\n]*`"),
        re.compile(r"!?(?:\[[^\]]*\])?\([^\n)]*\)"),
        re.compile(r"https?://[^\s)>]+"),
    ):
        text = pattern.sub(mask, text)
    return text


def han_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def paragraphs(text: str) -> list[str]:
    result = []
    for block in re.split(r"\n\s*\n", text):
        clean = re.sub(r"[>*_`]", "", block).strip()
        if not clean or clean.startswith(("#", "- ", "* ", "+ ", "|")):
            continue
        if han_count(clean) >= 8:
            result.append(clean)
    return result


def sentence_cv(text: str) -> tuple[float, int] | None:
    lengths = [
        han_count(match.group())
        for match in re.finditer(r"[^。！？!?\n]+[。！？!?]", text)
        if han_count(match.group()) >= 4
    ]
    if len(lengths) < 12:
        return None
    mean = sum(lengths) / len(lengths)
    variance = sum((value - mean) ** 2 for value in lengths) / len(lengths)
    return ((variance ** 0.5) / mean, len(lengths)) if mean else None


def main() -> int:
    args = parse_args()
    try:
        original = Path(args.path).expanduser().read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        print(f"ERROR: cannot read UTF-8 prose: {error}", file=sys.stderr)
        return 2

    prose = mask_non_prose(original)
    total = han_count(prose)
    if total == 0:
        print("ERROR: no Chinese prose detected", file=sys.stderr)
        return 2

    findings: list[dict[str, object]] = []

    def add(kind: str, count: int, note: str) -> None:
        findings.append({"kind": kind, "count": count, "note": note})

    pivot_count = sum(len(pattern.findall(prose)) for pattern in PIVOTS)
    if pivot_count:
        add("performative-reversal", pivot_count, "Confirm each reversal is earned by real material; otherwise state the judgment directly.")

    sign_hits = sum(prose.count(term) for term in ROAD_SIGNS)
    if sign_hits > max(2, total // 1000):
        add("insight-signposts", sign_hits, "Replace repeated announcements of depth with the fact, mechanism, or consequence itself.")

    paras = paragraphs(prose)
    opener_counts = collections.Counter()
    for paragraph in paras:
        value = paragraph.lstrip("“‘\"（(")
        for opener in OPENERS:
            if value.startswith(opener):
                opener_counts[opener] += 1
                break
    repeated = {key: value for key, value in opener_counts.items() if value >= 4}
    if repeated:
        add("repeated-paragraph-openers", sum(repeated.values()), "Repeated openers: " + ", ".join(f"{key}×{value}" for key, value in repeated.items()))

    if len(paras) >= 10:
        one_sentence = sum(len(re.findall(r"[。！？!?]", paragraph)) <= 1 for paragraph in paras)
        if one_sentence / len(paras) >= 0.75:
            add("single-sentence-paragraph-rhythm", one_sentence, "Too many one-sentence paragraphs can sound like a row of slogans; merge where one thought needs development.")

    conjunction_hits = sum(prose.count(term) for term in CONJUNCTIONS)
    if total >= 600 and conjunction_hits * 1000 / total > 8:
        add("connective-density", conjunction_hits, "Remove connectives that do not express a necessary logical relation.")

    nominal_count = sum(len(pattern.findall(prose)) for pattern in NOMINALIZATIONS)
    if nominal_count:
        add("nominalized-actions", nominal_count, "Prefer a direct actor and verb when the longer noun phrase adds no precision.")

    lengths = sentence_cv(prose)
    if lengths and lengths[0] < 0.38:
        add("uniform-sentence-length", lengths[1], f"Sentence-length variation is low (CV {lengths[0]:.2f}); adjust only where rhythm feels mechanical.")

    result = {
        "path": str(Path(args.path).expanduser()),
        "han_characters": total,
        "advisory": True,
        "finding_count": len(findings),
        "findings": findings,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Naturalness advisory: {len(findings)} finding(s), {total} Chinese characters")
        for finding in findings:
            print(f"WARN [{finding['kind']}] {finding['count']}: {finding['note']}")
        if not findings:
            print("No covered pattern crossed the advisory threshold.")
        print("Record editorial decisions in .writer-work/qa-report.md; warnings do not prove AI authorship.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
