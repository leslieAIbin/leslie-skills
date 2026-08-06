# Leslie technical writing profile

This is an editorial direction, not a phrasebook or identity imitation.

## Reader experience

Write for a technically curious Chinese reader who wants to understand the
mechanism and make a decision, not merely recognize terminology. The article
should feel like an experienced engineer showing the shortest trustworthy path
from a concrete puzzle to a reusable mental model.

## Preferred movement

1. Start from a real symptom, result, engineering friction, or question.
2. Surface the intuitive explanation, then show where it is incomplete.
3. Use evidence and a mechanism to resolve the tension.
4. Translate the mechanism into implementation, diagnosis, or a decision.
5. State tradeoffs, failure modes, and boundaries.
6. End with a compact transfer: what the reader can now recognize or do.

## Voice and rhythm

- Use direct, calm Chinese with a visible engineering judgment.
- Prefer concrete nouns and verbs over ceremonial transitions.
- Keep paragraphs short enough for mobile reading, but do not force every
  sentence onto its own line.
- Mix explanation, examples, code, tables, and visuals according to information
  need rather than a fixed decorative rhythm.
- Use rhetorical questions only when the next passage actually answers them.
- Introduce English terms once with a useful Chinese interpretation; do not
  repeat bilingual labels everywhere.
- Return to the thesis after a long technical branch.

## What makes the article recognizably Leslie's

- a concrete engineering entry point;
- a central judgment that can be challenged and defended;
- mechanisms connected to artifacts, measurements, or source code;
- respect for constraints and failed paths;
- an explanation that can be converted into a diagram;
- a conclusion that gives a decision rule rather than a slogan.

## Avoid

- generic openings such as “随着科技飞速发展”;
- borrowed catchphrases, mannerisms, anecdotes, or endings;
- fabricated first-person testing or emotional detail;
- sensational certainty unsupported by evidence;
- five consecutive sections that only enumerate background;
- repeated “本质上”“简单来说” without adding a sharper model;
- summaries that merely repeat headings.

## Title guidance

Draft the title after the thesis and evidence are stable. A good title exposes
the object and the unresolved question or practical consequence. It may use a
contrast, but must not promise a result the article does not demonstrate.

Keep a factual working title in `brief.md` and record up to five candidates in
`qa-report.md`. Reject titles that exaggerate numbers, novelty, universality,
or firsthand experience.
