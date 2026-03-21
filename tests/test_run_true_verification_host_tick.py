from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_true_verification_host_tick.py"
    spec = importlib.util.spec_from_file_location("run_true_verification_host_tick_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_sets_host_tick_defaults() -> None:
    module = _load_module()

    args = module.build_parser().parse_args([])

    assert args.profile == "security_watch"
    assert args.interval_seconds == 0.0
    assert args.max_cycles == 1
    assert args.experiment_days == 7.0
    assert args.wake_interval_hours == 3.0
    assert (
        args.tick_summary_path
        == "docs/status/true_verification_weekly/true_verification_host_tick_latest.json"
    )
    assert args.fresh_experiment_state is False


def test_run_host_tick_delegates_one_cycle_to_long_run(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    parser = module.build_parser()
    tick_summary_path = tmp_path / "true_verification_host_tick_latest.json"

    class DummyLongRunModule:
        def __init__(self) -> None:
            self.args = None

        def run_long_run(self, args):
            self.args = args
            return {
                "overall_ok": True,
                "gate": {"status": "passed"},
                "preflight": {"overall_ok": True},
                "schedule": {
                    "overall_ok": True,
                    "results": [
                        {
                            "cycle": 1,
                            "autonomous_payload": {
                                "overall_ok": True,
                                "runtime_state": {
                                    "session_id": "wakeup-host-001",
                                    "next_cycle": 2,
                                    "consecutive_failures": 1,
                                    "resumed": True,
                                },
                            },
                            "tension_budget": {
                                "status": "breached",
                                "observation": {"max_consecutive_failure_count": 1},
                            },
                        }
                    ],
                },
            }

    dummy = DummyLongRunModule()
    monkeypatch.setattr(module, "_LONG_RUN_MODULE", dummy)
    args = parser.parse_args(["--tick-summary-path", str(tick_summary_path)])

    payload = module.run_host_tick(args)

    assert payload["overall_ok"] is True
    assert payload["experiment"]["host_trigger_mode"] == "single_tick"
    assert payload["experiment"]["max_cycles_per_invocation"] == 1
    assert dummy.args.max_cycles == 1
    assert dummy.args.interval_seconds == pytest.approx(0.0)
    summary_payload = json.loads(tick_summary_path.read_text(encoding="utf-8"))
    assert summary_payload["gate"]["status"] == "passed"
    assert summary_payload["preflight"] == {"overall_ok": True}
    assert summary_payload["schedule"]["result_count"] == 1
    assert (
        summary_payload["schedule"]["latest_result"]["autonomous_payload"]["runtime_state"][
            "session_id"
        ]
        == "wakeup-host-001"
    )
    assert (
        summary_payload["schedule"]["latest_result"]["tension_budget"]["observation"][
            "max_consecutive_failure_count"
        ]
        == 1
    )


def test_run_host_tick_keeps_explicit_operator_overrides(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    parser = module.build_parser()
    tick_summary_path = tmp_path / "true_verification_host_tick_latest.json"

    class DummyLongRunModule:
        def __init__(self) -> None:
            self.args = None

        def run_long_run(self, args):
            self.args = args
            return {"overall_ok": True, "gate": None, "preflight": None, "schedule": None}

    dummy = DummyLongRunModule()
    monkeypatch.setattr(module, "_LONG_RUN_MODULE", dummy)
    args = parser.parse_args(
        [
            "--profile",
            "runtime_probe_watch",
            "--llm-probe-timeout-seconds",
            "5.5",
            "--preflight-llm-probe-timeout-seconds",
            "2.5",
            "--wake-interval-hours",
            "4",
            "--tick-summary-path",
            str(tick_summary_path),
        ]
    )

    payload = module.run_host_tick(args)

    assert payload["overall_ok"] is True
    assert dummy.args.profile == "runtime_probe_watch"
    assert dummy.args.llm_probe_timeout_seconds == pytest.approx(5.5)
    assert dummy.args.preflight_llm_probe_timeout_seconds == pytest.approx(2.5)
    assert payload["experiment"]["wake_interval_hours"] == pytest.approx(4.0)
    assert payload["experiment"]["tick_summary_path"] == str(tick_summary_path)


def test_run_host_tick_resets_experiment_artifacts_when_requested(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    parser = module.build_parser()

    class DummyLongRunModule:
        def run_long_run(self, _args):
            return {"overall_ok": True, "gate": None, "preflight": None, "schedule": None}

    monkeypatch.setattr(module, "_LONG_RUN_MODULE", DummyLongRunModule())
    history_path = tmp_path / "dream_wakeup_history.jsonl"
    snapshot_path = tmp_path / "dream_wakeup_snapshot.json"
    schedule_snapshot_path = tmp_path / "autonomous_registry_schedule_latest.json"
    schedule_history_path = tmp_path / "registry_schedule_history.jsonl"
    schedule_state_path = tmp_path / "registry_schedule_state.json"
    tick_summary_path = tmp_path / "true_verification_host_tick_latest.json"
    experiment_summary_path = tmp_path / "true_verification_experiment_latest.json"
    dashboard_dir = tmp_path / "status"
    dashboard_dir.mkdir()
    for path in (
        history_path,
        snapshot_path,
        schedule_snapshot_path,
        schedule_history_path,
        schedule_state_path,
        tick_summary_path,
        experiment_summary_path,
        dashboard_dir / "dream_observability_latest.json",
        dashboard_dir / "dream_observability_latest.html",
    ):
        path.write_text("stale", encoding="utf-8")

    monkeypatch.setattr(
        module._EXPERIMENT_MODULE,
        "DEFAULT_EXPERIMENT_SUMMARY_PATH",
        str(experiment_summary_path),
    )
    args = parser.parse_args(
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
            "--tick-summary-path",
            str(tick_summary_path),
            "--fresh-experiment-state",
        ]
    )

    module.run_host_tick(args)

    assert history_path.exists() is False
    assert schedule_history_path.exists() is False
    assert schedule_state_path.exists() is False
    assert experiment_summary_path.exists() is False
    assert tick_summary_path.exists() is True
    assert (dashboard_dir / "dream_observability_latest.json").exists() is False
    assert (dashboard_dir / "dream_observability_latest.html").exists() is False


def test_run_host_tick_rejects_non_positive_declared_interval() -> None:
    module = _load_module()
    args = module.build_parser().parse_args(["--wake-interval-hours", "0"])

    with pytest.raises(ValueError, match="wake_interval_hours must be > 0"):
        module.run_host_tick(args)


def test_main_strict_returns_non_zero_when_tick_not_ok(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "run_host_tick",
        lambda _args: {"overall_ok": False, "experiment": {}, "gate": None},
    )

    exit_code = module.main(["--strict"])

    assert exit_code == 1
