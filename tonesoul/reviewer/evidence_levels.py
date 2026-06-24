"""Reviewer-facing evidence-level definitions for claim-to-evidence findings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

__ts_layer__ = "surface"
__ts_purpose__ = "Public reviewer evidence levels for claim-to-evidence audit findings."


@dataclass(frozen=True)
class EvidenceLevel:
    """A public-facing evidence level used by reviewer findings."""

    level: str
    label: str
    meaning: str

    def to_dict(self) -> Dict[str, str]:
        return {"level": self.level, "label": self.label, "meaning": self.meaning}


EVIDENCE_LEVELS: Dict[str, EvidenceLevel] = {
    "E0": EvidenceLevel(
        level="E0",
        label="demo-only",
        meaning="Visible in a Space or demo, without a stable reproduction path.",
    ),
    "E1": EvidenceLevel(
        level="E1",
        label="fixture-scoped",
        meaning="Covered by sanitized fixtures or characterization reports only.",
    ),
    "E2": EvidenceLevel(
        level="E2",
        label="reproducible local check",
        meaning="Reproducible with documented local commands.",
    ),
    "E3": EvidenceLevel(
        level="E3",
        label="external reviewer reproduced",
        meaning="Reproduced or refuted by an outside reviewer in a public issue.",
    ),
    "E4": EvidenceLevel(
        level="E4",
        label="independent replication",
        meaning="Reproduced by an independent repo, write-up, or evaluation.",
    ),
}

DEFAULT_FINDING_LEVEL = "E1"


def get_evidence_level(level: str) -> EvidenceLevel:
    """Return an evidence-level definition, raising for unknown levels."""

    try:
        return EVIDENCE_LEVELS[level]
    except KeyError as exc:
        known = ", ".join(sorted(EVIDENCE_LEVELS))
        raise ValueError(f"unknown evidence level {level!r}; expected one of: {known}") from exc
