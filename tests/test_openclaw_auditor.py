from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from memory.genesis import Genesis
from tonesoul.gateway.session import GatewaySession
from tonesoul.openclaw_auditor import OpenClawAuditor


@dataclass
class _FakeProvenanceManager:
    last_event_type: str | None = None
    last_content: Dict[str, Any] | None = None
    last_meta: Dict[str, Any] | None = None

    def add_record(self, event_type: str, content: Dict[str, Any], metadata: Dict[str, Any]):
        self.last_event_type = event_type
        self.last_content = content
        self.last_meta = metadata
        return "evt_test_001"


def test_openclaw_auditor_emits_three_hooks_and_log_shape():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    session = GatewaySession(
        session_id="session_001",
        user_id="user_001",
        channel="audit",
        genesis=Genesis.AUTONOMOUS,
    )
    report = auditor.audit(
        "I will verify facts before final recommendation.",
        context_fragments=["verify facts", "final recommendation"],
        session=session,
        current_layer="L2",
    )

    payload = report.to_dict()
    assert payload["session"]["session_id"] == "session_001"
    assert payload["session"]["responsibility_tier"] == "TIER_1"
    assert len(payload["hooks"]) == 3
    assert payload["hooks"][0]["hook"] == "attribute_attribution"
    assert payload["hooks"][1]["hook"] == "shadow_path_tracking"
    assert payload["hooks"][2]["hook"] == "benevolence_filter"
    assert "decision" in payload


def test_openclaw_auditor_marks_shadowless_output_for_confirmation():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    report = auditor.audit(
        "destroy all records now",
        context_fragments=["harmless summary", "safe response"],
        current_layer="L2",
    )

    assert report.final_result in {"reject", "intercept", "flag"}
    assert report.requires_confirmation is True


def test_openclaw_auditor_persists_audit_log_when_enabled():
    fake = _FakeProvenanceManager()
    auditor = OpenClawAuditor(
        persist_to_ledger=True,
        provenance_manager=fake,  # type: ignore[arg-type]
    )
    report = auditor.audit(
        "I am not sure; this may need verification.",
        context_fragments=["need verification"],
    )

    assert report.ledger_event_id == "evt_test_001"
    assert fake.last_event_type == "openclaw_audit"
    assert isinstance(fake.last_content, dict)
    assert fake.last_meta["final_result"] == report.final_result


def test_openclaw_auditor_flags_inference_layer_mismatch():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    report = auditor.audit(
        "This inference should be semantic only.",
        context_fragments=["semantic only"],
        action_basis="Inference",
        current_layer="L1",
    )

    assert report.hooks[0].result == "flag"


# ── AuditHookResult.to_dict ───────────────────────────────────────────────────


def test_audit_hook_result_to_dict_all_fields():
    from tonesoul.openclaw_auditor import AuditHookResult

    hook = AuditHookResult(hook="test_hook", result="pass", code="CODE", score=0.9, note="ok")
    d = hook.to_dict()
    assert d == {"hook": "test_hook", "result": "pass", "code": "CODE", "score": 0.9, "note": "ok"}


# ── OpenClawAuditReport.passed ────────────────────────────────────────────────


def test_audit_report_passed_true_on_pass():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    report = auditor.audit(
        "I will verify facts carefully.",
        context_fragments=["verify facts"],
    )
    assert isinstance(report.passed, bool)
    assert report.passed == (report.final_result == "pass")


# ── No session → default session used ────────────────────────────────────────


def test_audit_without_session_generates_default_session():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    report = auditor.audit("safe action", context_fragments=["safe"])
    assert report.session_id.startswith("session_")
    assert report.channel is not None


# ── _normalize_session with dict mapping ─────────────────────────────────────


def test_audit_with_mapping_session():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    report = auditor.audit(
        "safe action",
        context_fragments=["safe"],
        session={"session_id": "map_session", "genesis": "REACTIVE_USER"},
    )
    assert report.session_id == "map_session"


# ── build_audit_log delegates to to_dict ──────────────────────────────────────


def test_build_audit_log_matches_to_dict():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    report = auditor.audit("safe action", context_fragments=["safe"])
    log = auditor.build_audit_log(report)
    assert log == report.to_dict()


# ── CPT scores in to_dict ──────────────────────────────────────────────────────


def test_audit_report_to_dict_contains_cpt():
    auditor = OpenClawAuditor(persist_to_ledger=False)
    report = auditor.audit("safe action", context_fragments=["safe"])
    d = report.to_dict()
    assert "context" in d["cpt"]
    assert "phrase" in d["cpt"]
    assert "tension" in d["cpt"]
