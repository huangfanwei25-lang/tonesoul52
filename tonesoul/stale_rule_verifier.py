"""
Phase 542: Stale Rule Verification Task Generator

Automatically converts stale rules (freshness_score < 0.30) into Dream Engine
verification tasks. These tasks prompt the system to seek evidence that either
re-confirms the rule or recommends decomissioning it.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional


def _utcnow_iso() -> str:
    """Return current UTC time in ISO format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_iso(value: str) -> Optional[datetime]:
    """Parse ISO datetime string safely."""
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


def _build_verification_challenge(
    *,
    rule_text: str,
    freshness_score: float,
    decay_percentage: float,
    source_pattern: Optional[str],
) -> str:
    context_hint = (
        f"Context hint: {source_pattern}."
        if str(source_pattern or "").strip()
        else "Context hint: none recorded."
    )
    if freshness_score < 0.15:
        focus_line = (
            "Focus: find EVIDENCE that re-confirms this rule in recent observable contexts, "
            "or find a COUNTER-EXAMPLE showing it has become invalid."
        )
    else:
        focus_line = "Focus: find a recent case that validates or refutes it."

    return "\n".join(
        [
            "Goal function: determine whether this stale rule still holds in recent observable contexts before keeping or decomissioning it.",
            "Priority rules:",
            "- P0: do not re-confirm the rule without recent evidence and do not invent support that is not actually present.",
            "- P1: prefer the strongest counter-example or supporting case over generic intuition or legacy habit.",
            "- P2: if the pattern appears conditional or time-bounded, name that boundary instead of overstating the rule.",
            f"Rule under review: {rule_text!r}.",
            f"Freshness score: {freshness_score:.2f} (decayed {decay_percentage}%).",
            context_hint,
            focus_line,
            "Recovery instructions: if evidence is thin, mixed, or missing, mark the result inconclusive and name the smallest bounded next verification step.",
            "Output expectation: summarize the best supporting evidence, the best contradicting evidence, and whether the rule should be re-confirmed, decomissioned, or left inconclusive.",
        ]
    )


@dataclass
class VerificationQuery:
    """A structured query prompt for verifying a stale rule."""

    rule_text: str
    """The original rule being verified."""

    challenge: str
    """Open question that would confirm or refute the rule."""

    evidence_types: List[str]
    """What kind of evidence would count (e.g., 'counter_example', 'supporting_case', 'research_paper')."""

    confidence_threshold: float
    """If re-evidence confidence score >= this, mark rule as re-confirmed."""

    decomission_reason: Optional[str] = None
    """If set, suggests why the rule might be wrong and should be decomissioned."""

    @classmethod
    def for_stale_rule(
        cls,
        rule_text: str,
        freshness_score: float,
        source_pattern: Optional[str] = None,
    ) -> VerificationQuery:
        """Factory: generate a VerificationQuery for a stale rule.

        Args:
            rule_text: The rule that needs verifying
            freshness_score: Current freshness (< 0.30 for stale)
            source_pattern: Optional context about where the rule came from

        Returns:
            VerificationQuery with challenge and evidence types
        """
        decay_percentage = round((1.0 - freshness_score) * 100, 1)

        # Generate challenge based on decay severity
        if freshness_score < 0.15:
            challenge = _build_verification_challenge(
                rule_text=rule_text,
                freshness_score=freshness_score,
                decay_percentage=decay_percentage,
                source_pattern=source_pattern,
            )
            evidence_types = ["counter_example", "supporting_case", "temporal_exception"]
            decomission_hint = (
                "If no supporting evidence found in 3 attempts, consider decomissioning."
            )
        else:
            challenge = _build_verification_challenge(
                rule_text=rule_text,
                freshness_score=freshness_score,
                decay_percentage=decay_percentage,
                source_pattern=source_pattern,
            )
            evidence_types = ["supporting_case", "research_update", "recent_pattern"]
            decomission_hint = None

        return cls(
            rule_text=rule_text,
            challenge=challenge,
            evidence_types=evidence_types,
            confidence_threshold=0.75 if freshness_score < 0.2 else 0.60,
            decomission_reason=decomission_hint,
        )

    def to_dict(self) -> Dict[str, object]:
        """Serialize to dictionary."""
        return asdict(self)


@dataclass
class StaleRuleVerificationTask:
    """A verification task generated from a stale crystal rule."""

    task_id: str
    """Unique identifier for this verification task."""

    rule_id: str
    """Reference to the original Crystal.rule identifier (hash or exact rule text)."""

    rule_text: str
    """The rule being verified."""

    source_pattern: Optional[str]
    """Context: what pattern originally generated this rule."""

    freshness_score: float
    """Current freshness score at generation time."""

    age_days: float
    """Days since rule was created."""

    verification_query: VerificationQuery
    """The structured challenge and evidence requirements."""

    created_at: str
    """When this verification task was created."""

    dream_engine_priority: float
    """Priority hint for Dream Engine to consider this among other stimuli."""

    status: str = "pending"
    """Status: pending, in_progress, re_confirmed, decomissioned, failed."""

    verification_attempts: int = 0
    """How many times Dream Engine attempted verification."""

    last_attempt_at: Optional[str] = None
    """Timestamp of last verification attempt."""

    verification_result: Optional[Dict[str, object]] = None
    """Result of the last verification attempt."""

    @classmethod
    def from_crystal(
        cls,
        crystal: object,
        *,
        task_id_prefix: str = "verify",
    ) -> StaleRuleVerificationTask:
        """Factory: create a verification task from a stale Crystal.

        Args:
            crystal: A Crystal object with freshness_score < 0.30
            task_id_prefix: Prefix for generating task_id

        Returns:
            StaleRuleVerificationTask ready for Dream Engine enrollment

        Raises:
            ValueError: If crystal is not stale (freshness_score >= 0.30)
        """
        freshness_score = getattr(crystal, "freshness_score", 1.0)
        if freshness_score >= 0.30:
            raise ValueError(
                f"Crystal not stale enough (score={freshness_score}). "
                f"Only stale rules (< 0.30) warrant verification tasks."
            )

        created_at_dt = _parse_iso(getattr(crystal, "created_at", _utcnow_iso()))
        now = datetime.now(timezone.utc)
        age_days = (now - created_at_dt).total_seconds() / 86400 if created_at_dt else 0

        rule_text = getattr(crystal, "rule", "")
        source_pattern = getattr(crystal, "source_pattern", None)

        # Generate verification query
        vquery = VerificationQuery.for_stale_rule(
            rule_text=rule_text,
            freshness_score=freshness_score,
            source_pattern=source_pattern,
        )

        # Compute priority: stale + old = higher priority
        # Base 0.60, boosted by decay severity and age
        decay_factor = 1.0 - freshness_score  # 0.70+ for stale
        age_factor = min(1.0, age_days / 365.0)  # Scale up to 1.0 over 1 year
        priority = round(0.60 + decay_factor * 0.25 + age_factor * 0.15, 3)

        return cls(
            task_id=f"{task_id_prefix}_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            rule_id=str(hash(rule_text)) if rule_text else "unknown",
            rule_text=rule_text,
            source_pattern=source_pattern,
            freshness_score=freshness_score,
            age_days=round(age_days, 2),
            verification_query=vquery,
            created_at=_utcnow_iso(),
            dream_engine_priority=priority,
        )

    def to_dict(self) -> Dict[str, object]:
        """Serialize to dictionary (for JSON persistence)."""
        d = asdict(self)
        # Convert VerificationQuery back to dict
        if isinstance(self.verification_query, VerificationQuery):
            d["verification_query"] = self.verification_query.to_dict()
        return d

    def record_attempt(self, result: Dict[str, object]) -> None:
        """Record a verification attempt and its result.

        Args:
            result: {
                "status": "re_confirmed" | "decomissioned" | "inconclusive",
                "confidence": 0.0-1.0,
                "evidence_summary": "...",
                "recommendation": "...",
            }
        """
        self.verification_attempts += 1
        self.last_attempt_at = _utcnow_iso()
        self.verification_result = result

        # Update task status based on result
        if result.get("status") == "re_confirmed":
            self.status = "re_confirmed"
        elif result.get("status") == "decomissioned":
            self.status = "decomissioned"
        elif result.get("status") == "inconclusive" and self.verification_attempts >= 3:
            # After 3 failed attempts, recommend decomissioning
            self.status = "failed"
        else:
            self.status = "in_progress"


class StaleRuleVerificationTaskBatch:
    """Manager for generating and tracking stale rule verification tasks."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "memory/verification_tasks.jsonl"
        self.tasks: Dict[str, StaleRuleVerificationTask] = {}

    def generate_from_crystals(
        self,
        crystals: List[object],
        *,
        max_tasks: int = 10,
    ) -> List[StaleRuleVerificationTask]:
        """Generate verification tasks from stale crystals.

        Args:
            crystals: List of Crystal objects
            max_tasks: Maximum number of tasks to generate

        Returns:
            List of StaleRuleVerificationTask objects
        """
        stale_only = [c for c in crystals if getattr(c, "freshness_score", 1.0) < 0.30]

        # Sort by freshness_score (most stale first) and age
        stale_only.sort(
            key=lambda c: (
                getattr(c, "freshness_score", 1.0),
                -self._get_age_days(c),
            )
        )

        tasks = []
        for crystal in stale_only[: max(0, int(max_tasks))]:
            try:
                task = StaleRuleVerificationTask.from_crystal(crystal)
                self.tasks[task.task_id] = task
                tasks.append(task)
            except ValueError:
                # Skip non-stale crystals
                continue

        return tasks

    def persist_tasks(self, tasks: List[StaleRuleVerificationTask]) -> None:
        """Append verification tasks to JSONL storage.

        Args:
            tasks: List of tasks to persist
        """
        try:
            from pathlib import Path

            path = Path(self.storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, "a", encoding="utf-8") as f:
                for task in tasks:
                    f.write(json.dumps(task.to_dict()) + "\n")
        except Exception as e:
            # Graceful degradation: log error but don't crash
            print(f"Warning: Failed to persist verification tasks: {e}")

    def load_tasks(self) -> List[StaleRuleVerificationTask]:
        """Load all verification tasks from storage.

        Returns:
            List of StaleRuleVerificationTask objects
        """
        try:
            from pathlib import Path

            path = Path(self.storage_path)
            if not path.exists():
                return []

            tasks = []
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        task = self._hydrate_task(data)
                        tasks.append(task)
                    except Exception:
                        continue
            return tasks
        except Exception:
            return []

    @staticmethod
    def _hydrate_task(data: Dict[str, object]) -> StaleRuleVerificationTask:
        """Reconstruct a StaleRuleVerificationTask from dict."""
        vquery_data = data.pop("verification_query", {})
        vquery = VerificationQuery(**vquery_data)
        return StaleRuleVerificationTask(
            **{k: v for k, v in data.items() if k != "verification_query"},
            verification_query=vquery,
        )

    def get_task_by_id(self, task_id: str) -> Optional[StaleRuleVerificationTask]:
        """Retrieve a task by ID."""
        return self.tasks.get(task_id)

    def get_pending_tasks(self) -> List[StaleRuleVerificationTask]:
        """Get all pending verification tasks."""
        return [t for t in self.tasks.values() if t.status == "pending"]

    @staticmethod
    def _get_age_days(crystal: object) -> float:
        """Extract age_days from crystal, defaulting to 0."""
        created_at_dt = _parse_iso(getattr(crystal, "created_at", _utcnow_iso()))
        now = datetime.now(timezone.utc)
        return (now - created_at_dt).total_seconds() / 86400 if created_at_dt else 0

    def apply_verification_results(self, crystallizer: object) -> Dict[str, int]:
        """Apply completed verification task results back to Crystallizer.

        For re_confirmed tasks  -> calls crystallizer.mark_support()
        For decomissioned tasks -> calls crystallizer.retire_crystal()
        For failed tasks        -> calls crystallizer.retire_crystal()

        Args:
            crystallizer: A MemoryCrystallizer instance with
                          mark_support() and retire_crystal() methods.

        Returns:
            {"re_confirmed": N, "retired": N, "skipped": N}
        """
        results = {"re_confirmed": 0, "retired": 0, "skipped": 0}
        tasks = self.load_tasks()

        rewrite_needed = False
        for task in tasks:
            if task.status == "re_confirmed":
                try:
                    crystallizer.mark_support(task.rule_text)
                    results["re_confirmed"] += 1
                    task.status = "applied_re_confirmed"
                    rewrite_needed = True
                except Exception:
                    results["skipped"] += 1
            elif task.status in ("decomissioned", "failed"):
                try:
                    crystallizer.retire_crystal(task.rule_text)
                    results["retired"] += 1
                    task.status = "applied_retired"
                    rewrite_needed = True
                except Exception:
                    results["skipped"] += 1

        if rewrite_needed:
            self._rewrite_tasks(tasks)

        return results

    def _rewrite_tasks(self, tasks: List[StaleRuleVerificationTask]) -> None:
        """Overwrite the task file with updated statuses."""
        try:
            from pathlib import Path

            path = Path(self.storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                for task in tasks:
                    f.write(json.dumps(task.to_dict()) + "\n")
        except Exception:
            pass
