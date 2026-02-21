from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import median
from time import perf_counter
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tonesoul.memory.soul_db import MemoryRecord, MemorySource, _decay_records  # noqa: E402


def _parse_sizes(raw: str) -> List[int]:
    values: List[int] = []
    for chunk in raw.split(","):
        text = chunk.strip()
        if not text:
            continue
        value = int(text)
        if value <= 0:
            raise ValueError(f"Size must be > 0, got: {value}")
        values.append(value)
    if not values:
        raise ValueError("At least one benchmark size is required.")
    return values


def _iso_z(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _build_records(size: int, now: datetime) -> List[MemoryRecord]:
    records: List[MemoryRecord] = []
    for idx in range(size):
        age_days = (idx * 7) % 365 + 1
        timestamp = now - timedelta(days=age_days)
        last_accessed = None
        if idx % 4 == 0:
            last_accessed = _iso_z(now - timedelta(days=idx % 30))
        record = MemoryRecord(
            source=MemorySource.SELF_JOURNAL,
            timestamp=_iso_z(timestamp),
            payload={"statement": f"record-{idx}"},
            record_id=f"record-{idx}",
            relevance_score=0.15 + ((idx * 13) % 80) / 100,
            access_count=(idx * 5) % 8,
            last_accessed=last_accessed,
        )
        records.append(record)
    return records


def _clone_records(records: Iterable[MemoryRecord]) -> List[MemoryRecord]:
    return [
        replace(record, payload=dict(record.payload), tags=list(record.tags)) for record in records
    ]


def _run_once_baseline(
    records: List[MemoryRecord], now: datetime, limit: int, threshold: float
) -> List[MemoryRecord]:
    ranked = _decay_records(
        _clone_records(records),
        now=now,
        forget_threshold=threshold,
        top_k=None,
    )
    return ranked[:limit]


def _run_once_topk(
    records: List[MemoryRecord], now: datetime, limit: int, threshold: float
) -> List[MemoryRecord]:
    return _decay_records(
        _clone_records(records),
        now=now,
        forget_threshold=threshold,
        top_k=limit,
    )


def _time_run(
    runner,
    records: List[MemoryRecord],
    now: datetime,
    limit: int,
    threshold: float,
) -> tuple[float, List[MemoryRecord]]:
    started = perf_counter()
    result = runner(records, now, limit, threshold)
    elapsed = perf_counter() - started
    return elapsed, result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark decay query baseline vs top-k heap path."
    )
    parser.add_argument(
        "--sizes",
        default="1000,5000,20000,50000",
        help="Comma-separated dataset sizes.",
    )
    parser.add_argument("--limit", type=int, default=50, help="Top-K limit for decayed query.")
    parser.add_argument("--runs", type=int, default=5, help="Timed runs per dataset size.")
    parser.add_argument(
        "--forget-threshold",
        type=float,
        default=0.1,
        help="Forget threshold passed into decay function.",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=None,
        help="Optional path to write raw benchmark results as JSON.",
    )
    args = parser.parse_args()

    sizes = _parse_sizes(args.sizes)
    if args.limit <= 0:
        raise ValueError("--limit must be > 0")
    if args.runs <= 0:
        raise ValueError("--runs must be > 0")

    now = datetime(2026, 2, 21, tzinfo=timezone.utc)
    rows = []

    for size in sizes:
        records = _build_records(size, now)

        baseline_check = _run_once_baseline(records, now, args.limit, args.forget_threshold)
        topk_check = _run_once_topk(records, now, args.limit, args.forget_threshold)
        if [r.record_id for r in topk_check] != [r.record_id for r in baseline_check]:
            raise RuntimeError(f"Top-k result mismatch at size={size}")
        if [r.relevance_score for r in topk_check] != [r.relevance_score for r in baseline_check]:
            raise RuntimeError(f"Top-k score mismatch at size={size}")

        baseline_durations: List[float] = []
        topk_durations: List[float] = []
        for _ in range(args.runs):
            baseline_elapsed, _ = _time_run(
                _run_once_baseline, records, now, args.limit, args.forget_threshold
            )
            topk_elapsed, _ = _time_run(
                _run_once_topk, records, now, args.limit, args.forget_threshold
            )
            baseline_durations.append(baseline_elapsed)
            topk_durations.append(topk_elapsed)

        baseline_median = median(baseline_durations)
        topk_median = median(topk_durations)
        speedup = baseline_median / topk_median if topk_median > 0 else float("inf")
        rows.append(
            {
                "size": size,
                "limit": args.limit,
                "baseline_median_seconds": baseline_median,
                "topk_median_seconds": topk_median,
                "speedup": speedup,
            }
        )

    print("# Decay Query Benchmark")
    print()
    print(f"- sizes: {sizes}")
    print(f"- limit: {args.limit}")
    print(f"- runs: {args.runs}")
    print(f"- forget_threshold: {args.forget_threshold}")
    print()
    print("| size | baseline_median_s | topk_median_s | speedup_x |")
    print("| ---: | ---: | ---: | ---: |")
    for row in rows:
        print(
            f"| {row['size']} | {row['baseline_median_seconds']:.6f} | "
            f"{row['topk_median_seconds']:.6f} | {row['speedup']:.2f} |"
        )

    if args.json_output is not None:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
        print()
        print(f"JSON saved: {args.json_output}")


if __name__ == "__main__":
    main()
