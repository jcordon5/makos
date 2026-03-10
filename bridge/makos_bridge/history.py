"""History and audit trail helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .metadata import compose_metadata, validate_metadata
from .utils import compact_json, slugify, utc_now_iso
from .vault import Vault


HISTORY_CATEGORIES = {"actions", "decisions", "changes"}


def append_history_entry(
    vault: Vault,
    *,
    category: str,
    actor: str,
    action: str,
    target: str,
    reason: str,
    inputs: dict[str, Any] | None = None,
    result: str = "ok",
    related: list[str] | None = None,
    dry_run: bool = False,
) -> Path:
    """Append a structured history entry as markdown note."""
    if category not in HISTORY_CATEGORIES:
        raise ValueError(f"category must be one of {sorted(HISTORY_CATEGORIES)}")

    timestamp = utc_now_iso()
    title = f"{action} on {target}"
    slug = slugify(f"{timestamp}-{action}-{target}")
    relative_path = Path("06-history") / category / f"{slug}.md"
    if not dry_run:
        counter = 2
        while (vault.root / relative_path).exists():
            relative_path = Path("06-history") / category / f"{slug}-{counter}.md"
            counter += 1

    metadata = compose_metadata(
        "history_entry",
        title,
        author=actor,
        owner="governance",
        tags=["history", category, action],
        domain="governance",
        status="active",
        confidence=1.0,
        source_type="system",
        source_refs=[target],
        related=related or [],
        visibility="shared",
    )

    errors = validate_metadata(metadata, expected_type="history_entry")
    if errors:
        raise ValueError(f"invalid history metadata: {errors}")

    body = "\n".join(
        [
            "# History Entry",
            "",
            f"- actor: {actor}",
            f"- timestamp: {timestamp}",
            f"- action: {action}",
            f"- target: {target}",
            f"- reason: {reason}",
            f"- result: {result}",
            f"- inputs: `{compact_json(inputs or {})}`",
            "",
            "## Related",
            *(f"- [[{item}]]" for item in (related or [])),
            "",
        ]
    )

    return vault.write_note(relative_path, metadata, body, overwrite=False, dry_run=dry_run)
