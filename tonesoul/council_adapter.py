import os
import sys
import uuid
import warnings
from datetime import datetime
from typing import Dict, Optional

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)


def _iso_now() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def run_council(
    question: str,
    context: Optional[Dict[str, object]] = None,
    user_intent: Optional[str] = None,
) -> Dict[str, object]:
    warnings.warn(
        "tonesoul.council_adapter is deprecated; use tonesoul.council.runtime.CouncilRuntime",
        DeprecationWarning,
        stacklevel=2,
    )
    from tonesoul.council.runtime import CouncilRequest, CouncilRuntime

    request = CouncilRequest(
        draft_output=question,
        context=context or {},
        user_intent=user_intent,
    )
    verdict = CouncilRuntime().deliberate(request)

    return {
        "event_type": "council_verdict",
        "trace_id": str(uuid.uuid4()),
        "timestamp": _iso_now(),
        "request": {
            "draft_output": question,
            "user_intent": user_intent,
        },
        "verdict": verdict.to_dict(),
    }
