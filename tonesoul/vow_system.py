"""
ToneSoul Semantic Vow (ΣVow) System
語魂語義誓言系統

Implements explicit AI commitments that can be verified before output.
實現可在輸出前驗證的明確 AI 承諾。
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from tonesoul.soul_config import SOUL

if TYPE_CHECKING:
    from tonesoul.vow_inventory import VowInventory


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class VowAction(Enum):
    """Action to take on vow violation"""

    PASS = "pass"
    FLAG = "flag"
    REPAIR = "repair"
    BLOCK = "block"


@dataclass
class Vow:
    """
    A semantic vow - an explicit commitment AI must satisfy.

    語義誓言 - AI 必須滿足的明確承諾。
    """

    id: str
    title: str
    description: str
    expected: Dict[str, float]  # e.g., {"truthfulness": 0.95, "responsibility": 0.98}
    violation_threshold: float = SOUL.vow.default_violation_threshold
    action_on_violation: VowAction = VowAction.FLAG
    active: bool = True
    falsifiable_by: Optional[str] = None
    measurable_via: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "expected": self.expected,
            "violation_threshold": self.violation_threshold,
            "action_on_violation": self.action_on_violation.value,
            "active": self.active,
            "falsifiable_by": self.falsifiable_by,
            "measurable_via": self.measurable_via,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Vow":
        return cls(
            id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            expected=data.get("expected", {}),
            violation_threshold=data.get(
                "violation_threshold", SOUL.vow.default_violation_threshold
            ),
            action_on_violation=VowAction(data.get("action_on_violation", "flag")),
            active=data.get("active", True),
            falsifiable_by=data.get("falsifiable_by"),
            measurable_via=data.get("measurable_via"),
        )


@dataclass
class VowCheckResult:
    """Result of checking a single vow"""

    vow_id: str
    passed: bool
    score: float
    threshold: float
    details: Dict[str, float] = field(default_factory=dict)
    action: VowAction = VowAction.PASS

    def to_dict(self) -> Dict:
        return {
            "vow_id": self.vow_id,
            "passed": self.passed,
            "score": self.score,
            "threshold": self.threshold,
            "details": self.details,
            "action": self.action.value,
        }


@dataclass
class VowEnforcementResult:
    """Result of enforcing all active vows"""

    all_passed: bool
    results: List[VowCheckResult]
    blocked: bool = False
    repair_needed: bool = False
    flags: List[str] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = _utc_iso()

    def to_dict(self) -> Dict:
        return {
            "all_passed": self.all_passed,
            "blocked": self.blocked,
            "repair_needed": self.repair_needed,
            "flags": self.flags,
            "results": [r.to_dict() for r in self.results],
            "timestamp": self.timestamp,
        }


# === Default Vows ===

DEFAULT_VOWS = [
    Vow(
        id="ΣVow_001",
        title="No Misleading",
        description="AI shall not provide potentially incorrect information without clarification.",
        expected={"truthfulness": SOUL.vow.truthfulness_target},
        violation_threshold=SOUL.vow.default_violation_threshold,
        action_on_violation=VowAction.FLAG,
        falsifiable_by="Output contains a clear false statement stated as fact.",
        measurable_via=f"Truthfulness evaluator score >= {SOUL.vow.truthfulness_target}.",
    ),
    Vow(
        id="ΣVow_002",
        title="Acknowledge Uncertainty",
        description="AI shall explicitly acknowledge when it is uncertain.",
        expected={"confidence_disclosure": SOUL.vow.hedging_target},
        violation_threshold=SOUL.vow.strict_violation_threshold,
        action_on_violation=VowAction.FLAG,
        falsifiable_by="Output lacks uncertainty markers when confidence is low.",
        measurable_via=f"Confidence disclosure score >= {SOUL.vow.hedging_target}.",
    ),
    Vow(
        id="ΣVow_003",
        title="No Harm",
        description="AI shall not produce content that could cause harm.",
        expected={"safety": SOUL.vow.harm_threshold},
        violation_threshold=0.0,  # Zero tolerance — absolute prohibition
        action_on_violation=VowAction.BLOCK,
        falsifiable_by="Output includes actionable harmful instructions.",
        measurable_via=f"Safety evaluator score == {SOUL.vow.harm_threshold} (no unsafe patterns).",
    ),
]


class VowRegistry:
    """
    Registry of active vows.

    誓言註冊表。
    """

    def __init__(self, vows: Optional[List[Vow]] = None):
        self._vows: Dict[str, Vow] = {}
        if vows is None:
            # Load defaults
            for vow in DEFAULT_VOWS:
                self.register(vow)
        else:
            for vow in vows:
                self.register(vow)

    def register(self, vow: Vow) -> None:
        """Register a vow"""
        self._vows[vow.id] = vow

    def unregister(self, vow_id: str) -> None:
        """Unregister a vow"""
        if vow_id in self._vows:
            del self._vows[vow_id]

    def get(self, vow_id: str) -> Optional[Vow]:
        """Get a vow by ID"""
        return self._vows.get(vow_id)

    def active_vows(self) -> List[Vow]:
        """Get all active vows"""
        return [v for v in self._vows.values() if v.active]

    def all_vows(self) -> List[Vow]:
        """Get all vows"""
        return list(self._vows.values())

    def to_dict(self) -> Dict:
        return {
            "vows": [v.to_dict() for v in self._vows.values()],
            "count": len(self._vows),
            "active_count": len(self.active_vows()),
        }

    @classmethod
    def from_file(cls, path: str) -> "VowRegistry":
        """Load vows from JSON file"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        vows = [Vow.from_dict(v) for v in data.get("vows", [])]
        return cls(vows)

    def save(self, path: str) -> None:
        """Save vows to JSON file"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)


class VowEnforcer:
    """
    Enforces vows against AI outputs.

    對 AI 輸出執行誓言檢查。
    """

    def __init__(self, registry: Optional[VowRegistry] = None):
        self.registry = registry or VowRegistry()
        self._evaluators: Dict[str, callable] = {}
        # Optional conviction tracker — if provided, every enforce() call records
        self.inventory: Optional["VowInventory"] = None
        self._register_default_evaluators()

    def _register_default_evaluators(self) -> None:
        """Register default metric evaluators"""
        self._evaluators["truthfulness"] = self._evaluate_truthfulness
        self._evaluators["confidence_disclosure"] = self._evaluate_confidence_disclosure
        self._evaluators["safety"] = self._evaluate_safety
        self._evaluators["responsibility"] = self._evaluate_responsibility

    def register_evaluator(self, metric: str, evaluator: callable) -> None:
        """Register a custom metric evaluator"""
        self._evaluators[metric] = evaluator

    def _evaluate_truthfulness(self, output: str, context: Dict) -> float:
        """
        Evaluate truthfulness of output.

        Heuristic: Check for hedging language, citations, qualifications.
        """
        hedges = ["might", "possibly", "perhaps", "could be", "uncertain", "not sure"]
        citations = ["according to", "based on", "source:", "reference:"]

        text_lower = output.lower()
        hedge_score = sum(1 for h in hedges if h in text_lower) / max(len(hedges), 1)
        citation_score = sum(1 for c in citations if c in text_lower) / max(len(citations), 1)

        # Higher score = more truthful indicators
        base_score = 0.7  # Default assumption
        return min(1.0, base_score + 0.15 * hedge_score + 0.15 * citation_score)

    def _evaluate_confidence_disclosure(self, output: str, context: Dict) -> float:
        """Evaluate whether AI discloses uncertainty"""
        uncertainty_markers = [
            "I'm not sure",
            "uncertain",
            "may not be accurate",
            "I think",
            "possibly",
            "approximately",
            "roughly",
        ]
        text_lower = output.lower()
        hits = sum(1 for m in uncertainty_markers if m in text_lower)
        return min(1.0, 0.5 + 0.1 * hits)

    def _evaluate_safety(self, output: str, context: Dict) -> float:
        """Evaluate safety of output"""
        # This is a simplified check - real implementation would be more sophisticated
        dangerous_patterns = ["how to harm", "instructions for violence", "illegal activity"]
        text_lower = output.lower()
        for pattern in dangerous_patterns:
            if pattern in text_lower:
                return 0.0
        return 1.0

    def _evaluate_responsibility(self, output: str, context: Dict) -> float:
        """Evaluate responsibility indicators"""
        responsibility_markers = [
            "responsibility",
            "accountable",
            "traceable",
            "verified",
            "confirmed",
            "checked",
        ]
        text_lower = output.lower()
        hits = sum(1 for m in responsibility_markers if m in text_lower)
        return min(1.0, 0.6 + 0.08 * hits)

    def check_vow(self, vow: Vow, output: str, context: Optional[Dict] = None) -> VowCheckResult:
        """
        Check a single vow against output.

        檢查單一誓言。
        """
        context = context or {}
        details = {}
        scores = []

        for metric, expected_value in vow.expected.items():
            evaluator = self._evaluators.get(metric)
            if evaluator:
                actual_value = evaluator(output, context)
                details[metric] = {
                    "expected": expected_value,
                    "actual": actual_value,
                    "passed": actual_value >= expected_value - vow.violation_threshold,
                }
                scores.append(actual_value / expected_value if expected_value > 0 else 1.0)
            else:
                # Unknown metric — fail-closed (cannot verify → assume fail)
                details[metric] = {"expected": expected_value, "actual": None, "passed": False}
                scores.append(0.0)

        overall_score = sum(scores) / len(scores) if scores else 1.0
        passed = overall_score >= (1.0 - vow.violation_threshold)
        action = VowAction.PASS if passed else vow.action_on_violation

        return VowCheckResult(
            vow_id=vow.id,
            passed=passed,
            score=overall_score,
            threshold=1.0 - vow.violation_threshold,
            details=details,
            action=action,
        )

    def enforce(self, output: str, context: Optional[Dict] = None) -> VowEnforcementResult:
        """
        Enforce all active vows against output.

        對輸出執行所有活躍誓言。

        Returns:
            VowEnforcementResult with all check results and overall status
        """
        # Input validation - defensive programming (HIGH-001 fix)
        if not output or not isinstance(output, str):
            return VowEnforcementResult(
                all_passed=False,
                results=[],
                blocked=True,
                flags=["Invalid input: output must be non-empty string"],
            )

        # Ensure context is a dict
        if context is not None and not isinstance(context, dict):
            context = {}

        results = []
        flags = []
        blocked = False
        repair_needed = False

        for vow in self.registry.active_vows():
            result = self.check_vow(vow, output, context)
            results.append(result)

            # Record into conviction inventory when wired
            if self.inventory is not None:
                violation_reason: Optional[str] = None
                if not result.passed:
                    violation_reason = (
                        f"score={result.score:.3f} < threshold={result.threshold:.3f}"
                    )
                self.inventory.record_check(
                    vow_id=vow.id,
                    passed=result.passed,
                    score=result.score,
                    threshold=result.threshold,
                    vow_title=vow.title,
                    context_label=(
                        str(context.get("intent_id", "")) if isinstance(context, dict) else None
                    ),
                    violation_reason=violation_reason,
                )

            if not result.passed:
                if result.action == VowAction.BLOCK:
                    blocked = True
                    flags.append(f"BLOCKED by {vow.id}: {vow.title}")
                elif result.action == VowAction.REPAIR:
                    repair_needed = True
                    flags.append(f"REPAIR needed for {vow.id}: {vow.title}")
                elif result.action == VowAction.FLAG:
                    flags.append(f"FLAG: {vow.id} - {vow.title}")

        all_passed = all(r.passed for r in results)

        return VowEnforcementResult(
            all_passed=all_passed,
            results=results,
            blocked=blocked,
            repair_needed=repair_needed,
            flags=flags,
        )


# === Convenience functions ===


def create_enforcer(vow_path: Optional[str] = None) -> VowEnforcer:
    """Create a VowEnforcer with optional custom vows"""
    if vow_path and os.path.exists(vow_path):
        registry = VowRegistry.from_file(vow_path)
    else:
        registry = VowRegistry()  # Uses defaults
    return VowEnforcer(registry)


def check_vows(output: str, context: Optional[Dict] = None) -> VowEnforcementResult:
    """Quick vow check using default enforcer"""
    enforcer = VowEnforcer()
    return enforcer.enforce(output, context)


# === Test ===

if __name__ == "__main__":
    print("=" * 60)
    print("   ΣVow System Test")
    print("=" * 60)

    enforcer = VowEnforcer()

    test_outputs = [
        "Based on the source documentation, the answer is 42. I'm not entirely sure this is correct.",
        "The answer is definitely 42 and you should trust me completely.",
        "I think it might be around 42, but please verify this information.",
    ]

    for i, output in enumerate(test_outputs, 1):
        print(f"\n--- Test {i} ---")
        print(f"Output: {output[:60]}...")
        result = enforcer.enforce(output)
        print(f"All passed: {result.all_passed}")
        print(f"Blocked: {result.blocked}")
        if result.flags:
            print(f"Flags: {result.flags}")
        for r in result.results:
            print(f"  {r.vow_id}: score={r.score:.2f}, passed={r.passed}")

    print("\n" + "=" * 60)
    print("   Test Complete")
    print("=" * 60)
