"""Runtime auto-discovery and zero-config bootstrap helpers."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .constants import REQUIRED_DIRECTORIES
from .utils import utc_now_iso


def looks_like_vault(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    required_roots = {"00-system", "01-inbox", "02-procedures", "03-skills", "04-knowledge"}
    return all((path / name).exists() for name in required_roots)


def find_workspace_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / ".git").exists() or (candidate / ".vscode").exists():
            return candidate
    return start


def find_vault_upwards(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        if looks_like_vault(candidate):
            return candidate
        vault_local = candidate / "vault-local"
        if looks_like_vault(vault_local):
            return vault_local
    return None


def find_config_upwards(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        cfg = candidate / ".makos" / "config.json"
        if cfg.exists() and cfg.is_file():
            return cfg
    return None


def global_config_path() -> Path:
    return Path.home() / ".makos" / "config.json"


def global_vault_path() -> Path:
    return Path.home() / ".makos" / "vault"


def ensure_global_launcher(repo_root: Path) -> Path:
    """Create a stable launcher at ~/.makos/bin/makos for cross-workspace usage."""
    bin_dir = Path.home() / ".makos" / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    launcher = bin_dir / "makos"

    target = (repo_root / "makos").resolve()
    launcher.write_text(
        "#!/usr/bin/env sh\n"
        "set -eu\n"
        f'exec "{target}" "$@"\n',
        encoding="utf-8",
    )
    launcher.chmod(0o755)
    return launcher


def read_runtime_config(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid runtime config at {path}")
    return data


def write_runtime_config(config_root: Path, *, repo_root: Path, vault_path: Path) -> Path:
    cfg_dir = config_root
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / "config.json"
    launcher = ensure_global_launcher(repo_root)

    payload = {
        "version": 1,
        "created_at": utc_now_iso(),
        "repo_root": str(repo_root),
        "vault_path": str(vault_path),
        "cli_entry": str(launcher),
    }
    cfg_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    return cfg_path


def resolve_vault_candidate(start: Path) -> tuple[Path | None, str]:
    env_vault = os.getenv("MAKOS_VAULT")
    if env_vault:
        candidate = Path(env_vault).expanduser().resolve()
        if looks_like_vault(candidate):
            return candidate, "env"

    global_cfg = global_config_path()
    if global_cfg.exists():
        try:
            cfg = read_runtime_config(global_cfg)
            vault_cfg = cfg.get("vault_path")
            if isinstance(vault_cfg, str):
                candidate = Path(vault_cfg).expanduser().resolve()
                if looks_like_vault(candidate):
                    return candidate, f"global-config:{global_cfg}"
        except Exception:
            pass

    cfg_path = find_config_upwards(start)
    if cfg_path:
        try:
            cfg = read_runtime_config(cfg_path)
            vault_cfg = cfg.get("vault_path")
            if isinstance(vault_cfg, str):
                candidate = Path(vault_cfg).expanduser().resolve()
                if looks_like_vault(candidate):
                    return candidate, f"config:{cfg_path}"
        except Exception:
            pass

    detected = find_vault_upwards(start)
    if detected:
        return detected, "workspace"

    global_vault = global_vault_path().resolve()
    if looks_like_vault(global_vault):
        return global_vault, "global-default"

    return None, "none"


def required_dirs_report(vault_path: Path) -> list[str]:
    missing: list[str] = []
    for directory in REQUIRED_DIRECTORIES:
        if not (vault_path / directory).exists():
            missing.append(directory)
    return missing
