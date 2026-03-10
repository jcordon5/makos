"""Procedure discovery and execution helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .history import append_history_entry
from .metadata import compose_metadata, validate_metadata
from .utils import slugify, utc_now_iso
from .vault import Vault, VaultError


@dataclass
class Procedure:
    path: Path
    metadata: dict[str, Any]
    body: str


def list_procedures(vault: Vault) -> list[Procedure]:
    """List procedures under 02-procedures."""
    procedures: list[Procedure] = []
    for path in vault.list_markdown("02-procedures"):
        rel = path.relative_to(vault.root)
        if rel.parts[0] != "02-procedures":
            continue
        if "templates" in rel.parts or rel.name.lower() == "readme.md":
            continue
        _, metadata, body = vault.read_note(rel)
        procedures.append(Procedure(path=path, metadata=metadata, body=body))
    return procedures


def find_procedure(vault: Vault, query: str) -> Procedure:
    """Find a procedure by id, title, file name, or path."""
    direct = Path(query)
    if direct.suffix == ".md":
        try:
            resolved, metadata, body = vault.read_note(direct)
            return Procedure(path=resolved, metadata=metadata, body=body)
        except VaultError:
            pass

    q = query.lower().strip()
    for proc in list_procedures(vault):
        rel = proc.path.relative_to(vault.root)
        pid = str(proc.metadata.get("id", "")).lower()
        title = str(proc.metadata.get("title", "")).lower()
        stem = proc.path.stem.lower()
        if q in {pid, title, stem, str(rel).lower()}:
            return proc

    for proc in list_procedures(vault):
        title = str(proc.metadata.get("title", "")).lower()
        if q in title:
            return proc

    raise VaultError(f"Procedure not found: {query}")


def extract_steps(body: str) -> list[str]:
    """Extract numbered or checklist steps from markdown body."""
    steps: list[str] = []
    for line in body.splitlines():
        if re.match(r"^\s*(\d+\.|- \[ \]|- )\s+", line):
            steps.append(line.strip())
    return steps[:20]


def run_procedure(
    vault: Vault,
    *,
    procedure_query: str,
    actor: str,
    inputs: dict[str, str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create an execution workspace from a reusable procedure."""
    procedure = find_procedure(vault, procedure_query)
    rel_proc = str(procedure.path.relative_to(vault.root))
    title = str(procedure.metadata.get("title") or procedure.path.stem)
    timestamp = utc_now_iso()

    run_name = f"run-{slugify(title)}-{timestamp.replace(':', '').replace('-', '').replace('T', '-').replace('Z', '')}"
    run_path = Path("07-workspaces") / "active-tasks" / f"{run_name}.md"

    steps = extract_steps(procedure.body)
    steps_md = "\n".join(f"- [ ] {step}" for step in steps) if steps else "- [ ] Ejecutar procedimiento manualmente"
    input_lines = "\n".join(f"- {k}: {v}" for k, v in sorted((inputs or {}).items())) or "- (sin inputs declarados)"

    metadata = compose_metadata(
        "scratchpad",
        f"Procedure Run: {title}",
        author=actor,
        owner="operations",
        tags=["procedure-run", slugify(title)],
        domain=str(procedure.metadata.get("domain", "operations")),
        status="in_progress",
        confidence=0.6,
        source_type="procedure-run",
        source_refs=[procedure.metadata.get("id", rel_proc)],
        related=[rel_proc],
        visibility="shared",
    )

    errors = validate_metadata(metadata, expected_type="scratchpad")
    if errors:
        raise ValueError(f"invalid run metadata: {errors}")

    body = f"""# Procedure Execution Workspace

- procedure: [[{rel_proc}]]
- actor: {actor}
- started_at: {timestamp}

## Inputs
{input_lines}

## Execution Checklist
{steps_md}

## Output Draft
- Resultado pendiente.

## Validation
- [ ] Criterios de validacion cumplidos
- [ ] History registrado
"""

    vault.write_note(run_path, metadata, body, overwrite=False, dry_run=dry_run)

    append_history_entry(
        vault,
        category="actions",
        actor=actor,
        action="run_procedure",
        target=rel_proc,
        reason="execute reusable procedure",
        inputs={"procedure": rel_proc, "workspace": str(run_path), "inputs": inputs or {}},
        result="workspace_created",
        related=[str(run_path), rel_proc],
        dry_run=dry_run,
    )

    return {
        "procedure": rel_proc,
        "procedure_title": title,
        "workspace": str(run_path),
        "inputs": inputs or {},
        "dry_run": dry_run,
    }
