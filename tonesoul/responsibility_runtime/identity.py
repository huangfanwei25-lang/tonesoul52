"""Stable request identity helpers for responsibility-runtime intents."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

__ts_layer__ = "governance"
__ts_purpose__ = "Stable responsibility-runtime request identity helpers."


def request_id_for_intent(intent_payload: Mapping[str, Any] | None) -> str:
    """Return a stable request id for a normalized intent payload."""

    canonical = json.dumps(
        intent_payload or {},
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
    return f"rr-{digest}"
