---
name: leslie-web-research
description: Leslie's canonical evidence-package router for web research. This skill must be used first for 调研、查资料、联网核验、多来源验证、证据审计、仓库/文档/论文研究、竞品比较、事实核查, and any current or niche question that needs traceable sources or a handoff to leslie-tech-writer. It initializes and validates the claim-to-source research package; native web tools or deep-research may be used only as retrieval backends inside this workflow, not instead of it. It must also trigger on private-bookmark or automatic-download requests to enforce scope. Prefer primary sources and separate evidence from inference. No separate search API, login-only data, private bookmarks, or automatic ASR is required.
---

# Leslie Web Research

Use the host's native web search/open tools. Do not request or install a separate search API merely to run this workflow. If the host has no web capability, stop and explain that limitation.

This skill owns the project folder, source ledger, claim mapping, validation, and writer handoff. A host-provided `deep-research` skill may help retrieve and challenge sources, but it does not replace this workflow or its package schema.

## Start a research package

```bash
python3 "$HOME/.agents/skills/leslie-web-research/scripts/init_research_project.py" \
  --output /absolute/path/to/research-project \
  --subject "research subject"
```

The project is a portable folder. Keep all outputs inside it.

## Research workflow

1. Define the decision, audience, scope, freshness requirement, and exclusions in `research-brief.md`.
2. Create claim IDs in `claims.json` before browsing. Mark central claims as `central`.
3. Discover broadly, then narrow. Search queries are leads, not sources.
4. Open and read sources. For technical questions, prefer official documentation, standards, repositories, changelogs, and original papers.
5. Record every used source in `source-ledger.json`. Use stable direct URLs, access dates, publisher, source type, and the claims it supports.
6. Verify central claims with one primary source plus an independent corroborating source when practical. If only one authoritative source exists, record `single_source_justification`.
7. Write `research-summary.md` with explicit sections for evidence, inference, uncertainty, conflicts, and open questions.
8. Prepare `handoff.md` for `leslie-tech-writer`: intended angle, verified facts, source IDs, disputed points, and suggested visuals.
9. Run strict validation before calling the package complete.

```bash
python3 "$HOME/.agents/skills/leslie-web-research/scripts/validate_research_package.py" \
  /absolute/path/to/research-project --strict
```

## Source rules

- Do not cite search result pages as evidence.
- Do not cite a source you did not open and inspect.
- Put the citation next to the supported claim in the final answer.
- Distinguish publication date, last-updated date, and event date.
- Mark conclusions drawn across sources as inference.
- Preserve disagreement; do not force consensus.
- Do not fabricate an access date, quote, DOI, version, benchmark, or source ID.

## Privacy and scope

This edition does not access private bookmarks, browser history, private social feeds, login-only pages, or personal archives. It does not install ASR tooling. User-supplied local files may be included only when they are explicitly in scope.

Known URLs are not downloaded automatically. Record them first, then archive only when the user requests a local copy and the site's terms permit it.

## Handoff to article writing

When the user wants an article, finish the evidence package first, then invoke `leslie-tech-writer`. The writer may change structure and language, but it must not upgrade weak evidence into a strong factual claim.
