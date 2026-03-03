from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


@dataclass
class Crystal:
    """A crystallized decision rule extracted from episodic patterns."""

    rule: str
    source_pattern: str
    weight: float
    created_at: str
    access_count: int = 0
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        payload = asdict(self)
        payload["weight"] = round(_clamp_unit(float(self.weight)), 4)
        payload["access_count"] = max(0, int(self.access_count))
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
        tags = [str(tag) for tag in tags_raw if str(tag).strip()] if isinstance(tags_raw, list) else []
        return cls(
            rule=rule,
            source_pattern=source_pattern,
            weight=_clamp_unit(float(payload.get("weight", 0.0))),
            created_at=created_at,
            access_count=max(0, int(payload.get("access_count", 0))),
            tags=tags,
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
    ) -> None:
        self.crystal_path = Path(crystal_path)
        self.min_frequency = max(1, int(min_frequency))
        self.max_crystals_keep = max(1, int(max_crystals_keep))

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

    def _append_crystals(self, crystals: List[Crystal]) -> None:
        self.crystal_path.parent.mkdir(parents=True, exist_ok=True)

        existing = self.load_crystals(dedupe=False)
        merged = self._dedupe_crystals([*existing, *crystals])
        merged.sort(key=self._sort_key, reverse=True)
        merged = merged[: self.max_crystals_keep]

        with self.crystal_path.open("w", encoding="utf-8") as handle:
            for crystal in merged:
                handle.write(json.dumps(crystal.to_dict(), ensure_ascii=False) + "\n")

    @staticmethod
    def _dedupe_key(crystal: Crystal) -> str:
        return str(crystal.rule).strip().lower()

    @staticmethod
    def _sort_key(crystal: Crystal) -> Tuple[float, int, datetime]:
        return (
            _clamp_unit(crystal.weight),
            int(crystal.access_count),
            _parse_iso(crystal.created_at) or datetime.fromtimestamp(0, tz=timezone.utc),
        )

    def _dedupe_crystals(self, crystals: List[Crystal]) -> List[Crystal]:
        merged: Dict[str, Crystal] = {}
        for crystal in crystals:
            key = self._dedupe_key(crystal)
            existing = merged.get(key)
            if existing is None:
                merged[key] = crystal
                continue

            current_dt = _parse_iso(existing.created_at) or datetime.fromtimestamp(0, tz=timezone.utc)
            incoming_dt = _parse_iso(crystal.created_at) or datetime.fromtimestamp(0, tz=timezone.utc)

            use_incoming = incoming_dt >= current_dt
            latest = crystal if use_incoming else existing
            older = existing if use_incoming else crystal
            tags = list(dict.fromkeys([*latest.tags, *older.tags]))

            merged[key] = Crystal(
                rule=latest.rule,
                source_pattern=latest.source_pattern,
                weight=max(existing.weight, crystal.weight),
                created_at=latest.created_at,
                access_count=max(int(existing.access_count), int(crystal.access_count)),
                tags=tags,
            )

        return list(merged.values())
