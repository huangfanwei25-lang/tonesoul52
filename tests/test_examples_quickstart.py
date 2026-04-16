from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_quickstart_json_mode_outputs_structured_payload() -> None:
    completed = subprocess.run(
        [sys.executable, "examples/quickstart.py", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["demo"] == "tonesoul_quickstart"
    assert payload["governance"]["active_vow_count"] >= 1
    assert payload["vow_enforcement"]["status"] in {"pass", "flagged", "repair", "blocked"}
    assert payload["council"]["perspective_count"] >= 4
    assert len(payload["council"]["votes"]) == payload["council"]["perspective_count"]
