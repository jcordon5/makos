# Escenario E2E 2: Agente crea conocimiento en inbox y lo promueve

## Contexto

Hallazgos nuevos con evidencia parcial.

## Flujo

1. Crear con baja confianza:
   `makos --vault ./vault-local create --type knowledge_note --title "Hallazgos iniciales de churn" --confidence 0.55 --source-type derived`
2. Nota cae en `01-inbox` por política.
3. Humano revisa, añade evidencia y sube confianza.
4. Actualizar metadata y mover a `04-knowledge/...` con `makos update` + decisión en history.

## Resultado

Conocimiento estable solo tras gate de revisión.

