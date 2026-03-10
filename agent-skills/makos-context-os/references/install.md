# Install

Use this reference only when MAKOS is not yet available on the machine or the user explicitly asks to install or activate it.

## Goal

Leave the machine with:

1. global vault at `~/.makos/vault`
2. global launcher at `~/.makos/bin/makos`
3. Claude-compatible skill enabled in `~/.claude/skills/makos-context-os`

## Installation path

If you are inside the MAKOS repo:

```bash
./makos agent-ready --json
```

This bootstraps the global runtime and enables the core MAKOS skill.

If you are not inside the MAKOS repo:

1. Ask the user for the repo path, or locate it if they already opened it somewhere accessible.
2. Run the repo launcher:

```bash
/path/to/makos/makos agent-ready --json
```

## Existing vault

If the user says they already have a MAKOS vault, ask for the path and run:

```bash
/path/to/makos/makos --vault /path/to/existing-vault agent-ready --json
```

This persists the chosen vault into the global MAKOS config for future sessions.
