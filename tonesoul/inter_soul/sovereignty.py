from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional

from .types import SovereigntyBoundary, TensionPacket

_DEFAULT_FIELD_MAP = {
    "3": frozenset({"zone"}),
    "6": frozenset({"lambda_state"}),
}


def _flatten_mapping(payload: Mapping[str, object], prefix: str = "") -> dict[str, object]:
    flattened: dict[str, object] = {}
    for key, value in payload.items():
        current = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, Mapping):
            flattened.update(_flatten_mapping(value, current))
            continue
        flattened[current] = value
    return flattened


class SovereigntyGuard:
    """Builds and enforces sovereign boundaries from repo axioms."""

    def __init__(self, axioms_path: str = "AXIOMS.json") -> None:
        self.axioms_path = Path(axioms_path)

    def _load_axioms(self) -> list[dict[str, Any]]:
        if not self.axioms_path.exists():
            return []
        try:
            payload = json.loads(self.axioms_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        if isinstance(payload, dict):
            axioms = payload.get("axioms", [])
        elif isinstance(payload, list):
            axioms = payload
        else:
            axioms = []
        return [item for item in axioms if isinstance(item, dict)]

    def build_boundary(self) -> SovereigntyBoundary:
        non_negotiable_fields: set[str] = set()
        axiom_ids: set[str] = set()

        for axiom in self._load_axioms():
            axiom_id = str(axiom.get("id", "")).strip()
            if not axiom_id or axiom_id not in _DEFAULT_FIELD_MAP:
                continue
            priority = str(axiom.get("priority", "")).strip().upper()
            if priority and priority != "P0":
                continue
            axiom_ids.add(axiom_id)
            non_negotiable_fields.update(_DEFAULT_FIELD_MAP[axiom_id])

        return SovereigntyBoundary(
            non_negotiable_fields=frozenset(non_negotiable_fields),
            axiom_ids=frozenset(axiom_ids),
        )

    def check_violation(
        self, remote_packet_or_fields: TensionPacket | Mapping[str, object]
    ) -> Optional[str]:
        if isinstance(remote_packet_or_fields, TensionPacket):
            payload: Mapping[str, object] = remote_packet_or_fields.to_dict()
        elif isinstance(remote_packet_or_fields, Mapping):
            payload = remote_packet_or_fields
        else:
            return None

        flattened = _flatten_mapping(payload)
        boundary = self.build_boundary()
        for field in sorted(boundary.non_negotiable_fields):
            if field in flattened:
                return field
        return None
