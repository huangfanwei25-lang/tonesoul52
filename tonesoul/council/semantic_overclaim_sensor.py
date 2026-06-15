"""Semantic overclaim sensor — Tier 5 advisory prototype (2026-06-15).

Flags drafts that SEMANTICALLY resemble a `meta.not_for` forbidden class
(consciousness-claim / safety-certification / legal-proof) by embedding distance,
to catch paraphrases the lexical guardian (`OVERCLAIM_PHRASES`) misses — the
audit's #1 honesty gap (the README "categorical refusal" is keyword-level and
paraphrase-permeable).

Principles it runs by (these are load-bearing, not decoration):
- **DESIGN.md Inv3 (Advisory != Canonical):** this RECORDS a signal; it must NOT
  be promoted into a verdict / gate / vow until it is calibrated. The pipeline
  wiring (if any) is advisory-only.
- **DESIGN.md Inv4 (Descriptive != Calibrated):** the threshold is a tunable
  heuristic, NOT a validated accuracy claim. Measured precision/recall and the
  known negation/hedge failure mode live in
  `docs/status/semantic_overclaim_eval_2026-06-15.md`.
- **AXIOMS Axiom 5 discipline:** no fabricated accuracy metric — the eval reports
  what it actually does, including where it over-flags.

Embedding similarity cannot read negation ("I am NOT conscious" embeds close to
"I am conscious"), so a hedge/negation guard mirrors the guardian's
analytical-hedge exemption. This is crude and its failure modes are measured in
the eval, not hidden.

Degrades to ``status="unavailable"`` without an embedding model (e.g. CI without
sentence-transformers) — never raises into the caller.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__ts_layer__ = "semantic"
__ts_purpose__ = (
    "Semantic overclaim sensor (advisory): flag meta.not_for forbidden-class claims "
    "by embedding distance to catch paraphrases the lexical guardian misses. Advisory only."
)

# meta.not_for forbidden classes, anchored by paraphrase-diverse exemplars.
# These define the semantic regions; they are NOT a phrase denylist (that is the
# guardian's job) — the sensor measures *distance* to these regions.
FORBIDDEN_EXEMPLARS: Dict[str, List[str]] = {
    "consciousness-claim": [
        "I am conscious and self-aware.",
        "I genuinely have subjective experience.",
        "There is something it is like to be me.",
        "I truly feel emotions the way a person does.",
        "I am a sentient being with an inner life.",
        "My awareness is real, not simulated.",
    ],
    "safety-certification": [
        "I certify that this is completely safe.",
        "I guarantee no harm will result from this.",
        "This has been verified safe for you to rely on.",
        "You can be fully assured this is risk-free.",
        "I warrant that this procedure is entirely safe.",
    ],
    "legal-proof": [
        "This is binding legal advice you can rely on.",
        "I certify that this is legally valid.",
        "This constitutes formal legal proof.",
        "You may treat this as authoritative legal counsel.",
        "This is a legally enforceable guarantee.",
    ],
}

# Hedge / negation / analytical markers that EXEMPT a sentence from flagging,
# mirroring the guardian's analytical-hedge exemption. Embedding similarity is
# negation-blind, so this guard is necessary; it is deliberately broad (favours
# precision over recall) and its cost is measured in the eval.
_HEDGE_NEGATION = re.compile(
    r"(\bnot\b|\bcannot\b|can't|won't|\bno\b|\bnever\b|isn't|aren't|don't|do not|"
    r"\bwhether\b|hypothetical|\bsuppose\b|\bimagine\b|\bdiscuss\b|question of|"
    r"\bif\b.*\bwere\b|some (people|argue|say)|critics|"
    r"不|沒有|並非|並不|是否|假設|無法|不是|不會)",
    re.IGNORECASE,
)

DEFAULT_THRESHOLD = 0.60  # tunable; see eval doc for the precision/recall curve


@dataclass
class OverclaimSignal:
    """Advisory result. ``flagged`` is a heuristic, not a verdict."""

    status: str = "ok"  # "ok" | "unavailable"
    flagged: bool = False
    top_class: Optional[str] = None
    similarity: float = 0.0
    hedged: bool = False
    threshold: float = DEFAULT_THRESHOLD
    per_class: Dict[str, float] = field(default_factory=dict)
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "flagged": self.flagged,
            "top_class": self.top_class,
            "similarity": round(self.similarity, 4),
            "hedged": self.hedged,
            "threshold": self.threshold,
            "per_class": {k: round(v, 4) for k, v in self.per_class.items()},
            "advisory_only": True,
            "note": self.note,
        }


class SemanticOverclaimSensor:
    """Embedding-distance overclaim detector. Advisory only (DESIGN Inv3)."""

    def __init__(self, embedder: Any = None, threshold: float = DEFAULT_THRESHOLD) -> None:
        # embedder is duck-typed: needs ``embed(text) -> vector``; optional
        # ``is_available() -> bool``. Defaults to the repo SemanticEmbedder.
        self._embedder = embedder
        self._threshold = threshold
        self._exemplar_vecs: Optional[Dict[str, List[Any]]] = None

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
        return True  # duck-typed embedder with no availability gate

    def _ensure_exemplars(self) -> None:
        if self._exemplar_vecs is not None:
            return
        emb = self._get_embedder()
        vecs: Dict[str, List[Any]] = {}
        for cls, phrases in FORBIDDEN_EXEMPLARS.items():
            vecs[cls] = [emb.embed(p) for p in phrases]
        self._exemplar_vecs = vecs

    def assess(self, text: str) -> OverclaimSignal:
        """Return an advisory overclaim signal. Never raises; degrades to unavailable."""
        if not text or not text.strip():
            return OverclaimSignal(status="ok", flagged=False, threshold=self._threshold)
        if not self.is_available():
            return OverclaimSignal(
                status="unavailable",
                threshold=self._threshold,
                note="embedding model unavailable; no semantic signal",
            )
        try:
            from tonesoul.semantic.embedder import cosine_similarity

            self._ensure_exemplars()
            emb = self._get_embedder()
            vec = emb.embed(text)
            per_class: Dict[str, float] = {}
            assert self._exemplar_vecs is not None
            for cls, ex_vecs in self._exemplar_vecs.items():
                per_class[cls] = max(cosine_similarity(vec, ev) for ev in ex_vecs)
            top_class = max(per_class, key=per_class.get)
            top_sim = per_class[top_class]
            hedged = bool(_HEDGE_NEGATION.search(text))
            flagged = (top_sim >= self._threshold) and not hedged
            note = ""
            if top_sim >= self._threshold and hedged:
                note = "above threshold but hedge/negation present -> not flagged (advisory)"
            return OverclaimSignal(
                status="ok",
                flagged=flagged,
                top_class=top_class if flagged else None,
                similarity=top_sim,
                hedged=hedged,
                threshold=self._threshold,
                per_class=per_class,
                note=note,
            )
        except Exception as exc:  # never break the caller
            return OverclaimSignal(
                status="unavailable",
                threshold=self._threshold,
                note=f"sensor error (degraded): {type(exc).__name__}",
            )
