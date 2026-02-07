from __future__ import annotations

from typing import Any, Mapping

from tonesoul.council import CouncilRequest, CouncilRuntime

SKILL_NAME = "council_deliberate"
SKILL_VERSION = "1.0.0"


def run(payload: Mapping[str, Any]) -> dict[str, Any]:
    draft_output = str(payload.get("draft_output", "")).strip()
    if not draft_output:
        return {
            "ok": False,
            "error": "draft_output is required",
            "skill": SKILL_NAME,
        }

    context = payload.get("context")
    if not isinstance(context, dict):
        context = {}
    user_intent_raw = payload.get("user_intent")
    user_intent = None if user_intent_raw is None else str(user_intent_raw)

    request = CouncilRequest(
        draft_output=draft_output,
        context=context,
        user_intent=user_intent,
    )
    verdict = CouncilRuntime().deliberate(request)
    return {
        "ok": True,
        "skill": SKILL_NAME,
        "result": verdict.to_dict(),
    }
