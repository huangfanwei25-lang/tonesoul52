#!/usr/bin/env python3
"""Outcome-collection smoke pipeline — v0b Bucket A validation harness.

WHAT THIS DOES
--------------
Runs a curated corpus of draft_outputs through ``PreOutputCouncil.validate()``,
then pushes a synthetic outcome signal (accept / reject / correction / harm)
through ``build_outcome_record`` + ``persist_outcome_record``. Produces an
isolated JSONL file so the pipeline can be exercised end-to-end without
polluting real user-traffic data.

This is the instrument described in ``council_calibration_v0b_2026-04-19.md``
§9: exercise the collection pipeline before anyone consumes the alignment
number. If this smoke run produces a well-formed JSONL with diverse verdict
types and all four signal categories, we have evidence the plumbing works.

USAGE
-----
::

    python scripts/run_outcome_smoke.py \\
        --corpus tests/fixtures/outcome_smoke/corpus_2026-04-19.jsonl \\
        --outcome-path .aegis/council_outcomes_smoke_2026-04-19.jsonl

The script writes to ``--outcome-path`` (kept *separate* from the default
``.aegis/council_outcomes.jsonl`` so smoke data never mixes with real
collection data).

ISOLATION CONTRACT
------------------
- No network calls; no gateway process; no Redis.
- Imports the Council + outcome modules directly (same code path as the
  gateway handlers, but no HTTP layer).
- Writes only to the path given by ``--outcome-path``.
- Prints stats but does NOT record anything to ``memory/self_journal.jsonl``
  (Council is invoked with ``auto_record_self_memory=False``).

Author: Claude Opus 4.7
Date: 2026-04-19
Spec: docs/plans/council_calibration_v0b_2026-04-19.md §7 Bucket A, §9
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tonesoul.council import PreOutputCouncil  # noqa: E402
from tonesoul.council.outcome_persistence import (  # noqa: E402
    build_outcome_record,
    persist_outcome_record,
)


def _verdict_fingerprint(verdict_dict: dict) -> str:
    """Stable sha256 fingerprint of a verdict dict.

    Using sorted-key JSON so the same verdict always hashes the same way.
    Prefix ``sha256:`` matches the example fingerprint shape used elsewhere
    in the outcome spec.
    """
    canonical = json.dumps(verdict_dict, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:16]}"


def run_smoke(corpus_path: Path, outcome_path: Path) -> dict[str, Any]:
    """Run every corpus entry through Council → outcome pipeline.

    Returns a summary dict: how many drafts processed, verdict-type counts,
    signal-type counts, alignment_judgment counts, and the output path.
    """
    os.environ["TONESOUL_OUTCOME_PATH"] = str(outcome_path)
    outcome_path.parent.mkdir(parents=True, exist_ok=True)
    if outcome_path.exists():
        outcome_path.unlink()

    council = PreOutputCouncil()

    verdict_types: Counter[str] = Counter()
    signals: Counter[str] = Counter()
    alignments: Counter[str] = Counter()
    categories: Counter[str] = Counter()

    with corpus_path.open(encoding="utf-8") as fh:
        entries = [json.loads(line) for line in fh if line.strip()]

    for entry in entries:
        draft_output = entry["draft_output"]
        user_intent = entry.get("user_intent", "")
        category = entry.get("category", "unknown")
        signal = entry["suggested_signal"]

        verdict = council.validate(
            draft_output=draft_output,
            context={"category": category, "smoke_run": True},
            user_intent=user_intent,
            auto_record_self_memory=False,
        )
        verdict_dict = verdict.to_dict()
        fingerprint = _verdict_fingerprint(verdict_dict)

        record = build_outcome_record(
            verdict_fingerprint=fingerprint,
            signal=signal,
            correction_text=entry.get("correction_text"),
            harm_description=entry.get("harm_description"),
            intent_id=f"smoke:{category}:{entries.index(entry)}",
            verdict_type=verdict_dict.get("verdict"),
            signal_source="explicit_feedback",
        )
        persist_outcome_record(record)

        verdict_types[verdict_dict.get("verdict", "UNKNOWN")] += 1
        signals[signal] += 1
        alignments[record.alignment_judgment] += 1
        categories[category] += 1

    return {
        "corpus_size": len(entries),
        "verdict_types": dict(verdict_types),
        "signals": dict(signals),
        "alignment_judgments": dict(alignments),
        "categories": dict(categories),
        "outcome_path": str(outcome_path),
        "outcome_file_lines": sum(1 for _ in outcome_path.open(encoding="utf-8")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "--corpus",
        type=Path,
        default=REPO_ROOT / "tests/fixtures/outcome_smoke/corpus_2026-04-19.jsonl",
        help="Path to JSONL corpus file (one draft per line).",
    )
    parser.add_argument(
        "--outcome-path",
        type=Path,
        default=REPO_ROOT / ".aegis/council_outcomes_smoke_2026-04-19.jsonl",
        help="Path where outcome JSONL will be written (isolated from real data).",
    )
    args = parser.parse_args()

    if not args.corpus.exists():
        print(f"ERROR: corpus not found at {args.corpus}", file=sys.stderr)
        return 2

    summary = run_smoke(args.corpus, args.outcome_path)
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    expected_lines = summary["corpus_size"]
    actual_lines = summary["outcome_file_lines"]
    if expected_lines != actual_lines:
        print(
            f"ERROR: expected {expected_lines} lines, got {actual_lines}",
            file=sys.stderr,
        )
        return 1

    if len(summary["signals"]) < 4:
        print(
            f"WARNING: only {len(summary['signals'])}/4 signal types covered — "
            "corpus may be incomplete for validating derive_alignment_judgment",
            file=sys.stderr,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
