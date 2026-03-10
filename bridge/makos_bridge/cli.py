"""Command-line interface for MAKOS bridge."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from .constants import DOCUMENT_TYPES
from .history import append_history_entry
from .indexer import reindex
from .metadata import compose_metadata, compute_checksum, parse_frontmatter, validate_metadata
from .obsidian_cli import obsidian_cli_available, search_with_obsidian
from .procedures import list_procedures, run_procedure
from .runtime import (
    ensure_global_launcher,
    find_workspace_root,
    global_vault_path,
    read_runtime_config,
    resolve_vault_candidate,
    write_runtime_config,
)
from .reviews import build_review_queue, write_review_queue_page
from .skills import (
    CORE_AGENT_SKILL_NAME,
    disable_skill,
    enable_skill,
    ensure_core_skill_registered_and_enabled,
    install_skill_to_registry,
    is_agent_skill_bundle_path,
    list_registry_skills,
    validate_agent_skill_metadata,
)
from .utils import parse_key_values, slugify, utc_now_iso
from .vault import Vault, VaultError
from .yaml_compat import safe_dump, safe_load


class CLIError(Exception):
    """CLI-level exception with user-friendly message."""


def _normalize_global_args(argv: list[str] | None) -> list[str] | None:
    """Allow global flags before or after subcommands.

    Many agents append global flags at the end; argparse only accepts them
    before subcommands by default.
    """
    if argv is None:
        return None
    if not argv:
        return argv

    globals_out: list[str] = []
    rest: list[str] = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token in {"--json", "--dry-run"}:
            globals_out.append(token)
            i += 1
            continue
        if token == "--vault":
            if i + 1 < len(argv):
                globals_out.extend([token, argv[i + 1]])
                i += 2
                continue
        if token.startswith("--vault="):
            globals_out.append(token)
            i += 1
            continue

        rest.append(token)
        i += 1

    return [*globals_out, *rest]


def _print_data(data: Any, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=True, default=str))
        return

    if isinstance(data, dict):
        message = data.get("message")
        if message:
            print(message)
        for key, value in data.items():
            if key == "message":
                continue
            if isinstance(value, list):
                print(f"{key}:")
                for item in value:
                    print(f"  - {item}")
            else:
                print(f"{key}: {value}")
        return

    if isinstance(data, list):
        for item in data:
            print(f"- {item}")
        return

    print(data)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_vault(path_str: str) -> Vault:
    vault = Vault(Path(path_str))
    if not vault.root.exists():
        raise CLIError(f"Vault path does not exist: {vault.root}")
    if not vault.root.is_dir():
        raise CLIError(f"Vault path must be a directory: {vault.root}")
    return vault


def _initialize_vault(target: Path, *, template: Path, force: bool = False) -> dict[str, Any]:
    if not template.exists():
        raise CLIError(f"Template vault not found: {template}")

    if target.exists() and any(target.iterdir()) and not force:
        raise CLIError(
            f"Target vault is not empty: {target}. Use --force to merge template files."
        )

    target.mkdir(parents=True, exist_ok=True)
    for item in template.iterdir():
        dest = target / item.name
        if item.is_dir():
            shutil.copytree(item, dest, dirs_exist_ok=force)
        else:
            if dest.exists() and not force:
                continue
            shutil.copy2(item, dest)

    vault = Vault(target)
    index_report = reindex(vault, dry_run=False)
    queue = build_review_queue(vault)
    write_review_queue_page(vault, queue, dry_run=False)
    return {
        "vault": str(target),
        "template": str(template),
        "reindex": index_report["totals"],
        "review_items": len(queue),
    }


def _autobootstrap_vault_if_needed(args: argparse.Namespace) -> tuple[Vault, dict[str, Any]]:
    cwd = Path.cwd().resolve()
    repo_root = _repo_root()
    template = (repo_root / "vault-template").resolve()
    runtime: dict[str, Any] = {
        "repo_root": str(repo_root),
        "workspace_root": str(find_workspace_root(cwd)),
        "vault_source": "arg",
        "mode": "explicit",
        "bootstrapped": False,
        "config_path": None,
        "recommended_cli": None,
    }
    launcher = ensure_global_launcher(repo_root)
    runtime["recommended_cli"] = str(launcher)

    if args.vault:
        vault = _resolve_vault(args.vault)
        cfg_path = write_runtime_config((Path.home() / ".makos").resolve(), repo_root=repo_root, vault_path=vault.root)
        runtime["vault_path"] = str(vault.root)
        runtime["config_path"] = str(cfg_path)
        return vault, runtime

    candidate, source = resolve_vault_candidate(cwd)
    if candidate is not None:
        vault = _resolve_vault(str(candidate))
        mode = "global" if source.startswith("global") else "workspace"
        runtime["vault_source"] = source
        runtime["mode"] = mode
        runtime["vault_path"] = str(vault.root)
        return vault, runtime

    workspace_root = find_workspace_root(cwd)
    makos_home = (Path.home() / ".makos").resolve()
    default_vault = global_vault_path().resolve()
    init_report = _initialize_vault(default_vault, template=template, force=True)
    cfg_path = write_runtime_config(makos_home, repo_root=repo_root, vault_path=default_vault)

    vault = _resolve_vault(str(default_vault))
    runtime.update(
        {
            "vault_path": str(vault.root),
            "vault_source": "auto-bootstrap",
            "bootstrapped": True,
            "config_path": str(cfg_path),
            "mode": "global",
            "init_report": init_report,
        }
    )
    return vault, runtime


def _load_body(body: str | None, body_file: str | None) -> str:
    if body_file:
        content = Path(body_file).expanduser().resolve().read_text(encoding="utf-8")
        return content.strip() + "\n"
    if body:
        return body.strip() + "\n"
    return "# Notes\n\n- Pendiente de completar contenido.\n"


def _parse_set_values(items: list[str] | None) -> dict[str, Any]:
    updates: dict[str, Any] = {}
    if not items:
        return updates
    for item in items:
        if "=" not in item:
            raise CLIError(f"Invalid --set entry '{item}', expected key=value")
        key, raw = item.split("=", 1)
        key = key.strip()
        if not key:
            raise CLIError(f"Invalid --set entry '{item}', empty key")
        value = safe_load(raw)
        updates[key] = value
    return updates


def _default_related(vault: Vault, title: str, limit: int = 3) -> list[str]:
    matches = vault.search(title, limit=limit)
    return [item["path"] for item in matches]


def _record_change_snapshot(
    vault: Vault,
    *,
    target_rel: str,
    actor: str,
    reason: str,
    metadata_before: dict[str, Any],
    body_before: str,
    dry_run: bool,
) -> str:
    snapshot_slug = slugify(f"{utc_now_iso()}-snapshot-{target_rel}")
    snapshot_rel = Path("06-history") / "changes" / f"{snapshot_slug}.md"

    snapshot_meta = compose_metadata(
        "history_entry",
        f"Snapshot before update: {target_rel}",
        author=actor,
        owner="governance",
        tags=["history", "snapshot", "update"],
        domain="governance",
        status="active",
        confidence=1.0,
        source_type="system",
        source_refs=[target_rel],
        related=[target_rel],
        visibility="shared",
    )
    snapshot_body = "\n".join(
        [
            "# Change Snapshot",
            "",
            f"- target: [[{target_rel}]]",
            f"- actor: {actor}",
            f"- reason: {reason}",
            f"- captured_at: {utc_now_iso()}",
            "",
            "## Metadata (before)",
            "```yaml",
            safe_dump(metadata_before, sort_keys=False, allow_unicode=False).rstrip(),
            "```",
            "",
            "## Body (before)",
            "```markdown",
            body_before.rstrip(),
            "```",
            "",
        ]
    )
    vault.write_note(snapshot_rel, snapshot_meta, snapshot_body, overwrite=False, dry_run=dry_run)
    return str(snapshot_rel)


def cmd_init(args: argparse.Namespace) -> dict[str, Any]:
    target_input = args.target or args.vault or "./vault-local"
    target = Path(target_input).expanduser().resolve()
    template = Path(args.template or (_repo_root() / "vault-template")).expanduser().resolve()
    report = _initialize_vault(target, template=template, force=args.force)
    return {
        "message": "Vault initialized successfully",
        **report,
    }


def cmd_doctor(vault: Vault) -> dict[str, Any]:
    missing_dirs = vault.ensure_structure()
    invalid_notes: list[dict[str, Any]] = []

    for path in vault.list_markdown():
        rel = str(path.relative_to(vault.root))
        raw = path.read_text(encoding="utf-8")
        metadata, _ = parse_frontmatter(raw)
        if not metadata:
            invalid_notes.append({"path": rel, "errors": ["missing frontmatter"]})
            continue
        if is_agent_skill_bundle_path(rel):
            errors = validate_agent_skill_metadata(metadata)
        else:
            errors = validate_metadata(metadata)
        if errors:
            invalid_notes.append({"path": rel, "errors": errors})

    return {
        "vault": str(vault.root),
        "obsidian_cli_available": obsidian_cli_available(),
        "total_notes": len(vault.list_markdown()),
        "missing_directories": missing_dirs,
        "invalid_notes": invalid_notes,
        "status": "ok" if not missing_dirs and not invalid_notes else "needs_attention",
    }


def cmd_search(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    if args.prefer_obsidian:
        obsidian_result = search_with_obsidian(args.query, str(vault.root))
        if obsidian_result and "error" not in obsidian_result:
            return {
                "query": args.query,
                "scope": args.scope or ".",
                "results": obsidian_result["results"][: args.limit],
                "backend": "obsidian-cli",
            }

    matches = vault.search(args.query, scope=args.scope, limit=args.limit)
    return {
        "query": args.query,
        "scope": args.scope or ".",
        "count": len(matches),
        "results": matches,
        "backend": "filesystem",
    }


def cmd_read(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    if args.raw:
        path, raw = vault.read_raw(args.path)
        return {"path": str(path.relative_to(vault.root)), "raw": raw}

    path, metadata, body = vault.read_note(args.path)
    return {
        "path": str(path.relative_to(vault.root)),
        "metadata": metadata,
        "body": body,
    }


def cmd_create(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    body = _load_body(args.body, args.body_file)
    duplicates = vault.find_similar_titles(args.title)
    if duplicates and not args.force:
        raise CLIError(
            "Potential duplicates found. Use --force to continue or choose another title.\n"
            + "\n".join(f"- {d['title']} ({d['path']}, similarity={d['similarity']})" for d in duplicates)
        )

    if args.type == "knowledge_note" and args.path and args.confidence < 0.7 and args.path.startswith("04-knowledge"):
        raise CLIError(
            "Policy violation: low-confidence knowledge must be created in 01-inbox or 07-workspaces first."
        )

    related = args.related or _default_related(vault, args.title)
    if args.type in {"procedure", "skill", "knowledge_note"} and not related:
        # Keep hard-link policy while allowing first-note creation in a clean vault.
        related = ["00-system/system-overview.md"]

    relative = vault.build_note_relative_path(
        args.type,
        args.title,
        domain=args.domain,
        confidence=args.confidence,
        preferred_path=args.path,
    )

    metadata = compose_metadata(
        args.type,
        args.title,
        author=(args.authors[0] if args.authors else args.actor),
        owner=(args.owners[0] if args.owners else "shared"),
        tags=args.tags or [],
        domain=args.domain,
        status=args.status,
        confidence=args.confidence if args.type in {"knowledge_note", "procedure", "skill", "review_item"} else None,
        source_type=args.source_type,
        source_refs=args.source_refs or [],
        related=related,
        supersedes=args.supersedes or [],
        procedure_for=args.procedure_for,
        skill_for=args.skill_for,
        review_due=args.review_due,
        write_permissions=args.write_permissions or ["owners", "agents"],
        visibility=args.visibility,
        checksum=compute_checksum(body) if args.with_checksum else None,
    )

    if args.authors:
        metadata["authors"] = args.authors
    if args.owners:
        metadata["owners"] = args.owners

    errors = validate_metadata(metadata, expected_type=args.type)
    if errors:
        raise CLIError("Metadata validation failed: " + "; ".join(errors))

    written = vault.write_note(relative, metadata, body, overwrite=False, dry_run=args.dry_run)

    append_history_entry(
        vault,
        category="actions",
        actor=args.actor,
        action="create_note",
        target=str(relative),
        reason=args.reason or "create note",
        inputs={
            "type": args.type,
            "title": args.title,
            "domain": args.domain,
            "confidence": args.confidence,
            "related": related,
        },
        result="created",
        related=[str(relative), *related],
        dry_run=args.dry_run,
    )

    return {
        "message": "Note created",
        "path": str(written.relative_to(vault.root)),
        "id": metadata["id"],
        "type": args.type,
        "dry_run": args.dry_run,
    }


def cmd_update(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    path, metadata, body = vault.read_note(args.path)
    rel = str(path.relative_to(vault.root))

    metadata_before = dict(metadata)
    body_before = body

    updates = _parse_set_values(args.set_values)
    metadata.update(updates)

    if args.append_text:
        body = body.rstrip() + "\n\n" + args.append_text.strip() + "\n"
    if args.body is not None or args.body_file:
        body = _load_body(args.body, args.body_file)

    metadata["updated_at"] = utc_now_iso()
    if "checksum" in metadata:
        metadata["checksum"] = compute_checksum(body)

    errors = validate_metadata(metadata)
    if errors:
        raise CLIError("Metadata validation failed after update: " + "; ".join(errors))

    snapshot_rel = None
    if not args.no_preserve_history:
        snapshot_rel = _record_change_snapshot(
            vault,
            target_rel=rel,
            actor=args.actor,
            reason=args.reason or "update note",
            metadata_before=metadata_before,
            body_before=body_before,
            dry_run=args.dry_run,
        )

    vault.write_note(rel, metadata, body, overwrite=True, dry_run=args.dry_run)

    related = [rel]
    if snapshot_rel:
        related.append(snapshot_rel)

    append_history_entry(
        vault,
        category="changes",
        actor=args.actor,
        action="update_note",
        target=rel,
        reason=args.reason or "update note",
        inputs={"updated_fields": sorted(list(updates.keys())), "append": bool(args.append_text)},
        result="updated",
        related=related,
        dry_run=args.dry_run,
    )

    return {
        "message": "Note updated",
        "path": rel,
        "snapshot": snapshot_rel,
        "dry_run": args.dry_run,
    }


def cmd_append_history(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    entry = append_history_entry(
        vault,
        category=args.category,
        actor=args.actor,
        action=args.action,
        target=args.target,
        reason=args.reason,
        inputs=parse_key_values(args.inputs),
        result=args.result,
        related=args.related or [],
        dry_run=args.dry_run,
    )
    return {
        "message": "History appended",
        "path": str(entry.relative_to(vault.root)),
        "dry_run": args.dry_run,
    }


def cmd_list_procedures(vault: Vault) -> dict[str, Any]:
    items = []
    for proc in list_procedures(vault):
        rel = str(proc.path.relative_to(vault.root))
        items.append(
            {
                "id": proc.metadata.get("id", ""),
                "title": proc.metadata.get("title", proc.path.stem),
                "status": proc.metadata.get("status", ""),
                "procedure_for": proc.metadata.get("procedure_for", ""),
                "path": rel,
            }
        )
    return {"count": len(items), "procedures": items}


def cmd_run_procedure(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    return run_procedure(
        vault,
        procedure_query=args.query,
        actor=args.actor,
        inputs=parse_key_values(args.inputs),
        dry_run=args.dry_run,
    )


def cmd_suggest_related(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    import difflib
    import re

    target_text = args.target
    target_path = None
    seed_title = args.target
    seed_tags: set[str] = set()
    seed_tokens: set[str] = set()

    try:
        path, metadata, body = vault.read_note(args.target)
        target_path = str(path.relative_to(vault.root))
        seed_title = metadata.get("title", path.stem)
        seed_tags = set(str(tag) for tag in metadata.get("tags", []))
        seed_tokens = set(re.findall(r"[a-zA-Z0-9_]{4,}", f"{seed_title} {body}".lower()))
    except Exception:
        seed_tokens = set(re.findall(r"[a-zA-Z0-9_]{4,}", target_text.lower()))

    suggestions: list[dict[str, Any]] = []
    for note in vault.list_markdown():
        rel = str(note.relative_to(vault.root))
        if rel == target_path:
            continue
        _, metadata, body = vault.read_note(rel)
        title = str(metadata.get("title", note.stem))
        note_tags = set(str(tag) for tag in metadata.get("tags", []))
        note_tokens = set(re.findall(r"[a-zA-Z0-9_]{4,}", f"{title} {body[:500]}".lower()))

        tag_score = len(seed_tags.intersection(note_tags)) * 3.0
        title_score = difflib.SequenceMatcher(None, str(seed_title).lower(), title.lower()).ratio() * 2.0
        token_den = max(1, len(seed_tokens.union(note_tokens)))
        token_score = (len(seed_tokens.intersection(note_tokens)) / token_den) * 5.0
        score = round(tag_score + title_score + token_score, 3)

        if score > 0.2:
            suggestions.append(
                {
                    "path": rel,
                    "title": title,
                    "score": score,
                    "shared_tags": sorted(seed_tags.intersection(note_tags)),
                }
            )

    suggestions.sort(key=lambda item: item["score"], reverse=True)
    return {
        "target": args.target,
        "count": min(args.limit, len(suggestions)),
        "suggestions": suggestions[: args.limit],
    }


def cmd_validate(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    path, metadata, _ = vault.read_note(args.path)
    rel = str(path.relative_to(vault.root))
    if is_agent_skill_bundle_path(rel):
        errors = validate_agent_skill_metadata(metadata)
    else:
        errors = validate_metadata(metadata)
    return {
        "path": rel,
        "valid": not errors,
        "errors": errors,
    }


def cmd_review_queue(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    queue = build_review_queue(vault)
    page = None
    if args.write_page:
        page_path = write_review_queue_page(vault, queue, dry_run=args.dry_run)
        page = str(page_path.relative_to(vault.root))
    return {
        "count": len(queue),
        "queue": queue,
        "page": page,
    }


def cmd_reindex(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    result = reindex(vault, dry_run=args.dry_run)
    return result


def cmd_install_skill(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    source = args.source or str((_repo_root() / "agent-skills" / CORE_AGENT_SKILL_NAME).resolve())
    report = install_skill_to_registry(vault, source=source, overwrite=args.force, dry_run=args.dry_run)
    append_history_entry(
        vault,
        category="actions",
        actor=args.actor,
        action="install_skill",
        target=report["registry_path"],
        reason=args.reason or "register shared agent skill",
        inputs={"source": source, "skill_name": report["skill_name"]},
        result="installed" if report["installed"] else report.get("reason", "skipped"),
        related=[report["registry_path"]],
        dry_run=args.dry_run,
    )
    return {
        "message": "Skill registered in MAKOS registry",
        **report,
        "dry_run": args.dry_run,
    }


def cmd_list_skills(vault: Vault) -> dict[str, Any]:
    skills = list_registry_skills(vault)
    return {"count": len(skills), "skills": skills}


def cmd_enable_skill(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    data = enable_skill(
        vault,
        skill_name=args.name,
        actor=args.actor,
        source=args.source,
        overwrite=args.force,
        dry_run=args.dry_run,
    )
    return {"message": "Skill enabled for agent runtime", **data, "dry_run": args.dry_run}


def cmd_disable_skill(vault: Vault, args: argparse.Namespace) -> dict[str, Any]:
    data = disable_skill(vault, skill_name=args.name, actor=args.actor, dry_run=args.dry_run)
    return {"message": "Skill disabled for agent runtime", **data, "dry_run": args.dry_run}


def cmd_agent_ready(vault: Vault, runtime: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
    core_skill = ensure_core_skill_registered_and_enabled(
        vault,
        repo_root=Path(runtime["repo_root"]),
        actor="system",
        dry_run=dry_run,
    )
    cfg_info = None
    cfg_path = runtime.get("config_path")
    if isinstance(cfg_path, str):
        try:
            cfg_info = read_runtime_config(Path(cfg_path))
        except Exception:
            cfg_info = {"warning": f"Could not parse config: {cfg_path}"}

    return {
        "message": "MAKOS runtime ready",
        "status": "ok",
        "mode": runtime.get("mode", "auto"),
        "repo_root": runtime.get("repo_root"),
        "workspace_root": runtime.get("workspace_root"),
        "vault_path": str(vault.root),
        "vault_source": runtime.get("vault_source"),
        "bootstrapped": runtime.get("bootstrapped", False),
        "config_path": runtime.get("config_path"),
        "config": cfg_info,
        "recommended_cli": runtime.get("recommended_cli", "~/.makos/bin/makos"),
        "core_skill": core_skill,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="makos", description="MAKOS multi-agent knowledge OS bridge")
    parser.add_argument(
        "--vault",
        default=None,
        help="Path to vault root (optional; auto-discovered/bootstrapped if omitted)",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--dry-run", action="store_true", help="Do not write files")

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init", help="Initialize a vault from template")
    init_cmd.add_argument("target", nargs="?", help="Target vault path")
    init_cmd.add_argument("--template", help="Path to vault template")
    init_cmd.add_argument("--force", action="store_true", help="Merge into non-empty target")

    subparsers.add_parser("agent-ready", help="Auto-discover/bootstrap runtime and return resolved paths")
    subparsers.add_parser("list-skills", help="List shared agent skills in MAKOS registry")
    install_skill_cmd = subparsers.add_parser("install-skill", help="Install a Claude-style skill bundle into MAKOS registry")
    install_skill_cmd.add_argument("source", nargs="?", help="Path to skill directory or SKILL.md; defaults to core MAKOS skill")
    install_skill_cmd.add_argument("--actor", default="agent")
    install_skill_cmd.add_argument("--reason", default="")
    install_skill_cmd.add_argument("--force", action="store_true", help="Overwrite existing registry bundle")

    enable_skill_cmd = subparsers.add_parser("enable-skill", help="Enable a shared skill for the Claude runtime")
    enable_skill_cmd.add_argument("name", help="Skill bundle name")
    enable_skill_cmd.add_argument("--source", help="Optional skill source to install before enabling")
    enable_skill_cmd.add_argument("--actor", default="agent")
    enable_skill_cmd.add_argument("--force", action="store_true", help="Overwrite existing registry bundle if source is provided")

    disable_skill_cmd = subparsers.add_parser("disable-skill", help="Disable a shared skill for the Claude runtime")
    disable_skill_cmd.add_argument("name", help="Skill bundle name")
    disable_skill_cmd.add_argument("--actor", default="agent")

    subparsers.add_parser("doctor", help="Health checks for vault")

    search_cmd = subparsers.add_parser("search", help="Search markdown content")
    search_cmd.add_argument("query", help="Search query")
    search_cmd.add_argument("--scope", help="Subfolder scope")
    search_cmd.add_argument("--limit", type=int, default=20)
    search_cmd.add_argument("--prefer-obsidian", action="store_true")

    read_cmd = subparsers.add_parser("read", help="Read a note")
    read_cmd.add_argument("path", help="Relative path to note")
    read_cmd.add_argument("--raw", action="store_true", help="Return raw file")

    create_cmd = subparsers.add_parser("create", help="Create a note with policy checks")
    create_cmd.add_argument("--type", required=True, choices=sorted(DOCUMENT_TYPES))
    create_cmd.add_argument("--title", required=True)
    create_cmd.add_argument("--path", help="Custom relative path")
    create_cmd.add_argument("--domain", default="general")
    create_cmd.add_argument("--status", default="draft")
    create_cmd.add_argument("--confidence", type=float, default=0.5)
    create_cmd.add_argument("--author", dest="authors", action="append")
    create_cmd.add_argument("--owner", dest="owners", action="append")
    create_cmd.add_argument("--tag", dest="tags", action="append")
    create_cmd.add_argument("--source-type", default="generated")
    create_cmd.add_argument("--source-ref", dest="source_refs", action="append")
    create_cmd.add_argument("--related", action="append")
    create_cmd.add_argument("--supersedes", action="append")
    create_cmd.add_argument("--procedure-for")
    create_cmd.add_argument("--skill-for")
    create_cmd.add_argument("--review-due")
    create_cmd.add_argument("--write-permission", dest="write_permissions", action="append")
    create_cmd.add_argument("--visibility", default="shared")
    create_cmd.add_argument("--with-checksum", action="store_true")
    create_cmd.add_argument("--body")
    create_cmd.add_argument("--body-file")
    create_cmd.add_argument("--actor", default="agent")
    create_cmd.add_argument("--reason", default="")
    create_cmd.add_argument("--force", action="store_true")

    update_cmd = subparsers.add_parser("update", help="Update a note preserving history")
    update_cmd.add_argument("path", help="Note path to update")
    update_cmd.add_argument("--set", dest="set_values", action="append", help="Metadata key=value")
    update_cmd.add_argument("--append", dest="append_text", help="Text to append to body")
    update_cmd.add_argument("--body", help="Replace body with explicit text")
    update_cmd.add_argument("--body-file", help="Replace body from file")
    update_cmd.add_argument("--actor", default="agent")
    update_cmd.add_argument("--reason", default="update note")
    update_cmd.add_argument("--no-preserve-history", action="store_true")

    append_history_cmd = subparsers.add_parser("append-history", help="Create history entry")
    append_history_cmd.add_argument("--category", required=True, choices=["actions", "decisions", "changes"])
    append_history_cmd.add_argument("--actor", default="agent")
    append_history_cmd.add_argument("--action", required=True)
    append_history_cmd.add_argument("--target", required=True)
    append_history_cmd.add_argument("--reason", default="n/a")
    append_history_cmd.add_argument("--input", dest="inputs", action="append")
    append_history_cmd.add_argument("--result", default="ok")
    append_history_cmd.add_argument("--related", action="append")

    subparsers.add_parser("list-procedures", help="List available procedures")

    run_proc_cmd = subparsers.add_parser("run-procedure", help="Execute procedure into workspace")
    run_proc_cmd.add_argument("query", help="Procedure id/title/path")
    run_proc_cmd.add_argument("--actor", default="agent")
    run_proc_cmd.add_argument("--input", dest="inputs", action="append")

    suggest_cmd = subparsers.add_parser("suggest-related", help="Suggest related notes")
    suggest_cmd.add_argument("target", help="Note path or free text query")
    suggest_cmd.add_argument("--limit", type=int, default=10)

    validate_cmd = subparsers.add_parser("validate-note", help="Validate frontmatter")
    validate_cmd.add_argument("path", help="Note path")

    review_cmd = subparsers.add_parser("review-queue", help="List pending review items")
    review_cmd.add_argument("--write-page", action="store_true", help="Write 10-human-views/review-queue.md")

    subparsers.add_parser("reindex", help="Rebuild indexes")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    raw_argv = sys.argv[1:] if argv is None else argv
    args = parser.parse_args(_normalize_global_args(raw_argv))

    try:
        if args.command == "init":
            data = cmd_init(args)
            _print_data(data, as_json=args.json)
            return 0

        vault, runtime = _autobootstrap_vault_if_needed(args)

        if args.command == "agent-ready":
            data = cmd_agent_ready(vault, runtime, dry_run=args.dry_run)
        elif args.command == "list-skills":
            data = cmd_list_skills(vault)
        elif args.command == "install-skill":
            data = cmd_install_skill(vault, args)
        elif args.command == "enable-skill":
            data = cmd_enable_skill(vault, args)
        elif args.command == "disable-skill":
            data = cmd_disable_skill(vault, args)
        elif args.command == "doctor":
            data = cmd_doctor(vault)
        elif args.command == "search":
            data = cmd_search(vault, args)
        elif args.command == "read":
            data = cmd_read(vault, args)
        elif args.command == "create":
            data = cmd_create(vault, args)
        elif args.command == "update":
            data = cmd_update(vault, args)
        elif args.command == "append-history":
            data = cmd_append_history(vault, args)
        elif args.command == "list-procedures":
            data = cmd_list_procedures(vault)
        elif args.command == "run-procedure":
            data = cmd_run_procedure(vault, args)
        elif args.command == "suggest-related":
            data = cmd_suggest_related(vault, args)
        elif args.command == "validate-note":
            data = cmd_validate(vault, args)
        elif args.command == "review-queue":
            data = cmd_review_queue(vault, args)
        elif args.command == "reindex":
            data = cmd_reindex(vault, args)
        else:
            raise CLIError(f"Unknown command: {args.command}")

        _print_data(data, as_json=args.json)
        return 0
    except (CLIError, VaultError, ValueError, FileNotFoundError) as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, ensure_ascii=True))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
