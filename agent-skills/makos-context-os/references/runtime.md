# Runtime

Use this reference when deciding how MAKOS should behave across multiple projects and agent sessions.

## Shared state model

- MAKOS is global shared context, not tied to the current project workspace.
- Default vault: `~/.makos/vault`
- Default launcher: `~/.makos/bin/makos`
- Default Claude user skill directory: `~/.claude/skills`

## Expected `agent-ready` behavior

`agent-ready` should leave the runtime in a known good state:

1. global launcher exists
2. vault exists or is reused
3. MAKOS core skill is registered in the MAKOS skill registry
4. MAKOS core skill is enabled for Claude

## Decision rules

Prefer the configured global vault unless the user explicitly chooses another one.

Ask the user before changing vaults when:

1. they mention an existing vault in another location
2. the task belongs to a different organization/client
3. using the wrong vault would mix sensitive contexts
