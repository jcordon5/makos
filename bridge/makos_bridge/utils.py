"""Utility functions for MAKOS bridge."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable


def slugify(value: str) -> str:
    """Create filesystem-safe slug."""
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-{2,}", "-", value)
    return value.strip("-") or "untitled"


def utc_now_iso() -> str:
    """Current UTC datetime in ISO8601 with Z suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact_json(data: Any) -> str:
    """Stable compact JSON representation."""
    return json.dumps(data, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def parse_key_values(items: Iterable[str] | None) -> dict[str, str]:
    """Parse key=value entries into a dictionary."""
    result: dict[str, str] = {}
    if not items:
        return result
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid key=value pair: {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Invalid empty key in pair: {item}")
        result[key] = value.strip()
    return result


def ensure_parent(path: Path) -> None:
    """Create parent directories if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_iso(value: Any) -> datetime:
    """Parse ISO date/datetime values with optional Z suffix."""
    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)

    normalized = str(value).strip()
    if " " in normalized and "T" not in normalized:
        normalized = normalized.replace(" ", "T", 1)
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    if "T" not in normalized:
        normalized = normalized + "T00:00:00+00:00"
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt
