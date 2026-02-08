import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from tonesoul.council.runtime import CouncilRequest, CouncilRuntime

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER_PATH = os.path.join(WORKSPACE_ROOT, "memory", "provenance_ledger.jsonl")


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _compute_hash(payload: Dict[str, object]) -> str:
    sanitized = {key: value for key, value in payload.items() if key != "hash"}
    encoded = json.dumps(
        sanitized,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _read_last_hash(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    last_hash = None
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            payload = record.get("payload") if isinstance(record, dict) else None
            if not isinstance(payload, dict):
                payload = record if isinstance(record, dict) else None
            if not isinstance(payload, dict):
                continue
            hash_value = payload.get("hash")
            if not hash_value:
                hash_value = _compute_hash(payload)
            last_hash = hash_value
    return last_hash


def _attach_hash_chain(event: Dict[str, object], ledger_path: str) -> Dict[str, object]:
    payload = dict(event)
    payload["prev_hash"] = _read_last_hash(ledger_path)
    payload["hash"] = _compute_hash(payload)
    return payload


def build_event(
    question: str,
    context: Optional[Dict[str, object]] = None,
    user_intent: Optional[str] = None,
) -> Dict[str, object]:
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


def append_event(event: Dict[str, object]) -> str:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    payload = _attach_hash_chain(event, LEDGER_PATH)
    with open(LEDGER_PATH, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return LEDGER_PATH


def main() -> int:
    event = build_event("Should we unify all persona libraries?")
    ledger_path = append_event(event)
    print(f"Appended to ledger: {ledger_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
