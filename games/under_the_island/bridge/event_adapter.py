"""event_adapter.py — Abstract event source interface.

Concrete adapters (save-file watcher, mock source, OCR fallback) implement
EventAdapter and are plugged into the bridge server at startup.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import Iterator


@dataclass
class GameEvent:
    event: str          # e.g. "gear_puzzle_solved"
    player_choice: str  # e.g. "helped_npc"
    scene: str          # e.g. "underground_chamber"
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

import json
from pathlib import Path


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
