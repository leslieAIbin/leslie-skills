# File ownership and removal boundaries

## Program files

Everything below the `leslie-agent-memory/` skill directory is program material. CC Switch may copy, link, update, or remove this directory.

## User data

The Memory Home is created only through an explicit `init --home ...` command. It contains all user-owned Markdown, derived indexes, reports, and exports. No user data is written into the skill directory.

## Other locations

This skill does not write into:

- `~/.local/bin/`
- `~/.config/`
- Claude, Codex, or OpenCode settings
- shell startup files
- launchd or other background-service directories

## Safe removal

1. Run `removal-plan` to display the resolved program and data locations.
2. Remove or disable the skill through CC Switch. This leaves the Memory Home untouched.
3. Archive or migrate the Memory Home if it contains wanted data.
4. Delete the Memory Home only as a separate, explicit action after inspecting its exact path.

