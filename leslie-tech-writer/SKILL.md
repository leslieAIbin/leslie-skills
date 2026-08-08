---
name: leslie-tech-writer
description: Create, restructure, review, and package Leslie-style Chinese long-form technical articles for WeChat Official Accounts. Use this skill whenever the user asks to write a 技术文章、公众号长文、工程复盘、源码或架构拆解、工具实测、教程、技术调研，or wants to turn repositories, experiments, notes, links, PDFs, transcripts, or rough drafts into a publishable article. It must also trigger for article evidence audits, outline and visual planning, Leslie-style rewrites, WeChat HTML preparation, and pre-publication quality review. Do not use for short social posts, pure translation, or image-only requests.
---

# Leslie Technical Writer

Create evidence-led Chinese technical articles with a clear point of view,
useful engineering detail, and an explicit visual plan. Treat public writing
samples as abstract references, never as identities or sentence templates.

## Read the right references

Read these files before doing the corresponding work:

- Always read `references/workflow.md`.
- Read `references/source-policy.md` when auditing facts, links, experiments,
  first-person claims, or current information.
- Read `references/archetypes.md` before choosing an outline.
- Read `references/style-profile.md` before drafting or editing prose.
- Read `references/human-writing.md` before drafting, rewriting, or running a
  naturalness review.
- Read `references/visual-workflow.md` when the output needs a cover, diagram,
  illustration, screenshot plan, infographic, or WeChat layout.
- Read `references/output-contract.md` when creating files.
- Read `references/quality-gates.md` before reporting completion.

## Choose the operating mode

Infer the least expansive mode that satisfies the request:

1. **Full production** — create an article package through draft or release.
2. **Collaborative writing** — stop after brief, outline, and first draft for
   human confirmation at each material decision.
3. **Edit/restructure** — preserve supplied facts and claims while improving
   argument, structure, clarity, rhythm, and visuals.
4. **Review only** — diagnose and report; do not rewrite unless asked.

Never treat a request to review or diagnose as permission to publish, upload,
or silently replace the source file.

## Follow the evidence gate

Before outlining, classify material into:

- Leslie's verified experience or experiment;
- a traceable public source;
- an explicitly labeled opinion or inference;
- missing or unusable information.

Create an evidence ledger using `references/output-contract.md`. A fluent
paragraph is not a substitute for evidence. Do not invent experiments,
metrics, quotations, users, internal systems, emotions, or first-person
experience.

Stop at a planning package when any central claim lacks evidence, the core
point of view is unknown, or the requested first-person story was not supplied.
List the smallest concrete inputs needed to resume.

## Route to an article archetype

Choose one primary archetype from `references/archetypes.md`, optionally one
secondary archetype. State the choice in `.writer-work/brief.md`; it determines the article
logic, not merely the title.

## Build the article package in order

1. Define reader, reader promise, core thesis, archetype, evidence state,
   material anchors, speaking position, and stop conditions in
   `.writer-work/brief.md`.
2. Record claims and sources in `.writer-work/evidence.md`.
3. Create `.writer-work/outline.md`, with every section tied to evidence IDs and a concrete
   reader takeaway.
4. Create `.writer-work/visual-plan.md` at the same time as the outline. Visuals must explain
   something; decoration alone is insufficient.
5. Draft `.writer-work/article.md` only after the evidence gate passes.
6. Run `scripts/check_naturalness.py`, review every finding contextually, and
   record the decision in `.writer-work/qa-report.md`.
7. Produce `.writer-work/qa-report.md` using all four quality gates.
8. Create `.writer-work/article.html` only when requested or when preparing a WeChat draft.
9. Never publish. `leslie-post-to-wechat` may save a draft only when the user
   explicitly asks for a WeChat draft.
10. After release validation and explicit cleanup authorization, run
    `scripts/finalize_article_package.py`. This is the only normal point at
    which `.writer-work/` and rejected candidates are deleted.

For a planning-only request, end by naming the exact planning validation
command, even when missing sources force the package to remain incomplete:

```bash
python3 scripts/validate_article_package.py /absolute/project/path --stage planning
```

Use `scripts/init_article_project.py` with a semantic English `--slug` to create
a new project package. Run
`scripts/validate_article_package.py` at the appropriate stage before claiming
the package is complete.

## Coordinate existing Leslie skills

Use rather than reimplement the existing specialist skills when their output
is needed:

- `leslie-cover-image` for covers;
- `leslie-article-illustrator` for article illustration planning;
- `leslie-diagram` for architecture, flow, sequence, or system diagrams;
- `leslie-infographic` for dense visual summaries;
- `leslie-image-gen` for generated bitmap assets;
- `leslie-markdown-to-html` for WeChat-compatible HTML;
- `leslie-post-to-wechat` for saving a draft, never public publishing.

For technical WeChat articles, use the article-level visual preset
`warm-paper-tech` from `references/visual-workflow.md` unless the user requests
another direction. This preset is local to this writing workflow; do not modify
the global `EXTEND.md` preferences of any Leslie skill.

Plan visuals through `leslie-article-illustrator`, route dense explanatory
graphics to `leslie-infographic`, and use `leslie-image-gen` as the bitmap
backend when the user asks to generate the assets. Save retained generation
prompts under `illustrations/<semantic-slug>/prompts/` before calling the
backend, and keep unaccepted candidates under `.writer-work/candidates/`.
Never repair generated text by drawing over the
bitmap: keep the rejected candidate, correct the prompt, and regenerate.

If a named skill is unavailable, preserve its planned handoff in
`visual-plan.md` or the delivery notes instead of pretending the asset exists.

## Write in Leslie's voice

Use `references/style-profile.md` as a direction, not a phrasebook:

- open from a concrete engineering friction, observation, or measured result;
- state a real judgment and support it;
- move from problem to evidence to mechanism to action;
- use technical terms precisely and explain only what the target reader needs;
- keep headings scannable and paragraphs varied in length;
- show tradeoffs, failed paths, conditions, and limits;
- return to the core thesis after examples, comparisons, and background;
- distinguish verified fact, source-backed report, and personal opinion.

Apply `references/human-writing.md` after the evidence gate:

- build from concrete material instead of expanding one point through repeated
  paraphrase;
- state what Leslie knows directly, what comes from sources, what remains
  uncertain, and what changed the judgment;
- make every paragraph add a fact, mechanism, example, distinction,
  consequence, or supported judgment change;
- put the actor and action early, vary sentence and paragraph length, and keep
  precise technical repetition when it improves clarity;
- remove performative reversals, slogan rows, empty insight signposts, and
  invented decorative detail.

Naturalness findings require editorial judgment. Do not globally ban colons,
dashes, parallel clauses, or terms such as “链路” when they express a real
technical relationship. A checker warning never overrides evidence or
technical correctness.

Do not imitate Khazix, Tencent, or another identifiable author. Do not inject
borrowed catchphrases, profanity, fixed endings, or fabricated "human" detail.
When a user asks for identity-level imitation, decline only that part and offer
the productive alternative immediately: extract high-level structure, evidence
density, explanatory rhythm, and visual strategy; keep the samples attributed;
then propose an original Leslie reader contract and thesis before drafting. In
the response, explicitly state that samples remain attributed external sources,
not Leslie's experience.

## Validate before delivery

Run the validator from the skill directory:

```bash
python3 scripts/validate_article_package.py /absolute/project/path --stage planning
python3 scripts/validate_article_package.py /absolute/project/path --stage draft
python3 scripts/validate_article_package.py /absolute/project/path --stage release --require-html
python3 scripts/check_naturalness.py /absolute/project/path/.writer-work/article.md
python3 scripts/finalize_article_package.py /absolute/project/path --confirm-delete-work
python3 scripts/validate_article_package.py /absolute/project/path --stage final
```

Then apply the qualitative gates in `references/quality-gates.md`. Fix failures
before delivery. Report warnings honestly; do not mark a package complete merely
because files exist.

Generated visuals must pass the visual evidence gate as well as aesthetic
review. Chinese labels, numbers, layer counts, formulas, arrows, and component
names must match the article and `evidence.md` exactly. A warm palette is not a
substitute for technical correctness.

When visual QA fails, explicitly report that the rejected candidate remains
preserved, and choose `regenerate` with a corrected saved prompt or
`replace-with-svg` through `leslie-diagram`. Never imply that a failed bitmap was
silently repaired or accepted. State directly that drawing corrected text over
the failed bitmap is prohibited.

## Delivery summary

Tell the user:

- which mode and archetype were used;
- what files were created or reviewed;
- whether validation passed at planning, draft, release, or final stage;
- which claims remain pending and what evidence would resolve them;
- whether any visual or WeChat draft action remains.
- whether finalization deleted `.writer-work/`, and the exact final article and
  illustration directory that remain.
