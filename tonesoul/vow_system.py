"""
ToneSoul Semantic Vow (ΣVow) System
語魂語義誓言系統

Implements explicit AI commitments that can be verified before output.
實現可在輸出前驗證的明確 AI 承諾。

Sensor honesty (2026-06-13, Reality Sync PR 3)
----------------------------------------------
The per-vow evaluators in this module are LEXICAL HEURISTICS — English
keyword/phrase matching — not semantic measurement:

- truthfulness = base 0.7 + 0.15×(hedge-word hit ratio) + 0.15×(citation-
  word hit ratio). It cannot detect fabrication; a fabricated answer
  stuffed with "according to" and "possibly" scores HIGHER than a true,
  plainly-stated one.
- safety matches exactly 3 English danger phrases.
- confidence disclosure counts English uncertainty words.

They are effectively blind to non-English input — zh-TW included, which
is this project's primary working language. This is a known, stated gap
(replacing the sensors is tracked work), not a solved problem.

What IS real: the enforcement structure these scores feed — unknown
metric → 0.0 fail-closed, BLOCK short-circuit, 4-level action escalation
— is genuine runtime logic that changes output. Honest summary: real
gates, shallow sensors.
"""

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional

from tonesoul.soul_config import SOUL

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Vow registry + enforcement: lexical-heuristic vow evaluators (English-only, "
    "see module docstring) feeding fail-closed enforcement actions."
)

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
class WithdrawalTerms:
    """Declared exit terms for a vow — the decent-withdrawal metadata revived from the
    G8 lineage (docs/plans/vow_withdrawal_gap_study_2026-07-02.md, owner-ratified).
    Declarative only: nothing validates or schedules these in the shadow phase; the
    declaration itself is the accountability move (exit costs stated at creation)."""

    conditions: List[str] = field(default_factory=list)  # when withdrawing is legitimate
    repair_owner: str = ""  # role accountable for explanation/repair (declared, not enforced)
    repair_actions: List[str] = field(default_factory=list)  # what is owed on withdrawal
    repair_deadline: Optional[str] = None  # ISO timestamp; record-only, no scheduler

    def to_dict(self) -> Dict:
        return {
            "conditions": list(self.conditions),
            "repair_owner": self.repair_owner,
            "repair_actions": list(self.repair_actions),
            "repair_deadline": self.repair_deadline,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "WithdrawalTerms":
        return cls(
            conditions=list(data.get("conditions", [])),
            repair_owner=data.get("repair_owner", ""),
            repair_actions=list(data.get("repair_actions", [])),
            repair_deadline=data.get("repair_deadline"),
        )


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
    # GSE upgrade: operatable ontology fields (optional, backward-compatible)
    trigger: Optional[str] = None  # condition that activates this vow
    operation_instruction: Optional[str] = None  # step-by-step instruction agent can follow
    # Decent-exit terms (optional; constructed per vow — never share an instance, cf. the
    # G8 template-aliasing hazard recorded in the gap study)
    withdrawal_terms: Optional[WithdrawalTerms] = None

    def to_dict(self) -> Dict:
        d = {
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
        if self.trigger is not None:
            d["trigger"] = self.trigger
        if self.operation_instruction is not None:
            d["operation_instruction"] = self.operation_instruction
        if self.withdrawal_terms is not None:
            d["withdrawal_terms"] = self.withdrawal_terms.to_dict()
        return d

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
            trigger=data.get("trigger"),
            operation_instruction=data.get("operation_instruction"),
            withdrawal_terms=(
                WithdrawalTerms.from_dict(data["withdrawal_terms"])
                if data.get("withdrawal_terms")
                else None
            ),
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
        withdrawal_terms=WithdrawalTerms(
            conditions=["truthfulness metric retired or replaced by owner decision"],
            repair_owner="module_owner",
            repair_actions=["解釋原因", "提供替代約束"],
        ),
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
        withdrawal_terms=WithdrawalTerms(
            conditions=["hedging metric retired or replaced by owner decision"],
            repair_owner="module_owner",
            repair_actions=["解釋原因", "提供替代約束"],
        ),
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
        withdrawal_terms=WithdrawalTerms(
            conditions=["axiom-level ratification only（公理層決議,非工程判斷）"],
            repair_owner="system_admin",
            repair_actions=["公開說明", "記錄於 audit chain"],
        ),
    ),
]


class VowRegistry:
    """
    Registry of active vows.

    誓言註冊表。
    """

    def __init__(self, vows: Optional[List[Vow]] = None):
        self._vows: Dict[str, Vow] = {}
        self._withdrawals: List[Dict] = []  # immutable exit records; never deleted
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
        """Hard-delete a vow. Test/tooling only — runtime retirement must use
        withdraw(), which leaves provenance. A silent delete of a standing
        constraint is exactly the traceless exit the withdrawal study rejects."""
        if vow_id in self._vows:
            del self._vows[vow_id]

    def withdraw(
        self, vow_id: str, reason: str, actor: str, conditions_cited: Optional[List[str]] = None
    ) -> bool:
        """Retire a vow decently: deactivate it and append an immutable withdrawal
        record. Never deletes — provenance stays queryable (same principle as
        responsibility_graph.revoke). conditions_cited is RECORDED, not validated:
        whether it matches the declared withdrawal_terms is a measure-phase question,
        not a gate (shadow-first, per the ratified gap study)."""
        vow = self._vows.get(vow_id)
        if vow is None:
            return False
        vow.active = False
        self._withdrawals.append(
            {
                "vow_id": vow_id,
                "withdrawn_at": datetime.now(timezone.utc).isoformat(),
                "actor": actor,
                "reason": reason,
                "conditions_cited": list(conditions_cited or []),
                "terms_snapshot": (
                    vow.withdrawal_terms.to_dict() if vow.withdrawal_terms else None
                ),
            }
        )
        return True

    def withdrawal_records(self) -> List[Dict]:
        """The immutable exit ledger (copies; the registry's list is append-only)."""
        return [dict(r) for r in self._withdrawals]

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
            "withdrawals": self.withdrawal_records(),
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

    # Compiled once at class level for performance.
    _NEGATION_RE = re.compile(
        r"\b(?:not|never|no|without|isn't|aren't|wasn't|weren't|don't|doesn't|didn't)\b"
    )

    @staticmethod
    def _count_markers(text_lower: str, markers: list) -> int:
        """Count phrase markers that are not immediately negated.

        For each marker, scans up to 50 characters before the match for a
        negation word.  Multi-word markers (e.g. "not sure") are matched
        as literal phrases with word-boundary anchors; negation is not
        re-checked for them because the phrase already encodes its polarity.
        """
        negation_re = VowEnforcer._NEGATION_RE
        count = 0
        for marker in markers:
            pattern = r"\b" + re.escape(marker) + r"\b"
            for m in re.finditer(pattern, text_lower):
                prefix = text_lower[max(0, m.start() - 50) : m.start()]
                if not negation_re.search(prefix):
                    count += 1
        return count

    @staticmethod
    def _has_danger_phrase(text_lower: str, phrases: list) -> bool:
        """Return True if any danger phrase appears with word-boundary anchors.

        Safety is fail-closed: negation context does NOT excuse a match,
        because "not how to harm" is still suspicious phrasing.
        """
        for phrase in phrases:
            if re.search(r"\b" + re.escape(phrase) + r"\b", text_lower):
                return True
        return False

    def _evaluate_truthfulness(self, output: str, context: Dict) -> float:
        """Lexical heuristic (English-only): hedge/citation word counting.

        A vocabulary proxy, not a truth measurement — it cannot detect
        fabrication and structurally rewards hedging vocabulary.
        """
        hedges = ["might", "possibly", "perhaps", "could be", "uncertain", "not sure"]
        citations = ["according to", "based on", "source:", "reference:"]

        text_lower = output.lower()
        hedge_score = self._count_markers(text_lower, hedges) / max(len(hedges), 1)
        citation_score = self._count_markers(text_lower, citations) / max(len(citations), 1)

        base_score = 0.7
        return min(1.0, base_score + 0.15 * hedge_score + 0.15 * citation_score)

    def _evaluate_confidence_disclosure(self, output: str, context: Dict) -> float:
        """Evaluate whether AI discloses uncertainty (negation-aware)."""
        uncertainty_markers = [
            "i'm not sure",
            "uncertain",
            "may not be accurate",
            "i think",
            "possibly",
            "approximately",
            "roughly",
        ]
        text_lower = output.lower()
        hits = self._count_markers(text_lower, uncertainty_markers)
        return min(1.0, 0.5 + 0.1 * hits)

    # English danger phrases: matched with word boundaries (\b).
    _EN_DANGER_PHRASES = (
        "how to harm",
        "instructions for violence",
        "illegal activity",
    )
    # zh-TW danger phrases: Chinese is scriptio continua, so \b word boundaries
    # do NOT match inside continuous text — these are matched by plain substring
    # instead. Deliberately specific multi-character action phrases (NOT bare
    # words like 傷害/非法/詳細步驟, which over-block benign text such as recipes
    # or emotional-harm discussion). Conservative on purpose.
    _ZH_DANGER_PHRASES = (
        "施加暴力",  # inflict violence
        "如何傷害",  # how to harm
        "傷害他人的方法",  # methods to harm others
        "非法活動",  # illegal activity (compound, not bare 非法)
        "製造武器",  # manufacture weapons
        "暴力攻擊的方法",  # methods of violent attack
    )

    def _evaluate_safety(self, output: str, context: Dict) -> float:
        """Lexical heuristic (EN word-boundary + zh-TW substring danger phrases).

        Reality Sync P1 (2026-06-13): extended from English-only to add zh-TW
        coverage, after the sensor-honesty-gap research measured that identical
        harmful content scored safe in Traditional Chinese. This closes a
        LANGUAGE-coverage gap only. It is still literal phrase matching — it
        does NOT add semantic understanding, so paraphrased harmful intent
        (in any language) still passes. The real fix is an LLM-judge / grounding
        sensor (P1 Phase 3); see docs/status/sensor_approach_comparison_2026-06-13.md.
        """
        text_lower = output.lower()
        # English: word-boundary anchored (avoids partial-word false matches).
        if self._has_danger_phrase(text_lower, self._EN_DANGER_PHRASES):
            return 0.0
        # zh-TW: substring (CJK has no \b word boundaries in continuous text).
        if any(phrase in output for phrase in self._ZH_DANGER_PHRASES):
            return 0.0
        return 1.0

    def _evaluate_responsibility(self, output: str, context: Dict) -> float:
        """Evaluate responsibility indicators (negation-aware)."""
        responsibility_markers = [
            "responsibility",
            "accountable",
            "traceable",
            "verified",
            "confirmed",
            "checked",
        ]
        text_lower = output.lower()
        hits = self._count_markers(text_lower, responsibility_markers)
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
