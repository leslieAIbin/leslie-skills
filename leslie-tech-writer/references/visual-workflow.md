# Visual workflow

## Default preset: `warm-paper-tech`

Use this article-level preset for Chinese technical WeChat articles unless the
user requests another style. It is distilled from Leslie's local KV-Cache
article package and must not overwrite global Leslie Skills preferences.

### Canvas and language

- aspect ratio: `16:9`;
- normal target: `1376×768` or the backend's nearest 1K 16:9 output;
- language: Simplified Chinese;
- output: PNG for bitmap infographics, SVG only for diagrams that require
  deterministic labels and geometry;
- text: large, sparse, horizontal, and readable on a phone.

### Visual character

- warm handmade educational infographic;
- cream paper background with subtle texture;
- paper-cut cards, small natural shadows, rounded imperfect edges;
- hand-drawn brown outlines and arrows;
- technical but friendly, structured rather than decorative;
- one visual thesis per image.

### Canonical palette

| Role | Color |
|---|---|
| paper background | `#FFFAF0` |
| primary orange | `#ED8936` |
| golden accent | `#F6AD55` |
| soft blue | `#BEE3F8` |
| pale green | `#C6F6D5` |
| success green | `#68D391` |
| pale yellow | `#FEFCBF` |
| deep brown | `#744210` |
| body charcoal | `#4A4A4A` |
| divider gray | `#E2E8F0` |

Do not require every color in every image. Preserve the cream-orange-brown
identity and use blue, green, or yellow to encode meaning consistently.

### Negative constraints

No dark background, glossy corporate 3D, neon cyberpunk treatment, tiny text,
photorealistic stock characters, logo, watermark, fake UI, or ornamental data.

## Plan before generating

Create `visual-plan.md` with one row per asset:

- asset ID and intended filename;
- section and reader question;
- visual thesis;
- evidence IDs and exact labels/data;
- format and layout;
- Leslie skill handoff;
- generation status and QA status.

Typical routing:

| Need | Skill | Suitable layout |
|---|---|---|
| cover metaphor | `leslie-cover-image` or `leslie-image-gen` | central object plus 3–4 supporting cards |
| concept comparison | `leslie-infographic` | split comparison or before/after |
| component anatomy | `leslie-infographic` | structural breakdown |
| execution path | `leslie-diagram` when exactness dominates; otherwise `leslie-infographic` | horizontal pipeline |
| article-wide illustration plan | `leslie-article-illustrator` | section-by-section storyboard |

For a substantial long-form article, start with one cover and three to five
explanatory visuals. Add more only when each image removes real explanation
cost. Screenshots and deterministic SVG diagrams may replace generated images.

## Prompt contract

Save prompts under `prompts/` before generation. Every prompt must contain:

1. `PURPOSE` — the question the image answers;
2. `VISUAL THESIS` — the single relationship the viewer should remember;
3. `LAYOUT` — named zones and reading order;
4. `EXACT TEXT` — a small allowlist of labels copied from the article;
5. `DATA` — numbers, formulas, direction, and evidence IDs;
6. `STYLE` — `warm-paper-tech` characteristics and palette;
7. `NEGATIVE` — forbidden content and common failure modes;
8. `OUTPUT` — 16:9, Simplified Chinese, 1K PNG unless specified otherwise.

Use reference images only for style or palette unless direct composition reuse
is explicitly requested. Do not ask the model to infer technical labels from a
reference image.

## Generation sequence

1. Confirm the visual plan and generation scope unless the user explicitly
   asked for direct generation.
2. Generate in batches of at most two, respecting the current Leslie skill
   configuration.
3. Preserve prompts and every candidate image.
4. Inspect each image at original or high detail.
5. If a label or technical relation is wrong, revise the prompt and regenerate;
   do not draw corrected text over the bitmap.
6. Link only accepted assets from `article.md` and record their status in
   `visual-plan.md`.

## Strict visual QA

An image fails if any item below fails:

- **Text fidelity:** every visible Chinese/English label matches the exact-text
  allowlist; no garbled glyphs, unwanted quotation marks, truncation, or fake
  words.
- **Uniqueness:** no duplicated layer number, component, token label, step, or
  legend entry unless duplication is semantically required.
- **Data fidelity:** numbers, formulas, units, versions, and comparisons match
  `article.md` and the cited evidence.
- **Relationship fidelity:** arrows, order, nesting, ownership, and before/after
  states express the intended mechanism.
- **Visual hierarchy:** title, main relation, labels, and annotation are readable
  at mobile width; minor labels do not overpower the thesis.
- **Style consistency:** cream paper, warm accents, brown line work, natural
  cards, and restrained blue/green/yellow accents remain consistent.
- **Safety and provenance:** no logos, watermarks, private data, misleading UI,
  or unlicensed copied artwork.

Record each result as `accepted`, `regenerate`, `replace-with-svg`, or `omit`.
“Pretty but technically wrong” is always `regenerate` or `replace-with-svg`.
