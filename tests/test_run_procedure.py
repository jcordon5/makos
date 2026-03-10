from __future__ import annotations

from pathlib import Path

from makos_bridge.procedures import run_procedure
from makos_bridge.vault import Vault


def test_run_procedure_creates_workspace_and_history(template_vault: Vault) -> None:
    result = run_procedure(
        template_vault,
        procedure_query="redactar-informe-recurrente",
        actor="agent-test",
        inputs={"periodo": "2026-Q1"},
        dry_run=False,
    )

    workspace = template_vault.root / result["workspace"]
    assert workspace.exists()

    history_files = list((template_vault.root / "06-history" / "actions").glob("*.md"))
    assert history_files

    raw = workspace.read_text(encoding="utf-8")
    assert "Procedure Execution Workspace" in raw
    assert "periodo: 2026-Q1" in raw
