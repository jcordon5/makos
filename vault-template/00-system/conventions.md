---
id: knowledge_note-conventions-20260309
type: knowledge_note
title: Canonical Conventions
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - system
owners:
  - governance
tags:
  - conventions
  - taxonomy
  - governance
domain: governance
confidence: 0.95
source_type: system
source_refs:
  - 00-system/system-overview.md
related:
  - 00-system/metadata-standard.md
  - 00-system/retrieval-policy.md
supersedes: []
write_permissions:
  - owners
  - agents
visibility: shared
---

# Canonical Conventions

## Niveles de carpetas

- `00-system`: normas del sistema.
- `01-inbox`: entradas de baja confianza o propuestas.
- `02-procedures`: procedimientos reutilizables.
- `03-skills`: capacidades operativas para agentes/humanos.
  - `03-skills/registry`: bundles runtime compatibles con Claude-style SKILLs.
  - `03-skills/enabled`: manifiestos de skills activas.
  - `03-skills/disabled`: manifiestos de skills desactivadas.
- `04-knowledge`: conocimiento consolidado y estable.
- `05-memory`: memoria humana, de agentes y sesiones.
- `06-history`: trazabilidad/auditoría.
- `07-workspaces`: trabajo activo y borradores.
- `08-indexes`: índices navegables.
- `09-templates`: plantillas oficiales.
- `10-human-views`: vistas de operación y revisión.

## Convenciones de nombres

- archivos en `kebab-case`
- títulos legibles en `title`
- enlaces internos vía wikilinks `[[ruta/nota.md]]`

## Convenciones operativas

- buscar antes de crear
- escribir en inbox/workspace cuando la confianza sea baja
- registrar acciones de escritura en `06-history`
- promover de `01-inbox` a `04-knowledge` solo tras revisión
- mantener skills instalables en `03-skills/registry` y habilitarlas mediante el bridge
