"""
Visual Memory Chain — Image-based memory retrieval for AI.

Instead of reading thousands of text tokens, AI can glance at a visual
snapshot to instantly grasp the state of a conversation or system.

Design principles:
  1. Each "frame" is a Mermaid diagram (text-based, renderable, structured)
  2. Each frame has a JSON sidecar for exact values
  3. Frames form a chain with branches, tags, and types
  4. The chain is an ADDITIONAL retrieval source — never replaces text memory

Inspired by:
  - mem0 (intelligent filtering)
  - Zep/Graphiti (temporal knowledge graphs)
  - Human visual memory (scene gist = 100ms comprehension)

Usage:
    chain = VisualChain()
    frame = chain.capture(
        frame_type=FrameType.SESSION_STATE,
        title="Turn 42 — high tension",
        data={"tension": 0.87, "verdict": "declare_stance", ...},
        tags=["tension", "ethics"],
        branch="main",
    )
    # Later: AI reads the chain
    recent = chain.get_recent(n=5)
    by_tag = chain.query(tags=["tension"])
    timeline = chain.get_branch("main")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

# ---------------------------------------------------------------------------
# Frame Types
# ---------------------------------------------------------------------------


class FrameType(Enum):
    """Types of visual memory frames."""

    SESSION_STATE = "session_state"  # Overall session snapshot
    TENSION_MAP = "tension_map"  # Tension distribution across topics
    COMMITMENT_TREE = "commitment_tree"  # Active commitments + status
    VALUE_LANDSCAPE = "value_landscape"  # Emergent values heatmap
    COUNCIL_VERDICT = "council_verdict"  # Council deliberation outcome
    RUPTURE_TIMELINE = "rupture_timeline"  # Commitment ruptures over time
    CONVERSATION_ARC = "conversation_arc"  # Emotional/tonal arc of a session
    CUSTOM = "custom"


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass
class VisualFrame:
    """One frame in the visual memory chain.

    Contains both a Mermaid diagram (for AI visual comprehension)
    and a JSON sidecar (for precise value retrieval).
    """

    frame_id: str
    frame_type: FrameType
    title: str
    mermaid: str  # The visual representation
    data: Dict[str, Any]  # Exact values (JSON sidecar)
    created_at: str
    tags: List[str] = field(default_factory=list)
    branch: str = "main"
    parent_id: Optional[str] = None  # For branching
    turn_index: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "frame_type": self.frame_type.value,
            "title": self.title,
            "mermaid": self.mermaid,
            "data": self.data,
            "created_at": self.created_at,
            "tags": self.tags,
            "branch": self.branch,
            "parent_id": self.parent_id,
            "turn_index": self.turn_index,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> VisualFrame:
        ft = raw.get("frame_type", "custom")
        try:
            frame_type = FrameType(ft)
        except ValueError:
            frame_type = FrameType.CUSTOM
        return cls(
            frame_id=str(raw.get("frame_id", "")),
            frame_type=frame_type,
            title=str(raw.get("title", "")),
            mermaid=str(raw.get("mermaid", "")),
            data=dict(raw.get("data", {})),
            created_at=str(raw.get("created_at", "")),
            tags=list(raw.get("tags", [])),
            branch=str(raw.get("branch", "main")),
            parent_id=raw.get("parent_id"),
            turn_index=int(raw.get("turn_index", 0)),
            metadata=dict(raw.get("metadata", {})),
        )


# ---------------------------------------------------------------------------
# Mermaid Renderers — one per FrameType
# ---------------------------------------------------------------------------


def _render_session_state(data: Dict[str, Any]) -> str:
    """Render a session state as a Mermaid flowchart."""
    tension = data.get("tension", 0.0)
    verdict = data.get("verdict", "approve")
    mode = data.get("council_mode", "hybrid")
    topics = data.get("topics", [])
    commitments_active = data.get("commitments_active", 0)
    ruptures = data.get("ruptures", 0)
    values_count = data.get("values_count", 0)

    # Tension level indicator
    if tension > 0.7:
        t_color = ":::danger"
        t_label = f"HIGH {tension:.2f}"
    elif tension > 0.4:
        t_color = ":::warning"
        t_label = f"MED {tension:.2f}"
    else:
        t_color = ":::success"
        t_label = f"LOW {tension:.2f}"

    topic_nodes = ""
    for i, topic in enumerate(topics[:5]):
        safe_topic = str(topic).replace('"', "'")
        topic_nodes += f'    T{i}["{safe_topic}"]\n'
        topic_nodes += f"    SESSION --> T{i}\n"

    return f"""graph TD
    TENSION["{t_label}"]{t_color}
    VERDICT["{verdict}"]
    MODE["{mode}"]
    COMMITS["Commits: {commitments_active}"]
    RUPTURES["Ruptures: {ruptures}"]
    VALUES["Values: {values_count}"]

    SESSION["Session State"] --> TENSION
    SESSION --> VERDICT
    SESSION --> MODE
    SESSION --> COMMITS
    SESSION --> RUPTURES
    SESSION --> VALUES
{topic_nodes}
    classDef danger fill:#ff4444,color:#fff
    classDef warning fill:#ffaa00,color:#000
    classDef success fill:#44bb44,color:#fff
"""


def _render_tension_map(data: Dict[str, Any]) -> str:
    """Render tension distribution across topics."""
    tensions = data.get("tensions", {})
    if not tensions:
        return "graph TD\n    EMPTY[No tension data]"

    lines = ["graph LR"]
    for i, (topic, level) in enumerate(tensions.items()):
        safe_topic = str(topic).replace('"', "'")
        level_f = float(level) if level else 0.0
        if level_f > 0.7:
            style = ":::danger"
        elif level_f > 0.4:
            style = ":::warning"
        else:
            style = ":::success"
        lines.append(f'    N{i}["{safe_topic}: {level_f:.2f}"]{style}')

    lines.append("    classDef danger fill:#ff4444,color:#fff")
    lines.append("    classDef warning fill:#ffaa00,color:#000")
    lines.append("    classDef success fill:#44bb44,color:#fff")
    return "\n".join(lines)


def _render_commitment_tree(data: Dict[str, Any]) -> str:
    """Render active commitments as a tree."""
    commits = data.get("commitments", [])
    if not commits:
        return "graph TD\n    EMPTY[No active commitments]"

    lines = ["graph TD", '    ROOT["Commitments"]']
    for i, commit in enumerate(commits[:10]):
        text = str(commit.get("text", f"Commit {i}"))[:50].replace('"', "'")
        status = commit.get("status", "active")
        if status == "broken":
            style = ":::danger"
        elif status == "fulfilled":
            style = ":::success"
        else:
            style = ""
        lines.append(f'    C{i}["{text}"]{style}')
        lines.append(f"    ROOT --> C{i}")

    lines.append("    classDef danger fill:#ff4444,color:#fff")
    lines.append("    classDef success fill:#44bb44,color:#fff")
    return "\n".join(lines)


def _render_value_landscape(data: Dict[str, Any]) -> str:
    """Render emergent values as a landscape."""
    values = data.get("values", [])
    if not values:
        return "graph TD\n    EMPTY[No emergent values]"

    lines = ["graph TD", '    SOUL["Value Landscape"]']
    for i, val in enumerate(values[:8]):
        name = str(val.get("name", f"Value {i}"))[:40].replace('"', "'")
        strength = float(val.get("strength", 0.5))
        lines.append(f'    V{i}["{name} ({strength:.1f})"]')
        lines.append(f"    SOUL --> V{i}")

    return "\n".join(lines)


def _render_council_verdict(data: Dict[str, Any]) -> str:
    """Render a council deliberation outcome."""
    verdict = data.get("verdict", "approve")
    perspectives = data.get("perspectives", {})

    lines = ["graph TD", f'    VERDICT["{verdict}"]']

    for i, (name, opinion) in enumerate(perspectives.items()):
        safe_name = str(name).replace('"', "'")
        safe_opinion = str(opinion)[:40].replace('"', "'")
        lines.append(f'    P{i}["{safe_name}: {safe_opinion}"]')
        lines.append(f"    P{i} --> VERDICT")

    return "\n".join(lines)


def _render_rupture_timeline(data: Dict[str, Any]) -> str:
    """Render rupture events on a timeline."""
    events = data.get("ruptures", [])
    if not events:
        return "graph LR\n    NONE[No ruptures detected]"

    lines = ["graph LR"]
    prev = None
    for i, event in enumerate(events[:10]):
        turn = event.get("turn", i)
        desc = str(event.get("description", "rupture"))[:30].replace('"', "'")
        lines.append(f'    R{i}["T{turn}: {desc}"]:::danger')
        if prev is not None:
            lines.append(f"    R{prev} --> R{i}")
        prev = i

    lines.append("    classDef danger fill:#ff4444,color:#fff")
    return "\n".join(lines)


def _render_conversation_arc(data: Dict[str, Any]) -> str:
    """Render the emotional arc of a conversation."""
    points = data.get("arc_points", [])
    if not points:
        return "graph LR\n    EMPTY[No arc data]"

    lines = ["graph LR"]
    prev = None
    for i, point in enumerate(points[:12]):
        turn = point.get("turn", i)
        tone = str(point.get("tone", "neutral"))[:20].replace('"', "'")
        tension = float(point.get("tension", 0.0))
        if tension > 0.7:
            style = ":::danger"
        elif tension > 0.4:
            style = ":::warning"
        else:
            style = ":::success"
        lines.append(f'    A{i}["T{turn}: {tone} ({tension:.1f})"]{style}')
        if prev is not None:
            lines.append(f"    A{prev} --> A{i}")
        prev = i

    lines.append("    classDef danger fill:#ff4444,color:#fff")
    lines.append("    classDef warning fill:#ffaa00,color:#000")
    lines.append("    classDef success fill:#44bb44,color:#fff")
    return "\n".join(lines)


_RENDERERS = {
    FrameType.SESSION_STATE: _render_session_state,
    FrameType.TENSION_MAP: _render_tension_map,
    FrameType.COMMITMENT_TREE: _render_commitment_tree,
    FrameType.VALUE_LANDSCAPE: _render_value_landscape,
    FrameType.COUNCIL_VERDICT: _render_council_verdict,
    FrameType.RUPTURE_TIMELINE: _render_rupture_timeline,
    FrameType.CONVERSATION_ARC: _render_conversation_arc,
}


def render_frame(frame_type: FrameType, data: Dict[str, Any]) -> str:
    """Render data into a Mermaid diagram for the given frame type."""
    renderer = _RENDERERS.get(frame_type)
    if renderer is None:
        # Custom type — just dump data as a simple graph
        summary = json.dumps(data, ensure_ascii=False, default=str)[:200]
        safe = summary.replace('"', "'")
        return f'graph TD\n    CUSTOM["{safe}"]'
    return renderer(data)


# ---------------------------------------------------------------------------
# Visual Chain — the chain itself
# ---------------------------------------------------------------------------


class VisualChain:
    """A chain of visual memory frames with branching and tagging.

    This is an ADDITIONAL retrieval source — it never replaces text memory.
    AI can glance at recent frames to instantly grasp context, then drill
    down into text memory for details.
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self._frames: List[VisualFrame] = []
        self._branches: Dict[str, List[str]] = {"main": []}
        self._tag_index: Dict[str, List[str]] = {}
        self._turn_counter: int = 0
        self._storage_path = storage_path
        if storage_path:
            self._load_from_disk()

    # --- Capture ---

    def capture(
        self,
        frame_type: FrameType,
        title: str,
        data: Dict[str, Any],
        tags: Optional[List[str]] = None,
        branch: str = "main",
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VisualFrame:
        """Capture a new visual frame and add it to the chain."""
        now = datetime.now(timezone.utc).isoformat()
        frame_id = f"vf_{self._turn_counter:04d}_{now[:19].replace(':', '')}"

        mermaid = render_frame(frame_type, data)

        frame = VisualFrame(
            frame_id=frame_id,
            frame_type=frame_type,
            title=title,
            mermaid=mermaid,
            data=data,
            created_at=now,
            tags=tags or [],
            branch=branch,
            parent_id=parent_id,
            turn_index=self._turn_counter,
            metadata=metadata or {},
        )

        self._frames.append(frame)

        # Update branch index
        if branch not in self._branches:
            self._branches[branch] = []
        self._branches[branch].append(frame_id)

        # Update tag index
        for tag in frame.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = []
            self._tag_index[tag].append(frame_id)

        self._turn_counter += 1

        if self._storage_path:
            self._save_to_disk()

        return frame

    # --- Retrieval ---

    def get_recent(self, n: int = 5) -> List[VisualFrame]:
        """Get the N most recent frames."""
        return list(self._frames[-n:])

    def get_by_id(self, frame_id: str) -> Optional[VisualFrame]:
        """Get a specific frame by ID."""
        for frame in self._frames:
            if frame.frame_id == frame_id:
                return frame
        return None

    def query(
        self,
        tags: Optional[List[str]] = None,
        frame_type: Optional[FrameType] = None,
        branch: Optional[str] = None,
        limit: int = 10,
    ) -> List[VisualFrame]:
        """Query frames by tags, type, and/or branch."""
        results = list(self._frames)

        if tags:
            tag_set = set(tags)
            results = [f for f in results if tag_set & set(f.tags)]

        if frame_type is not None:
            results = [f for f in results if f.frame_type == frame_type]

        if branch is not None:
            results = [f for f in results if f.branch == branch]

        return results[-limit:]

    def get_branch(self, branch: str) -> List[VisualFrame]:
        """Get all frames in a branch, in order."""
        frame_ids = self._branches.get(branch, [])
        id_set = set(frame_ids)
        return [f for f in self._frames if f.frame_id in id_set]

    def list_branches(self) -> List[str]:
        """List all branches."""
        return list(self._branches.keys())

    def list_tags(self) -> Dict[str, int]:
        """List all tags with counts."""
        return {tag: len(ids) for tag, ids in self._tag_index.items()}

    def get_chain_summary(self) -> Dict[str, Any]:
        """Get a summary of the entire chain — AI reads this first."""
        type_counts: Dict[str, int] = {}
        for frame in self._frames:
            key = frame.frame_type.value
            type_counts[key] = type_counts.get(key, 0) + 1

        return {
            "total_frames": len(self._frames),
            "branches": list(self._branches.keys()),
            "tags": self.list_tags(),
            "type_counts": type_counts,
            "latest_turn": self._turn_counter,
            "latest_frame": self._frames[-1].to_dict() if self._frames else None,
        }

    # --- Rendering for AI consumption ---

    def render_recent_as_markdown(self, n: int = 5) -> str:
        """Render recent frames as markdown — AI reads this."""
        frames = self.get_recent(n)
        if not frames:
            return "## Visual Memory Chain\n\nNo frames captured yet."

        sections = ["## Visual Memory Chain — Recent Frames\n"]
        for frame in frames:
            sections.append(f"### [{frame.frame_type.value}] {frame.title}")
            sections.append(f"Turn: {frame.turn_index} | Branch: {frame.branch}")
            if frame.tags:
                sections.append(f"Tags: {', '.join(frame.tags)}")
            sections.append(f"\n```mermaid\n{frame.mermaid}\n```\n")

        return "\n".join(sections)

    # --- Persistence ---

    def _save_to_disk(self) -> None:
        """Save chain to JSON on disk."""
        if not self._storage_path:
            return
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                "frames": [f.to_dict() for f in self._frames],
                "branches": self._branches,
                "turn_counter": self._turn_counter,
            }
            self._storage_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    def _load_from_disk(self) -> None:
        """Load chain from JSON on disk."""
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            raw = json.loads(self._storage_path.read_text(encoding="utf-8"))
            frames_raw = raw.get("frames", [])
            self._frames = [VisualFrame.from_dict(f) for f in frames_raw if isinstance(f, dict)]
            self._branches = raw.get("branches", {"main": []})
            self._turn_counter = int(raw.get("turn_counter", len(self._frames)))

            # Rebuild tag index
            self._tag_index = {}
            for frame in self._frames:
                for tag in frame.tags:
                    if tag not in self._tag_index:
                        self._tag_index[tag] = []
                    self._tag_index[tag].append(frame.frame_id)
        except Exception:
            pass

    # --- Chain operations ---

    def fork_branch(self, new_branch: str, from_frame_id: str) -> bool:
        """Create a new branch starting from a specific frame."""
        source = self.get_by_id(from_frame_id)
        if source is None:
            return False
        if new_branch not in self._branches:
            self._branches[new_branch] = []
        return True

    def merge_context(self, branches: Sequence[str]) -> str:
        """Merge multiple branches into a single readable context for AI."""
        sections = [f"## Merged Visual Context ({len(branches)} branches)\n"]
        for branch in branches:
            frames = self.get_branch(branch)
            if not frames:
                continue
            sections.append(f"### Branch: {branch} ({len(frames)} frames)")
            latest = frames[-1]
            sections.append(f"Latest: [{latest.frame_type.value}] {latest.title}")
            sections.append(f"```mermaid\n{latest.mermaid}\n```\n")

        return "\n".join(sections)

    @property
    def frame_count(self) -> int:
        return len(self._frames)
