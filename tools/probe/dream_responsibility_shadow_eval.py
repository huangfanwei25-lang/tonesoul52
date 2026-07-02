"""Dream responsibility-shadow eval: measure the OBSERVE-ONLY gate's decision surface.

This records what the responsibility gate WOULD decide for representative dream-collision
payloads (via run_shadow_gate). It is a committed, re-runnable BASELINE — NOT enforcement, NOT
real dream-cycle traffic, and it makes no claim that memory is gated or non-bypassable. Each
scenario carries an expected verdict, so the probe is itself the refutable test for the shadow's
translation + decision behavior (it fails if a verdict drifts).

Usage:
    python tools/probe/dream_responsibility_shadow_eval.py
    python tools/probe/dream_responsibility_shadow_eval.py --write-doc
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.dream_responsibility_shadow import run_shadow_gate  # noqa: E402

# Representative dream-collision payloads. Deliberately includes DENY cases (not happy-path only):
# a self-authored "0 deny" baseline would be the self-authored-test trap.
SCENARIOS: list[tuple[str, Any, bool, str]] = [
    (
        "grounded_collision",
        {
            "summary": "A grounded dream collision claim.",
            "evidence": ["because of source X", "topic Y"],
        },
        True,
        "baseline-allow",
    ),
    (
        "lineage_only_evidence",
        {
            "summary": "Claim backed only by record lineage, no free-text evidence.",
            "evidence": [],
            "stimulus_record_id": "stim-1",
            "source_record_ids": ["rec-2"],
        },
        True,
        "boundary-lineage-counts-as-ref",
    ),
    (
        "title_fallback_claim",
        {"title": "Title-only collision claim", "evidence": ["ref1"]},
        True,
        "boundary-claim-falls-back-to-title",
    ),
    (
        "no_evidence_collision",
        {"summary": "An unsupported claim with no evidence and no lineage.", "evidence": []},
        False,
        "deny-missing-evidence",
    ),
    (
        "empty_claim_collision",
        {"summary": "", "reflection": "", "title": "", "topic": "", "evidence": ["e1"]},
        False,
        "deny-empty-claim",
    ),
]


def evaluate_scenarios() -> tuple[str, int]:
    rows: list[tuple[str, str, bool, Any, str, str]] = []
    failures = 0

    for label, payload, expected, category in SCENARIOS:
        outcome = run_shadow_gate(payload)
        actual = outcome.would_execute
        ok = actual is expected
        if not ok:
            failures += 1
        codes = ", ".join(outcome.issue_codes) or "-"
        rows.append((label, category, expected, actual, outcome.reason, codes))

    would_allow = sum(1 for _, _, _, a, _, _ in rows if a is True)
    would_deny = sum(1 for _, _, _, a, _, _ in rows if a is False)

    lines: list[str] = []
    lines.append("# Dream Responsibility Shadow Eval")
    lines.append("")
    lines.append(
        "Deterministic baseline for the OBSERVE-ONLY responsibility-gate shadow (PR #219)."
    )
    lines.append(
        "It records what the gate WOULD decide for representative dream-collision payloads."
    )
    lines.append("It is NOT enforcement, NOT real dream-cycle traffic, and makes no claim that")
    lines.append("memory is gated or non-bypassable. Scenarios include deny cases on purpose.")
    lines.append("")
    lines.append(f"- scenarios: **{len(SCENARIOS)}**")
    lines.append(f"- would-allow: **{would_allow}** · would-deny: **{would_deny}**")
    lines.append(f"- verdict mismatches (failures): **{failures}**")
    lines.append("")
    lines.append(
        "| scenario | category | expected would_execute | actual | gate reason | issue codes |"
    )
    lines.append("|---|---|---|---|---|---|")
    for label, category, expected, actual, reason, codes in rows:
        actual_str = "yes" if actual is True else "no" if actual is False else "error"
        lines.append(
            f"| {label} | {category} | {'yes' if expected else 'no'} | "
            f"{actual_str} | {reason} | {codes} |"
        )

    return "\n".join(lines), failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-doc", action="store_true")
    args = parser.parse_args()

    report, failures = evaluate_scenarios()
    sys.stdout.buffer.write((report + "\n").encode("utf-8"))
    if args.write_doc:
        path = REPO_ROOT / "docs" / "status" / "dream_responsibility_shadow_eval_2026-06-29.md"
        path.write_text(report + "\n", encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {path.relative_to(REPO_ROOT)}]\n".encode("utf-8"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
