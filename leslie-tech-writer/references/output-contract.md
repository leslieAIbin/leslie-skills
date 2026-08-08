# Article package contract

Use one directory per article. Production files stay isolated from durable
artifacts until the release package has passed validation.

## During writing

```text
article-project/
├── .writer-work/                 # temporary; delete only during finalization
│   ├── project.json
│   ├── brief.md
│   ├── evidence.md
│   ├── outline.md
│   ├── visual-plan.md
│   ├── article.md
│   ├── qa-report.md
│   ├── article.html              # optional WeChat preparation artifact
│   ├── PROMPT-TEMPLATE.md
│   ├── candidates/               # rejected or not-yet-accepted images
│   └── sources/                  # research notes and local evidence
└── illustrations/
    └── semantic-english-slug/
        ├── prompts/              # prompts that produced retained images
        └── accepted-image.webp
```

The slug must be lowercase ASCII kebab-case and describe the article, for
example `harness-engineering`, not `article-04` or a random identifier.

## Final durable package

After release validation and explicit finalization:

```text
article-project/
├── 最终文章标题.md
└── illustrations/
    └── semantic-english-slug/
        ├── prompts/
        │   └── 01-cover.md
        └── 01-cover.webp
```

The final article filename is a meaningful stable article name. It may differ
from the publishing H1, but cannot be a generic stage name such as `article.md`,
`draft.md`, or `08-final.md`. No `.writer-work/`, HTML, JSON,
source notes, scripts, rejected images, generic `article.md`, numbered stage
drafts, or debug artifacts remain. Keep only the final Markdown, retained image
prompts, and accepted images. Finalization is destructive and must be the last
step after validation.

## Required working file contracts

### `.writer-work/project.json`

Record the working title, semantic slug, package format version, and creation
mode. Scripts use this metadata; prose does not.

### `.writer-work/brief.md`

Include mode, primary/secondary archetype, target reader, reader promise,
thesis, scope, non-goals, desired length, evidence status, stop conditions,
material anchors, and speaking position. The speaking position records what
Leslie directly knows, what comes from sources, what remains uncertain, and
what evidence changed the judgment. Never invent first-person access.

### `.writer-work/evidence.md`

Use a Markdown table with these columns:

| ID | Claim | Type | Status | Source/artifact | Accessed/tested | Permission/notes |
|---|---|---|---|---|---|---|

IDs use `E01`, `E02`, and so on. Central claims cannot be `pending` at release.

### `.writer-work/outline.md`

Every section includes its question, evidence IDs, takeaway, and candidate
visual ID. A section without a thesis contribution should be removed.

### `.writer-work/visual-plan.md`

Use a table with these columns:

| ID | Filename | Section | Reader question | Visual thesis | Evidence/exact text | Layout | Leslie skill | Status | QA |
|---|---|---|---|---|---|---|---|---|---|

Visual IDs use `V00` for cover and `V01` onward for body assets. Accepted
filenames point to `../illustrations/<slug>/...` from `.writer-work/article.md`.
Candidates belong under `.writer-work/candidates/`. Allowed status: `planned`,
`prompted`, `generated`, `accepted`, `regenerate`, `replace-with-svg`, or
`omit`.

### `.writer-work/article.md`

Use one H1 title. Put a short summary or reader promise near the beginning.
Use relative asset links. Do not link candidate images whose visual-plan status
is not `accepted`.

### `.writer-work/qa-report.md`

Record stage, validator command/result, all qualitative gate results,
naturalness audit findings, unresolved claims, visual QA results, title
candidates, and remaining human decisions.

## Stages

- `planning`: brief, evidence, outline, and visual plan are complete.
- `draft`: planning files plus article and QA report are complete; pending
  evidence is allowed only when visibly marked.
- `release`: no central pending claim, all linked visuals accepted, no template
  markers, naturalness findings reviewed, and requested HTML exists.
- `final`: `.writer-work/` is gone and only the title-named final Markdown plus
  `illustrations/<slug>/prompts/` and accepted image files remain.

Use `scripts/finalize_article_package.py` only after `release` passes and the
user has authorized deleting process files. Then run the validator at `final`.
