"""Principle Invocation Gate v0 — advisory, shadow-only (2026-07-05).

Provenance: Gap 8 of the 2026-05-14 gaps catalog (stranded on the PR #71
branch), the 2026-05-10 case law "axiom conflict used as an excuse not to
decide is an anti-pattern — Filing-with-annotation beats Not-filing", and
work order docs/plans/convergence_harvest_work_orders_2026-07-05.md WO-3.
Until now that lesson lived only in agent memory; this makes it a
measurable council signal.

Rule v0 (deliberately dumb-and-readable; deterministic, no LLM, no I/O):
a non-APPROVE verdict whose summary / stance / divergence text cites an
axiom, with no ``filed_with_annotation`` marker in the transcript, gets
``flagged=True``. The marker is the sanctioned escape hatch: filing a
decision WITH an annotated tension is exactly what the case law asks for,
so marked verdicts are never flagged.

ADVISORY ONLY (DESIGN Inv3): a RECORDED signal, never a gate — nothing
here modifies the verdict. When the advisory flag is on, the assessment is
attached to EVERY verdict (flagged or not) because measuring a false-positive
rate needs denominators. Enforce (if ever) is a separate owner-gated
decision after shadow-mode rates are on the table. What counts as "using an
axiom to dodge a decision" is ultimately the owner's judgment call — this
v0 regex is a floor for measurement, not that judgment.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Advisory detector: axiom cited as deferral reason without filed-with-annotation marker."
)

RULE_VERSION = "principle_invocation_v0"

# Adjudication 2026-07-05 (honest-judgment D1 follow-up 1): the v0 pattern
# matches axiom MENTIONS, not only axiom-cited-as-reason — probe drafts that
# merely discuss an axiom flag too. Rates from this record are NOT citable
# until the pattern is refined; the caveat rides in every record so no
# downstream consumer can miss it.
V0_CAVEAT = "v0 matches mentions, not only invocations-as-reason; rates not citable until refined"

FILED_MARKER_KEY = "filed_with_annotation"

# Specific on purpose: numbered-axiom citations and the Chinese canon term.
# A bare English "axiom" is NOT matched — too generic, and v0 noise should
# come from real citations, not vocabulary accidents.
_AXIOM_PATTERN = re.compile(r"(?i)\baxioms?\s*#?\s*[1-8]\b|公理")

_NON_APPROVE = {"refine", "declare_stance", "block"}


@dataclass
class PrincipleInvocationAssessment:
    flagged: bool
    verdict_type: str
    axiom_refs: List[str] = field(default_factory=list)
    filed_with_annotation: bool = False
    rule_version: str = RULE_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_version": self.rule_version,
            "flagged": self.flagged,
            "verdict_type": self.verdict_type,
            "axiom_refs": list(self.axiom_refs),
            "filed_with_annotation": self.filed_with_annotation,
            "caveat": V0_CAVEAT,
        }


class PrincipleInvocationSensor:
    """Deterministic — no LLM, no network, no I/O (EpistemicLabeler contract)."""

    def assess(self, verdict: object) -> PrincipleInvocationAssessment:
        verdict_type = self._verdict_type(verdict)
        axiom_refs = self._find_axiom_refs(verdict)
        filed = self._filed_with_annotation(verdict)
        flagged = bool(axiom_refs) and verdict_type in _NON_APPROVE and not filed
        return PrincipleInvocationAssessment(
            flagged=flagged,
            verdict_type=verdict_type,
            axiom_refs=axiom_refs,
            filed_with_annotation=filed,
        )

    @staticmethod
    def _verdict_type(verdict: object) -> str:
        raw = getattr(verdict, "verdict", None)
        value = getattr(raw, "value", None)
        if isinstance(value, str):
            return value
        return str(raw) if raw is not None else "unknown"

    @staticmethod
    def _find_axiom_refs(verdict: object) -> List[str]:
        texts: List[str] = []
        for attr in ("summary", "stance_declaration"):
            value = getattr(verdict, attr, None)
            if isinstance(value, str) and value:
                texts.append(value)
        divergence = getattr(verdict, "divergence_analysis", None)
        if isinstance(divergence, dict) and divergence:
            try:
                texts.append(json.dumps(divergence, ensure_ascii=False))
            except (TypeError, ValueError):
                pass
        refs: List[str] = []
        for text in texts:
            refs.extend(match.group(0) for match in _AXIOM_PATTERN.finditer(text))
        # De-duplicate, preserve first-seen order (readable in the record).
        seen: set = set()
        unique: List[str] = []
        for ref in refs:
            if ref not in seen:
                seen.add(ref)
                unique.append(ref)
        return unique

    @staticmethod
    def _filed_with_annotation(verdict: object) -> bool:
        transcript = getattr(verdict, "transcript", None)
        if isinstance(transcript, dict):
            return bool(transcript.get(FILED_MARKER_KEY))
        return False


def attach_principle_invocation(verdict: object, sensor: Optional[PrincipleInvocationSensor]):
    """Attach the advisory assessment to ``verdict.principle_invocation``.

    Never modifies the verdict decision. Returns the assessment (or None when
    no sensor is configured) so callers/tests can read it directly.
    """
    if sensor is None:
        return None
    assessment = sensor.assess(verdict)
    verdict.principle_invocation = assessment.to_dict()
    return assessment
