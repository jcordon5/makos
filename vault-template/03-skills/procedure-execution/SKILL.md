---
id: skill-procedure-execution-20260309
type: skill
title: Procedure Execution
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - operations-agent
owners:
  - operations
tags:
  - skill
  - procedures
  - execution
domain: operations
confidence: 0.94
source_type: system
source_refs:
  - 02-procedures/README.md
related:
  - 02-procedures/redactar-informe-recurrente.md
  - 03-skills/history-logging/SKILL.md
supersedes: []
skill_for: ejecutar procedimientos reutilizables y abrir workspace de trabajo
write_permissions:
  - owners
  - agents
visibility: shared
---

# Skill: Procedure Execution

## Propósito

Convertir procedimientos documentados en ejecución reproducible con workspace y trazabilidad.

## Cuándo cargarla

- hay tareas repetitivas
- se quiere evitar improvisación
- se necesita consistencia entre agentes

## Comandos disponibles

- `makos list-procedures`
- `makos run-procedure <id|titulo|path> --input k=v`
- `makos append-history --category actions --action run_procedure ...`

## Estrategia

1. localizar procedure existente
2. ejecutar en `07-workspaces/active-tasks`
3. completar checklist y salida
4. registrar resultado en history

## Restricciones

- no ejecutar procedimientos deprecados
- no saltar validación de outputs

## Ejemplos

- `makos run-procedure redactar-informe-recurrente --input periodo=2026-Q1 --input audiencia=Direccion`

## Anti-patrones

- crear un procedimiento nuevo sin comprobar si ya existe
- cerrar tarea sin registrar history

