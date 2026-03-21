from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import ClassVar, Dict, FrozenSet, Mapping


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp_unit(value: object) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(1.0, numeric))


def _normalize_signals(signals: Mapping[str, object] | None) -> Dict[str, float]:
    normalized: Dict[str, float] = {}
    if not isinstance(signals, Mapping):
        return normalized
    for key, value in signals.items():
        if isinstance(value, bool):
            normalized[str(key)] = float(value)
            continue
        try:
            normalized[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return normalized


@dataclass
class TensionPacket:
    """
    Signed tension snapshot shared across souls.

    The packet is intentionally compact and signed so a soul can preserve
    tension as memory sediment instead of exchanging unverifiable drift.
    """

    soul_id: str
    timestamp: str = field(default_factory=_utcnow_iso)
    total: float = 0.0
    zone: str = "safe"
    lambda_state: str = "stable"
    signals: Dict[str, float] = field(default_factory=dict)
    signature: str = ""

    def __post_init__(self) -> None:
        self.soul_id = str(self.soul_id or "").strip()
        self.timestamp = str(self.timestamp or _utcnow_iso())
        self.total = _clamp_unit(self.total)
        self.zone = str(self.zone or "").strip()
        self.lambda_state = str(self.lambda_state or "").strip()
        self.signals = _normalize_signals(self.signals)
        self.signature = str(self.signature or "").strip()

    def canonical_payload(self) -> Dict[str, object]:
        return {
            "soul_id": self.soul_id,
            "timestamp": self.timestamp,
            "total": self.total,
            "zone": self.zone,
            "lambda_state": self.lambda_state,
            "signals": dict(self.signals),
        }

    def to_dict(self) -> Dict[str, object]:
        payload = self.canonical_payload()
        payload["signature"] = self.signature
        return payload

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "TensionPacket":
        return cls(
            soul_id=str(payload.get("soul_id", "")).strip(),
            timestamp=str(payload.get("timestamp", "")).strip() or _utcnow_iso(),
            total=payload.get("total", 0.0),
            zone=str(payload.get("zone", "safe")).strip(),
            lambda_state=str(payload.get("lambda_state", "stable")).strip(),
            signals=_normalize_signals(
                payload.get("signals") if isinstance(payload, Mapping) else {}
            ),
            signature=str(payload.get("signature", "")).strip(),
        )

    def compute_signature(self, secret_key: str) -> str:
        canonical = json.dumps(self.canonical_payload(), sort_keys=True, ensure_ascii=False)
        return hmac.new(
            str(secret_key).encode("utf-8"),
            canonical.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def sign(self, secret_key: str) -> str:
        self.signature = self.compute_signature(secret_key)
        return self.signature

    def verify_signature(self, secret_key: str) -> bool:
        if not self.signature:
            return False
        expected = self.compute_signature(secret_key)
        return hmac.compare_digest(expected, self.signature)


@dataclass
class RuptureNotice:
    """Visible rupture signal propagated across souls without erasing conflict."""

    source_soul_id: str
    rupture_type: str
    severity: str
    context_excerpt: str
    timestamp: str = field(default_factory=_utcnow_iso)

    MAX_EXCERPT_LENGTH: ClassVar[int] = 256

    def __post_init__(self) -> None:
        self.source_soul_id = str(self.source_soul_id or "").strip()
        self.rupture_type = str(self.rupture_type or "").strip()
        self.severity = str(self.severity or "").strip()
        self.context_excerpt = str(self.context_excerpt or "").strip()[: self.MAX_EXCERPT_LENGTH]
        self.timestamp = str(self.timestamp or _utcnow_iso())

    def to_dict(self) -> Dict[str, str]:
        return {
            "source_soul_id": self.source_soul_id,
            "rupture_type": self.rupture_type,
            "severity": self.severity,
            "context_excerpt": self.context_excerpt,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "RuptureNotice":
        return cls(
            source_soul_id=str(payload.get("source_soul_id", "")).strip(),
            rupture_type=str(payload.get("rupture_type", "")).strip(),
            severity=str(payload.get("severity", "")).strip(),
            context_excerpt=str(payload.get("context_excerpt", "")).strip(),
            timestamp=str(payload.get("timestamp", "")).strip() or _utcnow_iso(),
        )


class NegotiationOutcome(str, Enum):
    ALIGNED = "aligned"
    DIVERGENT = "divergent"
    SOVEREIGN_OVERRIDE = "sovereign_override"


@dataclass(frozen=True)
class SovereigntyBoundary:
    """
    Hard boundary for a sovereign soul.

    These fields are not bargaining chips. If another packet attempts to
    rewrite them, the correct result is override, not compromise.
    """

    non_negotiable_fields: FrozenSet[str] = field(default_factory=frozenset)
    axiom_ids: FrozenSet[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "non_negotiable_fields",
            frozenset(
                str(item).strip() for item in self.non_negotiable_fields if str(item).strip()
            ),
        )
        object.__setattr__(
            self,
            "axiom_ids",
            frozenset(str(item).strip() for item in self.axiom_ids if str(item).strip()),
        )

    def to_dict(self) -> Dict[str, list[str]]:
        return {
            "non_negotiable_fields": sorted(self.non_negotiable_fields),
            "axiom_ids": sorted(self.axiom_ids),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "SovereigntyBoundary":
        fields_raw = payload.get("non_negotiable_fields", [])
        axioms_raw = payload.get("axiom_ids", [])
        fields = fields_raw if isinstance(fields_raw, (list, tuple, set, frozenset)) else []
        axioms = axioms_raw if isinstance(axioms_raw, (list, tuple, set, frozenset)) else []
        return cls(
            non_negotiable_fields=frozenset(
                str(item).strip() for item in fields if str(item).strip()
            ),
            axiom_ids=frozenset(str(item).strip() for item in axioms if str(item).strip()),
        )
