from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_dream_engine.py"
    spec = importlib.util.spec_from_file_location("run_dream_engine_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_parses_no_llm_flag() -> None:
    module = _load_module()
    args = module.build_parser().parse_args(["--limit", "2", "--no-llm"])
    assert args.limit == 2
    assert args.no_llm is True
    assert args.skip_llm_preflight is False


def test_run_engine_delegates_to_dream_engine(monkeypatch) -> None:
    module = _load_module()

    class DummyResult:
        def to_dict(self):
            return {"stimuli_selected": 1}

    class DummyEngine:
        def __init__(self) -> None:
            self.kwargs = None

        def run_cycle(self, **kwargs):
            self.kwargs = kwargs
            return DummyResult()

    dummy_engine = DummyEngine()
    monkeypatch.setattr(module, "build_dream_engine", lambda **kwargs: dummy_engine)
    args = module.build_parser().parse_args(["--no-llm", "--limit", "1"])

    payload = module.run_engine(args)

    assert payload == {"stimuli_selected": 1}
    assert dummy_engine.kwargs["limit"] == 1
    assert dummy_engine.kwargs["generate_reflection"] is False
    assert dummy_engine.kwargs["require_inference_ready"] is False


def test_run_engine_can_skip_llm_preflight_without_disabling_reflection(monkeypatch) -> None:
    module = _load_module()

    class DummyResult:
        def to_dict(self):
            return {"stimuli_selected": 1}

    class DummyEngine:
        def __init__(self) -> None:
            self.kwargs = None

        def run_cycle(self, **kwargs):
            self.kwargs = kwargs
            return DummyResult()

    dummy_engine = DummyEngine()
    monkeypatch.setattr(module, "build_dream_engine", lambda **kwargs: dummy_engine)
    args = module.build_parser().parse_args(
        ["--limit", "1", "--skip-llm-preflight", "--llm-probe-timeout-seconds", "4.5"]
    )

    payload = module.run_engine(args)

    assert payload == {"stimuli_selected": 1}
    assert dummy_engine.kwargs["generate_reflection"] is True
    assert dummy_engine.kwargs["require_inference_ready"] is False
    assert dummy_engine.kwargs["inference_timeout_seconds"] == 4.5
