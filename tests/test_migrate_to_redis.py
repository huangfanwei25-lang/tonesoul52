from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_script_module():
    module_name = "test_migrate_to_redis_module"
    module_path = Path(__file__).resolve().parents[1] / "scripts" / "migrate_to_redis.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class _StubFileStore:
    def __init__(self, state, traces, zones) -> None:
        self._state = state
        self._traces = traces
        self._zones = zones

    def get_state(self):
        return self._state

    def get_traces(self, n: int = 10000):
        assert n == 10000
        return self._traces

    def get_zones(self):
        return self._zones


def test_build_parser_sets_expected_defaults() -> None:
    module = _load_script_module()
    args = module.build_parser().parse_args([])

    assert args.url == "redis://localhost:6379/0"
    assert args.dry_run is False


def test_summarize_source_reports_presence_and_trace_count() -> None:
    module = _load_script_module()
    summary = module.summarize_source(
        _StubFileStore(
            state={"soul_integral": 0.6},
            traces=[{"session_id": "s1"}, {"session_id": "s2"}],
            zones={"default": {"mode": "file"}},
        )
    )

    assert summary == {
        "has_governance_state": True,
        "trace_count": 2,
        "has_zones": True,
    }
