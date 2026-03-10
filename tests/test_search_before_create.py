from __future__ import annotations

from makos_bridge.vault import Vault


def test_search_finds_existing_procedure_before_creation(template_vault: Vault) -> None:
    matches = template_vault.search("informe recurrente", scope="02-procedures")
    assert matches
    assert any("redactar-informe-recurrente.md" in item["path"] for item in matches)


def test_find_similar_titles_detects_existing_note(template_vault: Vault) -> None:
    duplicates = template_vault.find_similar_titles("Redactar informe recurrente")
    assert duplicates
