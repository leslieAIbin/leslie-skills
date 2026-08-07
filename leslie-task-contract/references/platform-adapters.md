# Platform adapters

## Portable form

Use by default for Claude Code, Codex, OpenCode, handoffs, tickets and saved project plans. It begins with `任务契约` or `Task Contract` and contains the required fields without a slash command.

## Codex form

Use `/goal` only when the user asks for Codex goal syntax, is actively using a Codex goal, or needs a paste-ready command. Preserve every contract field when adapting.

## Compact form

For a small, low-risk task, keep each field to one sentence. Compact does not mean omitting verification, boundaries, completion or pause conditions.

## Existing project form

Require an initial discovery pass over repository instructions, package scripts, CI, tests and conventions. Reference only commands actually found in the project.

## High-risk form

The goal should end before the risky action. Discovery, dry-run and a preview artifact may be in scope; credential entry, production mutation, deletion, public publishing and payment require explicit approval.
