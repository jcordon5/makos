---
id: skill-filesystem-governance-20260309
type: skill
title: Filesystem Governance
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - governance-agent
owners:
  - governance
tags:
  - skill
  - governance
  - metadata
domain: governance
confidence: 0.95
source_type: system
source_refs:
  - 00-system/metadata-standard.md
related:
  - 00-system/write-policy.md
  - 09-templates/knowledge-note.md
supersedes: []
skill_for: leer y escribir notas respetando metadatos y políticas de seguridad
write_permissions:
  - owners
  - agents
visibility: shared
---

# Skill: Filesystem Governance

## Propósito

Garantizar escrituras seguras en markdown con frontmatter válido, historial y rutas canónicas.

## Cuándo cargarla

- antes de crear/actualizar notas
- cuando se necesite validar metadatos
- cuando haya riesgo de sobreescritura

## Comandos disponibles

- `makos validate-note <path>`
- `makos create ...`
- `makos update ...`
- `makos append-history ...`

## Estrategia

1. validar metadatos antes de persistir
2. preservar snapshot antes de cambios
3. verificar enlaces `related`
4. registrar evento de history

## Restricciones

- prohibido sobrescribir sin snapshot
- prohibido crear conocimiento estable con baja confianza

## Ejemplos

- crear nota segura:
  `makos create --type knowledge_note --title "X" --confidence 0.5 --source-type derived`
- actualizar preservando historial:
  `makos update 01-inbox/x.md --append "nueva evidencia"`

## Anti-patrones

- editar archivos sin actualizar `updated_at`
- dejar notas sin `id` o sin `type`

