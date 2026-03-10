from __future__ import annotations

from argparse import Namespace

import pytest

from makos_bridge.cli import CLIError, cmd_create
from makos_bridge.vault import Vault


def _create_args(**overrides) -> Namespace:
    base = {
        "type": "knowledge_note",
        "title": "Weekly Sales Insight",
        "path": None,
        "domain": "sales",
        "status": "draft",
        "confidence": 0.5,
        "authors": None,
        "owners": None,
        "tags": ["sales"],
        "source_type": "derived",
        "source_refs": None,
        "related": None,
        "supersedes": None,
        "procedure_for": None,
        "skill_for": None,
        "review_due": None,
        "write_permissions": None,
        "visibility": "shared",
        "with_checksum": False,
        "body": "# Findings\n\n- New signal\n",
        "body_file": None,
        "actor": "agent-test",
        "reason": "test",
        "force": False,
        "dry_run": False,
    }
    base.update(overrides)
    return Namespace(**base)


def test_create_blocks_obvious_duplicates(template_vault: Vault) -> None:
    first = _create_args(title="Duplicate Candidate")
    cmd_create(template_vault, first)

    second = _create_args(title="Duplicate Candidate")
    with pytest.raises(CLIError):
        cmd_create(template_vault, second)


def test_create_low_confidence_cannot_force_knowledge_folder(template_vault: Vault) -> None:
    args = _create_args(
        title="Low confidence forced path",
        path="04-knowledge/concepts/low-confidence-forced-path.md",
        confidence=0.4,
    )

    with pytest.raises(CLIError):
        cmd_create(template_vault, args)
