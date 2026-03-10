# Arquitectura de la POC

## Objetivos de diseño

- model-agnostic y agent-agnostic
- local, portable, sin credenciales externas
- auditable por archivos legibles por humanos
- usable desde Obsidian y desde shell

## Decisiones técnicas

1. **Lenguaje del bridge: Python 3.9+**
   - robusto para filesystem + CLI
   - baja fricción en macOS/Linux
   - ecosistema estable para tests (`pytest`)

2. **Dependencias mínimas**
   - parser YAML con fallback embebido, sin dependencia obligatoria para el flujo base
   - sin SDKs de proveedores LLM
   - sin bases de datos externas

3. **Formato de persistencia**
   - markdown + YAML frontmatter
   - wikilinks para navegabilidad humana
   - JSON opcional en salida CLI para automatización

4. **Gobernanza de escritura**
   - validación de metadata por tipo
   - prevención de duplicados obvios
   - snapshot antes de update
   - log estructurado en history

5. **Skill-first activation**
   - bundle Claude-compatible en `agent-skills/makos-context-os`
   - registry compartida en `03-skills/registry`
   - activación/desactivación sincronizada con `~/.claude/skills`

## Capa 1: Vault

- `vault-template/` define la estructura canónica
- contenido inicial utilizable (no placeholders vacíos)
- separación explícita entre:
  - conocimiento estable (`04-knowledge`)
  - procedimientos (`02-procedures`)
  - skills (`03-skills`)
  - memoria (`05-memory`)
  - auditoría (`06-history`)

## Capa 2: Convenciones canónicas

- documentación en `00-system/*`
- esquema en `schemas/frontmatter.schema.json`
- plantillas en `09-templates/*`
- vistas humanas en `10-human-views/*`

## Capa 3: Bridge CLI (`makos`)

Comandos implementados:

- init, doctor
- agent-ready (auto-bootstrap zero-config)
- search, read
- create, update
- append-history
- list-procedures, run-procedure
- list-skills, install-skill, enable-skill, disable-skill
- suggest-related
- validate-note
- review-queue, reindex

Características:

- fallback filesystem-first
- integración opcional con Obsidian CLI (`--prefer-obsidian` en `search`)
- modo `--dry-run`
- salida texto/JSON (`--json`)
- auto-descubrimiento de vault y auto-creación de `~/.makos/vault` si no existe
- instalación del launcher global `~/.makos/bin/makos`
- instalación y activación de la skill núcleo `makos-context-os`

## Capa 4: Runtime universal

No existe agente central obligatorio.

Cualquier runtime con shell puede:

- ejecutar `makos`
- leer/escribir notas del vault
- abrir el mismo vault en Obsidian para revisión humana

## Capa 5: Agent Skill Layer

MAKOS también se distribuye como skill runtime:

- source bundle en `agent-skills/makos-context-os`
- runtime target en `~/.claude/skills/makos-context-os`
- estado compartido en `03-skills/registry`, `03-skills/enabled`, `03-skills/disabled`

Esto convierte MAKOS en una capacidad reusable entre proyectos, no en un prompt manual por workspace.

## Modelo de datos

Campos comunes obligatorios:

- id, type, title, status
- created_at, updated_at
- authors, owners, tags
- visibility, write_permissions

Campos por tipo:

- procedure: `procedure_for`, `related`
- skill: `skill_for`
- knowledge_note: `domain`, `confidence`, `source_type`
- memory_entry: `source_type`
- decision_log: `source_type`, `source_refs`
- review_item: `review_due`

## Flujo de escritura segura

1. `search` y `suggest-related`
2. `create` o `update` con validación
3. snapshot en cambios (si update)
4. append a history
5. `reindex` y `review-queue`
