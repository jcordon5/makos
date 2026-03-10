# MAKOS POC - Multi Agent Knowledge OS (Model-Agnostic)

POC local y portable de un sistema de conocimiento compartido para humanos y agentes, basado en un vault de Obsidian y operable vía shell.

## Objetivo

Permitir que cualquier agente con acceso a filesystem + CLI pueda:

- descubrir estructura del conocimiento
- recuperar procedimientos, skills y memoria
- buscar, crear y actualizar notas con gobernanza
- registrar auditoría mínima de acciones
- reutilizar procedimientos existentes antes de improvisar

## Arquitectura (4 capas)

1. **Vault**: fuente de verdad en markdown + YAML frontmatter.
2. **Canonical Conventions**: estructura, tipos, metadatos, políticas.
3. **Bridge (`makos`)**: CLI neutral, validación y trazabilidad.
4. **Runtime Universal**: cualquier humano/agente con shell opera sin SDK propietario.

Ver detalle en [docs/architecture.md](docs/architecture.md).

Prompt canónico para agentes (incluido en MAKOS):
- [vault-template/00-system/agent-system-prompt.md](vault-template/00-system/agent-system-prompt.md)

Skill Claude-compatible incluida en MAKOS:
- [docs/claude-skill.md](docs/claude-skill.md)

## Estructura del repo

- `agent-skills/`: skills bundles compatibles con Claude y otros runtimes que adopten la convención `SKILL.md`.
- `vault-template/`: vault base de Obsidian listo para usar.
- `bridge/`: CLI neutral en Python (`makos`).
- `schemas/`: esquema de frontmatter y campos requeridos por tipo.
- `scripts/`: bootstrap y demo local.
- `docs/`: arquitectura, uso, ejemplos y roadmap.
- `tests/`: tests de validación, seguridad de escritura y procedimientos.

## Modo Zero-Config (recomendado)

Sin instalación de paquetes ni paths manuales:

```bash
cd makos
./makos agent-ready --json
```

En macOS también puedes hacer doble clic en:

- [Install MAKOS.command](Install%20MAKOS.command)

Esto auto-descubre o auto-crea la bóveda global en `~/.makos/vault` y deja configuración en `~/.makos/config.json`.
Además crea launcher global en `~/.makos/bin/makos`.
Tambien registra y habilita la skill central `makos-context-os` en `~/.claude/skills/`.

## Instalación local (opcional)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Inicio rápido

```bash
./makos agent-ready
~/.makos/bin/makos doctor
./makos doctor
./makos list-procedures
./makos run-procedure "redactar-informe-recurrente" --input periodo=2026-Q1 --input audiencia=Direccion
./makos review-queue --write-page
./makos reindex
```

## Comandos del bridge

- `makos init`
- `makos agent-ready`
- `makos list-skills`
- `makos install-skill`
- `makos enable-skill`
- `makos disable-skill`
- `makos doctor`
- `makos search`
- `makos read`
- `makos create`
- `makos update`
- `makos append-history`
- `makos list-procedures`
- `makos run-procedure`
- `makos suggest-related`
- `makos validate-note`
- `makos review-queue`
- `makos reindex`

## Políticas implementadas

- búsqueda previa y detección de duplicados obvios antes de crear
- bloqueo de escritura de baja confianza en `04-knowledge`
- snapshot previo a updates (historial en `06-history/changes`)
- logging de escrituras relevantes en `06-history/actions|changes|decisions`
- validación estricta de frontmatter
- registry compartida de skills con sincronización a `~/.claude/skills`

## Limitaciones POC

- búsqueda textual sin embeddings/vector DB
- deduplicación basada en similitud de títulos + texto básico
- ejecución de procedures genera workspace (no orquesta herramientas externas por sí sola)

Detalles: [docs/limitations.md](docs/limitations.md)

## Roadmap v2

- motor opcional de embeddings desacoplado
- scoring semántico avanzado de relacionados
- métricas de uso y calidad por procedure
- pipeline de promoción automática inbox -> knowledge con gates configurables

Ver [docs/roadmap-v2.md](docs/roadmap-v2.md).
