from __future__ import annotations

from makos_bridge.metadata import compose_metadata, validate_metadata


def test_validate_valid_knowledge_metadata() -> None:
    metadata = compose_metadata(
        "knowledge_note",
        "Test Knowledge",
        domain="operations",
        confidence=0.8,
        source_type="derived",
        related=["00-system/system-overview.md"],
    )
    errors = validate_metadata(metadata, expected_type="knowledge_note")
    assert errors == []


def test_validate_missing_procedure_required_field() -> None:
    metadata = compose_metadata(
        "procedure",
        "Bad Procedure",
        domain="operations",
        confidence=0.8,
        source_type="derived",
        related=["00-system/system-overview.md"],
    )
    metadata.pop("procedure_for", None)
    errors = validate_metadata(metadata, expected_type="procedure")
    assert any("procedure_for" in error for error in errors)
