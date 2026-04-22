"""Gate readiness check for Phase 864c (Deliberation Trace).

Per the Phase 864c spec, the gate requires 4 weeks of real outcome data
collected via Bucket A before 864c deliberation-trace work can begin.

This test does not enforce a pass/fail on content; it makes the gate
condition machine-readable and visible in CI:
  - Day 0: file absent → gate is open for future collection, not yet eligible
  - Day N: file present with records → collection is underway; check count

The test will fail only when the file exists but is malformed (bad JSON).
The assertion on record count is informational only (no assert), so this
test can be added to CI now without blocking the build.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTCOME_PATH = REPO_ROOT / ".aegis" / "council_outcomes.jsonl"

# Gate threshold from the 864c spec: at least 4 weeks of real data.
# Proxy metric: ≥ 100 outcome records with signal_source == "real".
_REAL_RECORDS_REQUIRED = 100


def test_outcome_file_is_absent_or_valid_jsonl():
    """council_outcomes.jsonl must either be absent or contain valid JSONL."""
    if not OUTCOME_PATH.is_file():
        return  # Day 0: not started yet, gate not triggered
    bad_lines = []
    with OUTCOME_PATH.open(encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                bad_lines.append((i, str(exc)))
    assert (
        not bad_lines
    ), f"council_outcomes.jsonl has {len(bad_lines)} malformed line(s): {bad_lines[:3]}"


def test_864c_gate_collection_status():
    """Informational: report how close the collection is to the 864c gate threshold.

    Does NOT assert on record count — this test is here to make the gate
    condition visible in CI output, not to block the build.
    """
    if not OUTCOME_PATH.is_file():
        print(
            "\n[864c gate] No outcomes collected yet. "
            "Gate condition: collect real outcome data for ≥ 4 weeks before building 864c."
        )
        return

    records = []
    with OUTCOME_PATH.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

    real_count = sum(
        1 for r in records if (r.get("outcome_signal") or {}).get("signal_source") == "real"
    )
    total = len(records)
    gap = max(0, _REAL_RECORDS_REQUIRED - real_count)

    print(
        f"\n[864c gate] total_outcomes={total} real_outcomes={real_count} "
        f"gate_threshold={_REAL_RECORDS_REQUIRED} gap={gap}"
    )
    if gap == 0:
        print("[864c gate] ELIGIBLE — real outcome threshold reached.")
    else:
        print(f"[864c gate] NOT YET ELIGIBLE — need {gap} more real-source records.")
