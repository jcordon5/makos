"""Optional Obsidian CLI wrapper with graceful fallback."""

from __future__ import annotations

import shutil
import subprocess
from typing import Any


def obsidian_cli_available() -> bool:
    """Return True if obsidian CLI command is available in PATH."""
    return shutil.which("obsidian") is not None


def run_obsidian_cli(args: list[str]) -> tuple[int, str, str]:
    """Execute obsidian CLI and return (code, stdout, stderr)."""
    process = subprocess.run(
        ["obsidian", *args],
        capture_output=True,
        text=True,
        check=False,
    )
    return process.returncode, process.stdout.strip(), process.stderr.strip()


def search_with_obsidian(query: str, vault_path: str) -> dict[str, Any] | None:
    """Try obsidian search command if available."""
    if not obsidian_cli_available():
        return None
    code, out, err = run_obsidian_cli(["search", query, "--vault", vault_path])
    if code != 0:
        return {"error": err or "obsidian search failed", "query": query}
    lines = [line for line in out.splitlines() if line.strip()]
    return {"query": query, "results": lines, "source": "obsidian-cli"}
