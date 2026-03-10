from __future__ import annotations

from makos_bridge.history import append_history_entry
from makos_bridge.vault import Vault


def test_append_history_creates_structured_note(template_vault: Vault) -> None:
    path = append_history_entry(
        template_vault,
        category="actions",
        actor="agent-test",
        action="create_note",
        target="01-inbox/test.md",
        reason="unit test",
        inputs={"type": "knowledge_note"},
        result="ok",
        related=["01-inbox/test.md"],
    )

    assert path.exists()
    raw = path.read_text(encoding="utf-8")
    assert "History Entry" in raw
    assert "actor: agent-test" in raw
    assert "action: create_note" in raw
