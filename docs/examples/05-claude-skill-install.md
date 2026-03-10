# Escenario E2E 5: MAKOS como skill global de Claude

## Contexto

El usuario quiere que Claude use MAKOS en cualquier proyecto sin abrir el repo de MAKOS cada vez.

## Flujo

1. En el repo de MAKOS, una sola vez:
   `./makos agent-ready --json`
2. Esto crea:
   - `~/.makos/vault`
   - `~/.makos/bin/makos`
   - `~/.claude/skills/makos-context-os`
3. Después, Claude trabaja en cualquier otro workspace.
4. Cuando detecta necesidad de memoria compartida, procedimientos o trazabilidad, activa la skill `makos-context-os`.

## Resultado

MAKOS pasa a ser una capacidad global del runtime, no un prompt artesanal por proyecto.
