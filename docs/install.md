# Instalación

## Requisitos

- Python 3.9+
- macOS o Linux
- (Opcional) Obsidian CLI en `PATH`

## Setup zero-config (sin instalación de paquetes)

```bash
cd /Users/jose/Desktop/MISC/Proyectos/makos
./makos agent-ready --json
```

En macOS puedes hacer doble clic en `Install MAKOS.command`.

`agent-ready` auto-descubre o auto-crea la bóveda global en `~/.makos/vault`.
También crea launcher global en `~/.makos/bin/makos`.
Tambien instala y habilita la skill `makos-context-os` en `~/.claude/skills`.

## Setup opcional (entorno Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Apuntar a vault existente (opcional)

```bash
./makos --vault /ruta/a/mi/vault doctor
```

Si ya existe un vault MAKOS y quieres convertirlo en el vault global:

```bash
./makos --vault /ruta/a/mi/vault agent-ready --json
```

## Verificar estado

```bash
./makos doctor
~/.makos/bin/makos doctor
```
