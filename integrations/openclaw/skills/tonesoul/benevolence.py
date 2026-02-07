from __future__ import annotations

from typing import Any, Mapping

from tonesoul.benevolence import AuditLayer, filter_benevolence

SKILL_NAME = "benevolence_audit"
SKILL_VERSION = "1.0.0"


def run(payload: Mapping[str, Any]) -> dict[str, Any]:
    proposed_action = str(payload.get("proposed_action", "")).strip()
    if not proposed_action:
        return {
            "ok": False,
            "error": "proposed_action is required",
            "skill": SKILL_NAME,
        }

    context_fragments_raw = payload.get("context_fragments")
    context_fragments = (
        [str(item) for item in context_fragments_raw]
        if isinstance(context_fragments_raw, list)
        else []
    )

    layer_value = str(payload.get("current_layer", "L2")).strip().upper()
    current_layer = AuditLayer.__members__.get(layer_value, AuditLayer.L2)
    audit = filter_benevolence(
        proposed_action=proposed_action,
        context_fragments=context_fragments,
        action_basis=str(payload.get("action_basis", "Inference")),
        current_layer=current_layer,
        genesis_id=payload.get("genesis_id"),
        semantic_tension=payload.get("semantic_tension"),
        user_protocol=str(payload.get("user_protocol", "Honesty > Helpfulness")),
        shadow_threshold=float(payload.get("shadow_threshold", 0.3)),
        language=str(payload.get("language", "auto")),
    )
    return {
        "ok": True,
        "skill": SKILL_NAME,
        "result": audit.to_dict(),
    }
