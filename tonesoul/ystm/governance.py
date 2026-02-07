from dataclasses import replace
from typing import Optional, Tuple

import numpy as np

from ..error_event import ErrorEvent, ErrorLedger
from .energy import EnergyConfig, compute_raw_total
from .representation import EmbeddingConfig, embed_text
from .schema import (
    Node,
    NodeWhat,
    UpdateGate,
    UpdateRecord,
    Where,
    as_clean_dict,
    stable_hash,
    utc_now,
)


def _append_update(node: Node, update_id: str) -> Node:
    updates = list(node.audit.updates) + [update_id]
    new_audit = replace(node.audit, updates=updates)
    return replace(node, audit=new_audit)


def validate_where_update(current: Where, proposed: Where) -> UpdateGate:
    rule_ids = []
    passed = True
    total_rules = 0
    failed_rules = 0

    total_rules += 1
    if proposed.where_time.event_index < current.where_time.event_index:
        passed = False
        failed_rules += 1
        rule_ids.append("chronos_non_decreasing_fail")
    else:
        rule_ids.append("chronos_non_decreasing")

    for label, confidence in (
        ("field_confidence", proposed.where_field.confidence),
        ("task_confidence", proposed.where_task.confidence),
    ):
        total_rules += 1
        if not 0.0 <= confidence <= 1.0:
            passed = False
            failed_rules += 1
            rule_ids.append(f"{label}_range_fail")
        else:
            rule_ids.append(f"{label}_range")

    total_rules += 1
    if not proposed.where_field.mode:
        passed = False
        failed_rules += 1
        rule_ids.append("field_mode_missing")
    else:
        rule_ids.append("field_mode_present")
    total_rules += 1
    if not proposed.where_task.domain:
        passed = False
        failed_rules += 1
        rule_ids.append("task_domain_missing")
    else:
        rule_ids.append("task_domain_present")

    score = 1.0 if total_rules == 0 else max(0.0, 1.0 - (failed_rules / total_rules))
    return UpdateGate(passed=passed, rule_ids=rule_ids, score=round(score, 3))


def update_what(
    node: Node,
    new_text: str,
    config: EmbeddingConfig,
    energy: EnergyConfig,
    rationale: str,
) -> Tuple[Node, UpdateRecord]:
    vector = embed_text(new_text, config)
    norm = float(np.linalg.norm(vector))
    e_srsp = node.scalar.E_srsp or 0.0
    e_risk = node.scalar.E_risk or 0.0
    raw_total = compute_raw_total(norm, e_srsp, e_risk, energy)
    new_scalar = replace(
        node.scalar,
        E_energy=norm,
        E_total=raw_total,
    )
    new_what = NodeWhat(v_sem=vector.tolist(), mu=norm)
    new_source = replace(node.source, hash=stable_hash(new_text))
    updated = replace(node, text=new_text, what=new_what, scalar=new_scalar, source=new_source)

    update_id = f"upd_what_{stable_hash(f'{node.id}:{utc_now()}')}"
    record = UpdateRecord(
        id=update_id,
        target=node.id,
        change_type="WHAT_UPDATE",
        before=as_clean_dict(node),
        after=as_clean_dict(updated),
        rationale=rationale,
        gate=UpdateGate(passed=True, rule_ids=["R1"], score=1.0),
        timestamp=utc_now(),
        reversible=True,
        vetoable=True,
    )
    return _append_update(updated, update_id), record


def update_where(
    node: Node,
    new_where: Where,
    rationale: str,
    reviewer: Optional[str] = None,
    error_ledger_path: Optional[str] = None,
) -> Tuple[Node, UpdateRecord]:
    gate = validate_where_update(node.where, new_where)
    if reviewer:
        gate = replace(gate, reviewer=reviewer)
    proposed = replace(node, where=new_where)
    update_id = f"upd_where_{stable_hash(f'{node.id}:{utc_now()}')}"
    record = UpdateRecord(
        id=update_id,
        target=node.id,
        change_type="WHERE_UPDATE",
        before=as_clean_dict(node),
        after=as_clean_dict(proposed),
        rationale=rationale,
        gate=gate,
        timestamp=utc_now(),
        reversible=True,
        vetoable=True,
    )
    if gate.passed:
        return _append_update(proposed, update_id), record
    error_event_id = _record_where_failure(
        node,
        new_where,
        gate,
        rationale,
        ledger_path=error_ledger_path,
    )
    if error_event_id:
        record = replace(
            record,
            rationale=f"{rationale} (error_event_id: {error_event_id})",
        )
    return _append_update(node, update_id), record


def _record_where_failure(
    node: Node,
    new_where: Where,
    gate: UpdateGate,
    rationale: str,
    ledger_path: Optional[str] = None,
) -> Optional[str]:
    try:
        context = f"WHERE_UPDATE rejected for {node.id} | rules={','.join(gate.rule_ids)}"
        event = ErrorEvent(
            behavior=f"WHERE_UPDATE rejected for {node.id}",
            context=context,
            behavior_type="where_update_reject",
            input_signal=str(as_clean_dict(new_where)),
            mode_at_time=str(node.where.where_field.mode),
            island_id=str(node.where.where_time.turn_id),
            consequence_summary=rationale,
            strategy="Revise where update to satisfy gate rules.",
            strategy_type="adjust",
            implementation_notes="Gate failed; review rule_ids and propose compliant where.",
        )
        ledger = ErrorLedger(ledger_path or "error_ledger.jsonl")
        return ledger.record(event)
    except Exception:
        return None
