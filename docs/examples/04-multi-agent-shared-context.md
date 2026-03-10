# Escenario E2E 4: Varios agentes comparten contexto sin memoria propietaria

## Flujo

1. Agente A crea `memory_entry` en `05-memory/shared`.
2. Agente B busca `makos search "tema"` y reusa la memoria.
3. Ambos agentes registran cambios en `06-history`.
4. Humano audita actividad en `10-human-views/recent-activity.md`.

## Resultado

Continuidad operativa por conocimiento compartido en archivos.

