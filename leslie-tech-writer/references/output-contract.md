# Article package contract

Use one directory per article.

```text
article-project/
├── brief.md
├── evidence.md
├── outline.md
├── visual-plan.md
├── article.md
├── qa-report.md
├── article.html              # optional until release
├── prompts/                  # generation prompts
├── imgs/                     # accepted and candidate assets
└── sources/                  # optional local source notes/artifacts
```

## Required file contracts

### `brief.md`

Include mode, primary/secondary archetype, target reader, reader promise,
thesis, scope, non-goals, desired length, evidence status, and stop conditions.

### `evidence.md`

Use a Markdown table with these columns:

| ID | Claim | Type | Status | Source/artifact | Accessed/tested | Permission/notes |
|---|---|---|---|---|---|---|

IDs use `E01`, `E02`, and so on. Central claims cannot be `pending` at release.

### `outline.md`

Every section includes its question, evidence IDs, takeaway, and candidate
visual ID. A section without a thesis contribution should be removed.

### `visual-plan.md`

Use a table with these columns:

| ID | Filename | Section | Reader question | Visual thesis | Evidence/exact text | Layout | Leslie skill | Status | QA |
|---|---|---|---|---|---|---|---|---|---|

Visual IDs use `V00` for cover and `V01` onward for body assets. Allowed status:
`planned`, `prompted`, `generated`, `accepted`, `regenerate`, `replace-with-svg`,
or `omit`.

### `article.md`

Use one H1 title. Put a short summary or reader promise near the beginning.
Use relative asset links. Do not link candidate images whose visual-plan status
is not `accepted`.

### `qa-report.md`

Record stage, validator command/result, four qualitative gate results, unresolved
claims, visual QA results, title candidates, and the remaining human decisions.

## Stages

- `planning`: brief, evidence, outline, and visual plan are complete.
- `draft`: planning files plus article and QA report are complete; pending
  evidence is allowed only when visibly marked.
- `release`: no central pending claim, all linked visuals accepted, no template
  markers, and optional requested HTML exists.
