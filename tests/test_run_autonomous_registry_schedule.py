from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_autonomous_registry_schedule.py"
    spec = importlib.util.spec_from_file_location("run_autonomous_registry_schedule_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_parses_registry_schedule_args() -> None:
    module = _load_module()

    args = module.build_parser().parse_args(
        [
            "--profile",
            "security_watch",
            "--registry-id",
            "alpha",
            "--registry-category",
            "research",
            "--entries-per-cycle",
            "2",
            "--urls-per-cycle",
            "4",
            "--revisit-interval-cycles",
            "3",
            "--failure-backoff-cycles",
            "2",
            "--category-weight",
            "research=5",
            "--category-backoff-multiplier",
            "research=4",
            "--tension-max-friction-score",
            "0.9",
            "--tension-max-lyapunov-proxy",
            "0.3",
            "--tension-max-council-count",
            "2",
            "--tension-max-llm-preflight-latency-ms",
            "1800",
            "--tension-max-llm-selection-latency-ms",
            "700",
            "--tension-max-llm-probe-latency-ms",
            "1200",
            "--tension-max-llm-timeout-count",
            "0",
            "--tension-max-consecutive-failure-count",
            "2",
            "--tension-cooldown-cycles",
            "4",
            "--schedule-state-path",
            "memory/autonomous/state.json",
            "--strict",
            "--no-llm",
        ]
    )

    assert args.profile == "security_watch"
    assert args.registry_id == ["alpha"]
    assert args.registry_category == ["research"]
    assert args.entries_per_cycle == 2
    assert args.urls_per_cycle == 4
    assert args.revisit_interval_cycles == 3
    assert args.failure_backoff_cycles == 2
    assert args.category_weight == ["research=5"]
    assert args.category_backoff_multiplier == ["research=4"]
    assert args.tension_max_friction_score == 0.9
    assert args.tension_max_lyapunov_proxy == 0.3
    assert args.tension_max_council_count == 2
    assert args.tension_max_llm_preflight_latency_ms == 1800
    assert args.tension_max_llm_selection_latency_ms == 700
    assert args.tension_max_llm_probe_latency_ms == 1200
    assert args.tension_max_llm_timeout_count == 0
    assert args.tension_max_consecutive_failure_count == 2
    assert args.tension_cooldown_cycles == 4
    assert args.schedule_state_path == "memory/autonomous/state.json"
    assert args.strict is True
    assert args.no_llm is True
    assert args.skip_llm_preflight is False


def test_run_schedule_delegates_to_schedule_builder(monkeypatch) -> None:
    module = _load_module()

    class DummyProfile:
        registry_entry_ids = ["profile_alpha"]
        registry_categories = ["profile_research"]
        include_stale = False
        interval_seconds = 7200.0
        entries_per_cycle = 3
        urls_per_cycle = 5
        revisit_interval_cycles = 4
        failure_backoff_cycles = 6
        category_weights = {"profile_research": 2, "profile_news": 1}
        category_backoff_multipliers = {"profile_research": 3}
        tension_max_friction_score = 0.72
        tension_max_lyapunov_proxy = 0.18
        tension_max_council_count = 1
        tension_max_llm_preflight_latency_ms = 1600
        tension_max_llm_selection_latency_ms = 600
        tension_max_llm_probe_latency_ms = 1100
        tension_max_llm_timeout_count = 0
        tension_max_consecutive_failure_count = None
        tension_cooldown_cycles = 2
        limit = 4
        min_priority = 0.22
        related_limit = 7
        crystal_count = 8

        def to_dict(self):
            return {"name": "security_watch"}

    class DummySchedule:
        def __init__(self) -> None:
            self.calls = []

        def run(self, **kwargs):
            self.calls.append(kwargs)
            return {"overall_ok": True, "results": [{"cycle": 1}]}

    dummy_schedule = DummySchedule()
    monkeypatch.setattr(
        module,
        "build_autonomous_registry_schedule",
        lambda **kwargs: dummy_schedule,
    )
    monkeypatch.setattr(module, "resolve_schedule_profile", lambda *args: DummyProfile())

    payload = module.run_schedule(
        module.build_parser().parse_args(
            [
                "--profile",
                "security_watch",
                "--registry-id",
                "alpha",
                "--urls-per-cycle",
                "4",
                "--revisit-interval-cycles",
                "1",
                "--category-weight",
                "profile_news=5",
                "--category-backoff-multiplier",
                "profile_research=4",
                "--tension-max-friction-score",
                "0.8",
                "--tension-max-llm-probe-latency-ms",
                "1250",
                "--tension-max-consecutive-failure-count",
                "1",
                "--tension-cooldown-cycles",
                "5",
                "--skip-llm-preflight",
            ]
        )
    )

    assert payload == {
        "overall_ok": True,
        "results": [{"cycle": 1}],
        "profile": {"name": "security_watch"},
    }
    assert dummy_schedule.calls[0]["entry_ids"] == ["alpha"]
    assert dummy_schedule.calls[0]["categories"] == ["profile_research"]
    assert dummy_schedule.calls[0]["entries_per_cycle"] == 3
    assert dummy_schedule.calls[0]["urls_per_cycle"] == 4
    assert dummy_schedule.calls[0]["revisit_interval_cycles"] == 1
    assert dummy_schedule.calls[0]["failure_backoff_cycles"] == 6
    assert dummy_schedule.calls[0]["category_weights"] == {
        "profile_research": 2,
        "profile_news": 5,
    }
    assert dummy_schedule.calls[0]["category_backoff_multipliers"] == {
        "profile_research": 4,
    }
    assert dummy_schedule.calls[0]["tension_max_friction_score"] == 0.8
    assert dummy_schedule.calls[0]["tension_max_lyapunov_proxy"] == 0.18
    assert dummy_schedule.calls[0]["tension_max_council_count"] == 1
    assert dummy_schedule.calls[0]["tension_max_llm_preflight_latency_ms"] == 1600
    assert dummy_schedule.calls[0]["tension_max_llm_selection_latency_ms"] == 600
    assert dummy_schedule.calls[0]["tension_max_llm_probe_latency_ms"] == 1250
    assert dummy_schedule.calls[0]["tension_max_llm_timeout_count"] == 0
    assert dummy_schedule.calls[0]["tension_max_consecutive_failure_count"] == 1
    assert dummy_schedule.calls[0]["tension_cooldown_cycles"] == 5
    assert dummy_schedule.calls[0]["cycle_kwargs"]["limit"] == 4
    assert dummy_schedule.calls[0]["cycle_kwargs"]["min_priority"] == 0.22
    assert dummy_schedule.calls[0]["cycle_kwargs"]["generate_reflection"] is True
    assert dummy_schedule.calls[0]["cycle_kwargs"]["require_inference_ready"] is False
    assert dummy_schedule.calls[0]["cycle_kwargs"]["inference_timeout_seconds"] == 10.0


def test_main_strict_returns_non_zero_when_schedule_payload_not_ok(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()

    class DummySchedule:
        def run(self, **kwargs):
            return {"overall_ok": False, "results": []}

    monkeypatch.setattr(
        module,
        "build_autonomous_registry_schedule",
        lambda **kwargs: DummySchedule(),
    )
    monkeypatch.setattr("sys.argv", ["run_autonomous_registry_schedule.py", "--strict"])

    exit_code = module.main()

    assert exit_code == 1
