---
id: skill-search-before-create-20260309
type: skill
title: Search Before Create
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - governance-agent
owners:
  - governance
tags:
  - skill
  - search
  - dedup
domain: governance
confidence: 0.95
source_type: system
source_refs:
  - 00-system/retrieval-policy.md
related:
  - 03-skills/knowledge-curation/SKILL.md
  - 00-system/write-policy.md
supersedes: []
skill_for: buscar conocimiento, procedures y skills antes de crear nuevas notas
write_permissions:
  - owners
  - agents
visibility: shared
---

# Skill: Search Before Create

## Propósito

Reducir duplicación y mejorar reutilización de conocimiento existente.

## Cuándo cargarla

- antes de cualquier `makos create`
- cuando la tarea parezca repetitiva

## Comandos disponibles

- `makos search "query"`
- `makos list-procedures`
- `makos suggest-related "texto o path"`

## Estrategia

1. buscar por términos clave
2. revisar procedures aplicables
3. revisar notas relacionadas sugeridas
4. decidir: reutilizar, actualizar o crear

## Restricciones

- no crear nota si hay duplicado obvio salvo `--force`

## Ejemplos

- `makos search "informe recurrente"`
- `makos list-procedures`

## Anti-patrones

- crear nota directamente por defecto
- ignorar similitud alta de títulos

