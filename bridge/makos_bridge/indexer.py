"""Index generation for vault discovery."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .metadata import compose_metadata
from .vault import Vault


def _write_index(vault: Vault, relative_path: Path, title: str, body: str, *, dry_run: bool) -> Path:
    metadata = compose_metadata(
        "index",
        title,
        author="system",
        owner="governance",
        tags=["index"],
        domain="governance",
        status="active",
        confidence=1.0,
        source_type="system",
        source_refs=["makos reindex"],
        visibility="shared",
    )
    return vault.write_note(relative_path, metadata, body, overwrite=True, dry_run=dry_run)


def reindex(vault: Vault, *, dry_run: bool = False) -> dict[str, Any]:
    """Rebuild core indexes under 08-indexes."""
    notes = []
    for path in vault.list_markdown():
        rel = str(path.relative_to(vault.root))
        _, metadata, _ = vault.read_note(rel)
        notes.append((rel, metadata))

    procedures = [item for item in notes if item[0].startswith("02-procedures/") and item[0] != "02-procedures/README.md"]
    skills = [item for item in notes if item[0].startswith("03-skills/") and item[0].endswith("SKILL.md")]
    knowledge = [item for item in notes if item[0].startswith("04-knowledge/") or item[0].startswith("01-inbox/")]

    tag_map: dict[str, list[str]] = defaultdict(list)
    for rel, metadata in notes:
        for tag in metadata.get("tags", []) if isinstance(metadata, dict) else []:
            tag_map[str(tag)].append(rel)

    proc_lines = [
        "# Procedures Index",
        "",
        f"Total procedures: **{len(procedures)}**",
        "",
        "| Title | Status | Procedure For | Path |",
        "|---|---|---|---|",
    ]
    for rel, metadata in sorted(procedures):
        proc_lines.append(
            f"| {metadata.get('title', Path(rel).stem)} | {metadata.get('status', '')} | {metadata.get('procedure_for', '')} | [[{rel}]] |"
        )

    skill_lines = [
        "# Skills Index",
        "",
        f"Total skills: **{len(skills)}**",
        "",
        "| Title | Skill For | Path |",
        "|---|---|---|",
    ]
    for rel, metadata in sorted(skills):
        skill_lines.append(
            f"| {metadata.get('title') or metadata.get('name') or Path(rel).parent.name} | {metadata.get('skill_for', '')} | [[{rel}]] |"
        )

    knowledge_lines = [
        "# Knowledge Index",
        "",
        f"Items indexed: **{len(knowledge)}**",
        "",
        "| Title | Type | Status | Domain | Confidence | Path |",
        "|---|---|---|---|---|---|",
    ]
    for rel, metadata in sorted(knowledge):
        knowledge_lines.append(
            "| {title} | {type_} | {status} | {domain} | {confidence} | [[{path}]] |".format(
                title=metadata.get("title", Path(rel).stem),
                type_=metadata.get("type", ""),
                status=metadata.get("status", ""),
                domain=metadata.get("domain", ""),
                confidence=metadata.get("confidence", ""),
                path=rel,
            )
        )

    tags_lines = [
        "# Tags Index",
        "",
        f"Total tags: **{len(tag_map)}**",
        "",
        "| Tag | Count | Notes |",
        "|---|---|---|",
    ]
    for tag, rels in sorted(tag_map.items()):
        linked = ", ".join(f"[[{rel}]]" for rel in sorted(rels)[:12])
        tags_lines.append(f"| {tag} | {len(rels)} | {linked} |")

    written = []
    written.append(
        _write_index(
            vault,
            Path("08-indexes") / "procedures-index.md",
            "Procedures Index",
            "\n".join(proc_lines) + "\n",
            dry_run=dry_run,
        )
    )
    written.append(
        _write_index(
            vault,
            Path("08-indexes") / "skills-index.md",
            "Skills Index",
            "\n".join(skill_lines) + "\n",
            dry_run=dry_run,
        )
    )
    written.append(
        _write_index(
            vault,
            Path("08-indexes") / "knowledge-index.md",
            "Knowledge Index",
            "\n".join(knowledge_lines) + "\n",
            dry_run=dry_run,
        )
    )
    written.append(
        _write_index(
            vault,
            Path("08-indexes") / "tags-index.md",
            "Tags Index",
            "\n".join(tags_lines) + "\n",
            dry_run=dry_run,
        )
    )

    return {
        "written": [str(path.relative_to(vault.root)) for path in written],
        "totals": {
            "procedures": len(procedures),
            "skills": len(skills),
            "knowledge": len(knowledge),
            "tags": len(tag_map),
            "notes": len(notes),
        },
        "dry_run": dry_run,
    }
