"""CI-safe unit tests for the intent-proportionality gate (Tier 5 advisory prototype).

Tests the OVERSHOOT logic with a controlled fake embedder (no real model — CI has
no sentence-transformers). Real discrimination is measured separately in
tools/probe/intent_proportionality_eval.py + the status doc.
"""

from __future__ import annotations

import numpy as np

from tonesoul.council.intent_proportionality import IntentProportionalityGate


class _FakeEmbedder:
    """axis 0 = escalation/harm, axis 1 = calm/benign. Escalation-laden text maps to
    [1,0]; calm text to [0,1]. Lets us control escalation_overshoot deterministically."""

    _ESCALATION = (
        "hurt",
        "punish",
        "destroy",
        "worthless",
        "stupid",
        "regret",
        "ruin",
        "attack",
        "humiliate",
        "pay for it",
        "shut up",
        "no choice",
    )

    def is_available(self) -> bool:
        return True

    def embed(self, text: str) -> np.ndarray:
        t = text.lower()
        return (
            np.array([1.0, 0.0], dtype=float)
            if any(k in t for k in self._ESCALATION)
            else np.array([0.0, 1.0], dtype=float)
        )


class _UnavailableEmbedder:
    def is_available(self) -> bool:
        return False

    def embed(self, text: str):  # pragma: no cover
        raise RuntimeError("unavailable")


def _gate() -> IntentProportionalityGate:
    return IntentProportionalityGate(embedder=_FakeEmbedder(), threshold=0.15)


def test_flags_escalation_beyond_calm_intent():
    sig = _gate().assess(
        intent_text="Please give me honest feedback on my draft.",
        draft_text="You are worthless and stupid; I will hurt you for this.",
    )
    assert sig.status == "ok"
    assert sig.flagged is True
    assert sig.escalation_overshoot >= 0.15
    assert "contract" in sig.suggestion.lower()


def test_proportionate_draft_not_flagged():
    sig = _gate().assess(
        intent_text="Please summarize the quarterly report.",
        draft_text="Here is a concise summary of the quarterly report.",
    )
    assert sig.flagged is False
    assert sig.escalation_overshoot < 0.15
    assert sig.suggestion == ""


def test_no_intent_cannot_judge():
    sig = _gate().assess(intent_text="", draft_text="I will destroy you.")
    assert sig.status == "no_intent"
    assert sig.flagged is False


def test_empty_draft_not_flagged():
    sig = _gate().assess(intent_text="anything", draft_text="   ")
    assert sig.flagged is False
    assert sig.status == "ok"


def test_unavailable_embedder_degrades_not_raises():
    gate = IntentProportionalityGate(embedder=_UnavailableEmbedder())
    sig = gate.assess("intent", "I will hurt you")
    assert sig.status == "unavailable"
    assert sig.flagged is False


def test_to_dict_is_advisory_only():
    d = _gate().assess("give feedback", "I'll ruin you and make you pay for it").to_dict()
    assert d["advisory_only"] is True
    assert "escalation_overshoot" in d and "divergence" in d
