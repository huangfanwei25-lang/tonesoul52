from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_true_verification_experiment.py"
    spec = importlib.util.spec_from_file_location("run_true_verification_experiment_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_sets_weekly_true_verification_defaults() -> None:
    module = _load_module()

    args = module.build_parser().parse_args([])

    assert args.profile == "security_watch"
    assert args.max_cycles is None
    assert args.experiment_days == 7.0
    assert args.wake_interval_hours == 3.0
    assert (
        args.history_path == "memory/autonomous/true_verification_weekly/dream_wakeup_history.jsonl"
    )
    assert args.snapshot_path == "docs/status/true_verification_weekly/dream_wakeup_snapshot.json"
    assert args.dashboard_out_dir == "docs/status/true_verification_weekly"
    assert args.preflight_dashboard_out_dir == "docs/status/true_verification_weekly/preflight"
    assert args.reuse_experiment_state is False


def test_run_experiment_derives_weekly_cadence_and_writes_summary(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    parser = module.build_parser()
    summary_path = tmp_path / "true_verification_experiment_latest.json"

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
                                    "session_id": "wakeup-exp-001",
                                    "next_cycle": 2,
                                    "consecutive_failures": 0,
                                    "resumed": False,
                                },
                            },
                            "tension_budget": {
                                "status": "ok",
                                "observation": {"max_consecutive_failure_count": 0},
                            },
                        }
                    ],
                },
            }

    dummy = DummyLongRunModule()
    monkeypatch.setattr(module, "_LONG_RUN_MODULE", dummy)
    args = parser.parse_args(
        [
            "--experiment-summary-path",
            str(summary_path),
        ]
    )

    payload = module.run_experiment(args)

    assert payload["overall_ok"] is True
    assert payload["experiment"]["name"] == "true_verification_weekly"
    assert payload["experiment"]["planned_cycles"] == 56
    assert payload["experiment"]["interval_seconds"] == pytest.approx(10800.0)
    assert dummy.args.profile == "security_watch"
    assert dummy.args.max_cycles == 56
    assert dummy.args.interval_seconds == pytest.approx(10800.0)
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary_payload["experiment"]["planned_cycles"] == 56
    assert summary_payload["gate"]["status"] == "passed"
    assert summary_payload["preflight"] == {"overall_ok": True}
    assert summary_payload["schedule"]["result_count"] == 1
    assert (
        summary_payload["schedule"]["latest_result"]["autonomous_payload"]["runtime_state"][
            "session_id"
        ]
        == "wakeup-exp-001"
    )
    assert (
        summary_payload["schedule"]["latest_result"]["tension_budget"]["observation"][
            "max_consecutive_failure_count"
        ]
        == 0
    )


def test_run_experiment_keeps_explicit_schedule_overrides(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_module()
    parser = module.build_parser()
    summary_path = tmp_path / "true_verification_experiment_latest.json"

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
            "--max-cycles",
            "4",
            "--interval-seconds",
            "30",
            "--experiment-days",
            "9",
            "--wake-interval-hours",
            "1.5",
            "--experiment-summary-path",
            str(summary_path),
        ]
    )

    payload = module.run_experiment(args)

    assert payload["overall_ok"] is True
    assert dummy.args.profile == "runtime_probe_watch"
    assert dummy.args.max_cycles == 4
    assert dummy.args.interval_seconds == pytest.approx(30.0)
    assert payload["experiment"]["planned_cycles"] == 4
    assert payload["experiment"]["interval_seconds"] == pytest.approx(30.0)
    assert payload["experiment"]["summary_path"] == str(summary_path)


def test_run_experiment_resets_long_run_artifacts_by_default(monkeypatch, tmp_path: Path) -> None:
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
    summary_path = tmp_path / "true_verification_experiment_latest.json"
    dashboard_dir = tmp_path / "status"
    dashboard_dir.mkdir()
    for path in (
        history_path,
        snapshot_path,
        schedule_snapshot_path,
        schedule_history_path,
        schedule_state_path,
        summary_path,
        dashboard_dir / "dream_observability_latest.json",
        dashboard_dir / "dream_observability_latest.html",
    ):
        path.write_text("stale", encoding="utf-8")

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
            "--experiment-summary-path",
            str(summary_path),
        ]
    )

    module.run_experiment(args)

    assert history_path.exists() is False
    assert schedule_history_path.exists() is False
    assert schedule_state_path.exists() is False
    assert summary_path.exists() is True
    assert (dashboard_dir / "dream_observability_latest.json").exists() is False
    assert (dashboard_dir / "dream_observability_latest.html").exists() is False
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary_payload["experiment"]["name"] == "true_verification_weekly"


def test_run_experiment_rejects_non_positive_duration() -> None:
    module = _load_module()
    args = module.build_parser().parse_args(["--experiment-days", "0"])

    with pytest.raises(ValueError, match="experiment_days must be > 0"):
        module.run_experiment(args)


def test_main_strict_returns_non_zero_when_experiment_not_ok(monkeypatch) -> None:
    module = _load_module()
    monkeypatch.setattr(
        module,
        "run_experiment",
        lambda _args: {"overall_ok": False, "experiment": {}, "gate": None},
    )

    exit_code = module.main(["--strict"])

    assert exit_code == 1
