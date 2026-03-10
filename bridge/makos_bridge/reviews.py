"""Review queue logic for human curation workflows."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .constants import REVIEW_QUEUE_STATUSES, REVIEW_RELEVANT_TYPES
from .metadata import compose_metadata
from .utils import parse_iso
from .vault import Vault


def build_review_queue(vault: Vault, *, as_of: datetime | None = None) -> list[dict[str, Any]]:
    """Collect notes that require human review."""
    current = as_of or datetime.now(timezone.utc)
    queue: list[dict[str, Any]] = []

    for path in vault.list_markdown():
        rel = str(path.relative_to(vault.root))
        _, metadata, _ = vault.read_note(rel)
        if not metadata:
            continue

        note_type = metadata.get("type")
        status = metadata.get("status")
        review_due = metadata.get("review_due")

        should_include = False
        if note_type in REVIEW_RELEVANT_TYPES and status in REVIEW_QUEUE_STATUSES:
            should_include = True

        due_iso = ""
        if review_due:
            due = parse_iso(str(review_due))
            due_iso = due.isoformat()
            if due <= current:
                should_include = True

        if should_include:
            queue.append(
                {
                    "path": rel,
                    "title": metadata.get("title", path.stem),
                    "type": note_type,
                    "status": status,
                    "review_due": due_iso or str(review_due or ""),
                    "owners": metadata.get("owners", []),
                }
            )

    queue.sort(key=lambda item: (item.get("review_due") or "9999", item.get("path")))
    return queue


def write_review_queue_page(vault: Vault, queue: list[dict[str, Any]], *, dry_run: bool = False) -> Path:
    """Write human-readable review queue page into 10-human-views."""
    title = "Review Queue"
    metadata = compose_metadata(
        "index",
        title,
        author="system",
        owner="governance",
        tags=["review", "queue"],
        domain="governance",
        status="active",
        confidence=1.0,
        source_type="system",
        source_refs=["makos review-queue"],
        visibility="shared",
    )

    rows = []
    rows.append("# Review Queue\n")
    rows.append(f"Items pendientes: **{len(queue)}**\n")
    rows.append("| Title | Type | Status | Review Due | Owners | Path |")
    rows.append("|---|---|---|---|---|---|")
    for item in queue:
        owners = ", ".join(item.get("owners") or [])
        rows.append(
            f"| {item['title']} | {item.get('type','')} | {item.get('status','')} | {item.get('review_due','')} | {owners} | [[{item['path']}]] |"
        )

    body = "\n".join(rows) + "\n"
    return vault.write_note(
        Path("10-human-views") / "review-queue.md",
        metadata,
        body,
        overwrite=True,
        dry_run=dry_run,
    )
