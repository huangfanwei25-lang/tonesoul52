import json
from typing import Dict, List, Tuple

from .schema import (
    AuditLog,
    MathCoords,
    Node,
    NodeAudit,
    NodeDrift,
    NodeScalar,
    NodeWhat,
    SourceRef,
    UpdateGate,
    UpdateRecord,
    Where,
    WhereField,
    WhereTask,
    WhereTime,
    as_clean_dict,
    utc_now,
)


def _to_float(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_optional_float(value):
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_optional_str(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def node_from_dict(data: Dict[str, object]) -> Node:
    source_data = data.get("source", {}) if isinstance(data.get("source"), dict) else {}
    where_data = data.get("where", {}) if isinstance(data.get("where"), dict) else {}
    where_time_data = (
        where_data.get("where_time", {}) if isinstance(where_data.get("where_time"), dict) else {}
    )
    where_field_data = (
        where_data.get("where_field", {}) if isinstance(where_data.get("where_field"), dict) else {}
    )
    where_task_data = (
        where_data.get("where_task", {}) if isinstance(where_data.get("where_task"), dict) else {}
    )
    what_data = data.get("what", {}) if isinstance(data.get("what"), dict) else {}
    scalar_data = data.get("scalar", {}) if isinstance(data.get("scalar"), dict) else {}
    drift_data = data.get("drift", {}) if isinstance(data.get("drift"), dict) else {}
    audit_data = data.get("audit", {}) if isinstance(data.get("audit"), dict) else {}
    patch_history = data.get("patch_history", [])
    if not isinstance(patch_history, list):
        patch_history = []
    patch_history = [str(item) for item in patch_history if item is not None]
    source_grade = _to_optional_str(data.get("source_grade"))
    if source_grade is None:
        source_grade = _to_optional_str(source_data.get("grade"))
    math_coords = None
    math_coords_data = data.get("math_coords")
    if isinstance(math_coords_data, dict):
        height = _to_optional_float(math_coords_data.get("height"))
        geology = _to_optional_str(math_coords_data.get("geology"))
        ruggedness = _to_optional_float(math_coords_data.get("ruggedness"))
        if height is not None or geology is not None or ruggedness is not None:
            math_coords = MathCoords(
                height=height,
                geology=geology,
                ruggedness=ruggedness,
            )

    return Node(
        id=str(data.get("id", "")),
        text=str(data.get("text", "")),
        source=SourceRef(
            type=str(source_data.get("type", "unknown")),
            uri=source_data.get("uri"),
            hash=source_data.get("hash"),
            grade=source_grade,
            retrieved_at=source_data.get("retrieved_at"),
            verified_by=source_data.get("verified_by"),
        ),
        where=Where(
            where_time=WhereTime(
                turn_id=int(where_time_data.get("turn_id", 0)),
                event_index=int(where_time_data.get("event_index", 0)),
                timestamp=where_time_data.get("timestamp"),
                version_id=where_time_data.get("version_id"),
            ),
            where_field=WhereField(
                mode=str(where_field_data.get("mode", "")),
                submode=where_field_data.get("submode"),
                confidence=_to_float(where_field_data.get("confidence", 0.0)),
            ),
            where_task=WhereTask(
                domain=str(where_task_data.get("domain", "")),
                subdomain=where_task_data.get("subdomain"),
                confidence=_to_float(where_task_data.get("confidence", 0.0)),
            ),
        ),
        what=NodeWhat(
            v_sem=[_to_float(value) for value in what_data.get("v_sem", [])],
            mu=_to_float(what_data.get("mu", 0.0)),
        ),
        scalar=NodeScalar(
            E_energy=_to_optional_float(scalar_data.get("E_energy")),
            E_srsp=_to_optional_float(scalar_data.get("E_srsp")),
            E_risk=_to_optional_float(scalar_data.get("E_risk")),
            E_total=_to_float(scalar_data.get("E_total", 0.0)),
        ),
        drift=NodeDrift(
            delta_v=drift_data.get("delta_v"),
            delta_norm=_to_optional_float(drift_data.get("delta_norm")),
            drift_ref=drift_data.get("drift_ref"),
        ),
        audit=NodeAudit(
            created_at=str(audit_data.get("created_at", "")),
            created_by=str(audit_data.get("created_by", "")),
            updates=list(audit_data.get("updates", [])),
        ),
        source_grade=source_grade,
        math_coords=math_coords,
        patch_history=patch_history,
    )


def update_record_from_dict(data: Dict[str, object]) -> UpdateRecord:
    gate_data = data.get("gate", {}) if isinstance(data.get("gate"), dict) else {}
    return UpdateRecord(
        id=str(data.get("id", "")),
        target=str(data.get("target", "")),
        change_type=str(data.get("change_type", "")),
        before=data.get("before"),
        after=data.get("after"),
        rationale=str(data.get("rationale", "")),
        gate=UpdateGate(
            passed=bool(gate_data.get("passed", False)),
            rule_ids=list(gate_data.get("rule_ids", [])),
            reviewer=gate_data.get("reviewer"),
            score=gate_data.get("score"),
        ),
        timestamp=str(data.get("timestamp", "")),
        reversible=bool(data.get("reversible", False)),
        vetoable=bool(data.get("vetoable", False)),
    )


def load_nodes_payload(path: str) -> Tuple[List[Node], Dict[str, object]]:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    nodes_data = payload.get("nodes", [])
    nodes = [node_from_dict(item) for item in nodes_data]
    metadata = {key: value for key, value in payload.items() if key != "nodes"}
    return nodes, metadata


def save_nodes_payload(path: str, nodes: List[Node], metadata: Dict[str, object]) -> None:
    payload = dict(metadata)
    payload["generated_at"] = utc_now()
    payload["nodes"] = [as_clean_dict(node) for node in nodes]
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def load_audit_log(path: str) -> AuditLog:
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    updates = [update_record_from_dict(item) for item in payload.get("updates", [])]
    generated_at = payload.get("generated_at", utc_now())
    return AuditLog(generated_at=generated_at, updates=updates)


def save_audit_log(path: str, audit_log: AuditLog) -> None:
    audit_log = AuditLog(generated_at=utc_now(), updates=audit_log.updates)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(as_clean_dict(audit_log), handle, indent=2)
