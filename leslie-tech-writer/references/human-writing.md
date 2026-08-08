# Human, grounded Chinese technical prose

This reference adapts general methods from
[`KKKKhazix/human-writing`](https://github.com/KKKKhazix/human-writing), version
1.1.0, inspected at commit `4fda173f3fef7fb808f3eba991eeb2528ea4b189`.
The upstream project is MIT licensed. Copyright © 2026 Khazix. The original
license and permission notice are available in the linked repository.

Use these methods to make Leslie's writing sound like a technically experienced
person making a specific judgment. Do not imitate Khazix's identity, stock
phrases, or sentence-level voice.

## Material comes before tone

For substantial nonfiction, make sure the draft has enough concrete material to
move forward without paraphrasing itself. Useful anchors include a repository
location, an executable experiment, a measured result with conditions, a
primary document, an exact quotation, a failure mode, a comparison, or an
inspectable artifact.

Five distinct anchors is a useful readiness heuristic for an article longer
than roughly 1,200 Chinese characters, not a replacement for the evidence
ledger. If the material is insufficient, research, ask for the missing input,
or narrow the article. Never manufacture decorative detail to simulate lived
experience.

## Establish the speaking position

Before drafting, answer four questions in `brief.md`:

1. What does Leslie know directly, and from which permitted artifact or test?
2. What is known only through attributed sources?
3. What remains uncertain or disputed?
4. Which specific evidence changed or sharpened the article's judgment?

The prose can use “我” only where the evidence ledger supports that access.
Human presence comes from a traceable point of view and honest limits, not from
invented anecdotes, slang, profanity, or staged hesitation.

## Make every paragraph move

Each paragraph must add at least one of these:

- a new fact or observed result;
- a mechanism, action, or causal step;
- a concrete example or counterexample;
- a distinction, condition, tradeoff, or boundary;
- a consequence for the reader's engineering decision;
- a genuine judgment change supported by new material.

Two paragraphs that only restate the same conclusion in different words should
be merged or cut. Transitions should follow the actual reasoning; avoid
announcing depth with phrases such as “更深层次的是” when no new material
arrives.

## Let technical Chinese breathe

- Put the actor and action early; move long qualifications after the sentence
  trunk when possible.
- Mix short judgments with longer explanatory sentences. Do not make every
  paragraph a single slogan-like sentence or every sentence the same length.
- Repeat the precise technical noun when a pronoun or synonym would make the
  mechanism less clear.
- Use conjunctions only when they express a real relation. Chinese often joins
  adjacent clauses through order and context.
- Prefer direct verbs over inflated nominalizations such as “进行了优化” when
  “优化了” says the same thing.
- Keep domain terms such as “链路、闭环、对齐” when they are technically exact;
  remove them when they merely raise the tone.

## Patterns that require editorial review

These are signals, not automatic proof of bad writing:

- inventing a reader misconception and then overturning it to manufacture a
  revelation (“你以为……其实……”, “不是……而是……”);
- three or more clauses with the same grammatical shape;
- repeated abstract signposts that announce importance instead of showing it;
- several unrelated metaphor systems within one short section;
- giving abstract concepts decorative physical actions without explanatory
  value;
- excessive one-sentence paragraphs, highlighted “golden phrases”, colons, or
  dashes used as a repeated template.

Colons, dashes, parallel structure, and technical jargon are not globally
forbidden. Judge whether they clarify the current technical relationship.

## Naturalness revision passes

Run these after evidence and technical review, never before them:

1. **Speaker pass** — confirm every first-person statement and uncertainty has a
   real basis.
2. **Progression pass** — annotate what each paragraph adds; cut repetitions.
3. **Performance pass** — remove fake reversals, slogan rows, and inflated
   signposts.
4. **Syntax pass** — expose subjects and verbs, vary sentence and paragraph
   length, and reduce unnecessary connectives.
5. **Precision pass** — restore exact repeated terms where stylish synonyms
   would blur the mechanism.
6. **Ending pass** — end on a usable judgment, boundary, or next decision; do not
   inflate the conclusion beyond the evidence.

Run `scripts/check_naturalness.py` as an advisory scan and record its findings
in `qa-report.md`. The script cannot certify authorship or replace editorial
judgment.
