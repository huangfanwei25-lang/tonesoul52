"""event_adapter.py — Abstract event source interface.

Concrete adapters implement EventAdapter and are plugged into bridge server:
  MockEventAdapter   — replay fake_events.json, no game needed
  FileBridgeAdapter  — file I/O bridge for games without HTTP extension
                       GML writes event file → Python reads → writes reply file → GML polls
"""

from __future__ import annotations

import abc
import json
import os
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass
class GameEvent:
    event: str
    player_choice: str
    scene: str
    raw: dict | None = None


class EventAdapter(abc.ABC):
    """Base class for all event sources."""

    @abc.abstractmethod
    def poll(self) -> Iterator[GameEvent]:
        """Yield any new events since last poll."""

    def close(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Mock adapter — for local dev without the game running
# ---------------------------------------------------------------------------

class MockEventAdapter(EventAdapter):
    """Replays events from mock/fake_events.json in order."""

    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            path = Path(__file__).parent.parent / "mock" / "fake_events.json"
        self._events: list[dict] = []
        if path.is_file():
            with path.open(encoding="utf-8") as f:
                self._events = json.load(f)
        self._index = 0

    def poll(self) -> Iterator[GameEvent]:
        while self._index < len(self._events):
            e = self._events[self._index]
            self._index += 1
            yield GameEvent(
                event=e.get("event", ""),
                player_choice=e.get("player_choice", ""),
                scene=e.get("scene", ""),
                raw=e,
            )


# ---------------------------------------------------------------------------
# File bridge adapter — for GM builds without confirmed http_request support
#
# Protocol:
#   Game writes:  <event_file>   {"event":..., "player_choice":..., "scene":...}
#   Bridge reads event, calls AI, writes: <reply_file>  {"reply":..., "trust":...}
#   Game polls reply_file existence, reads reply, then deletes both files
#
# Default paths use system temp dir so no install path is hardcoded.
# Override via constructor or --event-file / --reply-file CLI flags.
# ---------------------------------------------------------------------------

_DEFAULT_EVENT_FILE = Path(tempfile.gettempdir()) / "bridge_event.json"
_DEFAULT_REPLY_FILE = Path(tempfile.gettempdir()) / "bridge_reply.json"


class FileBridgeAdapter(EventAdapter):
    """Polls a temp file written by GML file I/O; yields events when found."""

    def __init__(
        self,
        event_file: Path = _DEFAULT_EVENT_FILE,
        reply_file: Path = _DEFAULT_REPLY_FILE,
        poll_interval: float = 0.25,
    ) -> None:
        self.event_file = event_file
        self.reply_file = reply_file
        self.poll_interval = poll_interval
        self._last_mtime: float = 0.0

    def poll(self) -> Iterator[GameEvent]:
        if not self.event_file.exists():
            return
        try:
            mtime = self.event_file.stat().st_mtime
        except OSError:
            return
        if mtime <= self._last_mtime:
            return
        self._last_mtime = mtime
        try:
            raw = json.loads(self.event_file.read_text(encoding="utf-8"))
        except Exception:
            return
        yield GameEvent(
            event=raw.get("event", ""),
            player_choice=raw.get("player_choice", ""),
            scene=raw.get("scene", ""),
            raw=raw,
        )

    def write_reply(self, reply: str, trust: float) -> None:
        """Write AI reply so GML can read it."""
        self.reply_file.write_text(
            json.dumps({"reply": reply, "trust": round(trust, 3)}, ensure_ascii=False),
            encoding="utf-8",
        )

    def cleanup(self) -> None:
        """Remove both files after GML has read the reply."""
        for f in (self.event_file, self.reply_file):
            try:
                f.unlink(missing_ok=True)
            except OSError:
                pass
