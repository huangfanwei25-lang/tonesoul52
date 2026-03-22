from __future__ import annotations

import argparse
import json
from pathlib import Path

from tonesoul import audit_interface as module


def _write_json(path: Path, payload: object, *, encoding: str = "utf-8") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding=encoding)
    return path


def test_load_frame_role_meta_extracts_catalog_and_summary(tmp_path: Path) -> None:
    frame_plan_path = _write_json(
        tmp_path / "frame_plan.json",
        {"role_catalog": {"guardian": ["verify"]}, "role_summary": {"primary": "guardian"}},
    )

    result = module._load_frame_role_meta(str(frame_plan_path))

    assert result == {
        "role_catalog": {"guardian": ["verify"]},
        "role_summary": {"primary": "guardian"},
    }


def test_gate_loaders_extract_nested_results(tmp_path: Path) -> None:
    gate_report = _write_json(
        tmp_path / "gate_report.json",
        {
            "results": [
                {"gate": "poav_gate", "status": "pass"},
                {"gate": "escalation_gate", "status": "warn"},
                {"gate": "mercy_gate", "status": "review"},
            ]
        },
    )

    assert module._load_poav_result(str(gate_report)) == {"gate": "poav_gate", "status": "pass"}
    assert module._load_escalation_result(str(gate_report)) == {
        "gate": "escalation_gate",
        "status": "warn",
    }
    assert module._load_mercy_result(str(gate_report)) == {
        "gate": "mercy_gate",
        "status": "review",
    }


def test_gate_loaders_support_direct_nested_payloads(tmp_path: Path) -> None:
    poav_path = _write_json(
        tmp_path / "poav.json", {"poav_result": {"gate": "poav_gate", "ok": True}}
    )
    escalation_path = _write_json(
        tmp_path / "escalation.json",
        {"escalation_result": {"gate": "escalation_gate", "level": "L2"}},
    )
    mercy_path = _write_json(tmp_path / "mercy.json", {"gate": "mercy_gate", "decision": "hold"})

    assert module._load_poav_result(str(poav_path)) == {"gate": "poav_gate", "ok": True}
    assert module._load_escalation_result(str(escalation_path)) == {
        "gate": "escalation_gate",
        "level": "L2",
    }
    assert module._load_mercy_result(str(mercy_path)) == {
        "gate": "mercy_gate",
        "decision": "hold",
    }


def test_load_json_accepts_bom_and_invalid_json_returns_none(tmp_path: Path) -> None:
    payload_path = _write_json(tmp_path / "payload.json", {"ok": True}, encoding="utf-8-sig")
    invalid_path = tmp_path / "invalid.json"
    invalid_path.write_text("{not-json}", encoding="utf-8")

    assert module._load_json(str(payload_path)) == {"ok": True}
    assert module._load_json(str(invalid_path)) is None


def test_truncate_and_count_entries_apply_normalization() -> None:
    text = "alpha   beta   gamma   delta"
    items = [{"uri": "a"}, {"uri": ""}, "  note  ", ""]

    assert module._truncate(text, limit=14) == "alpha beta ..."
    assert module._count_entries(items, key="uri") == 2


def test_claim_preview_counts_and_limits_preview() -> None:
    claims = [
        {"text": "first claim"},
        {"claim": "second claim"},
        {"statement": "third claim"},
        "fourth claim",
    ]

    result = module._claim_preview(claims)

    assert result["count"] == 4
    assert result["preview"] == ["first claim", "second claim", "third claim"]


def test_tech_trace_digest_summarizes_claims_links_and_attributions(tmp_path: Path) -> None:
    trace_path = _write_json(
        tmp_path / "normalize.json",
        {
            "summary": "  This summary keeps enough detail for the audit digest.  ",
            "claims": [{"text": "claim one"}, {"claim": "claim two"}],
            "links": [{"uri": "https://a"}, {"uri": ""}, "ignore"],
            "attributions": [{"source_ref": "doc-1"}, {"source_ref": None}],
        },
    )

    digest = module._tech_trace_digest(str(trace_path))

    assert digest == {
        "normalize_path": str(trace_path),
        "summary": "This summary keeps enough detail for the audit digest.",
        "claim_count": 2,
        "claims_preview": ["claim one", "claim two"],
        "link_count": 2,
        "attribution_count": 1,
    }


def test_intent_verification_digest_extracts_audit_intent_and_source(tmp_path: Path) -> None:
    path = _write_json(
        tmp_path / "intent.json",
        {
            "audit": {"status": "verified", "confidence": 0.9, "reason": "clear"},
            "intent": {"surface": "summarize", "deep": "preserve trust"},
            "source": {"evidence_path": "evidence.json"},
        },
    )

    digest = module._intent_verification_digest(str(path))

    assert digest == {
        "status": "verified",
        "confidence": 0.9,
        "reason": "clear",
        "surface": "summarize",
        "deep": "preserve trust",
        "evidence_path": "evidence.json",
    }


def test_build_audit_request_includes_optional_digests_and_role_meta(tmp_path: Path) -> None:
    frame_plan_path = _write_json(
        tmp_path / "frame_plan.json",
        {"role_catalog": {"guardian": ["verify"]}, "role_summary": {"primary": "guardian"}},
    )
    tech_trace_path = _write_json(
        tmp_path / "normalize.json",
        {"summary": "trace summary", "claims": ["a"], "links": [{"uri": "u"}], "attributions": []},
    )
    intent_path = _write_json(
        tmp_path / "intent.json",
        {
            "audit": {"status": "verified", "confidence": 0.8, "reason": "aligned"},
            "intent": {"surface": "review", "deep": "protect"},
            "source": {"evidence_path": "evidence.json"},
        },
    )

    payload = module.build_audit_request(
        context_path=str(tmp_path / "context.yaml"),
        frame_plan_path=str(frame_plan_path),
        constraints_path=None,
        execution_report_path=None,
        evidence_summary_path=None,
        gate_report_path=None,
        error_ledger_path=None,
        action_set_path=None,
        mercy_objective_path=None,
        council_summary_path=None,
        tsr_metrics_path=None,
        dcs_result_path=None,
        ystm_nodes_path=None,
        ystm_audit_path=None,
        tech_trace_normalize_path=str(tech_trace_path),
        intent_verification_path=str(intent_path),
        poav_result={"gate": "poav_gate", "status": "pass"},
        escalation_result={"gate": "escalation_gate", "status": "warn"},
        mercy_result={"gate": "mercy_gate", "status": "hold"},
    )

    assert payload["inputs"]["context"] == str(tmp_path / "context.yaml")
    assert payload["responsibility_roles"]["role_summary"]["primary"] == "guardian"
    assert payload["poav_result"]["status"] == "pass"
    assert payload["escalation_result"]["status"] == "warn"
    assert payload["mercy_result"]["status"] == "hold"
    assert payload["tech_trace_digest"]["claim_count"] == 1
    assert payload["intent_verification_digest"]["surface"] == "review"


def test_resolve_output_defaults_to_context_directory(tmp_path: Path) -> None:
    context_path = tmp_path / "run" / "context.yaml"

    assert module._resolve_output(None, str(context_path)) == str(
        tmp_path / "run" / "audit_request.json"
    )
    assert module._resolve_output(str(tmp_path / "custom.json"), str(context_path)) == str(
        tmp_path / "custom.json"
    )


def test_main_writes_audit_request_file(tmp_path: Path, monkeypatch) -> None:
    output_path = tmp_path / "out" / "audit_request.json"
    args = argparse.Namespace(
        context=str(tmp_path / "context.yaml"),
        frame_plan=None,
        constraints=None,
        execution_report=None,
        evidence_summary=None,
        gate_report=None,
        error_ledger=None,
        action_set=None,
        mercy_objective=None,
        council_summary=None,
        tsr_metrics=None,
        dcs_result=None,
        ystm_nodes=None,
        ystm_audit=None,
        ystm_diff=None,
        ystm_terrain=None,
        ystm_terrain_json=None,
        ystm_terrain_svg=None,
        ystm_terrain_png=None,
        ystm_terrain_p2=None,
        ystm_terrain_p2_json=None,
        ystm_terrain_p2_svg=None,
        ystm_terrain_p2_png=None,
        tech_trace_capture=None,
        tech_trace_normalize=None,
        intent_verification=None,
        skills_applied=None,
        reflection=None,
        poav_result=None,
        escalation_result=None,
        mercy_result=None,
        output=str(output_path),
    )

    class _Parser:
        def parse_args(self) -> argparse.Namespace:
            return args

    monkeypatch.setattr(module, "build_arg_parser", lambda: _Parser())

    result = module.main()

    assert result == {"audit_request": str(output_path)}
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["inputs"]["context"] == str(tmp_path / "context.yaml")
    assert payload["notes"]
