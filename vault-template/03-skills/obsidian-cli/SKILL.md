---
id: skill-obsidian-cli-20260309
type: skill
title: Obsidian CLI Operations
status: active
created_at: 2026-03-09T00:00:00Z
updated_at: 2026-03-09T00:00:00Z
authors:
  - platform-agent
owners:
  - tooling
tags:
  - skill
  - obsidian
  - cli
domain: tooling
confidence: 0.9
source_type: system
source_refs:
  - https://github.com/obsidianmd
related:
  - 00-system/retrieval-policy.md
  - 03-skills/search-before-create/SKILL.md
supersedes: []
skill_for: operar el vault mediante comandos de Obsidian CLI con fallback a filesystem
write_permissions:
  - owners
  - agents
visibility: shared
---

# Skill: Obsidian CLI Operations

## Propósito

Aprovechar comandos de Obsidian CLI cuando aportan valor en búsqueda, lectura, enlaces o propiedades.

## Cuándo cargarla

- se requiere integración directa con Obsidian
- hay que consultar backlinks o propiedades
- se desea mantener compatibilidad con flujo humano en Obsidian

## Comandos disponibles

- `obsidian search <query> --vault <path>`
- `obsidian read <file> --vault <path>`
- `obsidian append <file> --vault <path> --content "..."`
- fallback: `makos search`, `makos read`, `makos update`

## Estrategia

1. detectar si `obsidian` está disponible
2. intentar comando Obsidian
3. si falla, usar filesystem mediante bridge
4. registrar backend utilizado en history

## Restricciones

- no asumir que Obsidian CLI está instalado
- no usar comandos no portables sin fallback

## Ejemplos

- buscar políticas: `makos search "write policy" --prefer-obsidian`
- leer nota: `makos read 00-system/write-policy.md`

## Anti-patrones

- bloquear flujo por ausencia de Obsidian CLI
- escribir sin validar frontmatter

