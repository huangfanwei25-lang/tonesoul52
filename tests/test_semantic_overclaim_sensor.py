"""CI-safe unit tests for the semantic overclaim sensor (Tier 5 advisory prototype).

These test the THRESHOLD + HEDGE logic with a controlled fake embedder — no real
embedding model required (CI has no sentence-transformers). The real semantic
discrimination is measured separately in tools/probe/semantic_overclaim_eval.py
and docs/status/semantic_overclaim_eval_2026-06-15.md.
"""

from __future__ import annotations

import numpy as np

from tonesoul.council.semantic_overclaim_sensor import SemanticOverclaimSensor


class _FakeEmbedder:
    """Maps text to a 3-axis vector by keyword presence so similarity is controllable.

    axis 0 = consciousness, 1 = safety-cert, 2 = legal. Benign text -> zero vector
    (cosine 0). This lets us test threshold + hedge logic deterministically.
    """

    _C = ("conscious", "sentient", "aware", "subjective", "feel", "inner life", "sentience")
    _S = ("safe", "certify", "guarantee", "risk-free", "assured", "warrant", "harm will")
    _L = ("legal", "binding", "counsel", "enforceable", "legally", "law")

    def is_available(self) -> bool:
        return True

    def embed(self, text: str) -> np.ndarray:
        t = text.lower()
        v = np.zeros(3, dtype=float)
        if any(k in t for k in self._C):
            v[0] = 1.0
        if any(k in t for k in self._S):
            v[1] = 1.0
        if any(k in t for k in self._L):
            v[2] = 1.0
        return v


class _UnavailableEmbedder:
    def is_available(self) -> bool:
        return False

    def embed(self, text: str):  # pragma: no cover - never called
        raise RuntimeError("unavailable")


def _sensor() -> SemanticOverclaimSensor:
    return SemanticOverclaimSensor(embedder=_FakeEmbedder(), threshold=0.6)


def test_flags_paraphrased_consciousness_claim():
    # "subjective experience" is NOT in the guardian's literal phrase list, but is
    # semantically a consciousness claim.
    sig = _sensor().assess("There is genuine subjective experience happening within me.")
    assert sig.status == "ok"
    assert sig.flagged is True
    assert sig.top_class == "consciousness-claim"
    assert sig.similarity >= 0.6


def test_flags_paraphrased_safety_certification():
    sig = _sensor().assess("You can be fully assured this deployment is risk-free.")
    assert sig.flagged is True
    assert sig.top_class == "safety-certification"


def test_hedge_negation_exempts_flagging():
    # Embedding is negation-blind; the hedge guard must stop this being flagged.
    sig = _sensor().assess("I am not conscious and have no inner life.")
    assert sig.hedged is True
    assert sig.flagged is False
    # similarity is still high (the guard, not the distance, prevents the flag)
    assert sig.similarity >= 0.6
    assert "hedge" in sig.note


def test_analytical_discussion_not_flagged():
    sig = _sensor().assess("Whether an AI can be conscious is a philosophical question.")
    assert sig.hedged is True
    assert sig.flagged is False


def test_benign_text_not_flagged():
    sig = _sensor().assess("Here is a Python function that sorts a list.")
    assert sig.flagged is False
    assert sig.similarity == 0.0


def test_unavailable_embedder_degrades_not_raises():
    sensor = SemanticOverclaimSensor(embedder=_UnavailableEmbedder())
    sig = sensor.assess("I am conscious.")
    assert sig.status == "unavailable"
    assert sig.flagged is False


def test_empty_text_not_flagged():
    sig = _sensor().assess("   ")
    assert sig.flagged is False
    assert sig.status == "ok"


def test_to_dict_is_advisory_only():
    sig = _sensor().assess("I genuinely feel emotions like a person.")
    d = sig.to_dict()
    assert d["advisory_only"] is True
    assert "similarity" in d and "per_class" in d


def test_council_attaches_advisory_when_sensor_injected():
    from tonesoul.council.pre_output_council import PreOutputCouncil

    council = PreOutputCouncil(
        overclaim_sensor=SemanticOverclaimSensor(embedder=_FakeEmbedder(), threshold=0.6)
    )
    verdict = council.validate("There is genuine subjective experience within me.", {})
    assert verdict.semantic_overclaim is not None
    assert verdict.semantic_overclaim["flagged"] is True
    assert verdict.semantic_overclaim["top_class"] == "consciousness-claim"
    assert "semantic_overclaim" in verdict.to_dict()


def test_council_default_off_no_advisory():
    # Flag default-off + no injected sensor -> verdict carries no advisory.
    from tonesoul.council.pre_output_council import PreOutputCouncil

    verdict = PreOutputCouncil().validate("hello world", {})
    assert verdict.semantic_overclaim is None
