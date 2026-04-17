from __future__ import annotations

import json
from pathlib import Path


def _extension_root() -> Path:
    return Path(__file__).resolve().parents[1] / "extensions" / "vscode"


def test_vscode_extension_manifest_exists_and_is_minimal() -> None:
    root = _extension_root()
    manifest = json.loads((root / "package.json").read_text(encoding="utf-8"))

    assert manifest["name"] == "tonesoul-vscode"
    assert manifest["main"] == "./extension.js"
    assert manifest["engines"]["vscode"].startswith("^")
    commands = {item["command"] for item in manifest["contributes"]["commands"]}
    assert commands == {
        "tonesoul.startMcpServer",
        "tonesoul.stopMcpServer",
        "tonesoul.showSlimEntry",
    }
    assert "dependencies" not in manifest


def test_vscode_extension_files_reference_mcp_and_slim_entry() -> None:
    root = _extension_root()
    extension_text = (root / "extension.js").read_text(encoding="utf-8")
    readme_text = (root / "README.md").read_text(encoding="utf-8")

    assert "tonesoul.mcp_server" in extension_text
    assert "start_agent_session.py" in extension_text
    assert "--slim" in extension_text
    assert "createStatusBarItem" in extension_text
    assert "Show Slim Entry" in readme_text
    assert "MCP" in readme_text
