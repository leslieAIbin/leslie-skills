# Memory schema

Every durable memory file must start with this frontmatter:

```yaml
---
memory_id: mem-20260806-example
title: Example durable fact
memory_type: project
status: active
agent_scope: shared
project_id: example-project
verified_at: 2026-08-06
review_after_days: 90
tags: [deployment, boundary]
---
```

Required fields:

- `memory_id`: stable unique identifier.
- `title`: one durable subject.
- `memory_type`: `preference`, `project`, `decision`, `workflow`, `fact`, `open_loop`, or `case`.
- `status`: `active`, `outdated`, or `resolved`.
- `agent_scope`: `shared`, `claude`, `codex`, or `opencode`.
- `project_id`: stable project identifier or `global`.
- `verified_at`: last real verification date in `YYYY-MM-DD` form.
- `review_after_days`: positive integer.
- `tags`: inline list.

Recommended body:

```markdown
# Title

## Current fact

State the verified current fact directly.

## Evidence

- Where it was verified.
- When it was verified.

## Consequences

- What future agents should do differently.

## History

- Date and reason for material updates.
```

When a fact is superseded, prefer updating the current file and adding a history entry. Use `status: outdated` only when the whole file is no longer current.

