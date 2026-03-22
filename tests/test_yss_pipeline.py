from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from tonesoul import yss_pipeline as module
from tonesoul.yss_gates import GateResult


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _write_yaml(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True), encoding="utf-8")
    return path


def _gate_result(name: str, *, passed: bool = True) -> GateResult:
    return GateResult(name, passed, [], {"decision": "pass"})


def _pipeline_context(
    tmp_path: Path,
    *,
    skip_gates: bool = False,
    skill_directives: dict[str, bool] | None = None,
) -> module.PipelineContext:
    evidence_summary_path = tmp_path / "summary.md"
    evidence_summary_path.write_text("# Evidence Summary\n", encoding="utf-8")
    return module.PipelineContext(
        config=module.PipelineConfig(skip_gates=skip_gates),
        workspace=str(tmp_path),
        run_dir=str(tmp_path / "run-001"),
        context_payload={"context": {"task": "Review"}},
        registry=[],
        frame_plan={},
        constraints_doc="## Safety\nP0 non-harm",
        execution_report="report",
        mercy_objective={"score": 0.5},
        skill_directives=skill_directives or {},
        ystm_outputs={"nodes": None},
        context_path=str(tmp_path / "context.yaml"),
        action_set_path=str(tmp_path / "action_set.json"),
        mercy_objective_path=str(tmp_path / "mercy_objective.json"),
        execution_report_path=str(tmp_path / "execution_report.md"),
        evidence_summary_path=str(evidence_summary_path),
        error_ledger_path=str(tmp_path / "error_ledger.jsonl"),
        gate_report_path=str(tmp_path / "gate_report.json"),
        council_summary_path=None,
        tsr_metrics_path=None,
        skills_path=None,
        ystm_diff_path=None,
        tech_trace_capture_path=None,
        tech_trace_normalize_path=None,
        intent_verification_path=None,
    )


@pytest.mark.parametrize("suffix", [".json", ".yaml"])
def test_load_seed_supports_json_and_yaml(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f"seed{suffix}"
    payload = {"task": "Review"}
    if suffix == ".json":
        _write_json(path, payload)
    else:
        _write_yaml(path, payload)

    assert module._load_seed(str(path)) == payload


def test_load_seed_rejects_unknown_extension(tmp_path: Path) -> None:
    path = tmp_path / "seed.txt"
    path.write_text("task: review", encoding="utf-8")

    with pytest.raises(ValueError):
        module._load_seed(str(path))


def test_resolve_run_dir_returns_explicit_absolute_path(tmp_path: Path) -> None:
    run_dir = tmp_path / "custom-run"

    assert module._resolve_run_dir(module.PipelineConfig(run_dir=str(run_dir))) == str(
        run_dir.resolve()
    )


def test_resolve_run_dir_builds_generated_workspace_path(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(module, "_workspace_root", lambda: str(tmp_path))
    monkeypatch.setattr(module, "_generate_run_id", lambda: "run-xyz")

    assert module._resolve_run_dir(module.PipelineConfig()) == str(
        tmp_path / "run" / "execution" / "run-xyz"
    )


def test_resolve_retention_config_handles_disabled_and_relative_archive_dir(
    tmp_path: Path,
) -> None:
    assert module._resolve_retention_config({}, str(tmp_path)) is None

    config = module._resolve_retention_config(
        {
            "retention": {
                "enabled": True,
                "evidence": {"max_entries": 5, "keep_latest": 2, "archive_dir": "archive/evidence"},
            }
        },
        str(tmp_path),
    )

    assert config == {
        "max_entries": 5,
        "keep_latest": 2,
        "archive_dir": str((tmp_path / "archive" / "evidence").resolve()),
    }


def test_extract_gate_result_returns_named_entry() -> None:
    gate_report = {
        "results": [
            {"gate": "p0_gate", "passed": True},
            {"gate": "poav_gate", "passed": False},
        ]
    }

    assert module._extract_gate_result(gate_report, "poav_gate") == {
        "gate": "poav_gate",
        "passed": False,
    }
    assert module._extract_gate_result(gate_report, "missing") is None


def test_build_required_files_includes_optional_artifacts(tmp_path: Path) -> None:
    ctx = _pipeline_context(tmp_path)
    ctx.skills_path = str(tmp_path / "skills.json")
    ctx.ystm_diff_path = str(tmp_path / "diff.json")
    ctx.tech_trace_capture_path = str(tmp_path / "capture.json")
    ctx.tech_trace_normalize_path = str(tmp_path / "normalize.json")
    ctx.intent_verification_path = str(tmp_path / "intent.json")
    ctx.ystm_outputs.update(
        {"audit": str(tmp_path / "audit.json"), "terrain": str(tmp_path / "terrain.html")}
    )

    required = module._build_required_files(ctx)

    assert required["context"] == ctx.context_path
    assert required["skills_applied"] == ctx.skills_path
    assert required["ystm_diff"] == ctx.ystm_diff_path
    assert required["tech_trace_capture"] == ctx.tech_trace_capture_path
    assert required["tech_trace_normalize"] == ctx.tech_trace_normalize_path
    assert required["intent_verification"] == ctx.intent_verification_path


def test_extract_dispatch_trace_from_context_returns_nested_payload() -> None:
    payload = {
        "inputs": {
            "payload": {
                "dispatch_trace": {"state": "B", "route": "pass_council"},
            }
        }
    }

    assert module._extract_dispatch_trace_from_context(payload) == {
        "state": "B",
        "route": "pass_council",
    }
    assert module._extract_dispatch_trace_from_context({}) is None


def test_collect_gate_results_short_circuits_when_skip_gates_enabled(
    tmp_path: Path,
    monkeypatch,
) -> None:
    ctx = _pipeline_context(tmp_path, skip_gates=True)
    monkeypatch.setattr(module, "p0_gate", lambda _text: _gate_result("p0_gate"))
    monkeypatch.setattr(
        module,
        "poav_gate",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("poav_gate should not run")),
    )

    results = module._collect_gate_results(ctx)

    assert [result.gate for result in results] == ["p0_gate"]


def test_collect_gate_results_force_gates_overrides_skip(
    tmp_path: Path,
    monkeypatch,
) -> None:
    ctx = _pipeline_context(tmp_path, skip_gates=True, skill_directives={"force_gates": True})
    monkeypatch.setattr(module, "p0_gate", lambda _text: _gate_result("p0_gate"))
    monkeypatch.setattr(
        module,
        "poav_gate",
        lambda *_args, **_kwargs: GateResult("poav_gate", True, [], {"components": {"total": 0.9}}),
    )
    monkeypatch.setattr(module, "mercy_gate", lambda *_args, **_kwargs: _gate_result("mercy_gate"))
    monkeypatch.setattr(module, "load_drift_metrics", lambda _path: {})
    monkeypatch.setattr(
        module,
        "escalation_gate",
        lambda *_args, **_kwargs: _gate_result("escalation_gate"),
    )
    monkeypatch.setattr(module, "context_lint", lambda _payload: _gate_result("context_lint"))
    monkeypatch.setattr(
        module, "router_replay", lambda *_args, **_kwargs: _gate_result("router_replay")
    )
    monkeypatch.setattr(module, "role_alignment", lambda _plan: _gate_result("role_alignment"))
    monkeypatch.setattr(
        module,
        "guardian_gate",
        lambda *_args, **_kwargs: _gate_result("guardian_gate"),
    )
    monkeypatch.setattr(
        module,
        "constraint_consistency",
        lambda _text: _gate_result("constraint_consistency"),
    )
    monkeypatch.setattr(
        module,
        "tech_trace_gate",
        lambda *_args, **_kwargs: _gate_result("tech_trace_gate"),
    )
    monkeypatch.setattr(
        module,
        "intent_achievement_gate",
        lambda *_args, **_kwargs: _gate_result("intent_achievement_gate"),
    )
    monkeypatch.setattr(module, "dcs_gate", lambda *_args, **_kwargs: _gate_result("dcs_gate"))
    monkeypatch.setattr(
        module, "build_test_gate", lambda _workspace: _gate_result("build_test_gate")
    )
    monkeypatch.setattr(
        module,
        "evidence_completeness",
        lambda *_args, **_kwargs: _gate_result("evidence_completeness"),
    )

    results = module._collect_gate_results(ctx)

    gate_names = [result.gate for result in results]
    assert "poav_gate" in gate_names
    assert gate_names[-1] == "evidence_completeness"
    assert len(results) == 14


def test_write_gate_outputs_writes_report_and_reflection(
    tmp_path: Path,
    monkeypatch,
) -> None:
    gate_report_path = tmp_path / "gate_report.json"
    execution_report_path = tmp_path / "execution_report.md"
    execution_report_path.write_text("# Execution\n", encoding="utf-8")
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        module,
        "build_reflection",
        lambda report, directives: {"summary": report["overall"], "directives": directives},
    )

    def _write_reflection(path: str, payload: dict[str, object]) -> None:
        captured["path"] = path
        captured["payload"] = payload
        Path(path).write_text(json.dumps(payload), encoding="utf-8")

    monkeypatch.setattr(module, "write_reflection", _write_reflection)
    gate_results = [
        GateResult("p0_gate", True, [], {"decision": "pass"}),
        GateResult("guardian_gate", True, [], {"decision": "pass", "guardian_present": True}),
    ]

    gate_report, reflection_path = module._write_gate_outputs(
        str(gate_report_path),
        str(execution_report_path),
        gate_results,
        {"force_gates": True},
    )

    assert gate_report_path.exists()
    assert gate_report["overall"] == "PASS"
    assert reflection_path == str(tmp_path / "reflection.json")
    assert captured["path"] == reflection_path
    assert json.loads(Path(reflection_path).read_text(encoding="utf-8"))["summary"] == "PASS"


def test_run_pipeline_from_unified_request_preserves_existing_config_fields(
    monkeypatch,
) -> None:
    captured: dict[str, str] = {}

    def _fake_run_pipeline(config: module.PipelineConfig) -> dict[str, object]:
        captured["task"] = config.task
        captured["objective"] = config.objective
        captured["domain"] = config.domain
        captured["decision_mode"] = config.decision_mode
        return {"run_dir": "dummy"}

    monkeypatch.setattr(module, "run_pipeline", _fake_run_pipeline)

    result = module.run_pipeline_from_unified_request(
        {
            "user_message": "Review this",
            "dispatch_trace": {"state": "C"},
        },
        config=module.PipelineConfig(
            task="preset task",
            objective="preset objective",
            domain="preset domain",
            decision_mode="preset mode",
        ),
    )

    assert captured == {
        "task": "preset task",
        "objective": "preset objective",
        "domain": "preset domain",
        "decision_mode": "preset mode",
    }
    assert result["unified_seed"]["decision_mode"] == "strict"
