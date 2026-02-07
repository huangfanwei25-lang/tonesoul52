"""
ToneSoul Time-Island Protocol
語魂時間島協議

Encapsulates decision periods with bounded context, inputs, outputs, and audit trails.
封裝決策週期，包含有界上下文、輸入、輸出和審計軌跡。
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_iso() -> str:
    return _utc_now().isoformat().replace("+00:00", "Z")


def _utc_id_stamp() -> str:
    return _utc_now().strftime("%Y-%m-%d-%H%M%S-%f")


class IslandState(Enum):
    """Time-Island lifecycle states"""

    DRAFT = "draft"  # 草稿，尚未確定
    ACTIVE = "active"  # 進行中
    COMPLETED = "completed"  # 完成
    ARCHIVED = "archived"  # 歸檔


@dataclass
class SourceTrace:
    """A single source reference"""

    kind: str  # e.g., "file", "memory", "user_input", "api"
    ref: str  # Path or identifier
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = _utc_iso()

    def to_dict(self) -> Dict:
        return {
            "kind": self.kind,
            "ref": self.ref,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "SourceTrace":
        return cls(
            kind=data["kind"],
            ref=data["ref"],
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class ChangelogEntry:
    """A single changelog entry"""

    action: str
    reason: str
    timestamp: str = ""
    actor: str = "system"

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = _utc_iso()

    def to_dict(self) -> Dict:
        return {
            "action": self.action,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "actor": self.actor,
        }


@dataclass
class TimeIsland:
    """
    Time-Island: A bounded decision context.

    時間島：有界的決策上下文。

    每個重要決策/演進都映射為一個 Time-Island。
    """

    id: str
    bounded_context: str
    window_start: str
    window_end: str = ""

    # Inputs and Outputs
    inputs: List[SourceTrace] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)

    # Quality metrics
    poav_weights: Dict[str, float] = field(
        default_factory=lambda: {"P": 0.25, "O": 0.25, "A": 0.25, "V": 0.25}
    )

    # Resonance signal
    resonance_signal: Dict[str, float] = field(
        default_factory=lambda: {
            "value_fit": 0.0,
            "consensus": 0.0,
            "risk": 0.0,
        }
    )

    # Drift tracking
    drift_from_start: float = 0.0

    # Human interventions
    human_interventions: int = 0

    # Changelog
    changelog: List[ChangelogEntry] = field(default_factory=list)

    # State
    state: IslandState = IslandState.DRAFT

    # Metadata
    created_at: str = ""
    completed_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = _utc_iso()
        if not self.window_start:
            self.window_start = self.created_at

    @classmethod
    def create(cls, context: str, island_id: Optional[str] = None) -> "TimeIsland":
        """Factory method to create a new Time-Island"""
        if not island_id:
            timestamp = _utc_id_stamp()
            island_id = f"TI-{timestamp}"

        return cls(
            id=island_id,
            bounded_context=context,
            window_start=_utc_iso(),
        )

    def activate(self) -> None:
        """Activate the island"""
        if self.state != IslandState.DRAFT:
            raise ValueError(f"Cannot activate island in {self.state} state. Must be DRAFT.")
        if self.state == IslandState.DRAFT:
            self.state = IslandState.ACTIVE
            self.add_changelog("activated", "Island activated for processing")

    def complete(self) -> None:
        """Mark island as completed"""
        if self.state != IslandState.ACTIVE:
            raise ValueError(f"Cannot complete island in {self.state} state. Must be ACTIVE.")
        if self.state == IslandState.ACTIVE:
            self.state = IslandState.COMPLETED
            self.window_end = _utc_iso()
            self.completed_at = self.window_end
            self.add_changelog("completed", "Island processing completed")

    def archive(self) -> None:
        """Archive the island"""
        if self.state not in {IslandState.COMPLETED, IslandState.ACTIVE}:
            raise ValueError(
                f"Cannot archive island in {self.state} state. Must be COMPLETED or ACTIVE."
            )
        if self.state == IslandState.COMPLETED:
            self.state = IslandState.ARCHIVED
            self.add_changelog("archived", "Island archived for long-term storage")

    def add_input(self, kind: str, ref: str) -> None:
        """Add an input source"""
        self.inputs.append(SourceTrace(kind=kind, ref=ref))

    def add_output(self, output_ref: str) -> None:
        """Add an output reference"""
        self.outputs.append(output_ref)

    def add_changelog(self, action: str, reason: str, actor: str = "system") -> None:
        """Add a changelog entry"""
        self.changelog.append(
            ChangelogEntry(
                action=action,
                reason=reason,
                actor=actor,
            )
        )

    def record_intervention(self, reason: str) -> None:
        """Record a human intervention"""
        self.human_interventions += 1
        self.add_changelog("human_intervention", reason, actor="human")

    def update_resonance(self, value_fit: float, consensus: float, risk: float) -> None:
        """Update resonance signal"""
        self.resonance_signal = {
            "value_fit": value_fit,
            "consensus": consensus,
            "risk": risk,
        }

    def update_drift(self, drift: float) -> None:
        """Update drift measurement"""
        self.drift_from_start = drift

    def hash(self) -> str:
        """Generate a hash for this island state"""
        content = json.dumps(self.to_dict(), sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "bounded_context": self.bounded_context,
            "window": {
                "start": self.window_start,
                "end": self.window_end,
            },
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": self.outputs,
            "poav_weights": self.poav_weights,
            "resonance_signal": self.resonance_signal,
            "drift_from_start": self.drift_from_start,
            "human_interventions": self.human_interventions,
            "changelog": [c.to_dict() for c in self.changelog],
            "state": self.state.value,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }

    def to_yaml(self) -> str:
        """Serialize to YAML format (for documentation)"""
        import yaml

        return yaml.dump(
            {"island": self.to_dict()},
            default_flow_style=False,
            allow_unicode=True,
        )

    @classmethod
    def from_dict(cls, data: Dict) -> "TimeIsland":
        """Deserialize from dictionary"""
        island = cls(
            id=data["id"],
            bounded_context=data["bounded_context"],
            window_start=data["window"]["start"],
            window_end=data["window"].get("end", ""),
            poav_weights=data.get("poav_weights", {}),
            resonance_signal=data.get("resonance_signal", {}),
            drift_from_start=data.get("drift_from_start", 0.0),
            human_interventions=data.get("human_interventions", 0),
            state=IslandState(data.get("state", "draft")),
            created_at=data.get("created_at", ""),
            completed_at=data.get("completed_at", ""),
        )

        # Restore inputs
        for inp in data.get("inputs", []):
            island.inputs.append(SourceTrace.from_dict(inp))

        # Restore outputs
        island.outputs = data.get("outputs", [])

        # Restore changelog
        for entry in data.get("changelog", []):
            island.changelog.append(ChangelogEntry(**entry))

        return island


class TimeIslandManager:
    """
    Manages Time-Islands for a session.

    管理會話中的時間島。
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.islands: Dict[str, TimeIsland] = {}
        self.current_island: Optional[TimeIsland] = None
        self.storage_path = storage_path

    def create_island(self, context: str) -> TimeIsland:
        """Create and activate a new island"""
        island = TimeIsland.create(context)
        island.activate()
        self.islands[island.id] = island
        self.current_island = island
        return island

    def get_island(self, island_id: str) -> Optional[TimeIsland]:
        """Get an island by ID"""
        return self.islands.get(island_id)

    def complete_current(self) -> Optional[TimeIsland]:
        """Complete the current island"""
        if self.current_island:
            self.current_island.complete()
            completed = self.current_island
            self.current_island = None
            return completed
        return None

    def list_islands(self, state: Optional[IslandState] = None) -> List[TimeIsland]:
        """List all islands, optionally filtered by state"""
        if state:
            return [i for i in self.islands.values() if i.state == state]
        return list(self.islands.values())

    def save(self, path: Optional[str] = None) -> None:
        """Save all islands to disk"""
        save_path = path or self.storage_path
        if not save_path:
            raise ValueError("No storage path specified")

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        data = {
            "islands": {id: island.to_dict() for id, island in self.islands.items()},
            "current_island_id": self.current_island.id if self.current_island else None,
        }
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, path: Optional[str] = None) -> None:
        """Load islands from disk"""
        load_path = path or self.storage_path
        if not load_path or not os.path.exists(load_path):
            return

        with open(load_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.islands = {
            id: TimeIsland.from_dict(island_data)
            for id, island_data in data.get("islands", {}).items()
        }

        current_id = data.get("current_island_id")
        self.current_island = self.islands.get(current_id) if current_id else None


# === Convenience Functions ===


def create_island(context: str) -> TimeIsland:
    """Quick way to create a standalone island"""
    return TimeIsland.create(context)


def wrap_in_island(context: str, func: callable, *args, **kwargs) -> tuple:
    """
    Execute a function within a Time-Island context.

    Returns: (result, island)
    """
    island = TimeIsland.create(context)
    island.activate()

    try:
        result = func(*args, **kwargs)
        island.add_output(f"function_result:{type(result).__name__}")
        island.complete()
        return result, island
    except Exception as e:
        island.add_changelog("error", str(e))
        island.complete()
        raise


# === Test ===

if __name__ == "__main__":
    print("=" * 60)
    print("   Time-Island Protocol Test")
    print("=" * 60)

    # Create manager
    manager = TimeIslandManager()

    # Create island
    island = manager.create_island("documentation_task")
    print(f"\n✅ Created island: {island.id}")

    # Add inputs
    island.add_input("file", "docs/philosophy/manifesto.md")
    island.add_input("user_input", "expand documentation")
    print(f"   Added {len(island.inputs)} inputs")

    # Simulate processing
    island.update_drift(0.15)
    island.update_resonance(value_fit=0.85, consensus=0.78, risk=0.12)
    island.add_output("docs/core_concepts.md")
    print(f"   Updated metrics: drift={island.drift_from_start}")

    # Complete
    manager.complete_current()
    print(f"   State: {island.state.value}")
    print(f"   Hash: {island.hash()}")

    # Print YAML
    print("\n--- YAML Output ---")
    print(island.to_yaml())

    print("\n" + "=" * 60)
    print("   Test Complete")
    print("=" * 60)
