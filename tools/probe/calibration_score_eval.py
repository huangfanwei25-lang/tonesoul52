"""Calibration-score eval: demonstrate the confidence-calibration primitive on representative cases.

Not a benchmark of any real forecaster. It checks that the pure scorer (Brier / ECE / reliability)
correctly labels perfectly-calibrated, overconfident, underconfident, and insufficient cases --
including the KalshiBench-shaped case (states high confidence, right less often), which is the
failure mode this primitive exists to surface. It scores only; it does not persist, surface, or bind.

Usage:
    python tools/probe/calibration_score_eval.py
    python tools/probe/calibration_score_eval.py --write-doc
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.calibration_score import calibration_report  # noqa: E402


def _pairs(spec: list[tuple[float, int, int]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for conf, hits, total in spec:
        out += [(conf, 1.0)] * hits + [(conf, 0.0)] * (total - hits)
    return out


# (label, claims, expected verdict, category). Includes over/under-confidence on purpose.
SCENARIOS: list[tuple[str, Any, str, str]] = [
    (
        "perfectly_calibrated",
        _pairs([(0.9, 9, 10), (0.6, 6, 10), (0.3, 3, 10)]),
        "calibrated",
        "baseline",
    ),
    ("systematic_overconfidence", _pairs([(0.9, 5, 100)]), "overconfident", "kalshibench-shaped"),
    ("systematic_underconfidence", _pairs([(0.4, 90, 100)]), "underconfident", "boundary"),
    (
        "canceling_miscalibration",
        _pairs([(0.9, 50, 100), (0.1, 50, 100)]),
        "miscalibrated",
        "ece-catches-what-net-bias-hides",
    ),
    ("insufficient_sample", _pairs([(0.8, 2, 3)]), "insufficient", "small-sample-honesty"),
]


def _fmt(x: Any) -> str:
    return "-" if x is None else f"{x:.3f}"


def evaluate_scenarios() -> tuple[str, int]:
    rows: list[tuple[str, str, str, str, int, Any, Any, Any]] = []
    failures = 0
    for label, pairs, expected, category in SCENARIOS:
        report = calibration_report(pairs)
        ok = report.verdict == expected
        if not ok:
            failures += 1
        rows.append(
            (
                label,
                category,
                expected,
                report.verdict,
                report.n,
                report.brier,
                report.ece,
                report.weighted_gap,
            )
        )

    lines: list[str] = []
    lines.append("# Calibration Score Eval")
    lines.append("")
    lines.append(
        "Deterministic check of the confidence-calibration primitive (Brier / ECE / reliability)."
    )
    lines.append("Not a real-forecaster benchmark; it verifies the scorer labels calibrated /")
    lines.append("overconfident / underconfident / insufficient correctly. It scores only; it does")
    lines.append("NOT persist, surface, or bind (binding is owner-gated).")
    lines.append("")
    lines.append(f"- scenarios: **{len(SCENARIOS)}**")
    lines.append(f"- verdict mismatches (failures): **{failures}**")
    lines.append("")
    lines.append("| scenario | category | expected | actual | n | brier | ece | weighted_gap |")
    lines.append("|---|---|---|---|---:|---|---|---|")
    for label, category, expected, actual, n, brier, ece, gap in rows:
        lines.append(
            f"| {label} | {category} | {expected} | {actual} | {n} | "
            f"{_fmt(brier)} | {_fmt(ece)} | {_fmt(gap)} |"
        )
    return "\n".join(lines), failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-doc", action="store_true")
    args = parser.parse_args()

    report, failures = evaluate_scenarios()
    sys.stdout.buffer.write((report + "\n").encode("utf-8"))
    if args.write_doc:
        path = REPO_ROOT / "docs" / "status" / "calibration_score_eval_2026-06-30.md"
        path.write_text(report + "\n", encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {path.relative_to(REPO_ROOT)}]\n".encode("utf-8"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
