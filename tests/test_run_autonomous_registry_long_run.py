from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_autonomous_registry_long_run.py"
    spec = importlib.util.spec_from_file_location("run_autonomous_registry_long_run_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_includes_runtime_probe_gate_options() -> None:
    module = _load_module()

    args = module.build_parser().parse_args(["--profile", "security_watch"])

    assert args.profile == "security_watch"
    assert args.skip_runtime_probe_watch is False
    assert args.reuse_runtime_probe_state is False
    assert args.preflight_max_cycles == 2
    assert args.preflight_llm_probe_timeout_seconds == 2.0
    assert args.llm_probe_timeout_seconds is None
    assert (
        args.preflight_schedule_snapshot_path
        == "docs/status/runtime_probe_watch/autonomous_registry_schedule_latest.json"
    )


def test_run_long_run_blocks_schedule_when_runtime_probe_fails(monkeypatch) -> None:
    module = _load_module()
    args = module.build_parser().parse_args(["--profile", "security_watch"])

    class DummyPreflightModule:
        PROFILE_NAME = "runtime_probe_watch"

        def run_runtime_probe(self, _args):
            return {"overall_ok": False, "results": []}

    class DummyScheduleModule:
        def __init__(self) -> None:
            self.called = False

        def build_parser(self):
            raise AssertionError("unused in test")

        def run_schedule(self, _args):
            self.called = True
            return {"overall_ok": True}

    dummy_schedule = DummyScheduleModule()
    monkeypatch.setattr(module, "_PREFLIGHT_MODULE", DummyPreflightModule())
    monkeypatch.setattr(module, "_SCHEDULE_MODULE", dummy_schedule)

    payload = module.run_long_run(args)

    assert payload["overall_ok"] is False
    assert payload["gate"]["status"] == "blocked"
    assert payload["gate"]["reason"] == "runtime_probe_failed"
    assert payload["schedule"] is None
    assert dummy_schedule.called is False


def test_run_long_run_delegates_to_preflight_then_schedule(monkeypatch) -> None:
    module = _load_module()
    args = module.build_parser().parse_args(
        [
            "--profile",
            "security_watch",
            "--max-cycles",
            "4",
            "--preflight-max-cycles",
            "3",
            "--preflight-llm-probe-timeout-seconds",
            "4.5",
        ]
    )

    class DummyPreflightModule:
        PROFILE_NAME = "runtime_probe_watch"

        def __init__(self) -> None:
            self.args = None

        def run_runtime_probe(self, args):
            self.args = args
            return {"overall_ok": True, "preflight_profile": "runtime_probe_watch"}

    class DummyScheduleModule:
        def __init__(self) -> None:
            self.args = None

        def run_schedule(self, args):
            self.args = args
            return {"overall_ok": True, "results": [{"cycle": 1}]}

    dummy_preflight = DummyPreflightModule()
    dummy_schedule = DummyScheduleModule()
    monkeypatch.setattr(module, "_PREFLIGHT_MODULE", dummy_preflight)
    monkeypatch.setattr(module, "_SCHEDULE_MODULE", dummy_schedule)

    payload = module.run_long_run(args)

    assert payload["overall_ok"] is True
    assert payload["gate"] == {
        "status": "passed",
        "reason": "runtime_probe_ok",
        "profile": "runtime_probe_watch",
    }
    assert payload["preflight"] == {
        "overall_ok": True,
        "preflight_profile": "runtime_probe_watch",
    }
    assert payload["schedule"] == {"overall_ok": True, "results": [{"cycle": 1}]}
    assert dummy_preflight.args.max_cycles == 3
    assert dummy_preflight.args.llm_probe_timeout_seconds == 4.5
    assert dummy_preflight.args.reuse_state is False
    assert dummy_schedule.args.profile == "security_watch"
    assert dummy_schedule.args.max_cycles == 4
    assert dummy_schedule.args.llm_probe_timeout_seconds == 4.5


def test_run_long_run_skips_runtime_probe_when_llm_disabled(monkeypatch) -> None:
    module = _load_module()
    args = module.build_parser().parse_args(["--profile", "security_watch", "--no-llm"])

    class DummyPreflightModule:
        PROFILE_NAME = "runtime_probe_watch"

        def run_runtime_probe(self, _args):
            raise AssertionError("preflight should be skipped when no-llm is set")

    class DummyScheduleModule:
        def run_schedule(self, _args):
            return {"overall_ok": True, "results": []}

    monkeypatch.setattr(module, "_PREFLIGHT_MODULE", DummyPreflightModule())
    monkeypatch.setattr(module, "_SCHEDULE_MODULE", DummyScheduleModule())

    payload = module.run_long_run(args)

    assert payload["overall_ok"] is True
    assert payload["gate"] == {
        "status": "skipped",
        "reason": "llm_disabled",
        "profile": "runtime_probe_watch",
    }
    assert payload["preflight"] is None


def test_run_long_run_keeps_explicit_schedule_probe_timeout(monkeypatch) -> None:
    module = _load_module()
    args = module.build_parser().parse_args(
        [
            "--profile",
            "security_watch",
            "--llm-probe-timeout-seconds",
            "6.5",
            "--preflight-llm-probe-timeout-seconds",
            "2.5",
        ]
    )

    class DummyPreflightModule:
        PROFILE_NAME = "runtime_probe_watch"

        def run_runtime_probe(self, _args):
            return {"overall_ok": True}

    class DummyScheduleModule:
        def __init__(self) -> None:
            self.args = None

        def run_schedule(self, args):
            self.args = args
            return {"overall_ok": True, "results": []}

    dummy_schedule = DummyScheduleModule()
    monkeypatch.setattr(module, "_PREFLIGHT_MODULE", DummyPreflightModule())
    monkeypatch.setattr(module, "_SCHEDULE_MODULE", dummy_schedule)

    payload = module.run_long_run(args)

    assert payload["overall_ok"] is True
    assert dummy_schedule.args.llm_probe_timeout_seconds == 6.5
