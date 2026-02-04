import argparse
import json
import os
from typing import Dict, List, Optional


def load_jsonl(path: Optional[str]) -> List[Dict[str, object]]:
    if not path or not os.path.exists(path):
        return []
    entries: List[Dict[str, object]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                entries.append(payload)
    return entries


def _mean(values: List[float]) -> Optional[float]:
    if not values:
        return None
    return sum(values) / len(values)


def _persona_counts(entries: List[Dict[str, object]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for entry in entries:
        persona_id = entry.get("persona_id") or "base"
        counts[persona_id] = counts.get(persona_id, 0) + 1
    return counts


def _trace_stats(entries: List[Dict[str, object]]) -> Dict[str, object]:
    changed_values: List[bool] = []
    delta_lengths: List[int] = []
    mean_distances: List[float] = []
    max_distances: List[float] = []

    for entry in entries:
        diff = entry.get("diff") if isinstance(entry.get("diff"), dict) else {}
        if isinstance(diff.get("changed"), bool):
            changed_values.append(diff["changed"])
        delta_len = diff.get("delta_len")
        if isinstance(delta_len, int):
            delta_lengths.append(delta_len)

        shadow = entry.get("shadow") if isinstance(entry.get("shadow"), dict) else {}
        distance = (
            shadow.get("vector_distance") if isinstance(shadow.get("vector_distance"), dict) else {}
        )
        mean_value = distance.get("mean")
        max_value = distance.get("max")
        if isinstance(mean_value, (int, float)):
            mean_distances.append(float(mean_value))
        if isinstance(max_value, (int, float)):
            max_distances.append(float(max_value))

    changed_ratio = None
    if changed_values:
        changed_ratio = sum(1 for value in changed_values if value) / len(changed_values)

    return {
        "changed_ratio": round(changed_ratio, 3) if changed_ratio is not None else None,
        "avg_delta_len": round(_mean(delta_lengths), 2) if delta_lengths else None,
        "avg_distance_mean": round(_mean(mean_distances), 3) if mean_distances else None,
        "avg_distance_max": round(_mean(max_distances), 3) if max_distances else None,
    }


def _dimension_stats(entries: List[Dict[str, object]]) -> Dict[str, object]:
    valid_values: List[bool] = []
    reason_counts: Dict[str, int] = {}

    for entry in entries:
        valid = entry.get("valid")
        if isinstance(valid, bool):
            valid_values.append(valid)
        reasons = entry.get("reasons")
        if isinstance(reasons, list):
            for reason in reasons:
                key = str(reason)
                reason_counts[key] = reason_counts.get(key, 0) + 1

    valid_ratio = None
    if valid_values:
        valid_ratio = sum(1 for value in valid_values if value) / len(valid_values)

    return {
        "valid_ratio": round(valid_ratio, 3) if valid_ratio is not None else None,
        "reason_counts": reason_counts,
    }


def build_report(
    trace_entries: List[Dict[str, object]],
    dimension_entries: List[Dict[str, object]],
) -> Dict[str, object]:
    return {
        "trace": {
            "count": len(trace_entries),
            "personas": _persona_counts(trace_entries),
            "stats": _trace_stats(trace_entries),
        },
        "dimension": {
            "count": len(dimension_entries),
            "personas": _persona_counts(dimension_entries),
            "stats": _dimension_stats(dimension_entries),
        },
    }


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persona trace summary report.")
    parser.add_argument("--trace", help="Path to persona_trace.jsonl.")
    parser.add_argument("--dimension", help="Path to persona_dimension_ledger.jsonl.")
    parser.add_argument("--output", help="Optional output JSON path.")
    return parser


def _default_path(rel_path: str) -> str:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base, rel_path)


def main() -> Dict[str, object]:
    parser = build_arg_parser()
    args = parser.parse_args()
    trace_path = args.trace or _default_path(os.path.join("memory", "persona_trace.jsonl"))
    dimension_path = args.dimension or _default_path(
        os.path.join("memory", "persona_dimension_ledger.jsonl")
    )

    report = build_report(load_jsonl(trace_path), load_jsonl(dimension_path))
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
    return report


if __name__ == "__main__":
    payload = main()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
