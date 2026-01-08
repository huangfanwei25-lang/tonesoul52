import re
from typing import Dict, Sequence

from .schema import AuditLog, UpdateGate, UpdateRecord, utc_now


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return slug or "visual"


def build_audit_log(
    e_def: Dict[str, object],
    visual_params: Sequence[Dict[str, object]],
    node_updates: Sequence[UpdateRecord] = (),
) -> AuditLog:
    timestamp = utc_now()
    updates = [
        UpdateRecord(
            id="update_e_def",
            target="system",
            change_type="E_DEF_UPDATE",
            before=None,
            after=e_def,
            rationale="E_total definition captured for replay (v0.1 demo).",
            gate=UpdateGate(passed=True, rule_ids=["R1", "R3"]),
            timestamp=timestamp,
            reversible=True,
            vetoable=True,
        ),
    ]
    for params in visual_params:
        plane = str(params.get("plane", "visual"))
        updates.append(
            UpdateRecord(
                id=f"update_visual_params_{_slug(plane)}",
                target="visualization",
                change_type="VISUAL_PARAM_UPDATE",
                before=None,
                after=params,
                rationale="Terrain interpolation parameters captured for replay.",
                gate=UpdateGate(passed=True, rule_ids=["R2", "R3"]),
                timestamp=timestamp,
                reversible=True,
                vetoable=True,
            )
        )
    if node_updates:
        existing = {record.id for record in updates}
        for record in node_updates:
            if record.id in existing:
                continue
            updates.append(record)
            existing.add(record.id)
    return AuditLog(generated_at=timestamp, updates=updates)
