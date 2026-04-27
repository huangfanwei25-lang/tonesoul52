"""tonesoul.gse.strategy_mirror — self-observation layer for compositional moves.

Where governance/ enforces hard runtime rules, strategy_mirror watches
the AI's own draft for rhetorical/strategic moves and surfaces them as a
StrategySignature that travels with the verdict. The mirror catches
what the AI did to the listener; it does not gate truth claims.

See docs/gse/phase_2_strategy_mirror_spec.md for the full design.

This is the L_meta self-observation sub-layer. Per spec §3:
  - governance/ holds 12 hard runtime triggers (Phase 1)
  - strategy_mirror/ holds ~700 detection-only moves (Phase 2+)
  - both live under tonesoul/gse/ but answer different questions
"""

from .catalog_loader import CatalogLoader
from .strategy import (
    DetectedMove,
    StrategyMove,
    StrategySignature,
    TransparencyClass,
)

__all__ = [
    "StrategyMove",
    "DetectedMove",
    "StrategySignature",
    "TransparencyClass",
    "CatalogLoader",
]
__ts_layer__ = "governance"
__ts_purpose__ = (
    "Strategy mirror: self-observation surface for AI's compositional moves. "
    "Phase 2 of GSE; reads detoxified PSE catalog with three-color transparency classification."
)
