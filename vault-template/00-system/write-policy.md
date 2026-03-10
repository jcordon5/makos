---
id: knowledge_note-write-policy-20260309
type: knowledge_note
title: Write Policy
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - system
owners:
  - governance
tags:
  - write-policy
  - safety
  - governance
domain: governance
confidence: 0.97
source_type: system
source_refs:
  - 00-system/metadata-standard.md
related:
  - 00-system/retrieval-policy.md
  - 03-skills/filesystem-governance/SKILL.md
supersedes: []
write_permissions:
  - owners
  - agents
visibility: shared
---

# Write Policy

## Hard Rules

1. Buscar notas relacionadas o duplicadas antes de crear.
2. No escribir conocimiento estable (`04-knowledge`) con baja confianza.
3. Si `confidence < 0.70`, crear en `01-inbox` o `07-workspaces`.
4. Toda escritura relevante debe registrar history en `06-history/actions|changes|decisions`.
5. No sobrescribir sin preservar snapshot previo en `06-history/changes`.
6. Exigir metadatos mínimos y validar frontmatter antes de persistir.
7. Añadir enlaces `related` a procedimientos/skills/conocimiento existente.

## Promotion Gate (inbox -> knowledge)

- validación de metadatos: OK
- evidencia o fuente enlazada
- review humano o decisión documentada
- confidence >= 0.70

