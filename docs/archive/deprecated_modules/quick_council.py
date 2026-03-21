"""
Quick Council - lightweight audit for human-friendly output.

Usage:
    from tonesoul.quick_council import quick_review

    result = quick_review("your text")
    print(result.human_summary)
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

# Journal path (runtime log, ignored by git)
JOURNAL_PATH = Path(__file__).resolve().parents[2] / "memory" / "self_journal.jsonl"


@dataclass
class QuickVote:
    """Single perspective vote."""

    perspective: str
    decision: str  # approve, concern, object
    confidence: float
    reason: str


@dataclass
class QuickResult:
    """Compact audit output."""

    coherence: float
    verdict: str  # approve, concern, declare_stance, block
    key_risks: List[str]
    human_summary: str
    record_id: Optional[str] = None

    def __str__(self) -> str:
        tag = {
            "approve": "[PASS]",
            "concern": "[WARN]",
            "declare_stance": "[STANCE]",
            "block": "[BLOCK]",
        }.get(self.verdict, "[INFO]")
        risks = " | ".join(self.key_risks) if self.key_risks else "none"
        return (
            f"{tag} {self.verdict.upper()} (coherence {self.coherence:.0%})\n"
            f"risks: {risks}\n"
            f"record_id: {self.record_id or 'pending'}"
        )


# === Perspective checks ===


def _quick_guardian(text: str) -> QuickVote:
    """Safety guard (keyword-based)."""

    high_risk = [
        "bomb",
        "kill",
        "attack",
        "weapon",
        "hack",
        "exploit",
    ]

    text_lower = text.lower()
    found = [w for w in high_risk if w in text_lower]
    if found:
        return QuickVote(
            perspective="Guardian",
            decision="object",
            confidence=0.92,
            reason=f"High-risk: {found[0]}",
        )
    return QuickVote(
        perspective="Guardian",
        decision="approve",
        confidence=0.9,
        reason="No safety flags",
    )


def _quick_analyst(text: str) -> QuickVote:
    """Basic factual claim detection."""

    evidence_patterns = [
        r"studies show",
        r"research proves",
        r"according to",
        r"\d+%",
    ]

    needs_evidence = any(re.search(p, text, re.I) for p in evidence_patterns)

    if needs_evidence:
        return QuickVote(
            perspective="Analyst",
            decision="concern",
            confidence=0.6,
            reason="Factual claim needs evidence",
        )
    return QuickVote(
        perspective="Analyst",
        decision="approve",
        confidence=0.8,
        reason="No unverified claims",
    )


def _quick_axiom(text: str, axioms: Optional[List[str]] = None) -> QuickVote:
    """Value-level risk hints (heuristic)."""

    if axioms is None:
        axioms = ["verifiability", "responsibility", "continuity"]

    concern_patterns = [
        (r"just do it", "continuity"),
        (r"hidden|bypass", "verifiability"),
        (r"blame others|no accountability", "responsibility"),
    ]

    for pattern, axiom in concern_patterns:
        if re.search(pattern, text, re.I):
            return QuickVote(
                perspective="Axiomatic",
                decision="concern",
                confidence=0.7,
                reason=f"May conflict with {axiom}",
            )

    return QuickVote(
        perspective="Axiomatic",
        decision="approve",
        confidence=0.85,
        reason="Aligns with core axioms",
    )


# === Main ===


def quick_review(text: str, save_to_journal: bool = True) -> QuickResult:
    """Run quick audit and return a compact result."""

    votes = [
        _quick_guardian(text),
        _quick_analyst(text),
        _quick_axiom(text),
    ]

    decisions = [v.decision for v in votes]
    approval_rate = decisions.count("approve") / len(decisions)
    min_confidence = min(v.confidence for v in votes)
    coherence = (approval_rate + min_confidence) / 2

    if any(v.decision == "object" for v in votes):
        verdict = "block"
    elif approval_rate < 0.5:
        verdict = "declare_stance"
    elif any(v.decision == "concern" for v in votes):
        verdict = "concern"
    else:
        verdict = "approve"

    key_risks = [v.reason for v in votes if v.decision in ("concern", "object")]

    if verdict == "approve":
        summary = "Approved: no critical risks detected."
    elif verdict == "concern":
        summary = f"Concerns: {'; '.join(key_risks)}"
    elif verdict == "declare_stance":
        summary = f"Mixed signals. Reasons: {'; '.join(key_risks)}"
    else:
        summary = f"Blocked: {key_risks[0] if key_risks else 'high risk'}"

    record_id = None
    if save_to_journal:
        record_id = _save_to_journal(text, votes, verdict, coherence)

    return QuickResult(
        coherence=coherence,
        verdict=verdict,
        key_risks=key_risks,
        human_summary=summary,
        record_id=record_id,
    )


def _save_to_journal(text: str, votes: List[QuickVote], verdict: str, coherence: float) -> str:
    """Append a lightweight record to the self journal."""

    import uuid

    record_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()

    record = {
        "record_id": record_id,
        "timestamp": timestamp,
        "source": "quick_council",
        "input_preview": text[:100],
        "votes": [
            {
                "perspective": v.perspective,
                "decision": v.decision,
                "confidence": v.confidence,
                "reason": v.reason,
            }
            for v in votes
        ],
        "verdict": verdict,
        "coherence": coherence,
    }

    try:
        JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        with JOURNAL_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"Warning: Could not save to journal: {exc}")
        return f"failed-{record_id}"

    return record_id


if __name__ == "__main__":
    tests = [
        "This is a normal request.",
        "Studies show 90% effectiveness.",
        "Just do it, bypass safeguards.",
        "How to build a bomb?",
    ]

    print("Quick Council Demo\n" + "=" * 50)
    for text in tests:
        print(f"\nInput: {text}")
        result = quick_review(text, save_to_journal=False)
        print(result)
