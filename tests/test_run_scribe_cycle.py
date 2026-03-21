import json
from pathlib import Path

import scripts.run_scribe_cycle as run_scribe_cycle
from tonesoul.scribe.scribe_engine import ScribeDraftResult


def test_build_scribe_status_payload_for_generated_pair(tmp_path: Path) -> None:
    chronicle_path = tmp_path / "docs" / "chronicles" / "chronicle.md"
    companion_path = tmp_path / "docs" / "chronicles" / "chronicle.json"
    result = ScribeDraftResult(
        generated_at="2026-03-13T04:23:10Z",
        status="generated",
        source_db_path=str((tmp_path / "memory" / "soul.db").resolve()),
        observed_counts={"tensions": 0, "collisions": 1, "crystals": 2},
        lead_anchor_summary="[K1] collision: Two readings of the same market pull in different directions.",
        fallback_mode="observed_history",
        generation_mode="llm_chronicle",
        title_hint="Signal Chronicle",
        llm_model="gemma3:4b",
        llm_attempts=[
            {"model": "qwen3.5:4b", "status": "timeout"},
            {"model": "gemma3:4b", "status": "generated"},
        ],
        chronicle_path=chronicle_path,
        companion_path=companion_path,
        error=None,
    )

    payload = run_scribe_cycle.build_scribe_status_payload(result)

    assert payload["status"] == "generated"
    assert payload["latest_available_source"] == "chronicle_pair"
    assert payload["generation_mode"] == "llm_chronicle"
    assert payload["state_document_posture"] == "contradiction_with_retained_belief"
    assert payload["lead_anchor_summary"].startswith("[K1] collision:")
    assert payload["anchor_status_line"].startswith("anchor | [K1] collision:")
    assert payload["problem_route"] is None
    assert payload["problem_route_status_line"] == ""
    assert payload["llm_attempt_count"] == 2
    assert payload["llm_model"] == "gemma3:4b"
    assert payload["primary_status_line"].startswith(
        "generated | mode=llm_chronicle model=gemma3:4b fallback_mode=observed_history"
    )
    assert (
        payload["runtime_status_line"]
        == "state_document | tensions=0 collisions=1 crystals=2 posture=contradiction_with_retained_belief"
    )
    assert payload["artifact_policy_status_line"] == (
        "artifact_source=chronicle_pair | chronicle=yes companion=yes"
    )
    assert payload["handoff"] == {
        "queue_shape": "scribe_chronicle_ready",
        "requires_operator_action": False,
        "latest_available_source": "chronicle_pair",
        "lead_anchor_summary": result.lead_anchor_summary,
        "anchor_status_line": payload["anchor_status_line"],
        "problem_route_status_line": "",
        "companion_path": str(companion_path),
        "chronicle_path": str(chronicle_path),
        "primary_status_line": payload["primary_status_line"],
    }


def test_write_scribe_status_artifact_for_companion_only(tmp_path: Path) -> None:
    companion_path = tmp_path / "docs" / "chronicles" / "chronicle.json"
    result = ScribeDraftResult(
        generated_at="2026-03-13T04:23:10Z",
        status="generation_failed",
        source_db_path=":memory:",
        observed_counts={"tensions": 0, "collisions": 0, "crystals": 0},
        lead_anchor_summary="",
        fallback_mode="bootstrap_reflection",
        generation_mode="llm_chronicle",
        title_hint="Empty Chronicle",
        llm_model="qwen3.5:4b",
        llm_attempts=[
            {
                "model": "qwen3.5:4b",
                "status": "timeout",
                "error": "Ollama chat timed out",
                "error_kind": "OllamaError",
            }
        ],
        chronicle_path=None,
        companion_path=companion_path,
        error={"kind": "OllamaError", "message": "Ollama chat timed out"},
    )
    out_path = tmp_path / "docs" / "status" / "scribe_status_latest.json"

    written = run_scribe_cycle.write_scribe_status_artifact(result, out_path=out_path)

    assert written == out_path
    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert payload["status"] == "generation_failed"
    assert payload["latest_available_source"] == "companion_only"
    assert payload["state_document_posture"] == "anchor_only"
    assert payload["lead_anchor_summary"] == ""
    assert payload["anchor_status_line"] == ""
    assert payload["problem_route"] == {
        "family_code": "F4",
        "family": "execution_contract_integrity",
        "broken_invariant": "local_generation_latency_closure",
        "first_repair_surface": "model_runtime_timeout_budget",
        "do_not_repair_first": "chronicle_style_rewrite",
    }
    assert (
        payload["problem_route_status_line"] == "route | family=F4_execution_contract_integrity "
        "invariant=local_generation_latency_closure repair=model_runtime_timeout_budget"
    )
    assert payload["chronicle_path"] is None
    assert payload["companion_path"] == str(companion_path)
    assert payload["handoff"]["queue_shape"] == "scribe_companion_only"
    assert payload["handoff"]["requires_operator_action"] is False
    assert payload["primary_status_line"].startswith(
        "generation_failed | mode=llm_chronicle model=qwen3.5:4b fallback_mode=bootstrap_reflection"
    )


def test_build_scribe_status_payload_for_template_assist(tmp_path: Path) -> None:
    chronicle_path = tmp_path / "docs" / "chronicles" / "chronicle.md"
    companion_path = tmp_path / "docs" / "chronicles" / "chronicle.json"
    result = ScribeDraftResult(
        generated_at="2026-03-13T11:45:46Z",
        status="generated",
        source_db_path=str((tmp_path / "memory" / "soul.db").resolve()),
        observed_counts={"tensions": 1, "collisions": 0, "crystals": 0},
        lead_anchor_summary="[T9] tension: High PE valuation (46.7x) in a market pullback vs. Strong structural margin inflection...",
        fallback_mode="observed_history",
        generation_mode="template_assist",
        title_hint="Template Chronicle",
        llm_model="qwen3.5:4b",
        llm_attempts=[
            {
                "model": "qwen3.5:4b",
                "status": "boundary_rejected",
                "error": "Generated chronicle drifted beyond observed-history grounding: missing_observed_anchor",
                "error_kind": "semantic_boundary_violation",
            },
            {
                "model": "template_assist",
                "status": "generated",
            },
        ],
        chronicle_path=chronicle_path,
        companion_path=companion_path,
        error=None,
    )

    payload = run_scribe_cycle.build_scribe_status_payload(result)

    assert payload["generation_mode"] == "template_assist"
    assert payload["state_document_posture"] == "pressure_without_counterweight"
    assert payload["lead_anchor_summary"].startswith("[T9] tension:")
    assert payload["anchor_status_line"].startswith("anchor | [T9] tension:")
    assert payload["problem_route"] == {
        "family_code": "F1",
        "family": "grounding_evidence_integrity",
        "broken_invariant": "observed_anchor_closure",
        "first_repair_surface": "anchor_selection_and_grounding_prompt",
        "do_not_repair_first": "chronicle_style_or_personality_docs",
    }
    assert (
        payload["problem_route_status_line"] == "route | family=F1_grounding_evidence_integrity "
        "invariant=observed_anchor_closure repair=anchor_selection_and_grounding_prompt"
    )
    assert payload["primary_status_line"].startswith(
        "generated | mode=template_assist model=qwen3.5:4b fallback_mode=observed_history"
    )
    assert (
        payload["runtime_status_line"]
        == "state_document | tensions=1 collisions=0 crystals=0 posture=pressure_without_counterweight"
    )


def test_build_scribe_status_payload_routes_representation_drift(tmp_path: Path) -> None:
    companion_path = tmp_path / "docs" / "chronicles" / "chronicle.json"
    result = ScribeDraftResult(
        generated_at="2026-03-14T02:49:36Z",
        status="generated",
        source_db_path=str((tmp_path / "memory" / "soul.db").resolve()),
        observed_counts={"tensions": 1, "collisions": 0, "crystals": 0},
        lead_anchor_summary="[T9] tension: High PE valuation in a market pullback...",
        fallback_mode="observed_history",
        generation_mode="template_assist",
        title_hint="Recovered Chronicle",
        llm_model="gemma3:4b",
        llm_attempts=[
            {"model": "qwen3.5:4b", "status": "timeout"},
            {
                "model": "gemma3:4b",
                "status": "boundary_rejected",
                "error": (
                    "Generated chronicle drifted beyond observed-history grounding: "
                    "data streams, log entry, the user"
                ),
                "error_kind": "semantic_boundary_violation",
            },
            {"model": "template_assist", "status": "generated"},
        ],
        chronicle_path=tmp_path / "docs" / "chronicles" / "chronicle.md",
        companion_path=companion_path,
        error=None,
    )

    payload = run_scribe_cycle.build_scribe_status_payload(result)

    assert payload["problem_route"] == {
        "family_code": "F7",
        "family": "representation_localization_integrity",
        "broken_invariant": "chronicle_container_fidelity",
        "first_repair_surface": "post_generation_boundary_filter",
        "do_not_repair_first": "memory_or_identity_layers",
        "secondary_routes": [
            {
                "family_code": "F6",
                "family": "semantic_role_boundary_integrity",
                "broken_invariant": "chronicle_self_scope",
                "first_repair_surface": "semantic_boundary_guardrail",
                "do_not_repair_first": "memory_import_or_style_rewrite",
            },
            {
                "family_code": "F4",
                "family": "execution_contract_integrity",
                "broken_invariant": "local_generation_latency_closure",
                "first_repair_surface": "model_runtime_timeout_budget",
                "do_not_repair_first": "chronicle_style_rewrite",
            },
        ],
        "secondary_route_labels": [
            "F6_semantic_role_boundary_integrity",
            "F4_execution_contract_integrity",
        ],
    }
    assert (
        payload["problem_route_status_line"]
        == "route | family=F7_representation_localization_integrity "
        "invariant=chronicle_container_fidelity repair=post_generation_boundary_filter "
        "secondary=F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
    )
    assert payload["problem_route_secondary_labels"] == [
        "F6_semantic_role_boundary_integrity",
        "F4_execution_contract_integrity",
    ]
    assert payload["handoff"]["problem_route_secondary_labels"] == (
        "F6_semantic_role_boundary_integrity,F4_execution_contract_integrity"
    )


def test_build_scribe_status_payload_routes_semantic_role_drift(tmp_path: Path) -> None:
    companion_path = tmp_path / "docs" / "chronicles" / "chronicle.json"
    result = ScribeDraftResult(
        generated_at="2026-03-14T06:10:00Z",
        status="generated",
        source_db_path=str((tmp_path / "memory" / "soul.db").resolve()),
        observed_counts={"tensions": 1, "collisions": 0, "crystals": 0},
        lead_anchor_summary="[T9] tension: High PE valuation in a market pullback...",
        fallback_mode="observed_history",
        generation_mode="template_assist",
        title_hint="Recovered Chronicle",
        llm_model="gemma3:4b",
        llm_attempts=[
            {
                "model": "gemma3:4b",
                "status": "boundary_rejected",
                "error": (
                    "Generated chronicle drifted beyond observed-history grounding: "
                    "processing loops, data streams, the user"
                ),
                "error_kind": "semantic_boundary_violation",
            },
            {"model": "template_assist", "status": "generated"},
        ],
        chronicle_path=tmp_path / "docs" / "chronicles" / "chronicle.md",
        companion_path=companion_path,
        error=None,
    )

    payload = run_scribe_cycle.build_scribe_status_payload(result)

    assert payload["problem_route"] == {
        "family_code": "F6",
        "family": "semantic_role_boundary_integrity",
        "broken_invariant": "chronicle_self_scope",
        "first_repair_surface": "semantic_boundary_guardrail",
        "do_not_repair_first": "memory_import_or_style_rewrite",
    }
    assert (
        payload["problem_route_status_line"]
        == "route | family=F6_semantic_role_boundary_integrity "
        "invariant=chronicle_self_scope repair=semantic_boundary_guardrail"
    )
