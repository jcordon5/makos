# Escenario E2E 1: Agente descubre procedure existente

## Contexto

Tarea repetitiva: preparar informe mensual para dirección.

## Flujo

1. `makos --vault ./vault-local search "informe mensual"`
2. `makos --vault ./vault-local list-procedures`
3. Agente detecta `redactar-informe-recurrente`.
4. `makos --vault ./vault-local run-procedure redactar-informe-recurrente --input periodo=2026-02 --input audiencia=Direccion`
5. Se crea workspace en `07-workspaces/active-tasks` y log en `06-history/actions`.

## Resultado

Se evita improvisación y se reutiliza flujo validado.

