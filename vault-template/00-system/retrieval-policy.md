---
id: knowledge_note-retrieval-policy-20260309
type: knowledge_note
title: Retrieval Policy
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - system
owners:
  - governance
tags:
  - retrieval
  - search
  - policy
domain: governance
confidence: 0.96
source_type: system
source_refs:
  - 08-indexes/knowledge-index.md
related:
  - 00-system/write-policy.md
  - 03-skills/search-before-create/SKILL.md
supersedes: []
write_permissions:
  - owners
  - agents
visibility: shared
---

# Retrieval Policy

## Orden de recuperación recomendado

1. `08-indexes/*`
2. `02-procedures`
3. `03-skills`
4. `04-knowledge`
5. `05-memory/shared` y `05-memory/sessions`
6. `01-inbox` y `07-workspaces`

## Estrategia mínima

- buscar por título y etiquetas
- buscar por texto libre
- revisar enlaces `related` y `source_refs`
- sugerir relacionados antes de crear contenido nuevo

## Criterio de suficiencia

Si existe procedimiento/skill aplicable, reutilizarlo antes de crear uno nuevo.

