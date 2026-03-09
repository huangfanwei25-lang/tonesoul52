from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_runtime_probe_watch.py"
    spec = importlib.util.spec_from_file_location("run_runtime_probe_watch_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_sets_runtime_probe_defaults() -> None:
    module = _load_module()

    args = module.build_parser().parse_args([])

    assert args.history_path == "memory/autonomous/runtime_probe_watch/dream_wakeup_history.jsonl"
    assert args.snapshot_path == "docs/status/runtime_probe_watch/dream_wakeup_snapshot.json"
    assert args.dashboard_out_dir == "docs/status/runtime_probe_watch"
    assert (
        args.schedule_snapshot_path
        == "docs/status/runtime_probe_watch/autonomous_registry_schedule_latest.json"
    )
    assert (
        args.schedule_history_path
        == "memory/autonomous/runtime_probe_watch/registry_schedule_history.jsonl"
    )
    assert (
        args.schedule_state_path
        == "memory/autonomous/runtime_probe_watch/registry_schedule_state.json"
    )
    assert args.interval_seconds == 0.0
    assert args.max_cycles == 2
    assert args.llm_probe_timeout_seconds == 2.0
    assert args.reuse_state is False
    assert args.skip_llm_preflight is False


def test_run_runtime_probe_delegates_to_generic_schedule_runner(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    snapshot_path = tmp_path / "runtime_probe_schedule_snapshot.json"

    class DummyScheduleModule:
        def __init__(self) -> None:
            self.args = None

        def run_schedule(self, args):
            self.args = args
            return {"overall_ok": True, "results": [{"cycle": 1}]}

    dummy = DummyScheduleModule()
    monkeypatch.setattr(module, "_SCHEDULE_MODULE", dummy)
    args = module.build_parser().parse_args(
        [
            "--max-cycles",
            "3",
            "--interval-seconds",
            "5",
            "--schedule-snapshot-path",
            str(snapshot_path),
            "--llm-probe-timeout-seconds",
            "4.5",
            "--no-llm",
        ]
    )

    payload = module.run_runtime_probe(args)

    assert payload == {
        "overall_ok": True,
        "results": [{"cycle": 1}],
        "preflight_profile": "runtime_probe_watch",
    }
    assert dummy.args.profile == "runtime_probe_watch"
    assert dummy.args.interval_seconds == 5.0
    assert dummy.args.max_cycles == 3
    assert dummy.args.llm_probe_timeout_seconds == 4.5
    assert dummy.args.no_llm is True
    assert dummy.args.skip_llm_preflight is False
    assert dummy.args.registry_id == []
    assert dummy.args.registry_category == []
    snapshot_payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    assert snapshot_payload["preflight_profile"] == "runtime_probe_watch"


def test_run_runtime_probe_resets_artifacts_by_default(monkeypatch, tmp_path: Path) -> None:
    module = _load_module()

    class DummyScheduleModule:
        def run_schedule(self, _args):
            return {"overall_ok": True, "results": []}

    monkeypatch.setattr(module, "_SCHEDULE_MODULE", DummyScheduleModule())
    history_path = tmp_path / "dream_wakeup_history.jsonl"
    snapshot_path = tmp_path / "dream_wakeup_snapshot.json"
    schedule_snapshot_path = tmp_path / "autonomous_registry_schedule_latest.json"
    schedule_history_path = tmp_path / "registry_schedule_history.jsonl"
    schedule_state_path = tmp_path / "registry_schedule_state.json"
    dashboard_dir = tmp_path / "status"
    dashboard_dir.mkdir()
    for path in (
        history_path,
        snapshot_path,
        schedule_snapshot_path,
        schedule_history_path,
        schedule_state_path,
        dashboard_dir / "dream_observability_latest.json",
        dashboard_dir / "dream_observability_latest.html",
    ):
        path.write_text("stale", encoding="utf-8")

    args = module.build_parser().parse_args(
        [
            "--history-path",
            str(history_path),
            "--snapshot-path",
            str(snapshot_path),
            "--schedule-snapshot-path",
            str(schedule_snapshot_path),
            "--schedule-history-path",
            str(schedule_history_path),
            "--schedule-state-path",
            str(schedule_state_path),
            "--dashboard-out-dir",
            str(dashboard_dir),
        ]
    )

    module.run_runtime_probe(args)

    assert history_path.exists() is False
    assert schedule_history_path.exists() is False
    assert schedule_state_path.exists() is False
    assert (dashboard_dir / "dream_observability_latest.json").exists() is False
    assert (dashboard_dir / "dream_observability_latest.html").exists() is False
    snapshot_payload = json.loads(schedule_snapshot_path.read_text(encoding="utf-8"))
    assert snapshot_payload["preflight_profile"] == "runtime_probe_watch"


def test_main_strict_returns_non_zero_when_probe_payload_not_ok(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "run_runtime_probe",
        lambda _args: {"overall_ok": False, "results": []},
    )

    exit_code = module.main(["--strict"])

    assert exit_code == 1
