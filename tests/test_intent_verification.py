from __future__ import annotations

import json
from pathlib import Path

from tonesoul.intent_verification import (
    AuditResult,
    Evidence,
    EvidenceCollector,
    Intent,
    IntentAnalyzer,
    SelfAuditor,
    _coerce_bool,
    _coerce_float,
    _contains_failure_signal,
    _criteria_met,
    _load_json,
    _string_or_none,
    build_intent_verification,
)


def _write_json(path: Path, payload: object, *, encoding: str = "utf-8") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding=encoding)
    return path


def test_intent_analyzer_prefers_task_and_preserves_success_criteria() -> None:
    intent = IntentAnalyzer().analyze(
        {
            "context": {
                "task": "Summarize report",
                "objective": "Preserve trust",
                "success_criteria": ["cite sources", "keep it concise"],
            }
        }
    )

    assert intent == Intent(
        surface="Summarize report",
        deep="Preserve trust",
        success_criteria=["cite sources", "keep it concise"],
    )


def test_intent_analyzer_falls_back_to_objective_when_task_missing() -> None:
    intent = IntentAnalyzer().analyze({"context": {"objective": "Preserve trust"}})

    assert intent.surface == "Preserve trust"
    assert intent.deep == "Preserve trust"
    assert intent.success_criteria == ["Preserve trust"]


def test_evidence_has_signal_only_when_any_field_is_present() -> None:
    assert Evidence().has_signal() is False
    assert Evidence(action_log="ran command").has_signal() is True


def test_evidence_collector_normalizes_aliases_and_status() -> None:
    evidence = EvidenceCollector().collect(
        {
            "before": "before.png",
            "screenshot_path": "after.png",
            "diff_detected": True,
            "ocr": "OCR text",
            "command": "run check",
            "status": "success",
            "actual_result": "Finished cleanly",
        }
    )

    assert evidence.before_screenshot == "before.png"
    assert evidence.after_screenshot == "after.png"
    assert evidence.diff_score == 1.0
    assert evidence.ocr_result == "OCR text"
    assert evidence.action_log == "run check"
    assert evidence.intent_achieved is True
    assert evidence.actual_result == "Finished cleanly"


def test_evidence_collector_returns_empty_evidence_for_non_mapping() -> None:
    assert EvidenceCollector().collect(None) == Evidence()


def test_self_auditor_returns_inconclusive_without_evidence() -> None:
    result = SelfAuditor().audit(Intent("task", "goal", ["goal"]), Evidence())

    assert result == AuditResult(status="inconclusive", confidence=0.2, reason="no_evidence")


def test_self_auditor_honors_explicit_intent_signal() -> None:
    result = SelfAuditor().audit(
        Intent("task", "goal", ["goal"]),
        Evidence(intent_achieved=False, actual_result="user cancelled"),
    )

    assert result == AuditResult(
        status="failed",
        confidence=0.6,
        reason="explicit_signal",
        actual_result="user cancelled",
    )


def test_self_auditor_uses_status_before_criteria() -> None:
    result = SelfAuditor().audit(
        Intent("task", "goal", ["goal"]),
        Evidence(status="ok", action_log="completed the goal"),
    )

    assert result == AuditResult(
        status="achieved",
        confidence=0.7,
        reason="status_success",
        actual_result="completed the goal",
    )


def test_self_auditor_detects_criteria_match() -> None:
    result = SelfAuditor().audit(
        Intent("review", "protect trust", ["trust"]),
        Evidence(action_log="all checks passed; trust preserved"),
    )

    assert result == AuditResult(
        status="achieved",
        confidence=0.6,
        reason="criteria_match",
        actual_result="all checks passed; trust preserved",
    )


def test_self_auditor_detects_failure_signal() -> None:
    result = SelfAuditor().audit(
        Intent("review", "protect trust", ["trust"]),
        Evidence(action_log="command failed with exception"),
    )

    assert result == AuditResult(
        status="failed",
        confidence=0.4,
        reason="failure_signal",
        actual_result="command failed with exception",
    )


def test_self_auditor_returns_insufficient_evidence_when_signal_is_ambiguous() -> None:
    result = SelfAuditor().audit(
        Intent("review", "protect trust", ["trust"]),
        Evidence(action_log="step executed"),
    )

    assert result == AuditResult(
        status="inconclusive",
        confidence=0.3,
        reason="insufficient_evidence",
        actual_result="step executed",
    )


def test_build_intent_verification_includes_evidence_source(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("tonesoul.intent_verification.utc_now", lambda: "2026-03-19T12:00:00Z")
    evidence_path = _write_json(
        tmp_path / "evidence.json",
        {"status": "ok", "actual_result": "goal achieved"},
    )

    payload = build_intent_verification(
        {"context": {"task": "Review", "objective": "goal achieved"}},
        evidence_path=str(evidence_path),
    )

    assert payload["generated_at"] == "2026-03-19T12:00:00Z"
    assert payload["intent"]["surface"] == "Review"
    assert payload["audit"]["status"] == "achieved"
    assert payload["source"] == {"evidence_path": str(evidence_path)}


def test_load_json_helpers_and_coercers_handle_edge_values(tmp_path: Path) -> None:
    valid_path = _write_json(tmp_path / "payload.json", {"ok": True}, encoding="utf-8-sig")
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{", encoding="utf-8")

    assert _load_json(str(valid_path)) == {"ok": True}
    assert _load_json(str(invalid_path)) is None
    assert _coerce_bool("yes") is True
    assert _coerce_bool("0") is False
    assert _coerce_bool("maybe") is None
    assert _coerce_float(3) == 3.0
    assert _coerce_float("3") is None
    assert _string_or_none("  text  ") == "text"
    assert _string_or_none("   ") is None


def test_criteria_and_failure_helpers_scan_evidence_text() -> None:
    evidence = Evidence(
        action_log="review complete",
        ocr_result="trust preserved",
        actual_result="no error",
    )

    assert _criteria_met(["trust"], evidence) is True
    assert _contains_failure_signal(Evidence(actual_result="runtime exception")) is True
