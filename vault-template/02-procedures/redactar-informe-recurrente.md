---
id: procedure-redactar-informe-recurrente-20260309
type: procedure
title: Redactar informe recurrente
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - operations-agent
owners:
  - bizops
tags:
  - procedure
  - reporting
  - recurrent
domain: business-operations
confidence: 0.92
source_type: derived
source_refs:
  - 04-knowledge/cheatsheets/frontmatter-checklist.md
related:
  - 03-skills/procedure-execution/SKILL.md
  - 03-skills/history-logging/SKILL.md
  - 09-templates/task-workspace.md
supersedes: []
procedure_for: generar informes operativos periódicos para dirección
write_permissions:
  - owners
  - agents
visibility: shared
review_due: 2026-06-30T00:00:00Z
---

# Redactar informe recurrente

## Propósito

Estandarizar la producción de informes periódicos (semanales/mensuales/trimestrales) para que sean comparables en el tiempo.

## Cuándo usarlo

- cierre semanal de operación
- comité mensual
- revisión trimestral de resultados

## Precondiciones

- existe periodo objetivo definido
- hay fuentes mínimas (KPI, incidencias, hitos)
- audiencia y nivel de detalle están claros

## Inputs esperados

- periodo
- audiencia
- métricas clave
- incidencias relevantes
- decisiones pendientes

## Pasos

1. Recopilar indicadores del periodo y validarlos.
2. Clasificar hallazgos en: resultados, riesgos, acciones.
3. Redactar resumen ejecutivo de 5-8 líneas.
4. Redactar detalle por bloque: rendimiento, riesgos, próximos pasos.
5. Añadir sección de decisiones requeridas.
6. Verificar consistencia de cifras y enlaces.
7. Publicar en workspace y registrar en history.

## Prompts base reutilizables

- "Resume los resultados del periodo en lenguaje ejecutivo, max 8 líneas, destacando cambios vs periodo anterior."
- "Convierte los hallazgos en acciones concretas con owner y fecha."

## Ejemplo

Input mínimo:

- periodo: 2026-Q1
- audiencia: comité dirección
- métricas: conversión, churn, margen

Output resumido:

- resumen ejecutivo
- tabla KPI
- riesgos y mitigaciones
- decisiones solicitadas

## Output esperado

Una nota markdown con:

- resumen ejecutivo
- KPIs
- riesgos
- decisiones requeridas
- enlaces a evidencia

## Criterios de validación

- [ ] todas las cifras tienen fuente
- [ ] los riesgos tienen owner
- [ ] las decisiones tienen fecha objetivo
- [ ] se registró entrada en `06-history/actions`

## Errores comunes

- mezclar opinión con dato sin marcarlo
- publicar sin fuentes
- omitir acciones concretas

## Notas de mejora

- evaluar plantilla con tabla comparativa automática
- añadir bloque de variación porcentual por KPI

## Historial de revisiones

- 2026-03-09: versión inicial POC

## Enlaces

- Skill ejecución: [[03-skills/procedure-execution/SKILL.md]]
- Skill history: [[03-skills/history-logging/SKILL.md]]
- Plantilla workspace: [[09-templates/task-workspace.md]]

