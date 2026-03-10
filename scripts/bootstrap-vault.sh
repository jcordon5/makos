#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-./vault-local}"
ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
MAKOS="$ROOT_DIR/makos"

"$MAKOS" --vault "$TARGET" init "$TARGET" --force
"$MAKOS" --vault "$TARGET" reindex
"$MAKOS" --vault "$TARGET" review-queue --write-page

echo "Vault listo en: $TARGET"
