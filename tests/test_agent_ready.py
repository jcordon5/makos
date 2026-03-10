from __future__ import annotations

import json
from pathlib import Path

from makos_bridge.cli import main


def test_agent_ready_bootstraps_workspace(monkeypatch, tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "workspace"
    fake_home = tmp_path / "home"
    workspace.mkdir()
    fake_home.mkdir()

    monkeypatch.chdir(workspace)
    monkeypatch.delenv("MAKOS_VAULT", raising=False)
    monkeypatch.setenv("HOME", str(fake_home))

    exit_code = main(["--json", "agent-ready"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["status"] == "ok"
    assert payload["bootstrapped"] is True
    assert payload["mode"] == "global"

    vault = fake_home / ".makos" / "vault"
    assert (vault / "00-system" / "system-overview.md").exists()
    assert (fake_home / ".makos" / "config.json").exists()
    assert (fake_home / ".makos" / "bin" / "makos").exists()
    assert (fake_home / ".claude" / "skills" / "makos-context-os").exists()


def test_command_without_vault_uses_bootstrapped_runtime(monkeypatch, tmp_path: Path) -> None:
    workspace = tmp_path / "workspace2"
    fake_home = tmp_path / "home2"
    workspace.mkdir()
    fake_home.mkdir()
    monkeypatch.chdir(workspace)
    monkeypatch.delenv("MAKOS_VAULT", raising=False)
    monkeypatch.setenv("HOME", str(fake_home))

    assert main(["agent-ready"]) == 0
    assert main(["doctor"]) == 0


def test_agent_ready_with_explicit_vault_persists_global_config(monkeypatch, tmp_path: Path, capsys) -> None:
    fake_home = tmp_path / "home3"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.chdir(tmp_path)

    existing_vault = tmp_path / "existing-vault"
    assert main(["init", str(existing_vault), "--force"]) == 0
    capsys.readouterr()

    exit_code = main(["--vault", str(existing_vault), "--json", "agent-ready"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["vault_path"] == str(existing_vault.resolve())

    config = json.loads((fake_home / ".makos" / "config.json").read_text(encoding="utf-8"))
    assert config["vault_path"] == str(existing_vault.resolve())
