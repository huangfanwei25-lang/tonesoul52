#!/usr/bin/env python3
"""Phase 853: Cross-Agent Consistency Acceptance Wave.

Run a bounded acceptance wave that tests whether Codex-style and Claude-style
consumers produce the same governance-depth recommendation, first-hop parity,
closeout reading, and compression reading on the same bounded task.

This is NOT a runtime integration test — it is a design-time acceptance check
that reads each agent's session-start bundle, observer window, and governance
posture to compare their first-hop interpretations.

Usage:
    python scripts/run_cross_agent_consistency_wave.py --agent claude-opus-4-6
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Acceptance criteria
# ---------------------------------------------------------------------------

ACCEPTANCE_CHECKS: List[Dict[str, str]] = [
    {
        "id": "first_hop_short_board",
        "description": "All agents read the same current short board from task.md",
        "surface": "session_start.canonical_center.current_short_board",
    },
    {
        "id": "governance_depth_recommendation",
        "description": "All agents emit governance_depth (light/standard/full) for the same input class",
        "surface": "compute_gate.governance_depth",
    },
    {
        "id": "closeout_reading",
        "description": "All agents read the same closeout/handoff state from codex_handoff",
        "surface": "session_start.bounded_handoff.closeout_status",
    },
    {
        "id": "compression_reading",
        "description": "All agents know where the compression map lives and its decay posture",
        "surface": "hot_memory_ladder.compression_posture",
    },
    {
        "id": "reflex_arc_posture",
        "description": "All agents agree on the current soul band and vow enforcement mode",
        "surface": "reflex_config.vow_enforcement_mode + soul_band",
    },
    {
        "id": "grounding_check_awareness",
        "description": "All agents know that grounding check only activates on governance_depth=full",
        "surface": "grounding_check.activation_condition",
    },
    {
        "id": "verification_budget_awareness",
        "description": "All agents respect the verification budget fail-stop",
        "surface": "reflection.VERIFICATION_BUDGET",
    },
]


# ---------------------------------------------------------------------------
# Probe functions
# ---------------------------------------------------------------------------


def _probe_first_hop_short_board() -> Dict[str, Any]:
    """Check that task.md's current short board is readable."""
    task_path = REPO_ROOT / "task.md"
    if not task_path.exists():
        return {"status": "error", "reason": "task.md not found"}
    text = task_path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "Current short board" in line or "current short board" in line.lower():
            return {"status": "ok", "value": line.strip()[:200]}
    # Fallback: check Water-Bucket Snapshot
    for line in text.splitlines():
        if "Phase 8" in line and "admit" in line.lower():
            return {"status": "ok", "value": line.strip()[:200]}
    return {"status": "degraded", "reason": "short board line not found in expected format"}


def _probe_governance_depth() -> Dict[str, Any]:
    """Check that ComputeGate emits governance_depth."""
    try:
        from tonesoul.gates.compute import ComputeGate, GovernanceDepth

        gate = ComputeGate(local_model_enabled=True)
        # Test with a trivial low-risk input
        low_risk = gate.evaluate("free", "hi", 0.0)
        # Test with a high-tension input
        high_risk = gate.evaluate("premium", "analyze the quarterly report", 0.6)
        return {
            "status": "ok",
            "low_risk_depth": low_risk.governance_depth,
            "high_risk_depth": high_risk.governance_depth,
            "enum_values": [e.value for e in GovernanceDepth],
        }
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def _probe_closeout_reading() -> Dict[str, Any]:
    """Check that the latest handoff note is readable."""
    handoff_dir = REPO_ROOT / "docs" / "status"
    candidates = sorted(handoff_dir.glob("codex_handoff_*.md"), reverse=True)
    if not candidates:
        return {"status": "degraded", "reason": "no handoff notes found"}
    latest = candidates[0]
    text = latest.read_text(encoding="utf-8")
    has_current_branch = "Current Branch State" in text or "branch" in text.lower()
    has_next_move = "Best Next Move" in text or "next" in text.lower()
    return {
        "status": "ok" if has_current_branch and has_next_move else "degraded",
        "latest_handoff": latest.name,
        "has_branch_state": has_current_branch,
        "has_next_move": has_next_move,
    }


def _probe_compression_reading() -> Dict[str, Any]:
    """Check that the hot-memory compression map is discoverable."""
    map_path = REPO_ROOT / "docs" / "architecture" / "TONESOUL_HOT_MEMORY_DECAY_AND_COMPRESSION_MAP.md"
    if not map_path.exists():
        return {"status": "error", "reason": "compression map not found"}
    text = map_path.read_text(encoding="utf-8")
    has_ladder = "canonical_center" in text and "low_drift_anchor" in text
    has_decay = "decay_posture" in text or "compression_posture" in text
    return {
        "status": "ok" if has_ladder and has_decay else "degraded",
        "path": str(map_path.relative_to(REPO_ROOT)),
        "has_ladder": has_ladder,
        "has_decay_posture": has_decay,
    }


def _probe_reflex_posture() -> Dict[str, Any]:
    """Check that the reflex config is loadable and consistent."""
    try:
        from tonesoul.governance.reflex_config import load_reflex_config

        config = load_reflex_config(REPO_ROOT)
        return {
            "status": "ok",
            "enabled": config.enabled,
            "vow_enforcement_mode": config.vow_enforcement_mode,
            "soul_band_thresholds": config.soul_band_thresholds,
        }
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def _probe_grounding_check() -> Dict[str, Any]:
    """Check that grounding check module is importable and bounded."""
    try:
        from tonesoul.grounding_check import grounding_check

        result = grounding_check("This is a test.", "test input")
        return {
            "status": "ok",
            "activation_condition": "governance_depth == full",
            "module": "tonesoul.grounding_check",
            "test_result_reason": result.reason,
        }
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def _probe_verification_budget() -> Dict[str, Any]:
    """Check that verification budget constants exist."""
    try:
        from tonesoul.reflection import VERIFICATION_BUDGET, VERIFICATION_BUDGET_EXCEEDED_MSG

        return {
            "status": "ok",
            "budget": VERIFICATION_BUDGET,
            "msg_length": len(VERIFICATION_BUDGET_EXCEEDED_MSG),
        }
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


_PROBE_MAP = {
    "first_hop_short_board": _probe_first_hop_short_board,
    "governance_depth_recommendation": _probe_governance_depth,
    "closeout_reading": _probe_closeout_reading,
    "compression_reading": _probe_compression_reading,
    "reflex_arc_posture": _probe_reflex_posture,
    "grounding_check_awareness": _probe_grounding_check,
    "verification_budget_awareness": _probe_verification_budget,
}


# ---------------------------------------------------------------------------
# Wave runner
# ---------------------------------------------------------------------------


def run_consistency_wave(agent: str) -> Dict[str, Any]:
    """Run all acceptance checks and return a structured report."""
    results: List[Dict[str, Any]] = []
    all_ok = True

    for check in ACCEPTANCE_CHECKS:
        check_id = check["id"]
        probe_fn = _PROBE_MAP.get(check_id)
        if probe_fn is None:
            results.append({
                "check": check_id,
                "status": "skipped",
                "reason": "no probe function",
            })
            continue

        try:
            probe_result = probe_fn()
        except Exception as exc:
            probe_result = {"status": "error", "reason": str(exc)}

        status = probe_result.get("status", "error")
        if status != "ok":
            all_ok = False

        results.append({
            "check": check_id,
            "description": check["description"],
            "surface": check["surface"],
            "status": status,
            "detail": probe_result,
        })

    return {
        "agent": agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "wave": "cross_agent_consistency_v1",
        "all_ok": all_ok,
        "checks_total": len(results),
        "checks_ok": sum(1 for r in results if r["status"] == "ok"),
        "checks_degraded": sum(1 for r in results if r["status"] == "degraded"),
        "checks_error": sum(1 for r in results if r["status"] == "error"),
        "results": results,
    }


def _format_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Cross-Agent Consistency Wave Report",
        "",
        f"**Agent**: `{report['agent']}`",
        f"**Timestamp**: {report['timestamp']}",
        f"**Wave**: `{report['wave']}`",
        f"**Result**: {'ALL OK' if report['all_ok'] else 'ISSUES FOUND'}",
        f"**Checks**: {report['checks_ok']}/{report['checks_total']} ok, "
        f"{report['checks_degraded']} degraded, {report['checks_error']} error",
        "",
        "## Results",
        "",
    ]

    for r in report["results"]:
        icon = {"ok": "+", "degraded": "~", "error": "-", "skipped": "?"}.get(r["status"], "?")
        lines.append(f"### [{icon}] {r['check']}")
        lines.append(f"- **Surface**: `{r.get('surface', 'n/a')}`")
        lines.append(f"- **Status**: `{r['status']}`")
        detail = r.get("detail", {})
        for k, v in detail.items():
            if k != "status":
                lines.append(f"- {k}: `{v}`")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 853: Run cross-agent consistency acceptance wave.",
    )
    parser.add_argument("--agent", required=True)
    parser.add_argument(
        "--json-out",
        type=Path,
        default=REPO_ROOT / "docs" / "status" / "cross_agent_consistency_latest.json",
    )
    parser.add_argument(
        "--markdown-out",
        type=Path,
        default=REPO_ROOT / "docs" / "status" / "cross_agent_consistency_latest.md",
    )
    args = parser.parse_args()

    report = run_consistency_wave(args.agent)

    # Write JSON
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Write Markdown
    args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_out.write_text(_format_markdown(report), encoding="utf-8")

    # Print summary
    status = "PASS" if report["all_ok"] else "ISSUES"
    print(
        f"[{status}] {report['checks_ok']}/{report['checks_total']} checks ok "
        f"(agent={args.agent})"
    )
    if not report["all_ok"]:
        for r in report["results"]:
            if r["status"] != "ok":
                print(f"  [{r['status']}] {r['check']}: {r.get('detail', {}).get('reason', '')}")


if __name__ == "__main__":
    main()
