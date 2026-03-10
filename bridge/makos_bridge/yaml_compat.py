"""YAML compatibility helpers with stdlib fallback.

PyYAML is used when available. If not installed, a minimal parser/dumper
supports the frontmatter subset used by MAKOS.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from typing import Any

try:
    import yaml as _yaml  # type: ignore
except Exception:  # pragma: no cover - exercised in environments without PyYAML
    _yaml = None


def _parse_scalar(value: str) -> Any:
    raw = value.strip()
    if raw == "":
        return ""
    if raw in {"null", "~", "None"}:
        return None
    if raw in {"true", "True"}:
        return True
    if raw in {"false", "False"}:
        return False
    if raw.startswith(("'", '"')) and raw.endswith(("'", '"')) and len(raw) >= 2:
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        try:
            return int(raw)
        except Exception:
            return raw
    if re.fullmatch(r"-?\d+\.\d+", raw):
        try:
            return float(raw)
        except Exception:
            return raw
    if raw == "[]":
        return []
    return raw


def _dump_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()

    text = str(value)
    if text == "":
        return '""'
    if any(ch in text for ch in [":", "#", "[", "]", "{", "}", "\n"]) or text.strip() != text:
        return f'"{text}"'
    return text


def _safe_load_fallback(text: str) -> Any:
    src = text.strip("\n")
    if not src.strip():
        return None

    lines = src.splitlines()
    result: dict[str, Any] = {}
    i = 0

    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue

        if ":" not in line:
            # Plain scalar document (used by CLI --set values).
            if len(lines) == 1:
                return _parse_scalar(line)
            i += 1
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if value == "":
            items: list[Any] = []
            j = i + 1
            while j < len(lines):
                child = lines[j]
                if not child.strip():
                    j += 1
                    continue
                if child.startswith("  - "):
                    items.append(_parse_scalar(child[4:]))
                    j += 1
                    continue
                if child.startswith("  ") and items:
                    items[-1] = f"{items[-1]}\n{child.strip()}"
                    j += 1
                    continue
                break
            result[key] = items
            i = j
            continue

        result[key] = _parse_scalar(value)
        i += 1

    return result


def _safe_dump_fallback(data: Any, *, sort_keys: bool = False, allow_unicode: bool = False) -> str:
    if not isinstance(data, dict):
        return _dump_scalar(data) + "\n"

    keys = sorted(data.keys()) if sort_keys else list(data.keys())
    out: list[str] = []
    for key in keys:
        value = data[key]
        if isinstance(value, list):
            out.append(f"{key}:")
            if not value:
                out[-1] += " []"
                continue
            for item in value:
                out.append(f"  - {_dump_scalar(item)}")
            continue
        out.append(f"{key}: {_dump_scalar(value)}")
    return "\n".join(out) + "\n"


def safe_load(text: str) -> Any:
    if _yaml is not None:
        return _yaml.safe_load(text)
    return _safe_load_fallback(text)


def safe_dump(data: Any, *, sort_keys: bool = False, allow_unicode: bool = False) -> str:
    if _yaml is not None:
        return _yaml.safe_dump(data, sort_keys=sort_keys, allow_unicode=allow_unicode)
    return _safe_dump_fallback(data, sort_keys=sort_keys, allow_unicode=allow_unicode)

