"""GSERegistry — load and query the element catalogue."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from .element import ClusterType, GSEElement, RoleType

__ts_layer__ = "governance"

_DEFAULT_CLUSTERS_DIR = Path(__file__).resolve().parent / "clusters"


class GSERegistry:
    """In-memory registry of GSE elements loaded from JSON cluster files."""

    def __init__(self, clusters_dir: Optional[Path] = None) -> None:
        self._dir = clusters_dir or _DEFAULT_CLUSTERS_DIR
        self._elements: Dict[str, GSEElement] = {}

    def load(self) -> "GSERegistry":
        """Load all *.json files from the clusters directory."""
        self._elements = {}
        if not self._dir.exists():
            return self
        for path in sorted(self._dir.glob("*.json")):
            self._load_file(path)
        return self

    def _load_file(self, path: Path) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("elements", []):
            el = GSEElement.from_dict(item)
            self._elements[el.symbol] = el

    # ------------------------------------------------------------------
    # Query interface
    # ------------------------------------------------------------------

    def get(self, symbol: str) -> Optional[GSEElement]:
        return self._elements.get(symbol)

    def all(self) -> Iterable[GSEElement]:
        return self._elements.values()

    def by_cluster(self, cluster: ClusterType) -> List[GSEElement]:
        return [e for e in self._elements.values() if e.cluster == cluster]

    def by_role(self, role: RoleType) -> List[GSEElement]:
        return [e for e in self._elements.values() if e.role == role]

    def symbols(self) -> List[str]:
        return sorted(self._elements.keys())

    def __len__(self) -> int:
        return len(self._elements)
