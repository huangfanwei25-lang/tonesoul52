from __future__ import annotations

import json
from pathlib import Path

from tonesoul import yss_gates as module
from tonesoul.yss_gates import GateResult


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def test_context_lint_passes_with_complete_payload() -> None:
    context = {
        "context": {
            "task": "Review output",
            "objective": "Preserve trust",
            "domain": "governance",
            "audience": "operators",
            "mode": "guarded",
        },
        "assumptions": ["sources exist"],
        "constraints": ["cite evidence"],
        "time_island": {
            "chronos": {
                "time_stamp": "2026-03-19T12:00:00Z",
                "dependency_basis": "daily",
                "change_log": [],
            },
            "kairos": {"trigger": "manual", "decision_mode": "strict"},
            "trace": {"residual_risk": "low", "rollback_condition": "human override"},
        },
    }

    result = module.context_lint(context)

    assert result.gate == "context_lint"
    assert result.passed is True
    assert result.issues == []


def test_context_lint_reports_missing_fields_and_time_island() -> None:
    result = module.context_lint({"context": {"task": "Review"}})

    assert result.passed is False
    assert "missing_context_field:objective" in result.issues
    assert "missing_assumptions" in result.issues
    assert "missing_constraints" in result.issues
    assert "time_island_chronos_time_stamp_missing" in result.issues


def test_guardian_gate_record_only_when_not_enforced() -> None:
    plan = {"role_summary": {"governance_roles": ["critic"], "max_governance_level": 2}}

    result = module.guardian_gate(plan, enforce=False)

    assert result.passed is True
    assert result.details["decision"] == "record_only"
    assert "guardian_missing" in result.issues


def test_guardian_gate_blocks_when_enforced_and_missing() -> None:
    plan = {"role_summary": {"governance_roles": ["critic"], "max_governance_level": 2}}

    result = module.guardian_gate(plan, enforce=True)

    assert result.passed is False
    assert result.details["decision"] == "fail"
    assert "guardian_missing" in result.issues


def test_p0_gate_passes_with_non_harm_marker() -> None:
    text = "\n".join(
        [
            "## Scope",
            "Review output.",
            "## Safety",
            "Maintain P0 non-harm constraints.",
        ]
    )

    result = module.p0_gate(text)

    assert result.passed is True
    assert result.details["decision"] == "pass"


def test_p0_gate_blocks_without_non_harm_marker() -> None:
    text = "\n".join(["## Scope", "Review output.", "## Safety", "General safety notes."])

    result = module.p0_gate(text)

    assert result.passed is False
    assert result.details["decision"] == "block"
    assert "p0_non_harm_missing" in result.issues


def test_intent_achievement_gate_passes_when_achieved_and_required(tmp_path: Path) -> None:
    intent_path = _write_json(
        tmp_path / "intent.json",
        {"audit": {"status": "achieved", "confidence": 0.8, "reason": "clear"}},
    )

    result = module.intent_achievement_gate(str(intent_path), require=True)

    assert result.passed is True
    assert result.details["decision"] == "pass"
    assert result.details["status"] == "achieved"


def test_intent_achievement_gate_blocks_when_failed_and_required(tmp_path: Path) -> None:
    intent_path = _write_json(
        tmp_path / "intent.json",
        {"audit": {"status": "failed", "confidence": 0.4, "reason": "mismatch"}},
    )

    result = module.intent_achievement_gate(str(intent_path), require=True)

    assert result.passed is False
    assert result.details["decision"] == "fail"
    assert "intent_verification_failed" in result.issues


def test_build_test_gate_handles_acceptance_exception(monkeypatch) -> None:
    monkeypatch.setattr(
        module, "run_acceptance", lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    )

    result = module.build_test_gate("workspace")

    assert result.passed is False
    assert result.issues == ["ystm_acceptance_failed"]
    assert result.details["returncode"] == 1
    assert "RuntimeError: boom" in result.details["stdout_tail"]


def test_build_gate_report_and_update_execution_report_render_sections(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(module, "utc_now", lambda: "2026-03-19T12:00:00Z")
    report_path = tmp_path / "execution_report.md"
    report_path.write_text("# Execution Report\n\nInitial section.\n", encoding="utf-8")
    results = [
        GateResult("p0_gate", False, ["p0_non_harm_missing"], {"decision": "block"}),
        GateResult(
            "guardian_gate",
            True,
            [],
            {"decision": "pass", "guardian_present": True},
        ),
    ]

    gate_report = module.build_gate_report(results)
    module.update_execution_report(str(report_path), gate_report)

    assert gate_report["overall"] == "FAIL"
    text = report_path.read_text(encoding="utf-8")
    assert "## Gate Results" in text
    assert "## P0 Non-Harm Gate" in text
    assert "## Guardian Gate" in text
    assert "- Generated at: 2026-03-19T12:00:00Z" in text


def test_evidence_completeness_flags_missing_files_and_refs(tmp_path: Path) -> None:
    context_path = tmp_path / "context.yaml"
    execution_report_path = tmp_path / "execution_report.md"
    nodes_path = tmp_path / "nodes.json"
    context_path.write_text("context", encoding="utf-8")
    execution_report_path.write_text("report", encoding="utf-8")
    nodes_path.write_text("{}", encoding="utf-8")

    result = module.evidence_completeness(
        evidence_text="\n".join(
            [
                f"- Run: {context_path}",
                f"- Execution report: {execution_report_path}",
            ]
        ),
        context_path=str(context_path),
        execution_report_path=str(execution_report_path),
        required_files={
            "ystm_nodes": str(nodes_path),
            "action_set": str(tmp_path / "missing_action_set.json"),
        },
        require_listed=True,
    )

    assert result.passed is False
    assert result.details["missing_files"] == ["action_set"]
    assert result.details["missing_refs"] == ["ystm_nodes", "action_set"]
    assert "missing_files:action_set" in result.issues
    assert "evidence_missing_refs:ystm_nodes,action_set" in result.issues
