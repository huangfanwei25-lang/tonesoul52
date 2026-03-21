"""Soul Persistence — cross-session Ψ integral storage.

Bridges the in-memory ``TensionEngine._persistence`` value to a durable
JSON file so that the cumulative tension history survives process restarts.

The canonical persistence path follows the private-runtime boundary:
``memory/autonomous/soul_psi.json``
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_DEFAULT_PATH = Path("memory/autonomous/soul_psi.json")


@dataclass
class SoulPsiSnapshot:
    """Serialisable snapshot of the Ψ integral state."""

    psi: float = 0.0
    step_count: int = 0
    updated_at: str = ""

    def __post_init__(self) -> None:
        if not self.updated_at:
            self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def save_psi(
    psi: float,
    step_count: int = 0,
    path: Optional[Path] = None,
) -> SoulPsiSnapshot:
    """Persist the current Ψ value to disk."""
    path = path or _DEFAULT_PATH
    snapshot = SoulPsiSnapshot(
        psi=psi,
        step_count=step_count,
        updated_at=datetime.now(timezone.utc).isoformat(),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot.to_dict(), indent=2), encoding="utf-8")
    return snapshot


def load_psi(path: Optional[Path] = None) -> SoulPsiSnapshot:
    """Load the persisted Ψ value, returning a zero snapshot if missing."""
    path = path or _DEFAULT_PATH
    if not path.exists():
        return SoulPsiSnapshot()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return SoulPsiSnapshot(
            psi=float(data.get("psi", 0.0)),
            step_count=int(data.get("step_count", 0)),
            updated_at=str(data.get("updated_at", "")),
        )
    except (json.JSONDecodeError, ValueError, TypeError):
        return SoulPsiSnapshot()
