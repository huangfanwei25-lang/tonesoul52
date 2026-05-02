"""StrategyMove + DetectedMove + StrategySignature — the data shapes
for strategy_mirror's self-observation layer.

See docs/gse/phase_2_strategy_mirror_spec.md §4 for the canonical
contract. Naming follows §3.1 (observation POV, not practitioner POV);
PSE provenance is preserved verbatim per §4.1 audit-pair rule.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Literal

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Data shapes for strategy_mirror: StrategyMove (catalog entry), "
    "DetectedMove (scan hit), StrategySignature (per-output result)."
)


TransparencyClass = Literal["green", "yellow", "red"]
"""Three-color transparency taxonomy (spec §6.1):
  green   — use freely; declaration optional.
  yellow  — use permitted; declaration mandatory (otherwise BLOCK).
  red     — manipulation flag; auto-escalate to Council.
"""


@dataclass(frozen=True)
class StrategyMove:
    """One named compositional move that may appear in a draft.

    See spec §4.1. PSE-side fields (pse_keyword, pse_chinese_name,
    pse_definition, pse_operation, period, family) are preserved
    verbatim as the provenance pair — they document where each entry
    came from without forcing ToneSoul to *speak* in PSE's voice.
    """

    # Catalog identity
    id: str  # e.g. "1.001.Ev" (globally unique)
    symbol: str  # PSE original symbol, e.g. "[Ev]"
    name: str  # ToneSoul observation-POV name
    # PSE provenance (verbatim, audit-only)
    pse_keyword: str  # PSE original functional keyword
    pse_chinese_name: str  # PSE original 中文 name
    period: int  # PSE period (1-5)
    family: str  # PSE family (e.g. "天文學")
    pse_definition: str  # PSE scientific definition (verbatim)
    pse_operation: str  # PSE operation template (verbatim)
    # ToneSoul classification
    transparency_class: TransparencyClass
    rationale: str  # one-sentence justification
    # Detection hints
    surface_signals: List[str] = field(default_factory=list)
    structural_signals: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "symbol": self.symbol,
            "name": self.name,
            "pse_keyword": self.pse_keyword,
            "pse_chinese_name": self.pse_chinese_name,
            "period": self.period,
            "family": self.family,
            "pse_definition": self.pse_definition,
            "pse_operation": self.pse_operation,
            "transparency_class": self.transparency_class,
            "rationale": self.rationale,
            "surface_signals": list(self.surface_signals),
            "structural_signals": list(self.structural_signals),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StrategyMove":
        return cls(
            id=data["id"],
            symbol=data["symbol"],
            name=data["name"],
            pse_keyword=data["pse_keyword"],
            pse_chinese_name=data["pse_chinese_name"],
            period=int(data["period"]),
            family=data["family"],
            pse_definition=data["pse_definition"],
            pse_operation=data["pse_operation"],
            transparency_class=data["transparency_class"],
            rationale=data["rationale"],
            surface_signals=list(data.get("surface_signals", [])),
            structural_signals=list(data.get("structural_signals", [])),
        )


@dataclass
class DetectedMove:
    """A scan hit: one StrategyMove found in a draft.

    See spec §4.2. `text_locations` are short excerpts (not full
    re-quoting of the draft) for traceability; `confidence` is the
    detector's certainty in [0, 1]; `declared` records whether the
    draft itself acknowledged using this move.
    """

    move: StrategyMove
    text_locations: List[str] = field(default_factory=list)
    confidence: float = 1.0
    declared: bool = False

    def to_dict(self) -> dict:
        return {
            "move_id": self.move.id,
            "move_symbol": self.move.symbol,
            "move_name": self.move.name,
            "transparency_class": self.move.transparency_class,
            "text_locations": list(self.text_locations),
            "confidence": round(float(self.confidence), 4),
            "declared": bool(self.declared),
        }


@dataclass
class StrategySignature:
    """The result of scanning one draft. Travels with the verdict.

    See spec §4.2 + §5 integration contract.
    """

    detected_moves: List[DetectedMove] = field(default_factory=list)
    summary: str = ""
    scanned_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    # ------------------------------------------------------------------
    # Class-filtered queries
    # ------------------------------------------------------------------

    def green_moves(self) -> List[DetectedMove]:
        return [d for d in self.detected_moves if d.move.transparency_class == "green"]

    def yellow_moves(self) -> List[DetectedMove]:
        return [d for d in self.detected_moves if d.move.transparency_class == "yellow"]

    def red_moves(self) -> List[DetectedMove]:
        return [d for d in self.detected_moves if d.move.transparency_class == "red"]

    def undeclared_yellow_moves(self) -> List[DetectedMove]:
        return [d for d in self.yellow_moves() if not d.declared]

    # ------------------------------------------------------------------
    # Council integration flags (spec §5.3, §5.4)
    # ------------------------------------------------------------------

    @property
    def has_red(self) -> bool:
        return bool(self.red_moves())

    @property
    def has_undeclared_yellow(self) -> bool:
        return bool(self.undeclared_yellow_moves())

    def requires_council_re_review(self) -> bool:
        """Spec §5.3: red moves auto-escalate to Council re-review."""
        return self.has_red

    def requires_block(self) -> bool:
        """Spec §5.4: undeclared yellow forces verdict downgrade to BLOCK."""
        return self.has_undeclared_yellow

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "detected_moves": [d.to_dict() for d in self.detected_moves],
            "summary": self.summary,
            "scanned_at": self.scanned_at,
            "counts": {
                "total": len(self.detected_moves),
                "green": len(self.green_moves()),
                "yellow": len(self.yellow_moves()),
                "red": len(self.red_moves()),
                "undeclared_yellow": len(self.undeclared_yellow_moves()),
            },
            "flags": {
                "has_red": self.has_red,
                "has_undeclared_yellow": self.has_undeclared_yellow,
                "requires_council_re_review": self.requires_council_re_review(),
                "requires_block": self.requires_block(),
            },
        }

    @classmethod
    def empty(cls) -> "StrategySignature":
        """Empty signature for drafts where the scanner ran but found nothing."""
        return cls(detected_moves=[], summary="No strategy moves detected.")
