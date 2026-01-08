import json
import os
from typing import Dict

from .council_adapter import run_council


WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LEDGER_PATHS = [
    os.path.join(WORKSPACE_ROOT, "ledger.jsonl"),
    os.path.join(WORKSPACE_ROOT, "body", "ledger", "ledger.jsonl"),
]


def append_event(event: Dict[str, object]) -> str:
    target = None
    for path in LEDGER_PATHS:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path):
            target = path
            break
    if target is None:
        target = LEDGER_PATHS[-1]

    with open(target, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return target


def main() -> int:
    event = run_council("Should we unify all persona libraries?")
    ledger_path = append_event(event)
    print(f"Appended to ledger: {ledger_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
