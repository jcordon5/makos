---
id: procedure-preparar-prompt-operativo-reutilizable-20260309
type: procedure
title: Preparar prompt operativo reutilizable para tarea empresarial
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - promptops-agent
owners:
  - promptops
tags:
  - procedure
  - prompts
  - operations
domain: prompt-operations
confidence: 0.9
source_type: derived
source_refs:
  - 00-system/conventions.md
related:
  - 03-skills/procedure-execution/SKILL.md
  - 03-skills/knowledge-curation/SKILL.md
  - 09-templates/procedure.md
supersedes: []
procedure_for: crear prompts repetibles, auditables y adaptables a distintos agentes
write_permissions:
  - owners
  - agents
visibility: shared
review_due: 2026-06-30T00:00:00Z
---

# Preparar prompt operativo reutilizable

## Propósito

Diseñar prompts que puedan ejecutarse en cualquier agente con shell sin acoplarse a un proveedor.

## Cuándo usarlo

- tareas repetitivas en operaciones o análisis
- estandarización de outputs entre equipos
- reducción de variabilidad entre ejecuciones

## Precondiciones

- tarea empresarial definida
- formato de salida esperado definido
- criterio de calidad explícito

## Inputs esperados

- objetivo de negocio
- contexto mínimo
- restricciones
- salida requerida

## Pasos

1. Definir objetivo en una frase verificable.
2. Especificar input contract (qué datos llegan).
3. Definir output contract (estructura, calidad y límites).
4. Añadir reglas de seguridad y gobernanza.
5. Incluir ejemplo de entrada/salida.
6. Probar en al menos dos casos.
7. Publicar prompt y enlazar procedure/skills relacionados.

## Prompts base reutilizables

- "Genera una respuesta estructurada en secciones fijas y valida contra criterios explícitos."
- "Si faltan datos críticos, declara supuestos y reduce confidence."

## Ejemplo

Objetivo: preparar briefing semanal de cuentas enterprise.

Output: markdown con resumen, riesgos, bloque de acciones y responsables.

## Output esperado

- nota reusable con prompt final
- checklist de validación
- registro en history

## Criterios de validación

- [ ] independiente del proveedor
- [ ] instrucciones claras y no ambiguas
- [ ] incluye manejo de datos faltantes
- [ ] enlazado a procedure y skills aplicables

## Errores comunes

- prompt demasiado genérico
- no definir formato de salida
- no definir criterio de parada

## Notas de mejora

- mantener librería de prompts por dominio
- medir tasa de retrabajo por prompt

## Historial de revisiones

- 2026-03-09: versión inicial POC

## Enlaces

- Skill ejecución: [[03-skills/procedure-execution/SKILL.md]]
- Skill curación: [[03-skills/knowledge-curation/SKILL.md]]

