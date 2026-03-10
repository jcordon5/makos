from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from makos_bridge.vault import Vault


@pytest.fixture()
def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture()
def template_vault(tmp_path: Path, repo_root: Path) -> Vault:
    source = repo_root / "vault-template"
    target = tmp_path / "vault"
    shutil.copytree(source, target)
    return Vault(target)
