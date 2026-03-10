---
id: knowledge_note-metadata-standard-20260309
type: knowledge_note
title: Metadata Standard
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - system
owners:
  - governance
tags:
  - metadata
  - yaml
  - schema
domain: governance
confidence: 0.98
source_type: system
source_refs:
  - /schemas/frontmatter.schema.json
related:
  - 00-system/conventions.md
  - 09-templates/knowledge-note.md
supersedes: []
write_permissions:
  - owners
  - agents
visibility: shared
---

# Metadata Standard

Campos comunes (obligatorios para todas las notas):

- `id`
- `type`
- `title`
- `status`
- `created_at`
- `updated_at`
- `authors`
- `owners`
- `tags`
- `visibility`
- `write_permissions`

Campos por contexto:

- `domain`
- `confidence`
- `source_type`
- `source_refs`
- `related`
- `supersedes`
- `procedure_for`
- `skill_for`
- `review_due`
- `checksum` (opcional)

## Obligatorios por tipo

- `procedure`: `procedure_for`, `related`
- `skill`: `skill_for`
- `knowledge_note`: `domain`, `confidence`, `source_type`
- `memory_entry`: `source_type`
- `decision_log`: `source_type`, `source_refs`
- `scratchpad`: solo comunes
- `index`: solo comunes
- `review_item`: `review_due`
- `history_entry`: `source_type`, `source_refs`

## Reglas

- `confidence` debe estar en `[0,1]`
- `created_at`, `updated_at`, `review_due` en ISO-8601
- `id` con patrón `^[a-z0-9][a-z0-9._-]+$`
- listas siempre representadas como arrays YAML

