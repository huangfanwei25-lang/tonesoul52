from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_run_r_memory_packet_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "run_r_memory_packet.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_run_r_memory_packet_emits_json(capsys, monkeypatch, tmp_path: Path) -> None:
    module = _load_script_module()
    state_path = tmp_path / "governance_state.json"
    traces_path = tmp_path / "session_traces.jsonl"
    sidecar_dir = tmp_path / ".aegis"
    claims_path = sidecar_dir / "task_claims.json"
    compactions_path = sidecar_dir / "compacted.json"
    state_path.write_text(
        json.dumps(
            {
                "version": "0.1.0",
                "last_updated": "2026-03-26T00:00:00+00:00",
                "soul_integral": 0.6,
                "tension_history": [],
                "active_vows": [],
                "aegis_vetoes": [],
                "baseline_drift": {
                    "caution_bias": 0.5,
                    "innovation_bias": 0.6,
                    "autonomy_level": 0.35,
                },
                "session_count": 4,
            }
        ),
        encoding="utf-8",
    )
    traces_path.write_text(
        json.dumps(
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-26T00:01:00+00:00",
                "topics": ["runtime"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["emit packet"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    claims_path.write_text(
        json.dumps(
            {
                "task-1": {
                    "task_id": "task-1",
                    "agent": "codex",
                    "summary": "sync gateway packet",
                    "paths": ["scripts/gateway.py"],
                    "source": "cli",
                    "created_at": "2026-03-26T00:02:00+00:00",
                    "expires_at": "4070908920.0",
                }
            }
        ),
        encoding="utf-8",
    )
    compactions_path.write_text(
        json.dumps(
            [
                {
                    "compaction_id": "cmp-1",
                    "agent": "codex",
                    "session_id": "sess-1",
                    "summary": "Packet-first handoff summary.",
                    "carry_forward": ["read packet before long prose"],
                    "pending_paths": ["scripts/gateway.py"],
                    "evidence_refs": [
                        "docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md"
                    ],
                    "next_action": "keep compaction non-canonical",
                    "source": "cli",
                    "updated_at": "2026-03-26T00:03:00+00:00",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_r_memory_packet.py",
            "--state-path",
            str(state_path),
            "--traces-path",
            str(traces_path),
        ],
    )

    module.main()
    output = json.loads(capsys.readouterr().out)
    assert output["contract_version"] == "v1"
    assert output["posture"]["session_count"] == 4
    assert set(output["posture"]["risk_posture"]) >= {"score", "level", "recommended_action"}
    assert "project_memory_summary" in output
    assert "repo_progress" in output["project_memory_summary"]
    assert output["recent_traces"][0]["agent"] == "codex"
    assert output["active_claims"][0]["task_id"] == "task-1"
    assert output["recent_compactions"][0]["compaction_id"] == "cmp-1"


def test_ensure_repo_root_on_path_adds_repo_root(monkeypatch) -> None:
    module = _load_script_module()
    repo_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != repo_root])

    resolved = module._ensure_repo_root_on_path()

    assert str(resolved) == repo_root
    assert sys.path[0] == repo_root
