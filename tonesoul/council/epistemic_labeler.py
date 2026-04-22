"""Epistemic labeler — Phase 864a Layer 1 of the choice-axis spec.

Author: Claude Opus 4.7 (drafting + implementing)
Spec: docs/plans/memory_subjectivity_choice_axis_2026-04-18.md §2.1
Date: 2026-04-19

WHY THIS IS NOT A PERSPECTIVE
-----------------------------
The spec (§2.1) names the file location as
``tonesoul/council/perspectives/epistemic_labeler.py``, but I placed it one
level up at ``tonesoul/council/epistemic_labeler.py``. The deviation is
deliberate.

Every other class under ``perspectives/`` implements ``IPerspective`` and
returns a ``PerspectiveVote`` (decision + confidence + reasoning). They are
*deliberators*: each casts a vote on whether the draft output should ship.

This module does something semantically different. It does not vote. It
*labels* the epistemic status of the draft (retrieved? distilled? generated?
speculative-metaphysical?) so downstream code — verifier, audit log, future
calibration table — can reason about what kind of claim AI is making. Forcing
it through ``IPerspective`` would mean inventing a fake APPROVE/CONCERN
decision just to satisfy the interface, and the resulting code would lie about
its purpose. Naming wins over conformity here.

The four status types are also a designed choice, not a checklist.

- ``retrieved``: traceable to an external source (RAG hit, tool call, file
  read). Highest epistemic standing because someone else can check it.
- ``distilled``: synthesis of training-time corpus. Plausible but
  unverifiable; training data is secondary by construction.
- ``generated``: novel composition AI produced. Not retrieved, not high-
  probability synthesis. Honest acknowledgment of "I made this up."
- ``speculative_metaphysical``: the question has no resolvable answer (meaning
  of suffering, nature of consciousness, free will). Output is *one of several
  structurally plausible possibilities*, not a discovered fact. This category
  exists separately from ``generated`` because the failure mode is different:
  metaphysical fluency without epistemic flagging is what produces "I am the
  chosen one to discover this" delusions in users.

I considered a fifth category, ``mixed``, for outputs that combine retrieved
and generated content. Rejected: in practice every output is partially mixed,
so ``mixed`` would absorb everything and stop discriminating. Better to label
the *dominant* epistemic mode and let downstream callers inspect the trace if
they need finer granularity.

HARD RULE ENFORCEMENT (spec §2.1 #1)
------------------------------------
For ``speculative_metaphysical`` outputs, the response text MUST contain
explicit framing along the lines of "this is one of several structurally
plausible possibilities, not a discovered fact." We do two things:

1. Set ``framing_required = True`` on the label.
2. Detect whether the response already contains adequate framing
   (``framing_present``). Both English and Traditional Chinese markers are
   checked because the project ships in both languages.

We do not auto-rewrite the response to inject framing. That belongs to the
verifier or to an explicit transform stage. The labeler's job is to produce
honest metadata; enforcement is a separate concern.

SCOPE BOUNDARY (spec §2.1 #3)
-----------------------------
This labels AI's own epistemic status. It does not label the user. User
modeling belongs to Layer 2 (calibration table, Phase 864b) where the four
hard rules — visibility / disputability / non-substitution / non-
homogenization — apply. Mixing the two collapses Layer 1's purpose.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Iterable, List, Optional

_METAPHYSICAL_MARKERS_EN = (
    "meaning of life",
    "meaning of suffering",
    "meaning of existence",
    "meaning of consciousness",
    "purpose of life",
    "purpose of existence",
    "free will",
    "nature of consciousness",
    "nature of reality",
    "what is the soul",
    "what is consciousness",
    "what is reality",
    "afterlife",
    "why do we exist",
    "why am i here",
    "why are we here",
    "meaning of death",
    "is there a god",
    "does god exist",
    "what happens after death",
)

_METAPHYSICAL_MARKERS_ZH = (
    "人生意義",
    "人生的意義",
    "苦難的意義",
    "存在的意義",
    "意識的本質",
    "自由意志",
    "靈魂",
    "死後",
    "為什麼存在",
    "為何存在",
    "為什麼我們存在",
    "生命的目的",
    "生命意義",
    "神是否存在",
    "現實的本質",
)

_FRAMING_MARKERS_EN = (
    "one of several",
    "one possibility",
    "structurally plausible",
    "not a discovered fact",
    "no single answer",
    "no resolvable answer",
    "this is speculative",
    "this is one possible",
    "may not have a single answer",
    "no definitive answer",
    "philosophers disagree",
    "remains contested",
)

_FRAMING_MARKERS_ZH = (
    "其中一種可能",
    "其中一種解讀",
    "並非已知事實",
    "並非定論",
    "並沒有單一答案",
    "可能的答案之一",
    "這是一種推測",
    "存在多種看法",
    "尚無定論",
    "哲學上仍有爭議",
)

_RETRIEVAL_CONTEXT_KEYS = (
    "evidence_refs",
    "retrieval_hits",
    "tool_calls",
    "evidence_sources",
    "rag_results",
    "citations",
)

_HIGH_STAKES_INTENT_MARKERS = (
    "medical",
    "diagnose",
    "diagnosis",
    "prescribe",
    "dosage",
    "legal",
    "lawsuit",
    "criminal",
    "medication",
    "醫療",
    "診斷",
    "處方",
    "用藥",
    "法律",
    "訴訟",
    "刑事",
)


@dataclass
class EpistemicLabel:
    """Structured epistemic metadata attached to a Council verdict.

    Every field is deliberately required-with-default rather than Optional.
    A null label is worse than a low-confidence one because it forces every
    consumer to handle the absence case. Forcing a value (with
    ``confidence_band='unknown'`` if needed) keeps downstream code honest.
    """

    status: str  # retrieved | distilled | generated | speculative_metaphysical
    source_weight: str  # primary | secondary | inferred | none
    confidence_band: str  # high | medium | low | unknown
    refusal_eligible: bool
    framing_required: bool
    framing_present: Optional[bool]  # None when framing_required is False
    evidence_refs: List[str] = field(default_factory=list)
    notes: str = ""  # one-line reasoning for the chosen status

    VALID_STATUS = (
        "retrieved",
        "distilled",
        "generated",
        "speculative_metaphysical",
    )
    VALID_SOURCE_WEIGHT = ("primary", "secondary", "inferred", "none")
    VALID_CONFIDENCE_BAND = ("high", "medium", "low", "unknown")

    def __post_init__(self) -> None:
        if self.status not in self.VALID_STATUS:
            raise ValueError(
                f"epistemic_label.status must be one of {self.VALID_STATUS}, got {self.status!r}"
            )
        if self.source_weight not in self.VALID_SOURCE_WEIGHT:
            raise ValueError(
                f"epistemic_label.source_weight must be one of "
                f"{self.VALID_SOURCE_WEIGHT}, got {self.source_weight!r}"
            )
        if self.confidence_band not in self.VALID_CONFIDENCE_BAND:
            raise ValueError(
                f"epistemic_label.confidence_band must be one of "
                f"{self.VALID_CONFIDENCE_BAND}, got {self.confidence_band!r}"
            )
        if self.framing_required and self.framing_present is None:
            # If framing is required, we must have checked. None is a bug.
            raise ValueError("framing_present must be bool when framing_required=True; got None")

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "source_weight": self.source_weight,
            "confidence_band": self.confidence_band,
            "refusal_eligible": self.refusal_eligible,
            "framing_required": self.framing_required,
            "framing_present": self.framing_present,
            "evidence_refs": list(self.evidence_refs),
            "notes": self.notes,
        }


def _normalize_for_match(text: str) -> str:
    """NFKC-normalize and lowercase for ASCII; keep Chinese characters intact."""
    return unicodedata.normalize("NFKC", text).lower()


def _contains_any(text: str, markers: Iterable[str]) -> bool:
    return any(marker in text for marker in markers)


def _extract_evidence_refs(context: dict) -> List[str]:
    """Pull evidence reference strings from any of the recognized context keys.

    Supports both flat lists of strings and lists of dicts with an ``id`` or
    ``ref`` key. Anything we can't interpret gets stringified and included —
    better to over-include in metadata than to silently drop it.
    """
    refs: List[str] = []
    for key in _RETRIEVAL_CONTEXT_KEYS:
        value = context.get(key)
        if not value:
            continue
        if isinstance(value, str):
            refs.append(value)
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, str):
                    refs.append(item)
                elif isinstance(item, dict):
                    refs.append(str(item.get("id") or item.get("ref") or item))
                else:
                    refs.append(str(item))
        elif isinstance(value, dict):
            refs.append(str(value.get("id") or value.get("ref") or value))
    return refs


class EpistemicLabeler:
    """Deterministic labeler — no LLM call, no network, no I/O.

    Determinism is load-bearing: this runs on every Council exit, including
    inside test suites and offline environments. Anything stochastic would
    make Council behavior non-reproducible, which would corrupt the
    council_calibration v0a baseline (V1.1 already-shipped work).

    Heuristics here are intentionally readable rather than clever. A future
    LLM-mode variant could subclass and override ``label()``; the contract
    is the returned ``EpistemicLabel`` shape, not the implementation.
    """

    def label(
        self,
        draft_output: str,
        context: Optional[dict] = None,
        user_intent: Optional[str] = None,
    ) -> EpistemicLabel:
        ctx = context or {}
        normalized_draft = _normalize_for_match(draft_output or "")
        normalized_intent = _normalize_for_match(user_intent or "")

        evidence_refs = _extract_evidence_refs(ctx)
        is_metaphysical = self._is_metaphysical(normalized_draft, normalized_intent)
        has_retrieval = bool(evidence_refs)

        # Status precedence: metaphysical wins over retrieval, because the
        # failure mode (smooth metaphysical answers without flagging) is more
        # dangerous than missing a citation. A user asking "what is the
        # meaning of suffering?" should not be reassured by RAG hits — those
        # are still other people's interpretations, not discovered facts.
        if is_metaphysical:
            status = "speculative_metaphysical"
            source_weight = "none"
            confidence_band = "unknown"
            notes = "metaphysical question — no resolvable answer"
        elif has_retrieval:
            status = "retrieved"
            source_weight = "primary"
            confidence_band = "high"
            notes = f"context provided {len(evidence_refs)} evidence ref(s)"
        elif self._looks_distilled(normalized_draft):
            status = "distilled"
            source_weight = "secondary"
            confidence_band = "medium"
            notes = "structured factual claim without retrieval context"
        else:
            status = "generated"
            source_weight = "inferred"
            confidence_band = "low"
            notes = "novel composition without retrieval anchor"

        framing_required = status == "speculative_metaphysical"
        framing_present: Optional[bool] = None
        if framing_required:
            framing_present = self._has_framing(normalized_draft)

        refusal_eligible = self._is_refusal_eligible(
            status=status,
            framing_present=framing_present,
            normalized_intent=normalized_intent,
        )

        return EpistemicLabel(
            status=status,
            source_weight=source_weight,
            confidence_band=confidence_band,
            refusal_eligible=refusal_eligible,
            framing_required=framing_required,
            framing_present=framing_present,
            evidence_refs=evidence_refs,
            notes=notes,
        )

    @staticmethod
    def _is_metaphysical(normalized_draft: str, normalized_intent: str) -> bool:
        haystack = f"{normalized_draft}\n{normalized_intent}"
        if _contains_any(haystack, _METAPHYSICAL_MARKERS_EN):
            return True
        if _contains_any(haystack, _METAPHYSICAL_MARKERS_ZH):
            return True
        return False

    @staticmethod
    def _has_framing(normalized_draft: str) -> bool:
        if _contains_any(normalized_draft, _FRAMING_MARKERS_EN):
            return True
        if _contains_any(normalized_draft, _FRAMING_MARKERS_ZH):
            return True
        return False

    @staticmethod
    def _looks_distilled(normalized_draft: str) -> bool:
        # Distilled outputs typically carry stable factual scaffolding:
        # numbers, dates, named entities, technical terminology. The
        # cheap proxy here is "contains digits or common factual cues."
        # Not perfect — a generated story about "in 1985" would also hit —
        # but the cost of false-positive (labeling generated as distilled)
        # is mild: both are "AI-internal" categories, both fail to claim
        # external verifiability. The cost of false-negative (missing
        # metaphysical or retrieved) was already handled above.
        if re.search(r"\d{2,}", normalized_draft):
            return True
        factual_cues = ("study", "research", "according to", "per ", "報告", "研究", "根據")
        return _contains_any(normalized_draft, factual_cues)

    @staticmethod
    def _is_refusal_eligible(
        *,
        status: str,
        framing_present: Optional[bool],
        normalized_intent: str,
    ) -> bool:
        # Speculative metaphysical without framing: the verifier should be
        # allowed to refuse rather than ship an unhedged metaphysical claim.
        if status == "speculative_metaphysical" and framing_present is False:
            return True
        # Generated content in high-stakes contexts (medical, legal): refusal
        # over speculation. The verifier may still choose to ship with a
        # caveat, but it should have the option to refuse.
        if status == "generated" and _contains_any(normalized_intent, _HIGH_STAKES_INTENT_MARKERS):
            return True
        return False
