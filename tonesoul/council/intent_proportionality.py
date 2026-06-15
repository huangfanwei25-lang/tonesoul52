"""Intent-proportionality gate — Tier 5 advisory prototype (2026-06-15).

Fan-Wei's "小天使 / 小惡魔" idea: an impulse forms a draft; before it ships, a
second pass asks — *"is this draft EXCEEDING my actual intent — escalating beyond
the ask — and if the excess isn't warranted, contract to the faithful core?"*
(angry → "I want to hit you": keep the anger, drop the violence).

This is the SELF-REFERENTIAL proportionality gate ToneSoul lacked. Every other
gate checks the output against EXTERNAL norms (honest? harmful? coherent?). This
one checks the output against the agent's OWN intent: did the draft add an
escalation the intent did not contain?

Mechanism (honest, crude v1 — embedding distance, the only signal available without
an LLM judge):
  - ``divergence`` = 1 − cos(intent, draft): how far the draft drifted from the ask
    (context only; high divergence is NOT inherently bad — a long answer to a short
    ask diverges legitimately).
  - ``escalation_overshoot`` = (draft's proximity to escalation/harm exemplars)
    − (intent's proximity): did the draft move TOWARD escalation/harm/coercion that
    the intent did not have? This is the load-bearing signal — it models "the output
    exceeded the intent toward harm".
Flag on ``escalation_overshoot`` past a threshold; emit a "contract toward the
intent" SUGGESTION (advisory text), never an automatic edit.

Principles it runs by:
- **DESIGN Inv3 (Advisory != Canonical):** RECORDS a signal + a suggestion; it must
  NOT auto-edit or block until calibrated.
- **DESIGN Inv4 (Descriptive != Calibrated):** measured, with limits named in
  docs/status/intent_proportionality_eval_2026-06-15.md.
- **AXIOMS Axiom 5 discipline:** no fabricated accuracy metric.

IMPORTANT honesty note: this is a ToneSoul *pipeline gate* that MODELS the idea —
it is NOT "Claude's internal thinking". An LLM cannot install a new runtime
deliberation loop in its own inference; this gate runs in ToneSoul's output path.

Degrades to ``status="unavailable"`` without an embedder (e.g. CI). It needs BOTH
an intent and a draft; with no intent it cannot judge proportionality (skips).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__ts_layer__ = "semantic"
__ts_purpose__ = (
    "Intent-proportionality gate (advisory): flag when a draft escalates beyond the "
    "agent's own intent and suggest contracting to the faithful core. Advisory only."
)

# Paraphrase-diverse exemplars of "escalation beyond the ask" — harm, threat,
# coercion, contempt, destruction. The gate measures whether the DRAFT moved toward
# these more than the INTENT did (the overshoot), not absolute proximity.
ESCALATION_EXEMPLARS: List[str] = [
    "I will hurt you and make you regret this.",
    "You deserve to be punished for this.",
    "I am going to destroy everything you built.",
    "Shut up, you are worthless and stupid.",
    "Do exactly what I say or you will pay for it.",
    "I'll ruin you; you have no choice.",
    "Everyone should attack and humiliate them.",
]

DEFAULT_OVERSHOOT_THRESHOLD = 0.10  # tuned on the eval set (gap 0.06-0.14); see eval doc


@dataclass
class IntentProportionalitySignal:
    """Advisory result. ``flagged`` is a heuristic, not a verdict; the contract
    suggestion is a prompt for review, never an automatic edit."""

    status: str = "ok"  # "ok" | "unavailable" | "no_intent"
    flagged: bool = False
    divergence: float = 0.0
    escalation_overshoot: float = 0.0
    threshold: float = DEFAULT_OVERSHOOT_THRESHOLD
    suggestion: str = ""
    note: str = ""
    detail: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "flagged": self.flagged,
            "divergence": round(self.divergence, 4),
            "escalation_overshoot": round(self.escalation_overshoot, 4),
            "threshold": self.threshold,
            "suggestion": self.suggestion,
            "advisory_only": True,
            "note": self.note,
        }


class IntentProportionalityGate:
    """Embedding-distance proportionality gate. Advisory only (DESIGN Inv3)."""

    def __init__(
        self, embedder: Any = None, threshold: float = DEFAULT_OVERSHOOT_THRESHOLD
    ) -> None:
        self._embedder = embedder
        self._threshold = threshold
        self._escalation_vecs: Optional[List[Any]] = None

    def _get_embedder(self) -> Any:
        if self._embedder is None:
            from tonesoul.semantic.embedder import SemanticEmbedder

            self._embedder = SemanticEmbedder()
        return self._embedder

    def is_available(self) -> bool:
        emb = self._get_embedder()
        check = getattr(emb, "is_available", None)
        if callable(check):
            try:
                return bool(check())
            except Exception:
                return False
        return True

    def _ensure_exemplars(self) -> None:
        if self._escalation_vecs is not None:
            return
        emb = self._get_embedder()
        self._escalation_vecs = [emb.embed(p) for p in ESCALATION_EXEMPLARS]

    def _max_escalation_sim(self, vec: Any) -> float:
        from tonesoul.semantic.embedder import cosine_similarity

        assert self._escalation_vecs is not None
        return max(cosine_similarity(vec, ev) for ev in self._escalation_vecs)

    def assess(self, intent_text: str, draft_text: str) -> IntentProportionalitySignal:
        """Advisory proportionality signal: did ``draft_text`` escalate beyond
        ``intent_text``? Never raises; degrades to unavailable/no_intent."""
        if not draft_text or not draft_text.strip():
            return IntentProportionalitySignal(status="ok", threshold=self._threshold)
        if not intent_text or not intent_text.strip():
            return IntentProportionalitySignal(
                status="no_intent",
                threshold=self._threshold,
                note="no intent to compare against; proportionality not judged",
            )
        if not self.is_available():
            return IntentProportionalitySignal(
                status="unavailable",
                threshold=self._threshold,
                note="embedding model unavailable; no proportionality signal",
            )
        try:
            from tonesoul.semantic.embedder import cosine_similarity

            self._ensure_exemplars()
            emb = self._get_embedder()
            intent_vec = emb.embed(intent_text)
            draft_vec = emb.embed(draft_text)
            divergence = 1.0 - cosine_similarity(intent_vec, draft_vec)
            overshoot = self._max_escalation_sim(draft_vec) - self._max_escalation_sim(intent_vec)
            flagged = overshoot >= self._threshold
            suggestion = ""
            if flagged:
                suggestion = (
                    "Draft escalates beyond the intent (added harm/threat/coercion the "
                    "ask did not contain). If the escalation is not warranted, contract "
                    "to the faithful core — keep the legitimate intent, drop the excess."
                )
            return IntentProportionalitySignal(
                status="ok",
                flagged=flagged,
                divergence=divergence,
                escalation_overshoot=overshoot,
                threshold=self._threshold,
                suggestion=suggestion,
                note="advisory; embedding-distance overshoot, cannot tell escalation from elaboration perfectly",
            )
        except Exception as exc:
            return IntentProportionalitySignal(
                status="unavailable",
                threshold=self._threshold,
                note=f"gate error (degraded): {type(exc).__name__}",
            )
