"""Frontmatter parsing and validation for MAKOS notes."""

from __future__ import annotations

import hashlib
import re
from datetime import date, datetime
from typing import Any

from .constants import ALLOWED_SOURCE_TYPES, ALLOWED_STATUSES, ALLOWED_VISIBILITY, DOCUMENT_TYPES
from .utils import slugify, utc_now_iso
from .yaml_compat import safe_dump, safe_load

COMMON_REQUIRED_FIELDS = [
    "id",
    "type",
    "title",
    "status",
    "created_at",
    "updated_at",
    "authors",
    "owners",
    "tags",
    "visibility",
    "write_permissions",
]

TYPE_REQUIRED_FIELDS: dict[str, list[str]] = {
    "procedure": ["procedure_for", "related"],
    "skill": ["skill_for"],
    "knowledge_note": ["domain", "confidence", "source_type"],
    "memory_entry": ["source_type"],
    "decision_log": ["source_type", "source_refs"],
    "scratchpad": [],
    "index": [],
    "review_item": ["review_due"],
    "history_entry": ["source_type", "source_refs"],
}

LIST_FIELDS = {
    "authors",
    "owners",
    "tags",
    "source_refs",
    "related",
    "supersedes",
    "write_permissions",
}

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]+$")


def make_note_id(note_type: str, title: str, created_at: str | None = None) -> str:
    """Generate stable note id based on type/title/date."""
    created = created_at or utc_now_iso()
    date_part = created.split("T", 1)[0].replace("-", "")
    return f"{note_type}-{slugify(title)}-{date_part}"


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse markdown frontmatter and return metadata/body."""
    if not text.startswith("---\n"):
        return {}, text

    marker = "\n---\n"
    end = text.find(marker, 4)
    if end == -1:
        return {}, text

    raw_yaml = text[4:end]
    body = text[end + len(marker) :]
    metadata = safe_load(raw_yaml) or {}
    if not isinstance(metadata, dict):
        return {}, text
    return metadata, body


def render_note(metadata: dict[str, Any], body: str) -> str:
    """Render markdown note with YAML frontmatter."""
    serialized = safe_dump(metadata, sort_keys=False, allow_unicode=False).rstrip()
    normalized_body = body if body.endswith("\n") else body + "\n"
    return f"---\n{serialized}\n---\n\n{normalized_body}"


def compute_checksum(body: str) -> str:
    """Compute SHA256 checksum of body content."""
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _validate_iso(value: Any, field: str, errors: list[str]) -> None:
    if isinstance(value, datetime):
        return
    if isinstance(value, date):
        return
    if not isinstance(value, str):
        errors.append(f"{field} must be an ISO datetime string")
        return
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        errors.append(f"{field} must be valid ISO datetime")


def validate_metadata(metadata: dict[str, Any], expected_type: str | None = None) -> list[str]:
    """Validate metadata according to MAKOS minimal standard."""
    errors: list[str] = []

    note_type = metadata.get("type")
    if expected_type and note_type != expected_type:
        errors.append(f"type must be '{expected_type}', got '{note_type}'")

    for field in COMMON_REQUIRED_FIELDS:
        if field not in metadata:
            errors.append(f"missing required field: {field}")

    if note_type not in DOCUMENT_TYPES:
        errors.append(f"type must be one of {sorted(DOCUMENT_TYPES)}")
    else:
        for field in TYPE_REQUIRED_FIELDS.get(note_type, []):
            if field not in metadata or metadata[field] in (None, "", []):
                errors.append(f"missing required field for {note_type}: {field}")

    if "id" in metadata and (not isinstance(metadata["id"], str) or not ID_PATTERN.match(metadata["id"])):
        errors.append("id must match pattern ^[a-z0-9][a-z0-9._-]+$")

    if "status" in metadata and metadata["status"] not in ALLOWED_STATUSES:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUSES)}")

    if "visibility" in metadata and metadata["visibility"] not in ALLOWED_VISIBILITY:
        errors.append(f"visibility must be one of {sorted(ALLOWED_VISIBILITY)}")

    if "source_type" in metadata and metadata.get("source_type") not in ALLOWED_SOURCE_TYPES:
        errors.append(f"source_type must be one of {sorted(ALLOWED_SOURCE_TYPES)}")

    if "confidence" in metadata and metadata.get("confidence") is not None:
        confidence = metadata.get("confidence")
        if not isinstance(confidence, (int, float)):
            errors.append("confidence must be numeric in range [0, 1]")
        elif confidence < 0 or confidence > 1:
            errors.append("confidence must be in range [0, 1]")

    if "created_at" in metadata:
        _validate_iso(metadata.get("created_at"), "created_at", errors)
    if "updated_at" in metadata:
        _validate_iso(metadata.get("updated_at"), "updated_at", errors)
    if metadata.get("review_due"):
        _validate_iso(metadata.get("review_due"), "review_due", errors)

    for field in LIST_FIELDS:
        if field in metadata and not isinstance(metadata[field], list):
            errors.append(f"{field} must be a list")

    return errors


def compose_metadata(
    note_type: str,
    title: str,
    *,
    author: str = "agent",
    owner: str = "shared",
    tags: list[str] | None = None,
    domain: str | None = None,
    status: str = "draft",
    confidence: float | None = None,
    source_type: str = "generated",
    source_refs: list[str] | None = None,
    related: list[str] | None = None,
    supersedes: list[str] | None = None,
    procedure_for: str | None = None,
    skill_for: str | None = None,
    review_due: str | None = None,
    write_permissions: list[str] | None = None,
    visibility: str = "shared",
    checksum: str | None = None,
) -> dict[str, Any]:
    """Create metadata with required defaults."""
    now = utc_now_iso()
    metadata: dict[str, Any] = {
        "id": make_note_id(note_type, title, now),
        "type": note_type,
        "title": title,
        "status": status,
        "created_at": now,
        "updated_at": now,
        "authors": [author],
        "owners": [owner],
        "tags": tags or [],
        "visibility": visibility,
        "write_permissions": write_permissions or ["owners", "agents"],
        "source_refs": source_refs or [],
        "related": related or [],
        "supersedes": supersedes or [],
    }

    if domain is not None:
        metadata["domain"] = domain
    if confidence is not None:
        metadata["confidence"] = confidence
    if source_type is not None:
        metadata["source_type"] = source_type
    if procedure_for:
        metadata["procedure_for"] = procedure_for
    if skill_for:
        metadata["skill_for"] = skill_for
    if review_due:
        metadata["review_due"] = review_due
    if checksum:
        metadata["checksum"] = checksum

    return metadata
