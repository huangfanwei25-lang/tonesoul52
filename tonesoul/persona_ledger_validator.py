import json
from typing import Dict

REQUIRED_FIELDS = [
    "event_type",
    "trace_id",
    "timestamp",
    "persona.active",
    "council.perspectives",
    "council.integration",
]


def _get_nested(data: Dict[str, object], key: str):
    parts = key.split(".")
    current = data
    for part in parts:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


def validate_event(event: Dict[str, object]) -> Dict[str, object]:
    missing = [field for field in REQUIRED_FIELDS if _get_nested(event, field) in (None, "")]
    coverage = 1.0 - (len(missing) / len(REQUIRED_FIELDS))
    return {"missing": missing, "coverage": coverage}


def main() -> int:
    sample = {
        "event_type": "persona_council",
        "trace_id": "sample",
        "timestamp": "2025-12-24T00:00:00Z",
        "persona": {"active": "Core"},
        "council": {"perspectives": {"Spark": "..."}, "integration": "..."},
    }
    result = validate_event(sample)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
