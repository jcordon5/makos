# Commands

Use this reference when you need the concrete MAKOS command patterns.

## Bootstrap

```bash
$MAKOS_CMD agent-ready --json
```

## Discovery

```bash
$MAKOS_CMD search "query"
$MAKOS_CMD list-procedures
$MAKOS_CMD suggest-related "text or path"
```

## Reuse

```bash
$MAKOS_CMD run-procedure "procedure-name" --input key=value
```

## Safe write

```bash
$MAKOS_CMD create --type knowledge_note --title "..." --confidence 0.5 --source-type derived
$MAKOS_CMD update path/to/note.md --append "new evidence"
```

## Audit

```bash
$MAKOS_CMD append-history --category actions --action create_note --target 01-inbox/example.md --reason "new finding"
```

## Human sync

```bash
$MAKOS_CMD reindex
$MAKOS_CMD review-queue --write-page
```

## Shared skill registry

```bash
$MAKOS_CMD list-skills
$MAKOS_CMD install-skill /path/to/skill-bundle
$MAKOS_CMD enable-skill skill-name
$MAKOS_CMD disable-skill skill-name
```
