"""run_outcome_summary.py — snapshot of council outcome collection progress.

Reads .aegis/council_outcomes.jsonl and prints:
  - total records
  - signal distribution
  - date range
  - whether collection has reached Bucket B synthetic promotion criteria

Usage:
    python scripts/run_outcome_summary.py
    python scripts/run_outcome_summary.py --path .aegis/council_outcomes.jsonl
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTCOME_PATH = REPO_ROOT / ".aegis" / "council_outcomes.jsonl"

# Bucket B synthetic promotion threshold (from Phase 864b spec):
# enough outcomes to produce a calibration table with at least one row per signal.
_MIN_RECORDS_FOR_SYNTHETIC_PROMOTION = 10


def summarize(outcome_path: Path) -> dict:
    if not outcome_path.is_file():
        return {
            "status": "no_data",
            "total_records": 0,
            "signal_distribution": {},
            "date_range": None,
            "bucket_b_synthetic_promotion_eligible": False,
            "note": "council_outcomes.jsonl not found — collection has not started.",
        }

    records = []
    with outcome_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    total = len(records)
    signals = Counter(r.get("signal") for r in records if r.get("signal"))
    timestamps = sorted(r["timestamp"] for r in records if r.get("timestamp"))
    date_range = {"earliest": timestamps[0], "latest": timestamps[-1]} if timestamps else None
    eligible = total >= _MIN_RECORDS_FOR_SYNTHETIC_PROMOTION

    return {
        "status": "active" if total > 0 else "empty",
        "total_records": total,
        "signal_distribution": dict(signals),
        "date_range": date_range,
        "bucket_b_synthetic_promotion_eligible": eligible,
        "promotion_threshold": _MIN_RECORDS_FOR_SYNTHETIC_PROMOTION,
        "note": (
            "Eligible for Bucket B synthetic promotion run."
            if eligible
            else f"Need {_MIN_RECORDS_FOR_SYNTHETIC_PROMOTION - total} more records "
            f"to reach Bucket B synthetic promotion threshold."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarise council outcome collection.")
    parser.add_argument(
        "--path",
        default=str(DEFAULT_OUTCOME_PATH),
        help="Path to council_outcomes.jsonl",
    )
    args = parser.parse_args()

    result = summarize(Path(args.path))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
