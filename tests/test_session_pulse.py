"""Tests for scripts/session_pulse.py — file-backed session heartbeat."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))  # noqa: E402

from scripts.session_pulse import build_pulse  # noqa: E402


def test_pulse_has_required_fields():
    pulse = build_pulse("test-agent")
    for field in ("timestamp", "agent", "git", "pending_phases", "pulse_schema"):
        assert field in pulse, f"missing field: {field}"


def test_pulse_agent_stored():
    pulse = build_pulse("my-agent-id")
    assert pulse["agent"] == "my-agent-id"


def test_pulse_note_stored():
    pulse = build_pulse("agent", note="some work note")
    assert pulse["note"] == "some work note"


def test_pulse_note_defaults_empty():
    pulse = build_pulse("agent")
    assert pulse["note"] == ""


def test_pulse_git_fields():
    pulse = build_pulse("agent")
    git = pulse["git"]
    assert "branch" in git
    assert "ahead_of_master" in git
    assert "uncommitted_files" in git
    assert "last_commit" in git


def test_pulse_git_uncommitted_is_int():
    pulse = build_pulse("agent")
    assert isinstance(pulse["git"]["uncommitted_files"], int)


def test_pulse_pending_phases_is_list():
    pulse = build_pulse("agent")
    assert isinstance(pulse["pending_phases"], list)


def test_pulse_schema_version():
    pulse = build_pulse("agent")
    assert pulse["pulse_schema"] == "v1"


def test_pulse_timestamp_is_iso():
    pulse = build_pulse("agent")
    ts = pulse["timestamp"]
    assert "T" in ts and "+" in ts or "Z" in ts


def test_pulse_serializable_to_json():
    pulse = build_pulse("agent", note="test")
    dumped = json.dumps(pulse)
    reloaded = json.loads(dumped)
    assert reloaded["agent"] == "agent"


def test_pulse_writes_to_file(tmp_path, monkeypatch):
    import scripts.session_pulse as sp

    target = tmp_path / "pulse.json"
    monkeypatch.setattr(sp, "PULSE_PATH", target)
    pulse = build_pulse("agent")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(pulse), encoding="utf-8")
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["agent"] == "agent"


def test_pulse_short_board_is_string():
    pulse = build_pulse("agent")
    assert isinstance(pulse["short_board"], str)
    assert len(pulse["short_board"]) > 0
