from __future__ import annotations

from pathlib import Path

from makos_bridge.skills import disable_skill, enable_skill, install_skill_to_registry, list_registry_skills
from makos_bridge.vault import Vault


def test_install_enable_disable_skill(template_vault: Vault, repo_root: Path, monkeypatch, tmp_path: Path) -> None:
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))

    source = repo_root / "agent-skills" / "makos-context-os"

    install_report = install_skill_to_registry(template_vault, source=source)
    assert install_report["skill_name"] == "makos-context-os"
    assert (template_vault.root / install_report["registry_path"]).exists()

    enable_report = enable_skill(template_vault, skill_name="makos-context-os", actor="test")
    assert enable_report["enabled"] is True
    assert (fake_home / ".claude" / "skills" / "makos-context-os").exists()
    assert (template_vault.root / enable_report["manifest_path"]).exists()

    skills = list_registry_skills(template_vault)
    assert any(skill["name"] == "makos-context-os" and skill["enabled"] for skill in skills)

    disable_report = disable_skill(template_vault, skill_name="makos-context-os", actor="test")
    assert disable_report["enabled"] is False
    assert not (fake_home / ".claude" / "skills" / "makos-context-os").exists()
    assert (template_vault.root / disable_report["manifest_path"]).exists()
