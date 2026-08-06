# leslie-agent-memory

Shared durable memory for Claude Code, Codex, and OpenCode. It uses Markdown as the sole fact source and a rebuildable SQLite/FTS index.

This distribution intentionally includes no vector database, embedding model, session hook, stop hook, or background service.

## Directory ownership

```text
~/.agents/skills/leslie-agent-memory/   program; managed by CC Switch
<chosen-memory-home>/                   personal data; managed by the user
  leslie-memory.json                    portable configuration and format version
  vault/                                durable Markdown facts
  state/memory.sqlite                   rebuildable index and session claims
  reports/                              audit and doctor reports
  exports/                              optional export packages
```

Initialize only after choosing the data location:

```bash
python3 scripts/memoryctl.py --home /absolute/path/to/leslie-memory init
```

Run `python3 scripts/memoryctl.py --help` for all commands.

