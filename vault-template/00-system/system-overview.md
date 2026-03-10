---
id: knowledge_note-system-overview-20260309
type: knowledge_note
title: MAKOS System Overview
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - system
owners:
  - architecture
tags:
  - makos
  - architecture
  - overview
domain: platform
confidence: 0.95
source_type: system
source_refs:
  - docs/architecture.md
related:
  - 00-system/conventions.md
  - 00-system/write-policy.md
  - 00-system/agent-system-prompt.md
  - 08-indexes/procedures-index.md
supersedes: []
write_permissions:
  - owners
  - agents
visibility: shared
---

# MAKOS System Overview

MAKOS es un Knowledge OS local y portable basado en un vault de Obsidian.

## Capas

1. Vault: markdown + frontmatter YAML como fuente de verdad.
2. Convenciones canónicas: tipos de nota, políticas de lectura/escritura, taxonomía.
3. Bridge CLI (`makos`): comandos neutrales para buscar, leer, crear, validar y auditar.
4. Runtime universal: cualquier humano o agente con shell + filesystem puede operar.
5. Agent skill layer: bundles `SKILL.md` para que runtimes como Claude usen MAKOS como capacidad instalada.

## Objetivo operativo

- reutilizar procedimientos y skills antes de improvisar
- separar conocimiento estable de memoria de trabajo
- dejar trazabilidad de cambios críticos
- mantener legibilidad humana sin tooling propietario

## Flujo recomendado

1. `./makos agent-ready`
2. `./makos doctor`
3. `./makos search "tema"`
4. `./makos list-procedures`
5. `./makos run-procedure <id|titulo>`
6. `./makos create ...` o `./makos update ...`
7. `./makos append-history ...`
8. `./makos reindex`
9. `./makos list-skills`

## Runtime contract para agentes

Para agentes sin soporte nativo de skills, el prompt base está en:

- [[00-system/agent-system-prompt.md]]

Para runtimes compatibles con Claude, la skill runtime principal es:

- [[03-skills/registry/README.md]]
