# Research package schema

Required files:

- `project.json`: package metadata and workflow status.
- `research-brief.md`: question, decision, scope, freshness, exclusions.
- `claims.json`: claim inventory and source links.
- `source-ledger.json`: inspected source records.
- `research-summary.md`: evidence, inference, uncertainty, conflicts, open questions.
- `handoff.md`: structured input for `leslie-tech-writer` or another consumer.

Central claims require at least one primary source and two total sources. A single authoritative source is allowed only with a non-empty `single_source_justification`.

Source records use:

```json
{
  "id": "S1",
  "title": "Exact page title",
  "url": "https://example.com/direct-page",
  "publisher": "Publisher",
  "source_type": "official-docs",
  "primary": true,
  "published_at": "2026-08-01",
  "accessed_at": "2026-08-06",
  "claim_ids": ["C1"],
  "notes": "What was inspected and why it matters"
}
```

Claim records use:

```json
{
  "id": "C1",
  "text": "A precise testable claim",
  "importance": "central",
  "status": "verified",
  "source_ids": ["S1", "S2"],
  "single_source_justification": ""
}
```

