---
id: index-skill-registry-readme-20260310
type: index
title: Agent Skill Registry
status: active
created_at: 2026-03-10T00:00:00Z
updated_at: 2026-03-10T00:00:00Z
authors:
  - system
owners:
  - platform
tags:
  - skills
  - registry
  - agent-runtime
visibility: shared
write_permissions:
  - owners
  - agents
source_refs:
  - 03-skills/README.md
related:
  - 03-skills/enabled/README.md
  - 03-skills/disabled/README.md
supersedes: []
---

# Agent Skill Registry

Directorio para bundles de skills compatibles con runtimes de agentes como Claude Code.

## Reglas

- cada bundle vive en `03-skills/registry/<skill-name>/`
- cada bundle debe incluir `SKILL.md`
- `SKILL.md` usa frontmatter estilo Claude (`name`, `description`)
- recursos opcionales permitidos: `references/`, `scripts/`, `assets/`, `agents/openai.yaml`

## Operaciones

- registrar bundle: `makos install-skill <path>`
- habilitar runtime: `makos enable-skill <name>`
- deshabilitar runtime: `makos disable-skill <name>`
