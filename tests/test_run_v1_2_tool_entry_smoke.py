from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.run_v1_2_tool_entry_smoke import run_v1_2_tool_entry_smoke


def test_run_v1_2_tool_entry_smoke_returns_compact_status() -> None:
    payload = run_v1_2_tool_entry_smoke(agent="smoke-test")

    assert payload["contract_version"] == "v1"
    assert payload["bundle"] == "v1_2_tool_entry_smoke"
    assert payload["workflow_alignment"]["first_hop"] == "session_start --slim"
    assert payload["session_start_size"]["slim_lt_2kb"] is True
    assert payload["mcp_stdio_smoke"]["returncode"] == 0
    assert payload["mcp_stdio_smoke"]["initialize_ok"] is True
    assert payload["mcp_stdio_smoke"]["initialized_notification_sent"] is True
    assert payload["mcp_stdio_smoke"]["batch_response_count"] >= 1
    assert payload["mcp_stdio_smoke"]["council_deliberate"]["_compact"] is True
    assert payload["mcp_stdio_smoke"]["council_get_status"]["kind"] == "governance_summary"
    assert payload["mcp_stdio_smoke"]["governance_load"]["kind"] == "governance_summary"


def test_run_v1_2_tool_entry_smoke_cli_writes_surfaces(tmp_path: Path) -> None:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_v1_2_tool_entry_smoke.py"
    json_out = tmp_path / "tool_entry_smoke.json"
    md_out = tmp_path / "tool_entry_smoke.md"

    completed = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--agent",
            "smoke-cli",
            "--json-out",
            str(json_out),
            "--markdown-out",
            str(md_out),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["session_start_size"]["slim_lt_2kb"] is True
    assert json_out.is_file()
    assert md_out.is_file()
    markdown = md_out.read_text(encoding="utf-8")
    assert "Tool-First Entry Smoke" in markdown
    assert "session_start --slim" in markdown
