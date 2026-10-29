"""Optional offline evidence sidecar; never replaces baseline findings."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .argument_review import integrate

__ts_layer__ = "surface"
__ts_purpose__ = "Optional evidence sidecar for advisory ts review reports."


def review_shadow(text: str, baseline: dict, sidecar_path: Path) -> dict:
    data = json.loads(sidecar_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("evidence sidecar must be an object")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if data.get("document_sha256") != digest:
        raise ValueError("evidence sidecar document hash mismatch; reassess before use")
    if not isinstance(data.get("case"), dict) or not isinstance(data.get("arguments"), dict):
        raise ValueError("sidecar requires case and arguments objects")
    evidence = integrate(data["case"], data["arguments"], sidecar_path.parent)
    return {"mode": "advisory_only", "baseline": baseline, "evidence": evidence}
