from __future__ import annotations

import pytest

from makos_bridge.vault import Vault, VaultError


def test_vault_resolve_blocks_path_escape(template_vault: Vault) -> None:
    with pytest.raises(VaultError):
        template_vault.resolve("../outside.md")


def test_vault_resolve_allows_relative_inside(template_vault: Vault) -> None:
    resolved = template_vault.resolve("00-system/system-overview.md")
    assert resolved.exists()
    assert template_vault.root in resolved.parents
