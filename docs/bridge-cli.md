# Diseño del Bridge CLI (`makos`)

## Principios

- neutral respecto a modelo/agente
- filesystem-first, Obsidian CLI opcional
- errores claros, salida legible y JSON opcional
- dry-run y validación previa a escritura

## Comandos

- `makos init [target] [--template] [--force]`
- `makos agent-ready`
- `makos list-skills`
- `makos install-skill [source]`
- `makos enable-skill <name> [--source path]`
- `makos disable-skill <name>`
- `makos doctor`
- `makos search <query> [--scope] [--limit] [--prefer-obsidian]`
- `makos read <path> [--raw]`
- `makos create --type ... --title ...`
- `makos update <path> [--set key=value] [--append]`
- `makos append-history --category ... --action ... --target ...`
- `makos list-procedures`
- `makos run-procedure <query> [--input k=v]`
- `makos suggest-related <path|texto> [--limit]`
- `makos validate-note <path>`
- `makos review-queue [--write-page]`
- `makos reindex`

## Reglas de escritura aplicadas por CLI

1. detectar duplicados por similitud de título antes de crear
2. aplicar gate de confianza para conocimiento estable
3. generar `related` mínimo incluso en vault vacío
4. validar frontmatter por tipo
5. preservar snapshot en updates
6. registrar history de acciones y cambios

## Backend strategy

- búsqueda:
  - si `--prefer-obsidian` y `obsidian` disponible: usar Obsidian CLI
  - fallback: búsqueda por filesystem
- lectura/escritura:
  - filesystem directo con validación

## Contrato de salida

- default: texto legible para humanos
- `--json`: objeto/array parseable para automatización

## Runtime zero-config

`makos agent-ready`:

- auto-descubre bóveda global existente
- si no existe, crea `~/.makos/vault` desde `vault-template`
- escribe `~/.makos/config.json` para fijar `vault_path`
- crea launcher estable `~/.makos/bin/makos`
- registra la skill núcleo `makos-context-os` en `03-skills/registry`
- la habilita en `~/.claude/skills/makos-context-os`
- permite que el agente trabaje sin paths manuales

## Shared skill registry

MAKOS mantiene una registry compartida dentro del vault:

- `03-skills/registry/<skill-name>/`: bundle Claude-compatible
- `03-skills/enabled/<skill-name>.md`: manifiesto de skill activa
- `03-skills/disabled/<skill-name>.md`: manifiesto de skill desactivada

La activación sincroniza el bundle del registry al runtime de Claude vía symlink en `~/.claude/skills`.
