---
name: makos-context-os
description: Use this skill whenever the user wants durable context, cross-project memory, shared procedures, audit trails, Obsidian-backed knowledge, or a reusable operating layer across multiple agent sessions. Trigger aggressively on requests to remember decisions, save findings, reuse previous workflows, coordinate several agents, maintain shared organizational context, install or activate MAKOS, or avoid starting from scratch in each conversation.
---

# MAKOS Context OS

Use MAKOS as the shared context layer between the user, their projects, and all agent sessions.

Read [references/install.md](references/install.md) if MAKOS is not yet installed or the user asks to activate it.
Read [references/runtime.md](references/runtime.md) when deciding whether to bootstrap, reuse an existing vault, or ask the user for a vault path.
Read [references/commands.md](references/commands.md) when you need concrete CLI flows.

## Core contract

1. Prefer existing knowledge and procedures before creating new content.
2. Use MAKOS for meaningful discovery, writing, and audit actions.
3. Keep outputs understandable in Obsidian for humans.
4. Treat MAKOS as global shared state, not as a project-local scratchpad.

## First action in a new session

Resolve `MAKOS_CMD` in this order:

1. `~/.makos/bin/makos` if it exists
2. `./makos` if the current workspace is the MAKOS repo
3. fallback to the repo path if the user points you to it

Then run:

```bash
$MAKOS_CMD agent-ready --json
```

If MAKOS is not installed yet, follow [references/install.md](references/install.md).

## When to ask the user

Ask before proceeding only if one of these is true:

1. The user says they already have an existing MAKOS vault but the path is unknown.
2. `agent-ready` cannot resolve or bootstrap a usable runtime.
3. There are multiple plausible vaults and using the wrong one would mix organizations or clients.

If the user says an existing vault already exists, ask for the vault path and then use:

```bash
$MAKOS_CMD --vault /path/to/vault agent-ready --json
```

## Working sequence

1. Discover: `search`, `list-procedures`, `suggest-related`
2. Reuse: `run-procedure` if an applicable one exists
3. Write safely: `create` or `update`
4. Audit: `append-history`
5. Refresh human views: `reindex` and `review-queue --write-page`

## Quality gates

Before finishing a task, confirm:

1. You searched for existing material first.
2. You reused a procedure if a relevant one existed.
3. You did not create an obvious duplicate.
4. Relevant writes were logged in history.
5. A human can open Obsidian and understand what happened.

## Response style

Speak to the user in natural language.

Do not tell the user to run MAKOS commands manually unless they explicitly ask for the commands.

In the final response, summarize:

1. What you did
2. What MAKOS artifacts were read or written
3. What needs human review next
