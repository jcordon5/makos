# Uso con cualquier agente (shell + filesystem)

## Arranque de runtime (una vez por sesión)

```bash
./makos agent-ready --json
```

Después puedes usar desde cualquier proyecto:

```bash
MAKOS=~/.makos/bin/makos
```

## Descubrir sistema

```bash
$MAKOS doctor
$MAKOS read 00-system/system-overview.md
$MAKOS list-procedures
```

## Buscar antes de crear

```bash
$MAKOS search "informe recurrente"
$MAKOS suggest-related "informe trimestral"
```

## Crear nota segura

```bash
$MAKOS create \
  --type knowledge_note \
  --title "Hallazgos preliminares pipeline" \
  --confidence 0.45 \
  --source-type derived \
  --tag ventas
```

Con `confidence < 0.70`, el bridge coloca por defecto la nota en `01-inbox`.

## Actualizar con snapshot

```bash
$MAKOS update 01-inbox/hallazgos-preliminares-pipeline.md \
  --append "Nueva evidencia: ..." \
  --reason "se integra feedback humano"
```

## Ejecutar procedure

```bash
$MAKOS run-procedure "redactar-informe-recurrente" \
  --input periodo=2026-Q1 \
  --input audiencia=Direccion
```

## Auditoría y revisión

```bash
$MAKOS review-queue --write-page
$MAKOS reindex
```

## Skills compartidas

Registrar una nueva skill bundle en MAKOS:

```bash
$MAKOS install-skill /path/to/skill-folder
```

Activarla para Claude:

```bash
$MAKOS enable-skill skill-name
```

Desactivarla:

```bash
$MAKOS disable-skill skill-name
```
