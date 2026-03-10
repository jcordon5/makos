---
id: skill-knowledge-curation-20260309
type: skill
title: Knowledge Curation and Merge
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - knowledge-agent
owners:
  - knowledge-team
tags:
  - skill
  - curation
  - dedup
domain: knowledge-ops
confidence: 0.92
source_type: system
source_refs:
  - 00-system/write-policy.md
related:
  - 03-skills/search-before-create/SKILL.md
  - 10-human-views/pending-consolidation.md
supersedes: []
skill_for: curar conocimiento y fusionar duplicados preservando trazabilidad
write_permissions:
  - owners
  - agents
visibility: shared
---

# Skill: Knowledge Curation and Merge

## Propósito

Mantener un grafo de conocimiento limpio, sin duplicados obvios y con historial de consolidación.

## Cuándo cargarla

- aparecen notas similares
- se quiere promover contenido de inbox a knowledge
- hay contradicciones entre notas

## Comandos disponibles

- `makos suggest-related <path|texto>`
- `makos search "..."`
- `makos update ... --set supersedes='[...]'`
- `makos append-history --category decisions --action merge_notes ...`

## Estrategia

1. detectar candidatos por título, tags y similitud
2. comparar y elegir nota canónica
3. mover o fusionar contenido
4. enlazar `supersedes` y registrar decisión

## Restricciones

- no borrar evidencia original sin snapshot
- no consolidar sin justificar motivo

## Ejemplos

- `makos suggest-related 01-inbox/hallazgos.md`
- `makos append-history --category decisions --action consolidate_knowledge --target 04-knowledge/... --reason "duplicates merged"`

## Anti-patrones

- fusionar notas con contextos distintos
- eliminar notas sin registrar `supersedes`

