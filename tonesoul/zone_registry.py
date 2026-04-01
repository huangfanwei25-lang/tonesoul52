"""Zone Registry — maps conversation topics to visual world zones.

Each zone represents a topic cluster that emerged from real sessions.
Zones grow organically: more sessions mentioning a topic → larger, more detailed zone.

Data flow:
  session_traces.jsonl → topics → zone_registry.json
  governance_state.json → soul_integral, drift → world mood/weather
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_DEFAULT_REGISTRY_PATH = Path("memory/autonomous/zone_registry.json")
_DEFAULT_TRACES_PATH = Path("memory/autonomous/session_traces.jsonl")

# Topic → zone name/icon mapping (extensible)
_ZONE_PRESETS: Dict[str, Dict[str, str]] = {
    "stock": {"name": "股市戰情中心", "icon": "chart", "color": "#ffd93d"},
    "governance": {"name": "治理議會廳", "icon": "shield", "color": "#7c5cfc"},
    "memory": {"name": "記憶圖書館", "icon": "book", "color": "#4ecdc4"},
    "architecture": {"name": "建築工坊", "icon": "gear", "color": "#6bcb77"},
    "testing": {"name": "試煉場", "icon": "flask", "color": "#ff6b6b"},
    "debug": {"name": "除錯迷宮", "icon": "bug", "color": "#ff9f43"},
    "infrastructure": {"name": "基礎設施塔", "icon": "tower", "color": "#a8a8c0"},
    "benevolence": {"name": "仁慈花園", "icon": "flower", "color": "#ff6b9d"},
    "diagnostic": {"name": "診斷工房", "icon": "scope", "color": "#54a0ff"},
    "gamification": {"name": "遊戲化實驗室", "icon": "game", "color": "#5f27cd"},
    "dashboard": {"name": "觀測站", "icon": "eye", "color": "#01a3a4"},
}


@dataclass
class Zone:
    """A single zone in the world map."""

    zone_id: str = ""
    name: str = ""
    icon: str = "star"
    color: str = "#7c5cfc"
    topics: List[str] = field(default_factory=list)
    visit_count: int = 0
    artifact_count: int = 0
    first_seen: str = ""
    last_seen: str = ""
    # Grid position (auto-assigned)
    grid_x: int = 0
    grid_y: int = 0
    # Level grows with visits: 1-5
    level: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Zone:
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class WorldState:
    """The full world: zones + global mood derived from governance state."""

    zones: List[Zone] = field(default_factory=list)
    total_sessions: int = 0
    world_mood: str = "calm"  # calm / alert / tense / serene
    weather: str = "clear"  # clear / cloudy / storm / aurora
    last_rebuilt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> WorldState:
        zones = [Zone.from_dict(z) for z in d.get("zones", [])]
        return cls(
            zones=zones,
            total_sessions=d.get("total_sessions", 0),
            world_mood=d.get("world_mood", "calm"),
            weather=d.get("weather", "clear"),
            last_rebuilt=d.get("last_rebuilt", ""),
        )


def _match_topic_to_zone(topic: str) -> Optional[str]:
    """Match a topic string to a known zone preset key."""
    topic_lower = topic.lower()
    for key in _ZONE_PRESETS:
        if key in topic_lower:
            return key
    # Fuzzy: check Chinese keywords
    cn_map = {
        "股": "stock",
        "投資": "stock",
        "市場": "stock",
        "治理": "governance",
        "議會": "governance",
        "council": "governance",
        "記憶": "memory",
        "memory": "memory",
        "架構": "architecture",
        "結構": "architecture",
        "測試": "testing",
        "test": "testing",
        "除錯": "debug",
        "bug": "debug",
        "修復": "debug",
        "基礎": "infrastructure",
        "仁慈": "benevolence",
        "診斷": "diagnostic",
        "遊戲": "gamification",
        "視覺": "gamification",
        "儀表": "dashboard",
        "觀測": "dashboard",
    }
    for keyword, zone_key in cn_map.items():
        if keyword in topic_lower:
            return zone_key
    return None


def _compute_mood(soul_integral: float, tension_count: int) -> str:
    """Derive world mood from governance posture."""
    if soul_integral > 0.8 and tension_count > 3:
        return "tense"
    if soul_integral > 0.5:
        return "alert"
    if tension_count == 0:
        return "serene"
    return "calm"


def _compute_weather(caution: float, innovation: float) -> str:
    """Derive weather from baseline drift values."""
    if caution > 0.7:
        return "storm"
    if innovation > 0.7:
        return "aurora"
    if caution > 0.55:
        return "cloudy"
    return "clear"


def _assign_grid_positions(zones: List[Zone]) -> None:
    """Arrange zones in a spiral pattern on a grid."""
    # Simple spiral: center out
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    x, y = 0, 0
    dx, dy = 0, 0
    step = 1
    step_count = 0
    dir_idx = 0
    turns = 0

    for i, zone in enumerate(sorted(zones, key=lambda z: -z.visit_count)):
        zone.grid_x = x
        zone.grid_y = y
        # Spiral movement
        dx, dy = directions[dir_idx]
        x += dx
        y += dy
        step_count += 1
        if step_count >= step:
            step_count = 0
            dir_idx = (dir_idx + 1) % 4
            turns += 1
            if turns % 2 == 0:
                step += 1


def rebuild_from_traces(
    traces_path: Optional[Path] = None,
    governance_path: Optional[Path] = None,
) -> WorldState:
    """Rebuild the entire world state from session traces + governance state."""
    t_path = traces_path or _DEFAULT_TRACES_PATH
    g_path = governance_path or Path("governance_state.json")

    # Collect all topics from traces
    topic_counter: Counter[str] = Counter()
    zone_first_seen: Dict[str, str] = {}
    zone_last_seen: Dict[str, str] = {}
    zone_artifacts: Counter[str] = Counter()
    total_sessions = 0

    if t_path.exists():
        for line in t_path.read_text(encoding="utf-8").strip().splitlines():
            if not line.strip():
                continue
            trace = json.loads(line)
            total_sessions += 1
            ts = trace.get("timestamp", "")

            # Count topics
            for topic in trace.get("topics", []):
                zone_key = _match_topic_to_zone(topic) or topic.lower().replace(" ", "_")
                topic_counter[zone_key] += 1
                if ts:  # Only update timestamps from traces that have one
                    if zone_key not in zone_first_seen:
                        zone_first_seen[zone_key] = ts
                    zone_last_seen[zone_key] = ts

            # Tension topics also generate zones
            for t in trace.get("tension_events", []):
                topic = t.get("topic", "")
                zone_key = _match_topic_to_zone(topic)
                if zone_key:
                    topic_counter[zone_key] += 1
                    if ts:
                        if zone_key not in zone_first_seen:
                            zone_first_seen[zone_key] = ts
                        zone_last_seen[zone_key] = ts

            # Key decisions count as artifacts
            for decision in trace.get("key_decisions", []):
                zone_key = _match_topic_to_zone(decision)
                if zone_key:
                    zone_artifacts[zone_key] += 1

    # Build zones
    zones: List[Zone] = []
    for zone_key, count in topic_counter.most_common():
        preset = _ZONE_PRESETS.get(zone_key, {})
        level = min(5, 1 + count // 3)
        zones.append(
            Zone(
                zone_id=zone_key,
                name=preset.get("name", zone_key.replace("_", " ").title()),
                icon=preset.get("icon", "star"),
                color=preset.get("color", "#7c5cfc"),
                topics=[zone_key],
                visit_count=count,
                artifact_count=zone_artifacts.get(zone_key, 0),
                first_seen=zone_first_seen.get(zone_key, ""),
                last_seen=zone_last_seen.get(zone_key, ""),
                level=level,
            )
        )

    _assign_grid_positions(zones)

    # Derive mood/weather from governance state
    mood = "calm"
    weather = "clear"
    if g_path.exists():
        gov = json.loads(g_path.read_text(encoding="utf-8"))
        soul_integral = float(gov.get("soul_integral", 0.0))
        tension_count = len(gov.get("tension_history", []))
        drift = gov.get("baseline_drift", {})
        mood = _compute_mood(soul_integral, tension_count)
        weather = _compute_weather(
            float(drift.get("caution_bias", 0.5)),
            float(drift.get("innovation_bias", 0.5)),
        )

    world = WorldState(
        zones=zones,
        total_sessions=total_sessions,
        world_mood=mood,
        weather=weather,
        last_rebuilt=datetime.now(timezone.utc).isoformat(),
    )
    return world


def save(
    world: WorldState,
    registry_path: Optional[Path] = None,
) -> None:
    """Save world state to zone_registry.json."""
    path = registry_path or _DEFAULT_REGISTRY_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(world.to_dict(), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def load(
    registry_path: Optional[Path] = None,
) -> WorldState:
    """Load world state from zone_registry.json."""
    path = registry_path or _DEFAULT_REGISTRY_PATH
    if not path.exists():
        return rebuild_from_traces()
    raw = json.loads(path.read_text(encoding="utf-8"))
    return WorldState.from_dict(raw)


def rebuild_and_save(
    traces_path: Optional[Path] = None,
    governance_path: Optional[Path] = None,
    registry_path: Optional[Path] = None,
    store=None,
) -> WorldState:
    """Convenience: rebuild from traces and save.

    If `store` is provided (Redis backend), reads traces from store
    and writes zones back to store instead of files.
    """
    if store is not None and store.is_redis:
        world = _rebuild_from_store(store)
        store.set_zones(world.to_dict())
        return world

    world = rebuild_from_traces(traces_path, governance_path)
    save(world, registry_path)
    return world


def _rebuild_from_store(store) -> WorldState:
    """Rebuild world state from Redis store."""
    from collections import Counter
    from datetime import datetime, timezone

    topic_counter: Counter = Counter()
    zone_first_seen: Dict[str, str] = {}
    zone_last_seen: Dict[str, str] = {}
    zone_artifacts: Counter = Counter()
    total_sessions = 0

    for trace in store.get_traces(n=10000):
        total_sessions += 1
        ts = trace.get("timestamp", "")
        for topic in trace.get("topics", []):
            zone_key = _match_topic_to_zone(topic) or topic.lower().replace(" ", "_")
            topic_counter[zone_key] += 1
            if ts:
                if zone_key not in zone_first_seen:
                    zone_first_seen[zone_key] = ts
                zone_last_seen[zone_key] = ts
        for t in trace.get("tension_events", []):
            zone_key = _match_topic_to_zone(t.get("topic", ""))
            if zone_key:
                topic_counter[zone_key] += 1
        for decision in trace.get("key_decisions", []):
            zone_key = _match_topic_to_zone(decision)
            if zone_key:
                zone_artifacts[zone_key] += 1

    zones: List[Zone] = []
    for zone_key, count in topic_counter.most_common():
        preset = _ZONE_PRESETS.get(zone_key, {})
        zones.append(
            Zone(
                zone_id=zone_key,
                name=preset.get("name", zone_key.replace("_", " ").title()),
                icon=preset.get("icon", "star"),
                color=preset.get("color", "#7c5cfc"),
                topics=[zone_key],
                visit_count=count,
                artifact_count=zone_artifacts.get(zone_key, 0),
                first_seen=zone_first_seen.get(zone_key, ""),
                last_seen=zone_last_seen.get(zone_key, ""),
                level=min(5, 1 + count // 3),
            )
        )

    _assign_grid_positions(zones)

    gov = store.get_state()
    soul_integral = float(gov.get("soul_integral", 0.0))
    tension_count = len(gov.get("tension_history", []))
    drift = gov.get("baseline_drift", {})

    return WorldState(
        zones=zones,
        total_sessions=total_sessions,
        world_mood=_compute_mood(soul_integral, tension_count),
        weather=_compute_weather(
            float(drift.get("caution_bias", 0.5)),
            float(drift.get("innovation_bias", 0.5)),
        ),
        last_rebuilt=datetime.now(timezone.utc).isoformat(),
    )
