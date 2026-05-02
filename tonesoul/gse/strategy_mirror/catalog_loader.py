"""CatalogLoader — load StrategyMove entries from period_*.json files.

The loader expects JSON files in tonesoul/gse/strategy_mirror/catalog/
following the schema documented in
docs/gse/phase_2_strategy_mirror_spec.md §4.1.

Phase 2 ships with period 1 (~150 elements) only; periods 2-5 land in
subsequent commits per spec §10 phased rollout.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .strategy import StrategyMove, TransparencyClass

__ts_layer__ = "governance"
__ts_purpose__ = (
    "CatalogLoader: read PSE-derived StrategyMove entries from JSON files "
    "under tonesoul/gse/strategy_mirror/catalog/."
)

_DEFAULT_CATALOG_DIR = Path(__file__).resolve().parent / "catalog"


class CatalogLoader:
    """Load and query the strategy_mirror catalog.

    Each entry is keyed by its globally unique `id` (composite of period
    + element index + symbol with disambiguator); duplicate ids on load
    raise ValueError so accidental shadowing is loud.
    """

    def __init__(self, catalog_dir: Optional[Path] = None) -> None:
        self._dir = catalog_dir or _DEFAULT_CATALOG_DIR
        self._moves: Dict[str, StrategyMove] = {}
        self._period_metadata: Dict[int, dict] = {}

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(self) -> "CatalogLoader":
        """Load all `period_*.json` files from the catalog directory."""
        self._moves = {}
        self._period_metadata = {}
        if not self._dir.exists():
            return self
        for path in sorted(self._dir.glob("period_*.json")):
            self._load_file(path)
        return self

    def _load_file(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        period = int(data.get("period", -1))
        # Capture period-level metadata for diagnostic / reporting use.
        self._period_metadata[period] = {k: v for k, v in data.items() if k not in ("elements",)}
        # Validate count if declared.
        declared = data.get("elements_count")
        actual = len(data.get("elements", []))
        if declared is not None and int(declared) != actual:
            raise ValueError(
                f"{path.name}: elements_count={declared} but actual={actual}; "
                f"catalog header out of sync with body"
            )
        for item in data.get("elements", []):
            move = StrategyMove.from_dict(item)
            self._validate_admission(move, path.name)
            if move.id in self._moves:
                raise ValueError(
                    f"{path.name}: duplicate id {move.id!r}; catalog ids must be globally unique"
                )
            self._moves[move.id] = move

    @staticmethod
    def _validate_admission(move: StrategyMove, source: str) -> None:
        """Spec §3.1 + §4.1 admission gate.

        Each entry must have a non-empty rationale (Axiom 1 — every
        classification must be accountable). Without rationale the
        entry would be a silent classification.
        """
        if not move.rationale or not move.rationale.strip():
            raise ValueError(
                f"{source}: move {move.id!r} has empty rationale; "
                f"classifications must be justified per spec §3.1 admission gate"
            )
        if move.transparency_class not in ("green", "yellow", "red"):
            raise ValueError(
                f"{source}: move {move.id!r} has unknown transparency_class "
                f"{move.transparency_class!r}; must be green/yellow/red"
            )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, move_id: str) -> Optional[StrategyMove]:
        return self._moves.get(move_id)

    def get_by_symbol(self, symbol: str) -> List[StrategyMove]:
        """Return all moves matching a PSE symbol (multiple may share due to
        PSE's symbol collisions across families — e.g. 8 entries with [Sp])."""
        return [m for m in self._moves.values() if m.symbol == symbol]

    def all(self) -> Iterable[StrategyMove]:
        return self._moves.values()

    def by_class(self, cls: TransparencyClass) -> List[StrategyMove]:
        return [m for m in self._moves.values() if m.transparency_class == cls]

    def by_period(self, period: int) -> List[StrategyMove]:
        return [m for m in self._moves.values() if m.period == period]

    def by_family(self, family: str) -> List[StrategyMove]:
        return [m for m in self._moves.values() if m.family == family]

    def ids(self) -> List[str]:
        return sorted(self._moves.keys())

    def period_metadata(self, period: int) -> Optional[dict]:
        return self._period_metadata.get(period)

    def __len__(self) -> int:
        return len(self._moves)

    def __contains__(self, move_id: str) -> bool:
        return move_id in self._moves

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def class_distribution(self) -> Dict[str, int]:
        """Quick diagnostic: how many of each class in the loaded catalog."""
        return {
            "green": len(self.by_class("green")),
            "yellow": len(self.by_class("yellow")),
            "red": len(self.by_class("red")),
        }

    def family_distribution(self) -> Dict[str, int]:
        families: Dict[str, int] = {}
        for m in self._moves.values():
            families[m.family] = families.get(m.family, 0) + 1
        return families
