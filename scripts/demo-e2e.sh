#!/usr/bin/env bash
set -euo pipefail

VAULT="${1:-./vault-local}"
ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
MAKOS="$ROOT_DIR/makos"

"$MAKOS" --vault "$VAULT" doctor
"$MAKOS" --vault "$VAULT" list-procedures
"$MAKOS" --vault "$VAULT" run-procedure "redactar-informe-recurrente" --input periodo=Q1 --input audiencia=Direccion
"$MAKOS" --vault "$VAULT" create \
  --type knowledge_note \
  --title "Hallazgos preliminares sobre pipeline comercial" \
  --confidence 0.45 \
  --tag ventas --tag pipeline \
  --source-type derived \
  --body "# Hallazgos\n\n- Se identifican 3 cuellos de botella."
"$MAKOS" --vault "$VAULT" review-queue --write-page
"$MAKOS" --vault "$VAULT" reindex
