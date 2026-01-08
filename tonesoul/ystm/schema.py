import hashlib
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class WhereTime:
    turn_id: int
    event_index: int
    timestamp: Optional[str] = None
    version_id: Optional[str] = None


@dataclass
class WhereField:
    mode: str
    submode: Optional[str]
    confidence: float


@dataclass
class WhereTask:
    domain: str
    subdomain: Optional[str]
    confidence: float


@dataclass
class Where:
    where_time: WhereTime
    where_field: WhereField
    where_task: WhereTask


@dataclass
class SourceRef:
    type: str
    uri: Optional[str] = None
    hash: Optional[str] = None
    # Tech-Trace extensions
    grade: Optional[str] = None  # "A" | "B" | "C" source grade
    retrieved_at: Optional[str] = None  # When the source was retrieved
    verified_by: Optional[str] = None  # Who verified the source


@dataclass
class NodeWhat:
    v_sem: List[float]
    mu: float


@dataclass
class NodeScalar:
    E_energy: Optional[float]
    E_srsp: Optional[float]
    E_risk: Optional[float]
    E_total: float


@dataclass
class NodeDrift:
    delta_v: Optional[List[float]] = None
    delta_norm: Optional[float] = None
    drift_ref: Optional[Dict[str, str]] = None


@dataclass
class NodeAudit:
    created_at: str
    created_by: str
    updates: List[str]


@dataclass
class MathCoords:
    height: Optional[float] = None
    geology: Optional[str] = None
    ruggedness: Optional[float] = None


@dataclass
class Node:
    id: str
    text: str
    source: SourceRef
    where: Where
    what: NodeWhat
    scalar: NodeScalar
    drift: NodeDrift
    audit: NodeAudit
    source_grade: Optional[str] = None
    math_coords: Optional[MathCoords] = None
    patch_history: List[str] = field(default_factory=list)


@dataclass
class UpdateGate:
    passed: bool
    rule_ids: List[str]
    reviewer: Optional[str] = None
    score: Optional[float] = None


@dataclass
class UpdateRecord:
    id: str
    target: str
    change_type: str
    before: Optional[Dict[str, object]]
    after: Optional[Dict[str, object]]
    rationale: str
    gate: UpdateGate
    timestamp: str
    reversible: bool
    vetoable: bool


@dataclass
class AuditLog:
    generated_at: str
    updates: List[UpdateRecord]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def stable_hash(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest[:12]


def round_floats(value: object, digits: int = 6) -> object:
    if isinstance(value, float):
        return round(value, digits)
    if isinstance(value, list):
        return [round_floats(item, digits) for item in value]
    if isinstance(value, dict):
        return {key: round_floats(val, digits) for key, val in value.items()}
    return value


def prune_none(value: object) -> object:
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            pruned = prune_none(item)
            if pruned is not None:
                cleaned[key] = pruned
        return cleaned
    if isinstance(value, list):
        return [prune_none(item) for item in value]
    return value


def as_clean_dict(value: object, digits: int = 6) -> object:
    if hasattr(value, "__dataclass_fields__"):
        value = asdict(value)
    return round_floats(prune_none(value), digits)
