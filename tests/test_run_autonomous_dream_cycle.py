from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def _load_module():
    path = Path(__file__).resolve().parents[1] / "scripts" / "run_autonomous_dream_cycle.py"
    spec = importlib.util.spec_from_file_location("run_autonomous_dream_cycle_script", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_parser_parses_url_file_and_strict_flags(tmp_path: Path) -> None:
    module = _load_module()
    url_file = tmp_path / "urls.txt"
    state_path = tmp_path / "state.json"
    scribe_state_path = tmp_path / "scribe_state.json"

    args = module.build_parser().parse_args(
        [
            "--url",
            "https://example.com/a",
            "--url-file",
            str(url_file),
            "--registry-path",
            "spec/external_source_registry.yaml",
            "--registry-id",
            "alpha",
            "--state-path",
            str(state_path),
            "--disable-scribe",
            "--scribe-state-path",
            str(scribe_state_path),
            "--strict",
            "--no-llm",
        ]
    )

    assert args.url == ["https://example.com/a"]
    assert args.url_file == str(url_file)
    assert args.registry_path == "spec/external_source_registry.yaml"
    assert args.registry_id == ["alpha"]
    assert args.state_path == str(state_path)
    assert args.disable_scribe is True
    assert args.scribe_state_path == str(scribe_state_path)
    assert args.strict is True
    assert args.no_llm is True
    assert args.skip_llm_preflight is False


def test_run_cycle_delegates_to_runner_and_merges_url_file_and_registry(
    monkeypatch, tmp_path: Path
) -> None:
    module = _load_module()
    url_file = tmp_path / "urls.txt"
    url_file.write_text(
        "https://example.com/b\n# comment\nhttps://example.com/c\n", encoding="utf-8"
    )
    builder_calls: list[dict[str, object]] = []

    class DummyResult:
        def to_dict(self):
            return {"overall_ok": True, "urls_requested": 4}

    class DummyRunner:
        def __init__(self) -> None:
            self.calls = []

        def run(self, **kwargs):
            self.calls.append(kwargs)
            return DummyResult()

    dummy_runner = DummyRunner()
    monkeypatch.setattr(
        module,
        "build_autonomous_cycle_runner",
        lambda **kwargs: builder_calls.append(dict(kwargs)) or dummy_runner,
    )

    class DummySelection:
        selected_urls = ["https://example.com/d", "https://example.com/a"]
        ok = True

        def to_dict(self):
            return {"ok": True, "selected_url_count": 2}

    monkeypatch.setattr(
        module,
        "select_curated_registry_urls",
        lambda *args, **kwargs: DummySelection(),
    )

    payload = module.run_cycle(
        module.build_parser().parse_args(
            [
                "--url",
                "https://example.com/a",
                "--url-file",
                str(url_file),
                "--registry-path",
                "spec/external_source_registry.yaml",
                "--no-llm",
            ]
        )
    )

    assert payload == {
        "overall_ok": True,
        "urls_requested": 4,
        "registry_selection": {"ok": True, "selected_url_count": 2},
    }
    assert dummy_runner.calls[0]["urls"] == [
        "https://example.com/a",
        "https://example.com/b",
        "https://example.com/c",
        "https://example.com/d",
    ]
    assert str(builder_calls[0]["state_path"]).endswith("dream_wakeup_state.json")
    assert dummy_runner.calls[0]["generate_reflection"] is False
    assert dummy_runner.calls[0]["require_inference_ready"] is False
    assert builder_calls[0]["enable_scribe"] is True
    assert str(builder_calls[0]["scribe_status_path"]).endswith("scribe_status_latest.json")


def test_main_strict_returns_non_zero_when_runner_reports_not_ok(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module = _load_module()

    class DummyResult:
        def to_dict(self):
            return {"overall_ok": False}

    class DummyRunner:
        def run(self, **kwargs):
            return DummyResult()

    monkeypatch.setattr(module, "build_autonomous_cycle_runner", lambda **kwargs: DummyRunner())
    monkeypatch.setattr("sys.argv", ["run_autonomous_dream_cycle.py", "--strict"])

    exit_code = module.main()

    assert exit_code == 1


def test_run_cycle_can_skip_llm_preflight_without_disabling_reflection(monkeypatch) -> None:
    module = _load_module()

    class DummyResult:
        def to_dict(self):
            return {"overall_ok": True}

    class DummyRunner:
        def __init__(self) -> None:
            self.calls = []

        def run(self, **kwargs):
            self.calls.append(kwargs)
            return DummyResult()

    dummy_runner = DummyRunner()
    monkeypatch.setattr(module, "build_autonomous_cycle_runner", lambda **kwargs: dummy_runner)

    payload = module.run_cycle(
        module.build_parser().parse_args(
            [
                "--skip-llm-preflight",
                "--llm-probe-timeout-seconds",
                "6.5",
            ]
        )
    )

    assert payload == {"overall_ok": True}
    assert dummy_runner.calls[0]["generate_reflection"] is True
    assert dummy_runner.calls[0]["require_inference_ready"] is False
    assert dummy_runner.calls[0]["inference_timeout_seconds"] == 6.5
