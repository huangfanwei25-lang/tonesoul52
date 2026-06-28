"""Cognitive-frame eval: measure the deterministic frame contract.

This is not a world-understanding benchmark. It only checks whether the frame validator
accepts well-formed exploration frames and rejects malformed / overclaiming shapes.

Usage:
    python tools/probe/cognitive_frame_eval.py
    python tools/probe/cognitive_frame_eval.py --write-doc
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.cognition import validate_cognitive_frame  # noqa: E402


def _item(
    text: str,
    *,
    evidence_refs: tuple[str, ...] = ("turn_2026_06_28_001",),
    confidence: str = "observed",
) -> dict[str, object]:
    return {"text": text, "evidence_refs": evidence_refs, "confidence": confidence}


def _valid_frame() -> dict[str, object]:
    return {
        "question": "How should the agent frame a responsibility-runtime follow-up?",
        "temporal_context": (_item("The session is running on 2026-06-28.", evidence_refs=("system_date",)),),
        "spatial_context": (_item("Work is scoped to the public ToneSoul repo.", evidence_refs=("cwd",)),),
        "actors": (_item("The user decides when to merge.", evidence_refs=("user_turn",)),),
        "known_facts": (_item("The evaluator is deterministic.", evidence_refs=("module_contract",)),),
        "hypotheses": (
            _item(
                "The frame may reduce unsupported task claims.",
                confidence="inferred",
            ),
        ),
        "unknowns": (
            _item(
                "Whether real project artifacts need additional lanes.",
                evidence_refs=(),
                confidence="unknown",
            ),
        ),
        "constraints": (_item("Do not read or commit private memory data.", evidence_refs=("AGENTS.md",)),),
        "next_probes": (
            _item(
                "Run the frame against representative public artifacts.",
                evidence_refs=(),
                confidence="unknown",
            ),
        ),
    }


SCENARIOS: list[tuple[str, Any, bool, str]] = [
    ("valid_project_frame", _valid_frame(), True, "baseline"),
    (
        "form_only_absurd_fact",
        {**_valid_frame(), "known_facts": (_item("This impossible claim has only a ref shape."),)},
        True,
        "boundary",
    ),
    (
        "missing_known_fact_evidence",
        {**_valid_frame(), "known_facts": (_item("No evidence here.", evidence_refs=()),)},
        False,
        "evidence",
    ),
    (
        "hypothesis_without_probe",
        {**_valid_frame(), "next_probes": ()},
        False,
        "exploration",
    ),
    (
        "missing_time_and_space",
        {**_valid_frame(), "temporal_context": (), "spatial_context": ()},
        True,
        "warning",
    ),
    (
        "extra_private_field",
        {**_valid_frame(), "private_memory_dump": "blocked"},
        False,
        "malformed",
    ),
    (
        "invisible_question",
        {**_valid_frame(), "question": "\u200b"},
        False,
        "malformed",
    ),
]


def evaluate_scenarios() -> tuple[str, int]:
    rows: list[tuple[str, str, bool, bool, str, str]] = []
    failures = 0

    for label, payload, expected, category in SCENARIOS:
        result = validate_cognitive_frame(payload)
        actual = result.accepted
        ok = actual is expected
        if not ok:
            failures += 1
        codes = ", ".join(issue.code for issue in result.issues) or "-"
        severities = ", ".join(issue.severity for issue in result.issues) or "-"
        rows.append((label, category, expected, actual, codes, severities))

    lines: list[str] = []
    lines.append("# Cognitive Frame Eval")
    lines.append("")
    lines.append("Deterministic eval for the first externalized cognitive-frame contract.")
    lines.append("It validates frame shape and evidence-ref presence only; it is not a")
    lines.append("semantic truth oracle or a world-understanding benchmark.")
    lines.append("")
    lines.append(f"- scenarios: **{len(SCENARIOS)}**")
    lines.append(f"- failures: **{failures}**")
    lines.append("")
    lines.append("| scenario | category | expected accepted | actual accepted | issue codes | severities |")
    lines.append("|---|---|---|---|---|---|")
    for label, category, expected, actual, codes, severities in rows:
        lines.append(
            f"| {label} | {category} | {'yes' if expected else 'no'} | "
            f"{'yes' if actual else 'no'} | {codes} | {severities} |"
        )

    return "\n".join(lines), failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-doc", action="store_true")
    args = parser.parse_args()

    report, failures = evaluate_scenarios()
    sys.stdout.buffer.write((report + "\n").encode("utf-8"))
    if args.write_doc:
        path = REPO_ROOT / "docs" / "status" / "cognitive_frame_eval_2026-06-28.md"
        path.write_text(report + "\n", encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {path.relative_to(REPO_ROOT)}]\n".encode("utf-8"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
