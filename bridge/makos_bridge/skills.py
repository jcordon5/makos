"""Claude-compatible skill bundle management for MAKOS."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .constants import CORE_AGENT_SKILL_NAME, SKILL_DISABLED_DIR, SKILL_ENABLED_DIR, SKILL_REGISTRY_DIR
from .history import append_history_entry
from .metadata import compose_metadata, parse_frontmatter, validate_metadata
from .vault import Vault, VaultError


def claude_user_skills_dir() -> Path:
    """Global Claude Code user skill directory."""
    return Path.home() / ".claude" / "skills"


def is_agent_skill_bundle_path(path: str | Path) -> bool:
    candidate = Path(path)
    if candidate.name != "SKILL.md":
        return False
    parts = set(candidate.parts)
    return "registry" in parts or "agent-skills" in parts


def validate_agent_skill_metadata(metadata: dict[str, Any]) -> list[str]:
    """Validate Claude-style skill frontmatter."""
    errors: list[str] = []
    name = metadata.get("name")
    description = metadata.get("description")

    if not isinstance(name, str) or not name.strip():
        errors.append("skill bundle missing required frontmatter field: name")
    if not isinstance(description, str) or not description.strip():
        errors.append("skill bundle missing required frontmatter field: description")
    compatibility = metadata.get("compatibility")
    if compatibility is not None and not isinstance(compatibility, (dict, str, list)):
        errors.append("skill bundle compatibility must be a mapping, string, or list")
    return errors


def _skill_dir_from_source(source: str | Path) -> Path:
    path = Path(source).expanduser().resolve()
    if path.is_dir():
        skill_dir = path
    elif path.name == "SKILL.md":
        skill_dir = path.parent
    else:
        raise ValueError(f"Skill source must be a directory or SKILL.md path: {source}")

    if not (skill_dir / "SKILL.md").exists():
        raise ValueError(f"Skill source missing SKILL.md: {skill_dir}")
    return skill_dir


def load_agent_skill_bundle(source: str | Path) -> dict[str, Any]:
    """Read a Claude-style skill bundle from a directory or SKILL.md."""
    skill_dir = _skill_dir_from_source(source)
    raw = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    metadata, body = parse_frontmatter(raw)
    errors = validate_agent_skill_metadata(metadata)
    if errors:
        raise ValueError("; ".join(errors))

    return {
        "name": metadata["name"],
        "description": metadata["description"],
        "metadata": metadata,
        "body": body,
        "path": skill_dir,
    }


def registry_dir(vault: Vault) -> Path:
    return vault.root / SKILL_REGISTRY_DIR


def enabled_manifest_dir(vault: Vault) -> Path:
    return vault.root / SKILL_ENABLED_DIR


def disabled_manifest_dir(vault: Vault) -> Path:
    return vault.root / SKILL_DISABLED_DIR


def registry_skill_path(vault: Vault, skill_name: str) -> Path:
    return registry_dir(vault) / skill_name


def enabled_manifest_path(vault: Vault, skill_name: str) -> Path:
    return enabled_manifest_dir(vault) / f"{skill_name}.md"


def disabled_manifest_path(vault: Vault, skill_name: str) -> Path:
    return disabled_manifest_dir(vault) / f"{skill_name}.md"


def _manifest_metadata(skill_name: str, title: str, status: str, related: list[str], source_refs: list[str]) -> dict[str, Any]:
    metadata = compose_metadata(
        "skill",
        title,
        author="system",
        owner="platform",
        tags=["skill", "agent-skill", skill_name],
        domain="agent-runtime",
        status=status,
        confidence=0.95,
        source_type="system",
        source_refs=source_refs,
        related=related,
        skill_for=f"manage and expose the agent skill bundle '{skill_name}'",
        visibility="shared",
    )
    errors = validate_metadata(metadata, expected_type="skill")
    if errors:
        raise ValueError(f"invalid skill manifest metadata: {errors}")
    return metadata


def _write_state_manifest(
    vault: Vault,
    *,
    skill_name: str,
    description: str,
    enabled: bool,
    dry_run: bool = False,
) -> str:
    registry_rel = f"{SKILL_REGISTRY_DIR}/{skill_name}/SKILL.md"
    manifest_rel = enabled_manifest_path(vault, skill_name) if enabled else disabled_manifest_path(vault, skill_name)
    other_rel = disabled_manifest_path(vault, skill_name) if enabled else enabled_manifest_path(vault, skill_name)
    title = f"Agent Skill {'Enabled' if enabled else 'Disabled'} - {skill_name}"
    metadata = _manifest_metadata(
        skill_name,
        title,
        "active" if enabled else "deprecated",
        [registry_rel],
        [registry_rel],
    )
    body = "\n".join(
        [
            f"# {title}",
            "",
            f"- skill_name: {skill_name}",
            f"- enabled: {'true' if enabled else 'false'}",
            f"- registry_bundle: [[{registry_rel}]]",
            "",
            "## Description",
            description,
            "",
            "## Runtime contract",
            "- Claude-compatible skill bundle stored in registry.",
            "- Enabled state means it is exposed to `~/.claude/skills`.",
            "",
        ]
    )

    vault.write_note(manifest_rel.relative_to(vault.root), metadata, body, overwrite=True, dry_run=dry_run)
    if other_rel.exists() and not dry_run:
        other_rel.unlink()
    return str(manifest_rel.relative_to(vault.root))


def install_skill_to_registry(
    vault: Vault,
    *,
    source: str | Path,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Install a Claude-compatible skill bundle into the shared vault registry."""
    bundle = load_agent_skill_bundle(source)
    skill_name = bundle["name"]
    skill_dir = bundle["path"]
    target = registry_skill_path(vault, skill_name)

    if target.exists():
        if not overwrite:
            return {
                "skill_name": skill_name,
                "description": bundle["description"],
                "registry_path": str(target.relative_to(vault.root)),
                "installed": False,
                "reason": "already-present",
            }
        if target.is_symlink() or target.is_file():
            raise VaultError(f"Registry path must be a directory: {target}")
        if not dry_run:
            shutil.rmtree(target)

    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(skill_dir, target)

    return {
        "skill_name": skill_name,
        "description": bundle["description"],
        "registry_path": str(target.relative_to(vault.root)),
        "installed": True,
    }


def _sync_skill_to_claude(vault: Vault, skill_name: str, *, dry_run: bool = False) -> Path:
    source = registry_skill_path(vault, skill_name)
    if not source.exists():
        raise VaultError(f"Skill not found in registry: {skill_name}")

    target_dir = claude_user_skills_dir()
    target = target_dir / skill_name

    if not dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            if target.is_symlink():
                target.unlink()
            elif target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        target.symlink_to(source, target_is_directory=True)
    return target


def enable_skill(
    vault: Vault,
    *,
    skill_name: str,
    actor: str = "system",
    source: str | Path | None = None,
    overwrite: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Enable a skill by installing it in registry and linking to Claude's user skills."""
    install_report = None
    description = ""
    if source is not None:
        install_report = install_skill_to_registry(vault, source=source, overwrite=overwrite, dry_run=dry_run)
        description = install_report["description"]

    bundle = load_agent_skill_bundle(registry_skill_path(vault, skill_name))
    description = description or bundle["description"]
    link = _sync_skill_to_claude(vault, skill_name, dry_run=dry_run)
    manifest_rel = _write_state_manifest(vault, skill_name=skill_name, description=description, enabled=True, dry_run=dry_run)

    append_history_entry(
        vault,
        category="actions",
        actor=actor,
        action="enable_skill",
        target=f"{SKILL_REGISTRY_DIR}/{skill_name}/SKILL.md",
        reason="expose skill to agent runtime",
        inputs={"skill_name": skill_name, "claude_path": str(link)},
        result="enabled",
        related=[manifest_rel, f"{SKILL_REGISTRY_DIR}/{skill_name}/SKILL.md"],
        dry_run=dry_run,
    )

    return {
        "skill_name": skill_name,
        "description": description,
        "manifest_path": manifest_rel,
        "claude_skill_path": str(link),
        "installed": install_report["installed"] if install_report else False,
        "enabled": True,
    }


def disable_skill(vault: Vault, *, skill_name: str, actor: str = "system", dry_run: bool = False) -> dict[str, Any]:
    """Disable a skill by unlinking it from Claude's user skills and updating state."""
    bundle = load_agent_skill_bundle(registry_skill_path(vault, skill_name))
    target = claude_user_skills_dir() / skill_name
    if not dry_run and (target.exists() or target.is_symlink()):
        if target.is_symlink() or target.is_file():
            target.unlink()
        else:
            shutil.rmtree(target)

    manifest_rel = _write_state_manifest(
        vault,
        skill_name=skill_name,
        description=bundle["description"],
        enabled=False,
        dry_run=dry_run,
    )

    append_history_entry(
        vault,
        category="actions",
        actor=actor,
        action="disable_skill",
        target=f"{SKILL_REGISTRY_DIR}/{skill_name}/SKILL.md",
        reason="remove skill from active agent runtime",
        inputs={"skill_name": skill_name, "claude_path": str(target)},
        result="disabled",
        related=[manifest_rel, f"{SKILL_REGISTRY_DIR}/{skill_name}/SKILL.md"],
        dry_run=dry_run,
    )

    return {
        "skill_name": skill_name,
        "manifest_path": manifest_rel,
        "claude_skill_path": str(target),
        "enabled": False,
    }


def list_registry_skills(vault: Vault) -> list[dict[str, Any]]:
    """List skill bundles in the shared registry and their runtime status."""
    items: list[dict[str, Any]] = []
    base = registry_dir(vault)
    if not base.exists():
        return items

    for entry in sorted(base.iterdir()):
        if not entry.is_dir():
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.exists():
            continue
        bundle = load_agent_skill_bundle(entry)
        claude_path = claude_user_skills_dir() / bundle["name"]
        enabled_manifest = enabled_manifest_path(vault, bundle["name"])
        disabled_manifest = disabled_manifest_path(vault, bundle["name"])
        items.append(
            {
                "name": bundle["name"],
                "description": bundle["description"],
                "registry_path": str(entry.relative_to(vault.root)),
                "enabled": claude_path.exists() or claude_path.is_symlink(),
                "state_note": str(enabled_manifest.relative_to(vault.root))
                if enabled_manifest.exists()
                else str(disabled_manifest.relative_to(vault.root))
                if disabled_manifest.exists()
                else None,
                "claude_skill_path": str(claude_path),
            }
        )
    return items


def ensure_core_skill_registered_and_enabled(
    vault: Vault,
    *,
    repo_root: Path,
    actor: str = "system",
    dry_run: bool = False,
) -> dict[str, Any]:
    """Ensure the bundled MAKOS agent skill exists in registry and is enabled for Claude."""
    source = repo_root / "agent-skills" / CORE_AGENT_SKILL_NAME
    if not source.exists():
        raise VaultError(f"Core MAKOS skill bundle not found: {source}")

    install_report = install_skill_to_registry(vault, source=source, overwrite=False, dry_run=dry_run)
    enabled_report = enable_skill(
        vault,
        skill_name=CORE_AGENT_SKILL_NAME,
        actor=actor,
        source=None,
        overwrite=False,
        dry_run=dry_run,
    )
    merged = {**install_report, **enabled_report}
    merged["installed"] = install_report["installed"]
    merged["registry_path"] = install_report["registry_path"]
    return merged
