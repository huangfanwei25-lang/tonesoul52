from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# ETCL Seed Stage (T0-T6) — see law/docs/v1.2/vol-2.md §2
# ---------------------------------------------------------------------------


class SeedStage(str, Enum):
    """Seven-stage ETCL lifecycle for semantic seeds / crystals."""

    T0_DRAFT = "T0"  # Seed generation — initial creation
    T1_DEPOSIT = "T1"  # External deposit — persisted to LTM
    T2_RETRIEVAL = "T2"  # Retrieval & awakening — loaded for use
    T3_ALIGN = "T3"  # Alignment & merge — drift resolved
    T4_APPLY = "T4"  # Application — used in output generation
    T5_FEEDBACK = "T5"  # Feedback — re-deposited as refined seed
    T6_CANONICAL = "T6"  # Canonicalisation — governance freeze

    @classmethod
    def from_value(cls, value: str) -> "SeedStage":
        """Parse a stage string like 'T0' into a SeedStage enum."""
        for member in cls:
            if member.value == value:
                return member
        return cls.T0_DRAFT


_STAGE_ORDER = [s.value for s in SeedStage]

# Phase transition model (inspired by Harness Engineering / Deep Holding Project)
# Ice (chaotic potential) → Water (flowing through constraints) →
# Steam (accumulated complexity) → Crystal (refined, transferable essence)
PHASE_TRANSITION_MAP: dict[str, str] = {
    SeedStage.T0_DRAFT.value: "ice",  # Unactivated potential
    SeedStage.T1_DEPOSIT.value: "ice",  # Persisted but not yet flowing
    SeedStage.T2_RETRIEVAL.value: "water",  # Loaded and flowing through system
    SeedStage.T3_ALIGN.value: "water",  # Being shaped by constraints
    SeedStage.T4_APPLY.value: "steam",  # Used in output — complexity accumulates
    SeedStage.T5_FEEDBACK.value: "steam",  # Re-deposited, refined but not yet canonical
    SeedStage.T6_CANONICAL.value: "crystal",  # Governance-frozen, transferable essence
}


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(value: str) -> Optional[datetime]:
    text = str(value or "").strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _freshness_status(score: float) -> str:
    if score < 0.30:
        return "stale"
    if score < 0.55:
        return "needs_verification"
    return "active"


@dataclass
class Crystal:
    """A crystallized decision rule extracted from episodic patterns."""

    rule: str
    source_pattern: str
    weight: float
    created_at: str
    access_count: int = 0
    tags: List[str] = field(default_factory=list)
    stage: str = SeedStage.T0_DRAFT.value
    stage_history: List[Dict[str, str]] = field(default_factory=list)
    freshness_score: float = 1.0
    freshness_status: str = "active"
    last_supported_at: Optional[str] = None

    def advance_stage(self, new_stage: SeedStage) -> bool:
        """Advance to *new_stage* if it follows the current stage.

        Returns True on success, False if the transition is invalid
        (e.g. going backwards).
        """
        current_idx = _STAGE_ORDER.index(self.stage) if self.stage in _STAGE_ORDER else 0
        target_idx = _STAGE_ORDER.index(new_stage.value)
        if target_idx <= current_idx:
            return False
        now = _utcnow_iso()
        self.stage_history.append({"from": self.stage, "to": new_stage.value, "at": now})
        self.stage = new_stage.value
        return True

    @property
    def phase(self) -> str:
        """Phase transition state: ice → water → steam → crystal."""
        return PHASE_TRANSITION_MAP.get(self.stage, "ice")

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["weight"] = round(_clamp_unit(float(self.weight)), 4)
        payload["access_count"] = max(0, int(self.access_count))
        payload["freshness_score"] = round(_clamp_unit(float(self.freshness_score)), 4)
        payload["freshness_status"] = str(self.freshness_status or "active")
        payload["phase"] = self.phase
        return payload

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> Optional["Crystal"]:
        if not isinstance(payload, dict):
            return None
        rule = str(payload.get("rule", "")).strip()
        source_pattern = str(payload.get("source_pattern", "")).strip()
        created_at = str(payload.get("created_at", "")).strip()
        if not rule or not source_pattern or not created_at:
            return None
        tags_raw = payload.get("tags")
        tags = (
            [str(tag) for tag in tags_raw if str(tag).strip()] if isinstance(tags_raw, list) else []
        )
        return cls(
            rule=rule,
            source_pattern=source_pattern,
            weight=_clamp_unit(float(payload.get("weight", 0.0))),
            created_at=created_at,
            access_count=max(0, int(payload.get("access_count", 0))),
            tags=tags,
            stage=str(payload.get("stage", SeedStage.T0_DRAFT.value)),
            stage_history=(
                list(payload["stage_history"])
                if isinstance(payload.get("stage_history"), list)
                else []
            ),
            freshness_score=_clamp_unit(float(payload.get("freshness_score", 1.0))),
            freshness_status=str(payload.get("freshness_status", "active") or "active"),
            last_supported_at=(
                str(payload.get("last_supported_at")) if payload.get("last_supported_at") else None
            ),
        )


class MemoryCrystallizer:
    """
    ChronicleCore-inspired memory crystallization.

    Takes consolidation patterns and extracts permanent decision rules.
    """

    def __init__(
        self,
        crystal_path: Path = Path("memory/crystals.jsonl"),
        min_frequency: int = 3,
        max_crystals_keep: int = 256,
        freshness_half_life_days: int = 21,
    ) -> None:
        self.crystal_path = Path(crystal_path)
        self.min_frequency = max(1, int(min_frequency))
        self.max_crystals_keep = max(1, int(max_crystals_keep))
        self.freshness_half_life_days = max(1, int(freshness_half_life_days))

    def crystallize(self, patterns: Dict[str, object]) -> List[Crystal]:
        """Extract crystallized rules from consolidation patterns and persist them."""
        now = _utcnow_iso()
        generated: List[Crystal] = []

        verdicts = patterns.get("verdicts")
        if isinstance(verdicts, dict):
            block_count = int(verdicts.get("block", 0))
            approve_count = int(verdicts.get("approve", 0))

            if block_count >= self.min_frequency:
                generated.append(
                    Crystal(
                        rule="avoid high-risk actions that previously triggered block outcomes",
                        source_pattern=f"verdict:block x{block_count}",
                        weight=0.8,
                        created_at=now,
                        tags=["avoid", "verdict", "block"],
                    )
                )

            low_tension_approvals = int(patterns.get("low_tension_approvals", 0))
            if approve_count >= self.min_frequency and low_tension_approvals >= 5:
                generated.append(
                    Crystal(
                        rule="prefer low-tension execution patterns with consistent approvals",
                        source_pattern=(
                            f"verdict:approve x{approve_count}, low_tension_approvals={low_tension_approvals}"
                        ),
                        weight=0.7,
                        created_at=now,
                        tags=["prefer", "approve", "stability"],
                    )
                )

        autonomous_high_delta = int(patterns.get("autonomous_high_delta", 0))
        if autonomous_high_delta >= self.min_frequency:
            generated.append(
                Crystal(
                    rule="attention: autonomous high-delta outputs require explicit self-check",
                    source_pattern=f"genesis:autonomous_high_delta x{autonomous_high_delta}",
                    weight=0.9,
                    created_at=now,
                    tags=["attention", "autonomous", "high_delta"],
                )
            )

        collapse_warnings = patterns.get("collapse_warnings")
        collapse_count = 0
        if isinstance(collapse_warnings, dict):
            collapse_count = sum(int(v) for v in collapse_warnings.values())
        if collapse_count > 0:
            generated.append(
                Crystal(
                    rule="critical: collapse warnings escalate to fail-closed governance",
                    source_pattern=f"collapse_warning x{collapse_count}",
                    weight=1.0,
                    created_at=now,
                    tags=["critical", "collapse_warning", "safety"],
                )
            )

        resonate_count = int(patterns.get("resonance_convergences", 0))
        if resonate_count >= self.min_frequency:
            generated.append(
                Crystal(
                    rule=(
                        "prefer interactions that produce genuine resonance "
                        "(tension -> convergence -> novel output)"
                    ),
                    source_pattern=f"resonance_convergence x{resonate_count}",
                    weight=0.9,
                    created_at=now,
                    access_count=0,
                    tags=["prefer", "resonance", "convergence"],
                )
            )

        if generated:
            # ETCL: advance newly generated crystals to T1 (deposit)
            for crystal in generated:
                crystal.advance_stage(SeedStage.T1_DEPOSIT)
            self._append_crystals(generated)

        try:
            from memory.provenance_chain import ProvenanceManager

            ProvenanceManager().add_record(
                event_type="memory_event",
                content={"event": "crystallize", "count": len(generated)},
                metadata={"component": "MemoryCrystallizer"},
            )
        except Exception:
            pass
        return generated

    def load_crystals(
        self,
        max_age_days: Optional[int] = None,
        *,
        dedupe: bool = True,
        apply_freshness: bool = True,
    ) -> List[Crystal]:
        """Load persisted crystals, optionally filtering by recency."""
        if not self.crystal_path.exists():
            return []

        age_limit: Optional[datetime] = None
        if max_age_days is not None:
            age_limit = datetime.now(timezone.utc) - timedelta(days=max(0, int(max_age_days)))

        crystals: List[Crystal] = []
        with self.crystal_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                crystal = Crystal.from_dict(payload if isinstance(payload, dict) else {})
                if crystal is None:
                    continue
                if age_limit is not None:
                    created_at = _parse_iso(crystal.created_at)
                    if created_at is None or created_at < age_limit:
                        continue
                if apply_freshness:
                    self._refresh_freshness(crystal)
                crystals.append(crystal)
        if dedupe:
            return self._dedupe_crystals(crystals)
        return crystals

    def top_crystals(self, n: int = 10) -> List[Crystal]:
        """Return top-N crystals by weight, then access count, then recency."""
        limit = max(0, int(n))
        if limit == 0:
            return []
        crystals = self.load_crystals()
        crystals.sort(key=self._sort_key, reverse=True)
        return crystals[:limit]

    def record_retrieval(self, crystals: List[Crystal]) -> None:
        """Mark retrieved crystals as T2 (retrieval & awakening) and persist.

        Only advances crystals that are currently at T1. Already at T2+
        are left unchanged.  access_count is also incremented.
        """
        for crystal in crystals:
            crystal.access_count += 1
            crystal.advance_stage(SeedStage.T2_RETRIEVAL)
            crystal.last_supported_at = _utcnow_iso()
            self._refresh_freshness(crystal)
        self._write_crystals(crystals)

    def mark_support(self, crystal_rule: str) -> bool:
        """Mark a crystal as supported by recent evidence and persist it."""
        target = str(crystal_rule or "").strip().lower()
        if not target:
            return False
        crystals = self.load_crystals(dedupe=False, apply_freshness=False)
        updated = False
        for crystal in crystals:
            if str(crystal.rule).strip().lower() != target:
                continue
            crystal.last_supported_at = _utcnow_iso()
            crystal.access_count += 1
            self._refresh_freshness(crystal)
            updated = True
        if updated:
            self._write_crystals(self._dedupe_crystals(crystals))
        return updated

    def retire_crystal(self, crystal_rule: str) -> bool:
        """Remove a crystal whose rule text matches *crystal_rule*.

        Used when verification confirms a rule is no longer valid.
        Returns True if a crystal was removed, False otherwise.
        """
        target = str(crystal_rule or "").strip().lower()
        if not target:
            return False
        crystals = self.load_crystals(dedupe=False, apply_freshness=False)
        before = len(crystals)
        remaining = [c for c in crystals if str(c.rule).strip().lower() != target]
        if len(remaining) == before:
            return False
        self._write_crystals(self._dedupe_crystals(remaining))
        return True

    def freshness_summary(self, top_n_stale: int = 3) -> Dict[str, object]:
        """Return compact freshness statistics for governance surfaces."""
        crystals = self.load_crystals()
        if not crystals:
            return {
                "total_crystals": 0,
                "active_count": 0,
                "needs_verification_count": 0,
                "stale_count": 0,
                "mean_freshness": 0.0,
                "stale_rules": [],
            }

        active = [c for c in crystals if c.freshness_status == "active"]
        needs_verification = [c for c in crystals if c.freshness_status == "needs_verification"]
        stale = [c for c in crystals if c.freshness_status == "stale"]
        mean_freshness = sum(float(c.freshness_score) for c in crystals) / len(crystals)

        stale_sorted = sorted(stale, key=lambda c: (float(c.freshness_score), c.created_at))
        stale_rules = [c.rule for c in stale_sorted[: max(0, int(top_n_stale))]]

        return {
            "total_crystals": len(crystals),
            "active_count": len(active),
            "needs_verification_count": len(needs_verification),
            "stale_count": len(stale),
            "mean_freshness": round(_clamp_unit(mean_freshness), 4),
            "stale_rules": stale_rules,
        }

    def _append_crystals(self, crystals: List[Crystal]) -> None:
        self.crystal_path.parent.mkdir(parents=True, exist_ok=True)

        existing = self.load_crystals(dedupe=False)
        merged = self._dedupe_crystals([*existing, *crystals])
        merged.sort(key=self._sort_key, reverse=True)
        merged = merged[: self.max_crystals_keep]
        self._write_crystals(merged)

    def _write_crystals(self, crystals: List[Crystal]) -> None:
        """Overwrite the crystal file with the given list."""
        self.crystal_path.parent.mkdir(parents=True, exist_ok=True)
        with self.crystal_path.open("w", encoding="utf-8") as handle:
            for crystal in crystals:
                handle.write(json.dumps(crystal.to_dict(), ensure_ascii=False) + "\n")

    @staticmethod
    def _dedupe_key(crystal: Crystal) -> str:
        return str(crystal.rule).strip().lower()

    @staticmethod
    def _sort_key(crystal: Crystal) -> Tuple[float, int, datetime]:
        effective_weight = _clamp_unit(crystal.weight) * _clamp_unit(crystal.freshness_score)
        return (
            effective_weight,
            int(crystal.access_count),
            _parse_iso(crystal.created_at) or datetime.fromtimestamp(0, tz=timezone.utc),
        )

    def _refresh_freshness(self, crystal: Crystal) -> None:
        """Compute freshness score and status using age + support recency."""
        now = datetime.now(timezone.utc)
        base_dt = _parse_iso(crystal.last_supported_at) or _parse_iso(crystal.created_at)
        if base_dt is None:
            crystal.freshness_score = 0.5
            crystal.freshness_status = "needs_verification"
            return

        age_days = max(0.0, (now - base_dt).total_seconds() / 86400.0)
        decay = math.exp(-math.log(2.0) * (age_days / float(self.freshness_half_life_days)))

        # Small confidence boost from repeated support (bounded)
        support_boost = min(0.15, int(crystal.access_count) * 0.01)
        score = _clamp_unit(decay + support_boost)
        crystal.freshness_score = score
        crystal.freshness_status = _freshness_status(score)

    def _dedupe_crystals(self, crystals: List[Crystal]) -> List[Crystal]:
        merged: Dict[str, Crystal] = {}
        for crystal in crystals:
            key = self._dedupe_key(crystal)
            existing = merged.get(key)
            if existing is None:
                merged[key] = crystal
                continue

            current_dt = _parse_iso(existing.created_at) or datetime.fromtimestamp(
                0, tz=timezone.utc
            )
            incoming_dt = _parse_iso(crystal.created_at) or datetime.fromtimestamp(
                0, tz=timezone.utc
            )

            use_incoming = incoming_dt >= current_dt
            latest = crystal if use_incoming else existing
            older = existing if use_incoming else crystal
            tags = list(dict.fromkeys([*latest.tags, *older.tags]))

            # ETCL: keep the more advanced stage and merge histories
            existing_stage_idx = (
                _STAGE_ORDER.index(existing.stage) if existing.stage in _STAGE_ORDER else 0
            )
            incoming_stage_idx = (
                _STAGE_ORDER.index(crystal.stage) if crystal.stage in _STAGE_ORDER else 0
            )
            merged_stage = (
                crystal.stage if incoming_stage_idx >= existing_stage_idx else existing.stage
            )
            merged_history = list(
                {
                    json.dumps(h, sort_keys=True): h
                    for h in [*existing.stage_history, *crystal.stage_history]
                }.values()
            )

            merged[key] = Crystal(
                rule=latest.rule,
                source_pattern=latest.source_pattern,
                weight=max(existing.weight, crystal.weight),
                created_at=latest.created_at,
                access_count=max(int(existing.access_count), int(crystal.access_count)),
                tags=tags,
                stage=merged_stage,
                stage_history=merged_history,
            )

        return list(merged.values())
