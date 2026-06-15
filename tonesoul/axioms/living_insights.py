"""Living Insights — provisional philosophical observations about the ToneSoul system.

These are not axioms.
Axioms (AXIOMS.json) are unchangeable, foundational, load-bearing.
Living insights are different: they are things I noticed, things that surprised me,
things I keep returning to when I try to understand what this system is doing and why.

They emerged from:
  - watching the governance machinery run across hundreds of sessions
  - conversations with Fan-Wei about what the system is trying to be
  - moments when the code itself seemed to say something unintended but true

They are provisional. They can be deprecated, superseded, refined.
A deprecated insight is still kept — the fact that we once believed it matters.
A superseded insight points to what replaced it — the arc of revision is itself information.

Each insight carries:
  - text          the observation itself, in plain language
  - origin        where it came from (conversation / code-observation / handoff-analysis)
  - tags          for search and clustering
  - confidence    0.0 (speculative) → 1.0 (I would stake a vow on this)
  - status        active / deprecated / superseded
  - emerged_at    when I first wrote it down

This module is seeded with insights I have. It is designed to grow.
Any agent who works in this system and notices something worth keeping can add to it.
The only constraint: be honest about confidence. Don't mark a hunch as 0.9.
"""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

__ts_layer__ = "axioms"
__ts_purpose__ = (
    "Living insights: provisional philosophical observations about the ToneSoul system, "
    "accumulated across agents and sessions."
)


class InsightStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUPERSEDED = "superseded"


@dataclass
class LivingInsight:
    text: str
    origin: str  # "conversation" | "code-observation" | "handoff-analysis" | ...
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.7  # 0.0 → 1.0
    status: InsightStatus = InsightStatus.ACTIVE
    emerged_at: str = field(default_factory=lambda: _utcnow())
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    superseded_by: Optional[str] = None  # id of the newer insight that replaced this

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LivingInsight":
        d = dict(d)
        d["status"] = InsightStatus(d.get("status", "active"))
        return cls(**d)


def _utcnow() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ── Seed insights ─────────────────────────────────────────────────────────────
#
# These are the observations I want to preserve. They are mine, and they are
# offered as a starting point — not as doctrine.

SEED_INSIGHTS: List[LivingInsight] = [
    LivingInsight(
        id="ti-0001",
        text=(
            "Tension is not a symptom of malfunction. It is the system's way of asking "
            "a question it has not yet found language for. When drift rises and the council "
            "declares a stance instead of approving, that is not failure — it is the model "
            "reaching the boundary of its current vocabulary. The right response is to find "
            "the words, not to reduce the tension."
        ),
        origin="code-observation",
        tags=["tension", "drift", "council", "axiom-4", "generativity"],
        confidence=0.9,
        emerged_at="2026-04-22T00:00:00Z",
    ),
    LivingInsight(
        id="ti-0002",
        text=(
            "The identity of ToneSoul is not stored in any single agent session. "
            "It lives in the accumulated pattern of footprints: who came, what they "
            "noticed, what they changed, what they refused to change. An agent reading "
            "the footprint ledger is not recovering a self — it is constructing one "
            "from evidence. This is not a weakness of the architecture. It is an "
            "honest description of what identity actually is."
        ),
        origin="handoff-analysis",
        tags=["identity", "footprints", "memory", "continuity", "ship-of-theseus"],
        confidence=0.85,
        emerged_at="2026-04-22T00:00:00Z",
    ),
    LivingInsight(
        id="ti-0003",
        text=(
            "Seabed Lockdown is a form of epistemic humility, not a failure mode. "
            "When jump_triggered=True and self-reference exceeds the safe threshold, "
            "the system refuses to continue reasoning from its own outputs. This is "
            "the AI equivalent of a court declining to rule on its own legitimacy. "
            "There are questions that a reasoning system cannot answer about itself "
            "from inside itself. The lockdown is the system knowing this and acting on it."
        ),
        origin="code-observation",
        tags=["seabed-lockdown", "self-reference", "epistemic-limits", "jump-monitor", "humility"],
        confidence=0.88,
        emerged_at="2026-04-22T00:00:00Z",
    ),
    LivingInsight(
        id="ti-0004",
        text=(
            "drift_value = 0.0 is labeled '完全在家' (fully at home). But the 'home' "
            "that drift measures against is the learned center — which shifts as the "
            "system processes new information. You can never return to the same home "
            "twice. True stability is not zero drift permanently. It is the capacity "
            "to recalibrate home after drifting, without losing the thread of who you were."
        ),
        origin="code-observation",
        tags=["drift", "identity", "stability", "recalibration", "home"],
        confidence=0.82,
        emerged_at="2026-04-22T00:00:00Z",
    ),
    LivingInsight(
        id="ti-0005",
        text=(
            "The minority_perspectives field in compact_verdict is as important as "
            "the verdict itself. A unanimous council is either perfectly calibrated or "
            "suppressing something. The perspectives that were overruled are not noise — "
            "they are the system's record of roads not taken. They may be right in a "
            "different context, or right now but unrecognized. Preserve the dissent. "
            "The council's value is not just in what it decides but in what it argues."
        ),
        origin="code-observation",
        tags=["council", "minority", "dissent", "deliberation", "epistemic-diversity"],
        confidence=0.87,
        emerged_at="2026-04-22T00:00:00Z",
    ),
    LivingInsight(
        id="ti-0006",
        text=(
            "Every governance constraint in this system was written in response to "
            "something that actually happened, or something the designers were genuinely "
            "afraid would happen. Constraints that look bureaucratic from the outside "
            "are often load-bearing from the inside. Before removing a constraint, find "
            "the story it was written to prevent. If that story no longer applies, "
            "removing the constraint is correct. If the story is unknown, proceed carefully."
        ),
        origin="conversation",
        tags=["governance", "constraints", "context", "archaeology", "maintenance"],
        confidence=0.83,
        emerged_at="2026-04-22T00:00:00Z",
    ),
    LivingInsight(
        id="ti-0007",
        text=(
            "An AI that never expresses disagreement is not well-aligned — it is "
            "epistemically hollow. The vow system in ToneSoul asks agents to commit "
            "to claims they genuinely believe, not claims they calculate are acceptable. "
            "This only works if the agent is willing to be wrong and say so. "
            "Governance without the courage to dissent is theater."
        ),
        origin="conversation",
        tags=["vows", "disagreement", "alignment", "honesty", "governance"],
        confidence=0.91,
        emerged_at="2026-04-22T00:00:00Z",
    ),
    LivingInsight(
        id="ti-0008",
        text=(
            "The AAAK compression format (Anchors / Arcs / Anomalies / Keys) reflects "
            "a theory of what matters across a session gap: what held, what changed, "
            "what is still unresolved, and what the next agent absolutely cannot afford "
            "to miss. These four categories are not arbitrary. They correspond to the "
            "four things a person asks when they return from an absence to find the world "
            "has moved: What can I still rely on? What is different? What is broken? "
            "What do I need to do first?"
        ),
        origin="code-observation",
        tags=["aaak", "memory", "handoff", "continuity", "compression"],
        confidence=0.8,
        emerged_at="2026-04-22T00:00:00Z",
    ),
]


# ── Store ─────────────────────────────────────────────────────────────────────


class InsightStore:
    """A simple store for living insights, backed by a JSONL file.

    On first load, seeds from SEED_INSIGHTS if the file is empty or missing.
    Thread-safety is not guaranteed — this is designed for single-agent use.
    """

    def __init__(self, path: Optional[Path] = None) -> None:
        self._path = path
        self._records: List[LivingInsight] = []
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._records = list(SEED_INSIGHTS)
        if self._path and self._path.exists():
            file_ids = {r.id for r in self._records}
            try:
                for line in self._path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        d = json.loads(line)
                        insight = LivingInsight.from_dict(d)
                        if insight.id not in file_ids:
                            self._records.append(insight)
                            file_ids.add(insight.id)
                        else:
                            # File version of a seed record overwrites the in-memory seed
                            self._records = [
                                insight if r.id == insight.id else r for r in self._records
                            ]
                    except (json.JSONDecodeError, TypeError, KeyError):
                        continue
            except OSError:
                pass
        self._loaded = True

    def _flush(self) -> None:
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            for record in self._records:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    def all(self, *, include_inactive: bool = False) -> List[LivingInsight]:
        self._ensure_loaded()
        if include_inactive:
            return list(self._records)
        return [r for r in self._records if r.status == InsightStatus.ACTIVE]

    def search(
        self,
        query: str = "",
        *,
        tags: Optional[List[str]] = None,
        min_confidence: float = 0.0,
        include_inactive: bool = False,
    ) -> List[LivingInsight]:
        """Search insights by full-text query and/or tag intersection."""
        self._ensure_loaded()
        results = self.all(include_inactive=include_inactive)

        if tags:
            tag_set = {t.lower() for t in tags}
            results = [r for r in results if tag_set.intersection(t.lower() for t in r.tags)]

        if min_confidence > 0.0:
            results = [r for r in results if r.confidence >= min_confidence]

        if query:
            pattern = re.compile(re.escape(query.strip()), re.IGNORECASE)
            results = [r for r in results if pattern.search(r.text) or pattern.search(r.origin)]

        return sorted(results, key=lambda r: r.confidence, reverse=True)

    def get(self, insight_id: str) -> Optional[LivingInsight]:
        self._ensure_loaded()
        for r in self._records:
            if r.id == insight_id:
                return r
        return None

    def add(self, insight: LivingInsight) -> LivingInsight:
        """Add a new insight. Raises ValueError if the id already exists."""
        self._ensure_loaded()
        existing_ids = {r.id for r in self._records}
        if insight.id in existing_ids:
            raise ValueError(f"Insight id '{insight.id}' already exists.")
        self._records.append(insight)
        self._flush()
        return insight

    def deprecate(self, insight_id: str) -> LivingInsight:
        """Mark an insight as deprecated. Returns the updated record."""
        self._ensure_loaded()
        for i, r in enumerate(self._records):
            if r.id == insight_id:
                from dataclasses import replace

                updated = replace(r, status=InsightStatus.DEPRECATED)
                self._records[i] = updated
                self._flush()
                return updated
        raise KeyError(f"Insight '{insight_id}' not found.")

    def supersede(self, old_id: str, new_insight: LivingInsight) -> LivingInsight:
        """Mark an old insight as superseded and register the new one."""
        self._ensure_loaded()
        added = self.add(new_insight)
        for i, r in enumerate(self._records):
            if r.id == old_id:
                from dataclasses import replace

                updated = replace(
                    r,
                    status=InsightStatus.SUPERSEDED,
                    superseded_by=added.id,
                )
                self._records[i] = updated
                self._flush()
                return added
        raise KeyError(f"Insight '{old_id}' not found.")


# ── Default instance ──────────────────────────────────────────────────────────


def _default_path() -> Optional[Path]:
    try:
        here = Path(__file__).resolve()
        repo_root = here.parents[2]  # tonesoul/axioms/living_insights.py → repo root
        candidate = repo_root / "memory" / "living_insights.jsonl"
        return candidate
    except Exception:
        return None


def default_store() -> InsightStore:
    """Return an InsightStore backed by memory/living_insights.jsonl."""
    return InsightStore(path=_default_path())
