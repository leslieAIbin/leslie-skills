---
name: leslie-agent-memory
description: Manage Leslie's durable cross-agent memory for Claude Code, Codex, and OpenCode. This skill must be used whenever the user asks to 记住、长期记忆、查以前的偏好/项目事实/决策/工作流/未闭环事项, or needs memory search, 写前去重/prewrite, session claim, closeout/收尾, audit/体检, backup/export, migration, or safe removal. It must also trigger on unsafe memory requests such as storing API keys or full chat dumps so it can refuse them. Markdown is the fact source and SQLite FTS is only a rebuildable keyword index. This edition has no vector database and installs no automatic hooks.
---

# Leslie Agent Memory

Use one explicit Memory Home shared by Claude Code, Codex, and OpenCode. Keep the program and data separate:

- Program: this skill directory.
- Data: one user-selected Memory Home containing `vault/`, `state/`, `reports/`, and `exports/`.

Do not initialize a real Memory Home without the user's requested path. Do not infer that every conversation should be remembered.

If the Memory Home path is unknown, ask the user for it. Do not scan shell files, provider settings, Claude/Codex/OpenCode configuration, browser data, or the whole home directory to guess the path; those locations may contain credentials.

## Command entrypoint

Set a convenient variable for the current shell:

```bash
MEMORYCTL="$HOME/.agents/skills/leslie-agent-memory/scripts/memoryctl.py"
```

Every command accepts either `--home /absolute/path` or `LESLIE_MEMORY_HOME`. Prefer the explicit flag in automation and tests.

## Required workflow

1. Before relying on memory, run `search`, inspect the candidates, then read the referenced Markdown file. Search results are not the fact source.
2. Before writing durable memory, run `prewrite` with the proposed stable fact.
3. Follow its action:
   - `ADD`: create a new Markdown memory from the schema.
   - `UPDATE`: update the cited current memory rather than duplicating it.
   - `NOOP`: do not write.
   - `MARK_OUTDATED`: mark superseded content explicitly; do not silently erase history.
   - `MERGE_REQUIRED`: inspect the candidates and reconcile manually.
   - `ASK_USER`: stop because the proposal is sensitive or ambiguous.
4. After editing, run `claim` for each changed Markdown file with the current actor and session ID.
5. Run `closeout --dry-run`, fix blocking findings, then run `closeout`. Git commit is opt-in through `--git-commit`.

Example:

```bash
python3 "$MEMORYCTL" --home /path/to/leslie-memory search "项目部署约束" --actor codex
python3 "$MEMORYCTL" --home /path/to/leslie-memory prewrite "项目必须通过灰度环境验证后才能发布"
python3 "$MEMORYCTL" --home /path/to/leslie-memory claim \
  --actor codex --session-id "$CODEX_THREAD_ID" --file /path/to/leslie-memory/vault/项目/example.md
python3 "$MEMORYCTL" --home /path/to/leslie-memory closeout \
  --actor codex --session-id "$CODEX_THREAD_ID" --dry-run
```

For Claude use `--actor claude` and a stable Claude session ID. For OpenCode use `--actor opencode` and its session ID. If the host exposes no ID, create a task-scoped value such as `manual-20260806-project-x`; never reuse a global constant across concurrent tasks.

## What belongs in durable memory

Store only stable and useful material:

- user preferences and explicit boundaries;
- verified project facts and current state;
- decisions with rationale and consequences;
- repeatable workflows;
- unresolved work that needs continuity;
- reusable agent cases that passed review.

Do not store:

- API keys, passwords, cookies, access tokens, private keys, or connection strings;
- full chat transcripts or automatic conversation dumps;
- temporary command output, speculative guesses, or facts that were not verified;
- content the user asked not to retain.

## File format

Read [references/memory-schema.md](references/memory-schema.md) before creating or restructuring memory files. Preserve frontmatter fields. Use one current fact per durable subject when practical.

## Maintenance and portability

Use:

```bash
python3 "$MEMORYCTL" --home /path/to/home paths
python3 "$MEMORYCTL" --home /path/to/home doctor
python3 "$MEMORYCTL" --home /path/to/home audit
python3 "$MEMORYCTL" --home /path/to/home export --output /path/to/backup.tar.gz
python3 "$MEMORYCTL" --home /path/to/home migrate --target /new/path/leslie-memory
python3 "$MEMORYCTL" --home /path/to/home removal-plan
```

`migrate` copies and verifies; it never deletes the source. `removal-plan` is read-only. Removing the skill must not remove the Memory Home, and removing the Memory Home must require a separate explicit user action.

When presenting a removal plan, show resolved paths and boundaries only. Do not print a ready-to-run `rm`, `rm -rf`, or equivalent deletion command. The eventual deletion must be handled as a separate, explicitly authorized task with fresh path validation.

## Safety boundaries

- Never install or modify Claude/Codex/OpenCode hooks.
- Never create or download embedding models or vector indexes.
- Never publish or push the memory repository.
- Never let SQLite override Markdown.
- Never delete the old Memory Home during migration.
- Never use a broad recursive deletion command; show exact resolved paths first.
- Never inspect host provider settings or shell configuration merely to discover the Memory Home.
