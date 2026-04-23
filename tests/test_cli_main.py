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


def test_no_args_shows_help_and_exits_zero():
    from tonesoul.cli.main import main
    rc = main([])
    assert rc == 0


def test_dash_h_shows_help_exits_zero():
    from tonesoul.cli.main import main
    rc = main(["-h"])
    assert rc == 0


def test_unknown_command_error_message(capsys):
    from tonesoul.cli.main import main
    main(["nonexistent_command"])
    err = capsys.readouterr().err
    assert "nonexistent_command" in err


def test_heartbeat_with_note(tmp_path):
    from tonesoul.cli.main import main
    hb_file = str(tmp_path / "hb_note.jsonl")
    rc = main(["heartbeat", "--agent", "noted-agent", "--path", hb_file, "--note", "test note"])
    assert rc == 0
    records = [json.loads(l) for l in Path(hb_file).read_text().splitlines() if l.strip()]
    assert records[0].get("note") == "test note"


def test_print_help_output(capsys):
    from tonesoul.cli.main import _print_help
    _print_help()
    out = capsys.readouterr().out
    assert "ToneSoul" in out
    assert "diagnose" in out
    assert "heartbeat" in out


def test_keyboard_interrupt_returns_130(monkeypatch):
    import importlib
    cli_mod = importlib.import_module("tonesoul.cli.main")

    def _raise_interrupt(argv):
        raise KeyboardInterrupt

    monkeypatch.setitem(cli_mod._SUBCOMMANDS, "vows", (_raise_interrupt, "test"))
    rc = cli_mod.main(["vows"])
    assert rc == 130


def test_system_exit_zero_from_handler(monkeypatch):
    import importlib
    cli_mod = importlib.import_module("tonesoul.cli.main")

    def _raise_exit(argv):
        raise SystemExit(0)

    monkeypatch.setitem(cli_mod._SUBCOMMANDS, "diagnose", (_raise_exit, "test"))
    rc = cli_mod.main(["diagnose"])
    assert rc == 0


def test_system_exit_nonzero_from_handler(monkeypatch):
    import importlib
    cli_mod = importlib.import_module("tonesoul.cli.main")

    def _raise_exit(argv):
        raise SystemExit(2)

    monkeypatch.setitem(cli_mod._SUBCOMMANDS, "diagnose", (_raise_exit, "test"))
    rc = cli_mod.main(["diagnose"])
    assert rc == 2


def test_subcommand_description_strings():
    from tonesoul.cli.main import _SUBCOMMANDS
    for name, (handler, desc) in _SUBCOMMANDS.items():
        assert isinstance(desc, str)
        assert len(desc) > 5
