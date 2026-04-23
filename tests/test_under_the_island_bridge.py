"""Tests for games/under_the_island/bridge — FileBridgeAdapter edge cases."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from games.under_the_island.bridge.event_adapter import FileBridgeAdapter


class TestFileBridgeAdapterBom:
    """PowerShell Set-Content -Encoding utf8 writes a UTF-8 BOM.
    The adapter must handle BOM-prefixed JSON without crashing.
    """

    def _adapter(self, tmp_path: Path) -> tuple[FileBridgeAdapter, Path, Path]:
        ev = tmp_path / "bridge_event.json"
        rp = tmp_path / "bridge_reply.json"
        return FileBridgeAdapter(event_file=ev, reply_file=rp), ev, rp

    def test_reads_bom_prefixed_json(self, tmp_path: Path) -> None:
        adapter, ev, _ = self._adapter(tmp_path)
        payload = {"event": "puzzle_solved", "player_choice": "helped", "scene": "cave"}
        # Write with BOM (simulates PowerShell Set-Content -Encoding utf8)
        bom_bytes = b"\xef\xbb\xbf" + json.dumps(payload).encode("utf-8")
        ev.write_bytes(bom_bytes)
        events = list(adapter.poll())
        assert len(events) == 1
        assert events[0].event == "puzzle_solved"
        assert events[0].player_choice == "helped"
        assert events[0].scene == "cave"

    def test_reads_plain_utf8_json(self, tmp_path: Path) -> None:
        adapter, ev, _ = self._adapter(tmp_path)
        payload = {"event": "npc_talk", "player_choice": "asked", "scene": "market"}
        ev.write_text(json.dumps(payload), encoding="utf-8")
        events = list(adapter.poll())
        assert len(events) == 1
        assert events[0].event == "npc_talk"

    def test_no_duplicate_read_same_mtime(self, tmp_path: Path) -> None:
        adapter, ev, _ = self._adapter(tmp_path)
        payload = {"event": "e", "player_choice": "c", "scene": "s"}
        ev.write_text(json.dumps(payload), encoding="utf-8")
        first = list(adapter.poll())
        second = list(adapter.poll())  # mtime unchanged → should yield nothing
        assert len(first) == 1
        assert len(second) == 0

    def test_write_reply_produces_valid_json(self, tmp_path: Path) -> None:
        adapter, _, rp = self._adapter(tmp_path)
        adapter.write_reply("你好，旅人。", 0.55)
        assert rp.exists()
        data = json.loads(rp.read_text(encoding="utf-8"))
        assert data["reply"] == "你好，旅人。"
        assert abs(data["trust"] - 0.55) < 0.001

    def test_cleanup_removes_both_files(self, tmp_path: Path) -> None:
        adapter, ev, rp = self._adapter(tmp_path)
        ev.write_text("{}", encoding="utf-8")
        rp.write_text("{}", encoding="utf-8")
        adapter.cleanup()
        assert not ev.exists()
        assert not rp.exists()
