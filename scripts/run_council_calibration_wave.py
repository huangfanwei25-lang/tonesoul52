#!/usr/bin/env python3
"""Run the council calibration v0a realism baseline wave."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the council calibration v0a realism baseline wave.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument(
        "--stress-journal",
        type=Path,
        default=REPO_ROOT / "memory" / "stress_test_journal.jsonl",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    return parser


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_markdown(path: Path, result: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Council Calibration v0a — Realism Baseline")
    lines.append("")
    lines.append(f"> Generated at `{result.get('generated_at', 'unknown')}`.")
    lines.append("")
    lines.append(f"- Schema version: `{result.get('schema_version', 'unknown')}`")
    lines.append(f"- Status: `{result.get('status', 'unknown')}`")
    lines.append("")

    lang = result.get("language_boundary", {})
    lines.append("## Language Boundary")
    lines.append("")
    lines.append(f"- This is: `{lang.get('this_is', '')}`")
    for neg in lang.get("this_is_not", []):
        lines.append(f"- This is NOT: `{neg}`")
    lines.append(f"- Ceiling effect: `{lang.get('ceiling_effect', '')}`")
    lines.append(f"- Maximum honest claim: `{lang.get('maximum_honest_claim', '')}`")
    lines.append("")

    ds = result.get("data_sources", {})
    lines.append("## Data Sources")
    lines.append("")
    stress = ds.get("stress_test_journal", {})
    persist = ds.get("council_verdict_persistence", {})
    lines.append(
        f"- Stress test journal: `{stress.get('path', '')}` ({stress.get('record_count', 0)} records)"
    )
    lines.append(f"- Council verdict persistence: {persist.get('record_count', 0)} records")
    lines.append("")

    metrics = result.get("metrics", {})
    lines.append("## Metrics")
    lines.append("")
    for name, m in metrics.items():
        lines.append(f"### {name}")
        lines.append("")
        lines.append(f"- Status: `{m.get('status', 'unknown')}`")
        lines.append(f"- Sample count: `{m.get('sample_count', 0)}`")

        for key, val in m.items():
            if key in (
                "metric",
                "status",
                "sample_count",
                "measures",
                "does_not_measure",
                "data_source",
                "interpretation",
            ):
                continue
            if isinstance(val, dict):
                lines.append(f"- {key}:")
                for sub_k, sub_v in val.items():
                    lines.append(f"  - {sub_k}: `{sub_v}`")
            else:
                lines.append(f"- {key}: `{val}`")

        lines.append(f"- Data source: `{m.get('data_source', '')}`")
        lines.append(f"- Measures: `{m.get('measures', '')}`")
        lines.append(f"- Does NOT measure: `{m.get('does_not_measure', '')}`")
        if m.get("interpretation"):
            lines.append(f"- Interpretation: {m['interpretation']}")
        lines.append("")

    exit_c = result.get("v0a_exit_criteria", {})
    lines.append("## v0a Exit Criteria")
    lines.append("")
    lines.append(f"- Baseline metrics stable: `{exit_c.get('baseline_metrics_stable', False)}`")
    lines.append(f"- Persistence operational: `{exit_c.get('persistence_operational', False)}`")
    lines.append(
        f"- Verdict records accumulating: `{exit_c.get('verdict_records_accumulating', False)}`"
    )
    lines.append("")

    v0b = result.get("v0b_prerequisites", {})
    lines.append("## v0b Prerequisites (not in V1.1 scope)")
    lines.append("")
    lines.append(
        f"- verdict_outcome_alignment N>=20: `{v0b.get('verdict_outcome_alignment_n_ge_20', False)}`"
    )
    lines.append(
        f"- Two consecutive stable waves: `{v0b.get('two_consecutive_stable_waves', False)}`"
    )
    lines.append(f"- Note: `{v0b.get('note', '')}`")
    lines.append("")

    lines.append("## Receiver Rule")
    lines.append("")
    lines.append(f"> {result.get('receiver_rule', '')}")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    args = _build_parser().parse_args(argv)

    from tonesoul.council.calibration import run_calibration_wave

    result = run_calibration_wave(stress_journal_path=args.stress_journal)
    result["agent"] = args.agent

    json_out = args.json_out or (REPO_ROOT / "docs" / "status" / "council_calibration_latest.json")
    md_out = args.markdown_out or (REPO_ROOT / "docs" / "status" / "council_calibration_latest.md")

    _write_json(json_out, result)
    _write_markdown(md_out, result)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
