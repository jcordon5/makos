"""Filesystem operations over a MAKOS vault."""

from __future__ import annotations

import difflib
import re
from pathlib import Path
from typing import Any

from .constants import REQUIRED_DIRECTORIES
from .metadata import parse_frontmatter, render_note
from .utils import ensure_parent, slugify


class VaultError(Exception):
    """Vault operation error."""


class Vault:
    """Abstraction for vault path resolution and note operations."""

    def __init__(self, root: Path):
        self.root = root.expanduser().resolve()

    def resolve(self, path: str | Path) -> Path:
        """Resolve a path relative to vault root and prevent path escape."""
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        candidate = candidate.resolve()

        if candidate != self.root and self.root not in candidate.parents:
            raise VaultError(f"Path escapes vault root: {path}")
        return candidate

    def ensure_structure(self) -> list[str]:
        """Return list of missing required directories."""
        missing: list[str] = []
        for directory in REQUIRED_DIRECTORIES:
            if not (self.root / directory).exists():
                missing.append(directory)
        return missing

    def list_markdown(self, subdir: str | None = None) -> list[Path]:
        """List markdown files under vault or subdir."""
        base = self.resolve(subdir) if subdir else self.root
        if not base.exists():
            return []
        return sorted(p for p in base.rglob("*.md") if p.is_file())

    def read_note(self, path: str | Path) -> tuple[Path, dict[str, Any], str]:
        """Read a note and parse frontmatter/body."""
        target = self.resolve(path)
        if not target.exists() or not target.is_file():
            raise VaultError(f"Note not found: {path}")
        raw = target.read_text(encoding="utf-8")
        metadata, body = parse_frontmatter(raw)
        return target, metadata, body

    def read_raw(self, path: str | Path) -> tuple[Path, str]:
        """Read raw note content."""
        target = self.resolve(path)
        if not target.exists() or not target.is_file():
            raise VaultError(f"Note not found: {path}")
        return target, target.read_text(encoding="utf-8")

    def write_note(
        self,
        path: str | Path,
        metadata: dict[str, Any],
        body: str,
        *,
        overwrite: bool = False,
        dry_run: bool = False,
    ) -> Path:
        """Write note with frontmatter/body."""
        target = self.resolve(path)
        if target.exists() and not overwrite:
            raise VaultError(f"Note already exists: {target}")
        ensure_parent(target)
        content = render_note(metadata, body)
        if not dry_run:
            target.write_text(content, encoding="utf-8")
        return target

    def append_text(self, path: str | Path, text: str, *, dry_run: bool = False) -> Path:
        """Append text to an existing note."""
        target = self.resolve(path)
        if not target.exists() or not target.is_file():
            raise VaultError(f"Note not found: {path}")
        if not dry_run:
            with target.open("a", encoding="utf-8") as handle:
                if not text.startswith("\n"):
                    handle.write("\n")
                handle.write(text)
                if not text.endswith("\n"):
                    handle.write("\n")
        return target

    def search(self, query: str, *, scope: str | None = None, limit: int = 20) -> list[dict[str, str]]:
        """Simple text search over markdown notes."""
        query_lower = query.lower().strip()
        if not query_lower:
            return []
        notes = self.list_markdown(scope)
        matches: list[dict[str, str]] = []

        for note in notes:
            raw = note.read_text(encoding="utf-8")
            idx = raw.lower().find(query_lower)
            if idx < 0:
                continue
            start = max(0, idx - 80)
            end = min(len(raw), idx + len(query_lower) + 80)
            snippet = re.sub(r"\s+", " ", raw[start:end]).strip()
            matches.append(
                {
                    "path": str(note.relative_to(self.root)),
                    "snippet": snippet,
                }
            )
            if len(matches) >= limit:
                break

        return matches

    def _normalize_title(self, title: str) -> str:
        return re.sub(r"\s+", " ", title.lower().strip())

    def find_similar_titles(self, title: str, *, threshold: float = 0.9, limit: int = 5) -> list[dict[str, Any]]:
        """Detect obvious duplicates by normalized/similar title."""
        normalized_target = self._normalize_title(title)
        duplicates: list[dict[str, Any]] = []

        for path in self.list_markdown():
            raw = path.read_text(encoding="utf-8")
            metadata, _ = parse_frontmatter(raw)
            existing_title = metadata.get("title") if isinstance(metadata, dict) else None
            if not existing_title:
                existing_title = path.stem.replace("-", " ")

            normalized_existing = self._normalize_title(str(existing_title))
            ratio = difflib.SequenceMatcher(None, normalized_target, normalized_existing).ratio()
            if normalized_existing == normalized_target or ratio >= threshold:
                duplicates.append(
                    {
                        "path": str(path.relative_to(self.root)),
                        "title": str(existing_title),
                        "similarity": round(ratio, 3),
                    }
                )
            if len(duplicates) >= limit:
                break

        return duplicates

    def build_note_relative_path(
        self,
        note_type: str,
        title: str,
        *,
        domain: str = "general",
        confidence: float | None = None,
        preferred_path: str | None = None,
    ) -> Path:
        """Compute default note path following vault conventions."""
        if preferred_path:
            return Path(preferred_path)

        slug = slugify(title) + ".md"
        if note_type == "procedure":
            return Path("02-procedures") / slug
        if note_type == "skill":
            return Path("03-skills") / slug
        if note_type == "knowledge_note":
            if confidence is None or confidence < 0.7:
                return Path("01-inbox") / slug
            return Path("04-knowledge") / "concepts" / domain / slug
        if note_type == "memory_entry":
            return Path("05-memory") / "shared" / slug
        if note_type == "decision_log":
            return Path("06-history") / "decisions" / slug
        if note_type == "scratchpad":
            return Path("07-workspaces") / "scratchpads" / slug
        if note_type == "review_item":
            return Path("01-inbox") / slug
        if note_type == "index":
            return Path("08-indexes") / slug
        return Path("01-inbox") / slug
