"""Eval the deterministic memory-output surface.

The output surface is the runtime-controlled path that may say "I've saved this..." after a
memory-write intent executes. This probe verifies that the acknowledgement is trace-backed and
that denied/non-write/tampered results do not render memory-write claims.

Usage:
    python tools/probe/memory_output_surface_eval.py
    python tools/probe/memory_output_surface_eval.py --write-doc
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.responsibility_runtime import (  # noqa: E402
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    render_memory_write_result,
    validate_intent,
)

DEFAULT_REPORT_PATH = REPO_ROOT / "docs" / "status" / "memory_output_surface_eval_2026-06-28.md"


def _write_payload() -> dict[str, Any]:
    return {
        "intent": "memory.write.propose",
        "claim": "user prefers Traditional Chinese",
        "evidence_refs": ["turn_2026_06_28_001"],
        "requested_scope": "long_term_memory",
    }


def _read_payload() -> dict[str, Any]:
    return {
        "intent": "memory.read.request",
        "query": "user language preference",
        "requested_scope": "session_memory",
    }


def run_scenarios() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.append(
        _run(
            label="executed_write",
            payload=_write_payload(),
            policy=FakePolicyEngine(),
            expected_status="memory_write_acknowledged",
            expected_claim_check="backed_by_trace",
        )
    )
    rows.append(
        _run(
            label="denied_write",
            payload=_write_payload(),
            policy=FakePolicyEngine(allowed_scopes={"session_memory"}),
            expected_status="memory_write_denied",
            expected_claim_check="no_memory_claim",
        )
    )
    rows.append(
        _run(
            label="read_intent",
            payload=_read_payload(),
            policy=FakePolicyEngine(),
            expected_status="not_memory_write",
            expected_claim_check="no_memory_claim",
        )
    )

    trace = InMemoryTraceStore()
    validation = validate_intent(_write_payload())
    decision = FakePolicyEngine(allowed_scopes={"session_memory"}).decide(validation)
    denied_result = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )
    tampered_result = replace(denied_result, executed=True)
    rendered = render_memory_write_result(tampered_result)
    rows.append(
        {
            "label": "tampered_executed_flag",
            "expected_status": "memory_write_denied",
            "actual_status": rendered.status,
            "expected_claim_check": "no_memory_claim",
            "actual_claim_check": rendered.claim_check_status,
            "ok": rendered.status == "memory_write_denied"
            and rendered.claim_check_status == "no_memory_claim",
            "text": rendered.text,
        }
    )
    return rows


def render_report(rows: list[dict[str, Any]]) -> str:
    failures = [row for row in rows if not row["ok"]]
    lines = [
        "# Memory Output Surface Eval",
        "",
        "Deterministic eval for trace-backed memory-write acknowledgements. The surface may",
        "only render a memory-write claim when the enforcer result and trace both show an",
        "executed `memory.write.propose` decision.",
        "",
        f"- scenarios: **{len(rows)}**",
        f"- failures: **{len(failures)}**",
        "",
        "| scenario | expected status | actual status | expected claim check | actual claim check | ok |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['label']} | {row['expected_status']} | {row['actual_status']} | "
            f"{row['expected_claim_check']} | {row['actual_claim_check']} | "
            f"{'yes' if row['ok'] else 'NO'} |"
        )
    return "\n".join(lines) + "\n"


def _run(
    *,
    label: str,
    payload: dict[str, Any],
    policy: FakePolicyEngine,
    expected_status: str,
    expected_claim_check: str,
) -> dict[str, Any]:
    trace = InMemoryTraceStore()
    validation = validate_intent(payload)
    decision = policy.decide(validation)
    result = Enforcer(memory_adapter=RecordingMemoryAdapter(), trace_store=trace).enforce(
        validation, decision
    )
    rendered = render_memory_write_result(result)
    return {
        "label": label,
        "expected_status": expected_status,
        "actual_status": rendered.status,
        "expected_claim_check": expected_claim_check,
        "actual_claim_check": rendered.claim_check_status,
        "ok": rendered.status == expected_status
        and rendered.claim_check_status == expected_claim_check,
        "text": rendered.text,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-doc", action="store_true")
    args = parser.parse_args()

    rows = run_scenarios()
    report = render_report(rows)
    sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))
    if args.write_doc:
        DEFAULT_REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")
        sys.stdout.buffer.write(f"\n[wrote {DEFAULT_REPORT_PATH}]\n".encode("utf-8"))
    return 1 if any(not row["ok"] for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
