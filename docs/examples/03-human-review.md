# Escenario E2E 3: Humano revisa propuesta de agente

## Flujo

1. Agente genera draft con `status=draft` y `review_due`.
2. Ejecutar `makos --vault ./vault-local review-queue --write-page`.
3. Humano abre `10-human-views/review-queue.md` en Obsidian.
4. Humano decide aprobar, pedir cambios o descartar.
5. Registrar decisión con `makos append-history --category decisions ...`.

## Resultado

Revisión humana integrada en el mismo sistema de archivos.

