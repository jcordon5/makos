---
id: procedure-analizar-documento-extraer-puntos-clave-20260309
type: procedure
title: Analizar documento y extraer puntos clave
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - research-agent
owners:
  - knowledge-team
tags:
  - procedure
  - analysis
  - summarization
domain: knowledge-ops
confidence: 0.9
source_type: derived
source_refs:
  - 00-system/retrieval-policy.md
related:
  - 03-skills/search-before-create/SKILL.md
  - 03-skills/filesystem-governance/SKILL.md
  - 09-templates/knowledge-note.md
supersedes: []
procedure_for: extraer ideas accionables de documentos largos con trazabilidad
write_permissions:
  - owners
  - agents
visibility: shared
review_due: 2026-06-30T00:00:00Z
---

# Analizar documento y extraer puntos clave

## Propósito

Reducir documentos extensos a hallazgos útiles, verificables y enlazables en el vault.

## Cuándo usarlo

- análisis de contratos, RFCs, papers, informes
- onboarding sobre material no familiar
- preparación de decisiones

## Precondiciones

- documento fuente accesible
- objetivo de extracción definido
- público del resultado identificado

## Inputs esperados

- ruta o URL del documento
- objetivo del análisis
- nivel de profundidad

## Pasos

1. Leer índice o estructura general del documento.
2. Identificar secciones de alto impacto para el objetivo.
3. Extraer hechos, supuestos y decisiones propuestas.
4. Etiquetar cada hallazgo con nivel de confianza.
5. Relacionar hallazgos con conocimiento existente (`makos suggest-related`).
6. Crear nota en inbox si la confianza es baja.
7. Registrar actividad y pendientes de revisión.

## Prompts base reutilizables

- "Extrae 5-10 puntos clave orientados a decisión ejecutiva y clasifícalos por impacto."
- "Distingue hechos, hipótesis y riesgos en formato tabla."

## Ejemplo

Input:

- documento: política interna de seguridad
- objetivo: identificar cambios requeridos

Output:

- resumen ejecutivo
- lista de brechas
- recomendación inicial

## Output esperado

- nota `knowledge_note` en `01-inbox` o `04-knowledge`
- `source_refs` al documento original
- `related` a notas existentes

## Criterios de validación

- [ ] trazabilidad clara al documento fuente
- [ ] separación explícita hecho/hipótesis
- [ ] confianza declarada
- [ ] seguimiento en review queue

## Errores comunes

- resumir sin objetivo
- no distinguir inferencia de cita
- no enlazar notas relacionadas

## Notas de mejora

- agregar checklist por tipo de documento (legal/técnico/finanzas)

## Historial de revisiones

- 2026-03-09: versión inicial POC

## Enlaces

- Skill búsqueda: [[03-skills/search-before-create/SKILL.md]]
- Skill gobernanza: [[03-skills/filesystem-governance/SKILL.md]]
- Template knowledge note: [[09-templates/knowledge-note.md]]

