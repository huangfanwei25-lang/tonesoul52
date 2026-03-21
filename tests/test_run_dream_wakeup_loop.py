from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from tonesoul.wakeup_loop import WakeupCycleResult


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_dream_wakeup_loop.py"
    spec = importlib.util.spec_from_file_location("run_dream_wakeup_loop_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_parses_interval_and_snapshot_paths(tmp_path: Path) -> None:
    module = _load_module()
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    args = module.build_parser().parse_args(
        [
            "--interval-seconds",
            "1800",
            "--max-cycles",
            "2",
            "--consolidate-every-cycles",
            "4",
            "--failure-threshold",
            "5",
            "--failure-pause-seconds",
            "7200",
            "--snapshot-path",
            str(snapshot_path),
            "--history-path",
            str(history_path),
        ]
    )

    assert args.interval_seconds == 1800
    assert args.max_cycles == 2
    assert args.consolidate_every_cycles == 4
    assert args.failure_threshold == 5
    assert args.failure_pause_seconds == 7200
    assert args.snapshot_path == str(snapshot_path)
    assert args.history_path == str(history_path)
    assert args.skip_llm_preflight is False


def test_run_wakeup_loop_writes_snapshot_and_history(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()
    snapshot_path = tmp_path / "latest.json"
    history_path = tmp_path / "history.jsonl"

    class DummyLoop:
        def __init__(self) -> None:
            self.calls = []

        def run(self, **kwargs):
            self.calls.append(kwargs)
            return [
                WakeupCycleResult(
                    cycle=1,
                    status="ok",
                    started_at="2026-03-07T18:00:00Z",
                    finished_at="2026-03-07T18:00:01Z",
                    duration_ms=1000,
                    interval_seconds=3600.0,
                    dream_result={"stimuli_selected": 1, "stimuli_considered": 2, "collisions": []},
                    summary={
                        "stimuli_considered": 2,
                        "stimuli_selected": 1,
                        "collision_count": 0,
                        "council_count": 0,
                        "frozen_count": 0,
                        "avg_friction_score": None,
                        "max_friction_score": None,
                        "max_lyapunov_proxy": None,
                    },
                )
            ]

        def get_runtime_state_snapshot(self):
            return {
                "session_id": "wakeup_test_session",
                "next_cycle": 2,
                "consecutive_failures": 0,
                "resumed": False,
                "state_path": "memory/autonomous/dream_wakeup_state.json",
            }

    dummy_loop = DummyLoop()
    monkeypatch.setattr(module, "build_autonomous_wakeup_loop", lambda **kwargs: dummy_loop)
    args = module.build_parser().parse_args(
        [
            "--interval-seconds",
            "3600",
            "--max-cycles",
            "2",
            "--no-llm",
            "--snapshot-path",
            str(snapshot_path),
            "--history-path",
            str(history_path),
        ]
    )

    payload = module.run_wakeup_loop(args)

    assert payload["overall_status"] == "ok"
    assert dummy_loop.calls[0]["max_cycles"] == 2
    assert dummy_loop.calls[0]["dream_kwargs"]["generate_reflection"] is False
    assert dummy_loop.calls[0]["dream_kwargs"]["require_inference_ready"] is False
    assert payload["config"]["consolidate_every_cycles"] == 3
    assert payload["config"]["failure_threshold"] == 3
    assert payload["config"]["failure_pause_seconds"] == 3600.0

    snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot_payload["overall_status"] == "ok"
    assert snapshot_payload["config"]["consolidate_every_cycles"] == 3
    assert len(snapshot_payload["results"]) == 1

    history_lines = history_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(history_lines) == 1
    assert json.loads(history_lines[0])["status"] == "ok"
