# MAKOS

Shared Knowledge OS for humans and AI agents.  
Model-agnostic. Local-first. Obsidian-native.

MAKOS convierte un vault de Obsidian en una capa compartida de:

- procedimientos reutilizables
- conocimiento estable
- memoria compartida
- historial y auditoría
- skills portables para agentes

Sin cloud. Sin lock-in de proveedor. Sin vector DB obligatoria.

## Why

La mayoría de agentes trabajan con contexto efímero y memoria fragmentada.  
MAKOS les da una base común, legible por humanos y operable por cualquier agente con acceso a filesystem + shell.

## Quick Start

Si solo quieres empezar a usar MAKOS y crear tu bóveda:

1. Descarga o clona este repo.
2. Arranca MAKOS.
3. Abre la bóveda en Obsidian.

macOS, sin terminal:

- doble clic en [Install MAKOS.command](Install%20MAKOS.command)

Cualquier shell:

```bash
./makos agent-ready
```

La primera vez, MAKOS crea o reutiliza tu bóveda compartida en:

```text
~/.makos/vault
```

Después, abre esa carpeta como vault en Obsidian.

Si ya tienes una bóveda MAKOS existente:

```bash
./makos agent-ready --vault /ruta/a/tu/vault
```

## Use With Any Agent

Para que un agente use MAKOS por defecto:

- Claude-compatible: instala o habilita la skill incluida `makos-context-os`
- otros agentes: usa el prompt canónico de [vault-template/00-system/agent-system-prompt.md](vault-template/00-system/agent-system-prompt.md)

Referencia de la skill:

- [docs/claude-skill.md](docs/claude-skill.md)

## What You Get

- un vault base de Obsidian listo para usar
- una CLI neutral: `makos`
- convenciones de escritura y lectura
- validación de frontmatter
- trazabilidad de cambios y decisiones
- índices y vistas para humanos

## Core Commands

```bash
./makos agent-ready
./makos doctor
./makos list-procedures
./makos run-procedure "redactar-informe-recurrente"
./makos review-queue --write-page
./makos reindex
```

## Repository Layout

- `agent-skills/`: skills bundles compatibles con la convención `SKILL.md`
- `vault-template/`: plantilla base del vault
- `bridge/`: implementación del bridge y CLI `makos`
- `schemas/`: esquema de metadatos y campos requeridos
- `scripts/`: utilidades de bootstrap y demos
- `docs/`: arquitectura, instalación, uso, ejemplos y roadmap
- `tests/`: tests de validación y comportamiento

## Docs

- [docs/architecture.md](docs/architecture.md)
- [docs/install.md](docs/install.md)
- [docs/usage.md](docs/usage.md)
- [docs/claude-skill.md](docs/claude-skill.md)
- [docs/examples](docs/examples)
- [docs/limitations.md](docs/limitations.md)
- [docs/roadmap-v2.md](docs/roadmap-v2.md)

## Status

POC funcional y portable para macOS/Linux.  
Diseñado para evolucionar hacia una capa estándar de contexto compartido entre agentes y organizaciones.
