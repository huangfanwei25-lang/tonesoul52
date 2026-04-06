from __future__ import annotations

import json
from pathlib import Path

from scripts.start_agent_session import run_session_start_bundle
from tonesoul.observer_window import build_low_drift_anchor


def _write_state(state_path: Path) -> None:
    state_path.write_text(
        json.dumps(
            {
                "version": "0.1.0",
                "last_updated": "2026-04-07T00:00:00+00:00",
                "soul_integral": 0.61,
                "tension_history": [],
                "active_vows": [],
                "aegis_vetoes": [],
                "baseline_drift": {
                    "caution_bias": 0.5,
                    "innovation_bias": 0.5,
                    "autonomy_level": 0.4,
                },
                "session_count": 4,
            }
        ),
        encoding="utf-8",
    )


def _write_traces(traces_path: Path) -> None:
    traces_path.write_text(
        json.dumps(
            {
                "session_id": "sess-shell-guard",
                "agent": "codex",
                "timestamp": "2026-04-07T00:01:00+00:00",
                "topics": ["self-improvement"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["guard first-hop shells"],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_self_improvement_cue_stays_out_of_session_start_and_packet(tmp_path: Path) -> None:
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    _write_state(state_path)
    _write_traces(traces_path)

    tier0 = run_session_start_bundle(
        agent_id="cue-shell-guard",
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=0,
    )
    tier1 = run_session_start_bundle(
        agent_id="cue-shell-guard",
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=1,
    )
    tier2 = run_session_start_bundle(
        agent_id="cue-shell-guard",
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=2,
    )

    assert "self_improvement" not in tier0
    assert "self_improvement" not in tier1
    assert "self_improvement" not in tier2
    assert "self_improvement" not in (tier2.get("packet") or {})


def test_self_improvement_cue_stays_out_of_observer_window(tmp_path: Path) -> None:
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    _write_state(state_path)
    _write_traces(traces_path)

    tier2 = run_session_start_bundle(
        agent_id="cue-shell-guard",
        state_path=state_path,
        traces_path=traces_path,
        no_ack=True,
        tier=2,
    )
    observer_window = build_low_drift_anchor(
        packet=tier2["packet"],
        import_posture=(tier2.get("import_posture") or {}).get("surfaces") or {},
        readiness=tier2["readiness"],
        canonical_center=tier2["canonical_center"],
        subsystem_parity=tier2["subsystem_parity"],
        mutation_preflight=tier2["mutation_preflight"],
    )

    assert "self_improvement" not in observer_window
    assert "improvement_cue" not in observer_window
