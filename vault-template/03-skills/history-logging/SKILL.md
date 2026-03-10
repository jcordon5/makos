---
id: skill-history-logging-20260309
type: skill
title: History Logging
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - audit-agent
owners:
  - governance
tags:
  - skill
  - history
  - audit
domain: governance
confidence: 0.97
source_type: system
source_refs:
  - 00-system/write-policy.md
related:
  - 06-history/actions
  - 06-history/changes
  - 06-history/decisions
supersedes: []
skill_for: registrar acciones, decisiones y cambios con trazabilidad mínima
write_permissions:
  - owners
  - agents
visibility: shared
---

# Skill: History Logging

## Propósito

Asegurar observabilidad mínima de operaciones críticas en el vault.

## Cuándo cargarla

- después de crear/actualizar contenido
- al ejecutar procedimientos
- al tomar decisiones de curación

## Comandos disponibles

- `makos append-history --category actions ...`
- `makos append-history --category changes ...`
- `makos append-history --category decisions ...`

## Estrategia

1. capturar actor, acción, target y motivo
2. incluir inputs de alto nivel
3. enlazar notas relacionadas
4. guardar en categoría correcta

## Restricciones

- no registrar datos sensibles innecesarios
- no omitir motivo en decisiones

## Ejemplos

- `makos append-history --category actions --action create_note --target 01-inbox/x.md --reason "new insight"`

## Anti-patrones

- logs ambiguos sin target
- logs sin enlaces relacionados

