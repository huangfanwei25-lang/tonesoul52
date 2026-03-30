#!/usr/bin/env python3
"""Run a bounded repeated continuity validation wave against session-start."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
START_AGENT_SESSION = REPO_ROOT / "scripts" / "start_agent_session.py"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run repeated launch continuity validation scenarios.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=REPO_ROOT / "temp" / "launch_validation_wave",
        help="Workspace directory used for generated scenario fixtures.",
    )
    parser.add_argument("--json-out", type=Path, default=None)
    parser.add_argument("--markdown-out", type=Path, default=None)
    return parser


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, *records: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
    path.write_text(text, encoding="utf-8")


def _base_state(*, soul_integral: float = 0.72) -> dict[str, Any]:
    return {
        "version": "0.1.0",
        "last_updated": "2026-03-30T00:00:00+00:00",
        "soul_integral": soul_integral,
        "tension_history": [{"topic": "launch-validation", "severity": 0.31}],
        "active_vows": [{"id": "v1", "content": "leave explicit handoff state"}],
        "aegis_vetoes": [],
        "baseline_drift": {
            "caution_bias": 0.52,
            "innovation_bias": 0.58,
            "autonomy_level": 0.34,
        },
        "session_count": 9,
    }


def _base_trace() -> dict[str, Any]:
    return {
        "session_id": "sess-validation",
        "agent": "codex",
        "timestamp": "2026-03-30T00:01:00+00:00",
        "topics": ["launch-validation"],
        "tension_events": [],
        "vow_events": [],
        "aegis_vetoes": [],
        "key_decisions": ["run repeated continuity validation wave"],
    }


def _scenario_clean_pass(root: Path) -> None:
    _write_json(root / "governance_state.json", _base_state())
    _write_jsonl(root / "session_traces.jsonl", _base_trace())


def _scenario_claim_conflict(root: Path) -> None:
    _scenario_clean_pass(root)
    _write_json(
        root / ".aegis" / "task_claims.json",
        {
            "task-1": {
                "task_id": "task-1",
                "agent": "agent-a",
                "summary": "hold runtime_adapter lane",
                "paths": ["tonesoul/runtime_adapter.py"],
                "source": "cli",
                "created_at": "2026-03-30T00:02:00+00:00",
                "expires_at": "4070908920.0",
            }
        },
    )


def _scenario_stale_compaction(root: Path) -> None:
    _scenario_clean_pass(root)
    _write_json(
        root / ".aegis" / "subject_snapshots.json",
        [
            {
                "snapshot_id": "subj-1",
                "agent": "codex",
                "session_id": "sess-0",
                "summary": "Operate as a packet-first runtime steward with explicit boundaries.",
                "stable_vows": ["never smuggle theory into runtime truth"],
                "durable_boundaries": ["do not edit protected human-managed files"],
                "decision_preferences": ["prefer packet before broad repo scan"],
                "verified_routines": ["end sessions with checkpoint or compaction before release"],
                "active_threads": ["subject snapshot hardening"],
                "evidence_refs": ["docs/AI_QUICKSTART.md"],
                "refresh_signals": ["refresh when durable boundaries change"],
                "source": "cli",
                "updated_at": "2026-03-28T00:00:30+00:00",
            }
        ],
    )
    _write_json(
        root / ".aegis" / "compacted.json",
        [
            {
                "compaction_id": "cmp-new",
                "agent": "codex",
                "session_id": "sess-2",
                "summary": "Repeated bounded handoff with no new backing evidence.",
                "carry_forward": ["keep packet-first session cadence stable"],
                "pending_paths": ["scripts/start_agent_session.py"],
                "evidence_refs": ["docs/AI_QUICKSTART.md"],
                "next_action": "refresh subject snapshot active threads",
                "source": "cli",
                "updated_at": "2026-03-28T00:05:00+00:00",
            },
            {
                "compaction_id": "cmp-old",
                "agent": "codex",
                "session_id": "sess-1",
                "summary": "Previous bounded handoff for the runtime lane.",
                "carry_forward": ["keep packet-first session cadence stable"],
                "pending_paths": ["scripts/start_agent_session.py"],
                "evidence_refs": ["docs/AI_QUICKSTART.md"],
                "next_action": "refresh subject snapshot active threads",
                "source": "cli",
                "updated_at": "2026-03-28T00:04:00+00:00",
            },
        ],
    )


def _scenario_contested_dossier(root: Path) -> None:
    _scenario_clean_pass(root)
    _write_json(
        root / ".aegis" / "compacted.json",
        [
            {
                "compaction_id": "cmp-dossier",
                "agent": "codex",
                "session_id": "sess-dossier",
                "summary": "Carry bounded council realism into the handoff.",
                "carry_forward": ["review minority signals before treating approval as settled"],
                "pending_paths": ["tonesoul/council/dossier.py"],
                "evidence_refs": ["docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md"],
                "council_dossier": {
                    "dossier_version": "v1",
                    "final_verdict": "approve",
                    "confidence_posture": "contested",
                    "coherence_score": 0.62,
                    "dissent_ratio": 0.35,
                    "minority_report": [
                        {
                            "perspective": "critic",
                            "decision": "concern",
                            "confidence": 0.75,
                            "reasoning": "migration path missing",
                            "evidence": ["docs/spec.md"],
                        }
                    ],
                    "vote_summary": [],
                    "deliberation_mode": "standard_council",
                    "change_of_position": [],
                    "evidence_refs": ["docs/spec.md"],
                    "grounding_summary": {
                        "has_ungrounded_claims": False,
                        "total_evidence_sources": 1,
                    },
                    "confidence_decomposition": {
                        "calibration_status": "descriptive_only",
                        "agreement_score": 0.5,
                        "coverage_posture": "partial",
                        "distinct_perspectives": 2,
                        "evidence_density": 0.5,
                        "evidence_posture": "moderate",
                        "grounding_posture": "not_required",
                        "adversarial_posture": "survived_dissent",
                    },
                    "evolution_suppression_flag": True,
                    "opacity_declaration": "partially_observable",
                },
                "next_action": "review minority signals before widening confidence claims",
                "source": "cli",
                "updated_at": "2026-03-30T00:04:00+00:00",
            }
        ],
    )


SCENARIO_BUILDERS = {
    "clean_pass": _scenario_clean_pass,
    "claim_conflict": _scenario_claim_conflict,
    "stale_compaction": _scenario_stale_compaction,
    "contested_dossier": _scenario_contested_dossier,
}


def build_scenarios(workspace: Path) -> list[dict[str, Any]]:
    workspace.mkdir(parents=True, exist_ok=True)
    scenarios: list[dict[str, Any]] = []
    for name, builder in SCENARIO_BUILDERS.items():
        scenario_root = workspace / name
        builder(scenario_root)
        scenarios.append(
            {
                "name": name,
                "root": scenario_root,
                "state_path": scenario_root / "governance_state.json",
                "traces_path": scenario_root / "session_traces.jsonl",
            }
        )
    return scenarios


def run_session_start(*, agent_id: str, state_path: Path, traces_path: Path) -> dict[str, Any]:
    proc = subprocess.run(
        [
            sys.executable,
            str(START_AGENT_SESSION),
            "--agent",
            agent_id,
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
            "--no-ack",
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(proc.stdout)


def summarize_payload(name: str, payload: dict[str, Any]) -> dict[str, Any]:
    compaction_surface = ((payload.get("import_posture") or {}).get("surfaces") or {}).get("compactions") or {}
    dossier_surface = ((payload.get("import_posture") or {}).get("surfaces") or {}).get("council_dossier") or {}
    interpretation = dossier_surface.get("dossier_interpretation") or {}
    receiver_parity = payload.get("receiver_parity") or {}
    alerts = list((payload.get("import_posture") or {}).get("receiver_alerts") or [])

    return {
        "scenario": name,
        "readiness": ((payload.get("readiness") or {}).get("status") or "unknown"),
        "task_track": ((payload.get("task_track_hint") or {}).get("suggested_track") or "unclassified"),
        "deliberation_mode": ((payload.get("deliberation_mode_hint") or {}).get("suggested_mode") or "unclassified"),
        "working_style_validation": ((payload.get("working_style_validation") or {}).get("status") or "unknown"),
        "receiver_parity_summary": str(receiver_parity.get("summary_text", "")),
        "compaction_import_posture": str(compaction_surface.get("import_posture", "absent")),
        "compaction_receiver_obligation": str(compaction_surface.get("receiver_obligation", "absent")),
        "council_calibration_status": str(interpretation.get("calibration_status", "absent")),
        "council_suppression_flag": bool(interpretation.get("evolution_suppression_flag")),
        "receiver_alert_count": len(alerts),
        "receiver_alerts": alerts,
    }


def render_markdown(results: list[dict[str, Any]]) -> str:
    lines = [
        "# ToneSoul Repeated Live Continuity Validation Wave",
        "",
        "> Generated by `python scripts/run_launch_continuity_validation_wave.py`.",
        "",
        "| Scenario | Readiness | Track | Mode | Style | Compaction posture | Council | Alerts |",
        "|---|---|---|---|---|---|---|---:|",
    ]
    for item in results:
        council = item["council_calibration_status"]
        if item["council_suppression_flag"]:
            council = f"{council} + suppression"
        lines.append(
            "| {scenario} | {readiness} | {task_track} | {deliberation_mode} | "
            "{working_style_validation} | {compaction_import_posture}/{compaction_receiver_obligation} | "
            "{council} | {receiver_alert_count} |".format(
                scenario=item["scenario"],
                readiness=item["readiness"],
                task_track=item["task_track"],
                deliberation_mode=item["deliberation_mode"],
                working_style_validation=item["working_style_validation"],
                compaction_import_posture=item["compaction_import_posture"],
                compaction_receiver_obligation=item["compaction_receiver_obligation"],
                council=council,
                receiver_alert_count=item["receiver_alert_count"],
            )
        )
    lines.append("")
    lines.append("## Receiver Alerts")
    lines.append("")
    for item in results:
        lines.append(f"### {item['scenario']}")
        if not item["receiver_alerts"]:
            lines.append("- none")
        else:
            for alert in item["receiver_alerts"]:
                lines.append(f"- {alert}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def run_validation_wave(workspace: Path) -> list[dict[str, Any]]:
    scenarios = build_scenarios(workspace)
    results: list[dict[str, Any]] = []
    for scenario in scenarios:
        agent_id = f"launch-wave-{scenario['name']}"
        payload = run_session_start(
            agent_id=agent_id,
            state_path=scenario["state_path"],
            traces_path=scenario["traces_path"],
        )
        results.append(summarize_payload(scenario["name"], payload))
    return results


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    results = run_validation_wave(args.workspace)

    if args.json_out is not None:
        _write_json(args.json_out, results)
    if args.markdown_out is not None:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(render_markdown(results), encoding="utf-8")

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
