import json
import os
from typing import Dict

from ..persona_ledger_validator import validate_event


def load_latest_event(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    if not lines:
        return {}
    return json.loads(lines[-1])


def main() -> int:
    from ..config import WORKSPACE_ROOT

    ledger_path = None
    for candidate in (
        "ledger.jsonl",
        "body/ledger/ledger.jsonl",
    ):
        full = os.path.join(WORKSPACE_ROOT, candidate)
        if os.path.exists(full):
            ledger_path = full
            break

    if not ledger_path:
        print("No ledger.jsonl found.")
        return 1

    event = load_latest_event(ledger_path)
    if not event:
        print("Ledger is empty.")
        return 1

    if event.get("event_type") != "persona_council":
        print("Latest event is not persona_council.")
        return 1

    result = validate_event(event)
    print(json.dumps(result, indent=2))
    return 0 if result["coverage"] == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
