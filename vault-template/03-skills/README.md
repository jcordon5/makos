---
id: index-skills-readme-20260309
type: index
title: Skills Catalog
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - system
owners:
  - operations
tags:
  - skills
  - catalog
visibility: shared
write_permissions:
  - owners
  - agents
source_refs:
  - 08-indexes/skills-index.md
related:
  - 03-skills/obsidian-cli/SKILL.md
  - 03-skills/filesystem-governance/SKILL.md
  - 03-skills/registry/README.md
supersedes: []
---

# Skills

MAKOS distingue dos capas de skills:

1. Notas operativas y procedimientos internos en `03-skills/<skill>/SKILL.md`
2. Skill bundles compatibles con runtimes de agentes en `03-skills/registry/<bundle>/SKILL.md`

Uso recomendado:

1. cargar skill relevante al problema
2. ejecutar comandos de forma reproducible
3. registrar actividad y enlaces en history

## Registry compartida

- `03-skills/registry`: bundles disponibles
- `03-skills/enabled`: manifiestos de skills activas
- `03-skills/disabled`: manifiestos de skills desactivadas

Los bundles del registry pueden sincronizarse al runtime de Claude con:

- `makos list-skills`
- `makos install-skill`
- `makos enable-skill`
- `makos disable-skill`
