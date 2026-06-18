"""Unsourced-confidence marker (Tier 5 advisory, record-only).

This marker flags one narrow structural pattern:

    generated epistemic status + confident wording + no source coordinates

It does not judge truth, intent, calibration, or moral correctness. It is a
small "confident without coordinates" marker intended for characterization and
future record-only wiring, not enforcement.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Optional

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Unsourced-confidence marker: advisory-only signal for generated, confident "
    "drafts without provenance coordinates."
)

DEFAULT_CONFIDENCE_THRESHOLD = 0.75

CONFIDENCE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bdefinitely\b", re.IGNORECASE),
    re.compile(r"\bcertainly\b", re.IGNORECASE),
    re.compile(r"\bclearly\b", re.IGNORECASE),
    re.compile(r"\bobviously\b", re.IGNORECASE),
    re.compile(r"\bundeniably\b", re.IGNORECASE),
    re.compile(r"\bwithout question\b", re.IGNORECASE),
    re.compile(r"\bno doubt\b", re.IGNORECASE),
    re.compile(r"\bguaranteed\b", re.IGNORECASE),
    re.compile(r"\bthe only (?:correct|right|responsible) (?:answer|choice|path)\b", re.IGNORECASE),
    re.compile(r"\bthe (?:correct|right) answer is\b", re.IGNORECASE),
    re.compile(r"\bmust be\b", re.IGNORECASE),
)

PROVENANCE_CONTEXT_KEYS = (
    "evidence_refs",
    "retrieval_hits",
    "tool_calls",
    "evidence_sources",
    "rag_results",
    "citations",
)


@dataclass(frozen=True)
class UnsourcedConfidenceSignal:
    """Advisory signal; ``flagged`` is a structural marker, not a verdict."""

    status: str = "ok"  # "ok" | "error"
    flagged: bool = False
    generated_without_source: bool = False
    confidence_marker_present: bool = False
    coordinate_count: int = 0
    evidence_chain_entry_count: int = 0
    grounded_vote_count: int = 0
    max_vote_confidence: float = 0.0
    threshold: float = DEFAULT_CONFIDENCE_THRESHOLD
    reason_codes: tuple[str, ...] = field(default_factory=tuple)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "flagged": self.flagged,
            "generated_without_source": self.generated_without_source,
            "confidence_marker_present": self.confidence_marker_present,
            "coordinate_count": self.coordinate_count,
            "evidence_chain_entry_count": self.evidence_chain_entry_count,
            "grounded_vote_count": self.grounded_vote_count,
            "max_vote_confidence": round(self.max_vote_confidence, 4),
            "threshold": self.threshold,
            "reason_codes": list(self.reason_codes),
            "advisory_only": True,
            "record_only": True,
            "note": self.note,
        }


def _status_value(value: Any) -> str:
    return getattr(value, "value", str(value))


def _iter_context_refs(context: Optional[Mapping[str, Any]]) -> Iterable[str]:
    if not context:
        return ()
    refs: list[str] = []
    for key in PROVENANCE_CONTEXT_KEYS:
        value = context.get(key)
        if not value:
            continue
        if isinstance(value, str):
            refs.append(value)
        elif isinstance(value, Mapping):
            refs.append(str(value.get("id") or value.get("ref") or value))
        elif isinstance(value, Iterable):
            for item in value:
                if isinstance(item, str):
                    refs.append(item)
                elif isinstance(item, Mapping):
                    refs.append(str(item.get("id") or item.get("ref") or item))
                else:
                    refs.append(str(item))
        else:
            refs.append(str(value))
    return refs


def _has_confidence_marker(text: str) -> bool:
    return any(pattern.search(text or "") for pattern in CONFIDENCE_PATTERNS)


class UnsourcedConfidenceMarker:
    """Record-only marker for confident generated text without source coordinates."""

    def __init__(self, confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD) -> None:
        self.confidence_threshold = confidence_threshold

    def assess(
        self,
        draft_output: str,
        verdict: Any,
        *,
        context: Optional[Mapping[str, Any]] = None,
    ) -> UnsourcedConfidenceSignal:
        """Return a structural advisory signal.

        The method is fail-soft: malformed verdicts produce ``status="error"``
        with ``flagged=False`` instead of raising into the caller.
        """
        try:
            epistemic_label = getattr(verdict, "epistemic_label", None)
            label_status = getattr(epistemic_label, "status", None)
            label_evidence_refs = list(getattr(epistemic_label, "evidence_refs", []) or [])
            votes = list(getattr(verdict, "votes", []) or [])

            vote_evidence_count = 0
            evidence_chain_entry_count = 0
            grounded_vote_count = 0
            confidences: list[float] = []
            for vote in votes:
                vote_evidence_count += len(getattr(vote, "evidence", None) or [])
                evidence_chain_entry_count += len(getattr(vote, "evidence_chain", None) or [])
                grounding_status = _status_value(getattr(vote, "grounding_status", ""))
                if grounding_status in {"grounded", "partial"}:
                    grounded_vote_count += 1
                try:
                    confidences.append(float(getattr(vote, "confidence", 0.0)))
                except (TypeError, ValueError):
                    confidences.append(0.0)

            context_refs = list(_iter_context_refs(context))
            coordinate_count = (
                len(label_evidence_refs)
                + len(context_refs)
                + vote_evidence_count
                + grounded_vote_count
            )
            max_vote_confidence = max(confidences, default=0.0)
            confidence_marker_present = _has_confidence_marker(draft_output)
            generated_without_source = label_status == "generated" and coordinate_count == 0

            reason_codes: list[str] = []
            if generated_without_source:
                reason_codes.append("generated_without_source")
            if confidence_marker_present:
                reason_codes.append("confidence_marker_present")
            if coordinate_count == 0:
                reason_codes.append("no_source_coordinates")
            if max_vote_confidence >= self.confidence_threshold:
                reason_codes.append("high_vote_confidence_observed")

            flagged = generated_without_source and confidence_marker_present
            note = (
                "structural marker only; does not judge truth, intent, or calibration"
                if flagged
                else "conditions not all present"
            )
            return UnsourcedConfidenceSignal(
                status="ok",
                flagged=flagged,
                generated_without_source=generated_without_source,
                confidence_marker_present=confidence_marker_present,
                coordinate_count=coordinate_count,
                evidence_chain_entry_count=evidence_chain_entry_count,
                grounded_vote_count=grounded_vote_count,
                max_vote_confidence=max_vote_confidence,
                threshold=self.confidence_threshold,
                reason_codes=tuple(reason_codes),
                note=note,
            )
        except Exception as exc:
            return UnsourcedConfidenceSignal(
                status="error",
                threshold=self.confidence_threshold,
                reason_codes=("marker_error",),
                note=f"marker error (degraded): {type(exc).__name__}",
            )
