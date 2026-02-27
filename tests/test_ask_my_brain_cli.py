from __future__ import annotations

import json
import subprocess
import sys


def test_ask_my_brain_learn_and_query_json(tmp_path):
    db_path = tmp_path / "brain-db"

    learn_cmd = [
        sys.executable,
        "scripts/ask_my_brain.py",
        "--learn",
        "tension memory resonance",
        "--db-path",
        str(db_path),
        "--profile",
        "tonesoul",
        "--tension",
        "0.8",
    ]
    learn_result = subprocess.run(learn_cmd, capture_output=True, text=True, check=False)
    assert learn_result.returncode == 0, learn_result.stderr
    assert "ingested" in learn_result.stdout

    query_cmd = [
        sys.executable,
        "scripts/ask_my_brain.py",
        "resonance",
        "--db-path",
        str(db_path),
        "--json",
    ]
    query_result = subprocess.run(query_cmd, capture_output=True, text=True, check=False)
    assert query_result.returncode == 0, query_result.stderr

    payload = json.loads(query_result.stdout)
    assert isinstance(payload, list)
    assert len(payload) >= 1
    assert payload[0]["content"] == "tension memory resonance"


def test_ask_my_brain_profile_note():
    cmd = [sys.executable, "scripts/ask_my_brain.py", "--why-tonesoul"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "OpenClaw vs ToneSoul" in result.stdout
