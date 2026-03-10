#!/bin/sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"

echo "Installing MAKOS global runtime..."
"$SCRIPT_DIR/makos" agent-ready
echo
echo "MAKOS installed."
echo "Global vault: ~/.makos/vault"
echo "Claude skill: ~/.claude/skills/makos-context-os"
echo
echo "Press Enter to close."
read dummy
