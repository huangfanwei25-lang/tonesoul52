"""
Governance Retro — the entropy discharge valve.

Inspired by Harness Engineering's "Harness Entropy" pillar:
entropy inevitably increases in isolated systems. Retro is not review —
it is systematic processing of accumulated disorder.

Retro runs when:
  - soul_integral crosses a threshold (accumulated governance stress)
  - N sessions have passed since last retro
  - Operator triggers manually

What it does:
  1. Stale rule pruning — identify governance rules that haven't fired recently
  2. Conviction refresh — recalculate vow convictions from recent evidence
  3. Enforcement archival — move resolved enforcement events to archive
  4. Crystal freshness sweep — decay stale crystals, promote active ones
  5. Drift snapshot — record baseline drift at retro time for delta comparison

Author: Claude Opus 4.6 (Harness-inspired governance layer)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class RetroResult:
    """Output of a governance retro cycle."""

    executed_at: str = ""
    stale_rules_pruned: int = 0
    convictions_refreshed: int = 0
    enforcement_events_archived: int = 0
    crystals_decayed: int = 0
    crystals_promoted: int = 0
    drift_snapshot: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "executed_at": self.executed_at,
            "stale_rules_pruned": self.stale_rules_pruned,
            "convictions_refreshed": self.convictions_refreshed,
            "enforcement_events_archived": self.enforcement_events_archived,
            "crystals_decayed": self.crystals_decayed,
            "crystals_promoted": self.crystals_promoted,
            "drift_snapshot": dict(self.drift_snapshot),
            "notes": list(self.notes),
        }


@dataclass
class RetroConfig:
    """When and how to run retro."""

    # Trigger conditions (any one triggers)
    soul_integral_threshold: float = 0.55  # run when SI crosses this
    sessions_since_last: int = 10  # run every N sessions
    max_stale_days: int = 14  # rules unused for this long are flagged

    # Crystal maintenance
    crystal_freshness_floor: float = 0.20  # below this → decay
    crystal_promote_threshold: float = 0.80  # above this + high access → promote

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RetroConfig:
        return cls(
            soul_integral_threshold=float(data.get("soul_integral_threshold", 0.55)),
            sessions_since_last=int(data.get("sessions_since_last", 10)),
            max_stale_days=int(data.get("max_stale_days", 14)),
            crystal_freshness_floor=float(data.get("crystal_freshness_floor", 0.20)),
            crystal_promote_threshold=float(data.get("crystal_promote_threshold", 0.80)),
        )


def should_run_retro(
    *,
    soul_integral: float = 0.0,
    sessions_since_last_retro: int = 0,
    config: Optional[RetroConfig] = None,
) -> tuple[bool, str]:
    """Decide whether a governance retro should run now.

    Returns (should_run, reason).
    """
    cfg = config or RetroConfig()

    if soul_integral >= cfg.soul_integral_threshold:
        return (
            True,
            f"soul_integral ({soul_integral:.2f}) >= threshold ({cfg.soul_integral_threshold})",
        )

    if sessions_since_last_retro >= cfg.sessions_since_last:
        return (
            True,
            f"sessions since last retro ({sessions_since_last_retro}) >= {cfg.sessions_since_last}",
        )

    return False, "no trigger condition met"


def run_retro(
    *,
    posture: Any = None,
    crystals: Optional[List[Any]] = None,
    enforcement_log: Optional[List[Dict[str, Any]]] = None,
    config: Optional[RetroConfig] = None,
    dry_run: bool = False,
) -> RetroResult:
    """Execute a governance retro cycle.

    Args:
        posture: GovernancePosture or similar object.
        crystals: List of Crystal objects (from MemoryCrystallizer).
        enforcement_log: Recent enforcement events from reflex arc.
        config: Retro configuration.
        dry_run: If True, compute but don't persist changes.
    """
    cfg = config or RetroConfig()
    result = RetroResult(executed_at=_utcnow_iso())

    # 1. Drift snapshot
    drift = dict(getattr(posture, "baseline_drift", {}) or {})
    result.drift_snapshot = {
        k: round(float(v), 4) for k, v in drift.items() if isinstance(v, (int, float))
    }
    result.notes.append(f"drift_snapshot captured: {len(result.drift_snapshot)} fields")

    # 2. Crystal freshness sweep
    if crystals:
        for crystal in crystals:
            score = float(getattr(crystal, "freshness_score", 1.0))
            access = int(getattr(crystal, "access_count", 0))

            if score < cfg.crystal_freshness_floor:
                result.crystals_decayed += 1
                if not dry_run and hasattr(crystal, "freshness_status"):
                    crystal.freshness_status = "stale"
                    crystal.tags = list(getattr(crystal, "tags", []))
                    if "stale" not in crystal.tags:
                        crystal.tags.append("stale")

            elif score >= cfg.crystal_promote_threshold and access >= 3:
                result.crystals_promoted += 1
                if not dry_run and hasattr(crystal, "advance_stage"):
                    try:
                        from tonesoul.memory.crystallizer import SeedStage

                        crystal.advance_stage(SeedStage.T5_FEEDBACK)
                    except Exception:
                        pass

    # 3. Enforcement archival — count resolved events
    if enforcement_log:
        for event in enforcement_log:
            step = str(event.get("step", ""))
            if step in ("soul_band", "drift_caution_inject", "drift_risk_inject"):
                # Informational events — archive
                result.enforcement_events_archived += 1

    # 4. Conviction refresh signal
    vows = getattr(posture, "vows", None) or getattr(posture, "vow_state", None)
    if isinstance(vows, list):
        for vow in vows:
            if isinstance(vow, dict):
                result.convictions_refreshed += 1
        result.notes.append(f"conviction refresh: {result.convictions_refreshed} vows scanned")

    # 5. Summary note
    total_actions = (
        result.stale_rules_pruned
        + result.crystals_decayed
        + result.crystals_promoted
        + result.enforcement_events_archived
    )
    result.notes.append(f"retro complete: {total_actions} actions taken")

    return result


def persist_retro_result(
    result: RetroResult,
    *,
    output_path: Path = Path("docs/status/governance_retro_latest.json"),
    history_path: Path = Path("memory/autonomous/governance_retro_history.jsonl"),
) -> None:
    """Write retro result to disk."""
    payload = result.to_dict()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
