"""Tests for the unified ToneSoul CLI entry point."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def test_help_exits_zero():
    from tonesoul.cli.main import main
    rc = main(["--help"])
    assert rc == 0


def test_unknown_command_exits_nonzero():
    from tonesoul.cli.main import main
    rc = main(["totally_unknown_command_xyz"])
    assert rc != 0


def test_heartbeat_subcommand(tmp_path):
    hb_file = str(tmp_path / "hb.jsonl")
    from tonesoul.cli.main import main
    rc = main(["heartbeat", "--agent", "test-agent", "--path", hb_file])
    assert rc == 0
    assert Path(hb_file).exists()
    records = [json.loads(l) for l in Path(hb_file).read_text().splitlines() if l.strip()]
    assert len(records) == 1
    assert records[0]["agent"] == "test-agent"


def test_heartbeat_status_only(tmp_path):
    from tonesoul.cli.main import main
    hb_file = str(tmp_path / "no_pulse.jsonl")
    rc = main(["heartbeat", "--status-only", "--path", hb_file])
    assert rc == 0


def test_vows_subcommand():
    from tonesoul.cli.main import main
    rc = main(["vows"])
    assert rc == 0


def test_diagnose_subcommand():
    from tonesoul.cli.main import main
    rc = main(["diagnose", "--compact"])
    assert rc == 0


def test_subcommand_list_is_complete():
    from tonesoul.cli.main import _SUBCOMMANDS
    expected = {"diagnose", "council", "context", "heartbeat", "ystm", "vows"}
    assert set(_SUBCOMMANDS.keys()) == expected
