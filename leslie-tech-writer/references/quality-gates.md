# Quality gates

Mechanical validation supports these gates but does not replace editorial
judgment. A release package must pass all four.

## Gate 1 — Evidence and truth

- Every central factual claim maps to an evidence ID.
- First-person claims map to verified `experience` or `experiment` evidence.
- Numbers retain definition, baseline, conditions, date/version, and source.
- Current claims have been checked against authoritative current sources.
- Opinions and inferences are labeled as such.
- No secret, private identifier, or unauthorized internal artifact appears.

Fail the release when a central claim is pending, contradictory, or invented.

## Gate 2 — Argument and reader value

- The opening creates a concrete problem or tension.
- The thesis is explicit and remains the organizing line.
- Each section answers a necessary question and changes what the reader knows or
  can do.
- Examples, background, and comparisons return to the thesis.
- Tradeoffs and unsuitable cases are visible.
- The conclusion provides a reusable mental model or decision rule.
- The speaking position is explicit: direct experience, sourced knowledge,
  uncertainty, and judgment changes are not blurred together.
- Each paragraph adds a fact, mechanism, example, distinction, consequence, or
  supported judgment change; repeated paraphrases have been cut.

Fail when the article is a source summary, feature list, or generic tutorial
without a defensible perspective.

## Gate 3 — Technical and visual correctness

- Code, commands, paths, versions, formulas, diagrams, and screenshots are
  internally consistent and reproducible where promised.
- All linked visual files exist.
- Each linked generated visual is `accepted` in `visual-plan.md`.
- Visible labels, numbers, arrows, order, nesting, and counts match the article
  and evidence ledger exactly.
- No garbled Chinese, duplicate layer/token labels, invented components,
  truncated text, watermark, or misleading decorative data remains.
- Style follows `warm-paper-tech` unless another approved preset is recorded.

Fail a technically inaccurate image even when its visual quality is high.
Prefer deterministic SVG through `leslie-diagram` when generated typography or
geometry cannot meet this gate.

## Gate 4 — Voice, naturalness, and publication readiness

- Title promise matches the demonstrated result.
- Mobile scanability, headings, paragraph rhythm, tables, code, captions, and
  image order have been reviewed.
- `scripts/check_naturalness.py` has been run and every warning has been
  accepted with a reason or corrected; the tool is advisory, not an authorship
  detector.
- Sentence and paragraph lengths vary with the reasoning. The draft does not
  rely on rows of slogan-like single sentences, fake reader misconceptions,
  repeated insight signposts, or three-part template lists.
- Subjects and actions arrive early enough to follow. Necessary technical terms
  may repeat; decorative synonyms and inflated nominalizations do not blur the
  mechanism.
- First-person presence is backed by the evidence ledger. No anecdote,
  uncertainty, emotion, or concrete detail was invented to create “humanity”.
- External links and citations are present and useful.
- There are no TODOs, placeholders, template markers, debug notes, or rejected
  image candidates linked from the article.
- WeChat HTML, when requested, matches the Markdown and does not silently drop
  code, formulas, diagrams, images, or citations.
- Publishing remains a human action; the workflow may prepare a draft only.
- Finalization happens only after release passes. The durable directory then
  contains only the title-named Markdown, retained prompts, and accepted images.

## Reporting format

For each gate record `PASS`, `WARN`, or `FAIL`, followed by evidence and the
smallest corrective action. Any `FAIL` prevents release-ready status.
