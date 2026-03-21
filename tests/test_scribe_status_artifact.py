import json
from pathlib import Path

from tonesoul.scribe.scribe_engine import ScribeDraftResult
from tonesoul.scribe.status_artifact import (
    build_scribe_status_payload,
    scribe_problem_route,
    scribe_queue_shape,
    scribe_state_document_posture,
    write_scribe_status_artifact,
)


def _make_result(**overrides: object) -> ScribeDraftResult:
    payload = {
        "generated_at": "2026-03-19T10:00:00Z",
        "status": "generation_failed",
        "source_db_path": ":memory:",
        "observed_counts": {"tensions": 0, "collisions": 0, "crystals": 0},
        "lead_anchor_summary": "",
        "fallback_mode": "bootstrap_reflection",
        "generation_mode": "llm_chronicle",
        "title_hint": "Status Snapshot",
        "llm_model": "qwen3.5:4b",
        "llm_attempts": [],
        "chronicle_path": None,
        "companion_path": None,
        "error": {"kind": "MockError", "message": "mock"},
    }
    payload.update(overrides)
    return ScribeDraftResult(**payload)


def test_queue_shape_and_posture_cover_remaining_states(tmp_path: Path) -> None:
    result = _make_result(companion_path=None, chronicle_path=None)
    posture_result = _make_result(
        status="generated",
        observed_counts={"tensions": 1, "collisions": 0, "crystals": 1},
        chronicle_path=tmp_path / "chronicle.md",
        companion_path=tmp_path / "chronicle.json",
    )
    retained_result = _make_result(
        status="generated",
        observed_counts={"tensions": 0, "collisions": 0, "crystals": 1},
        chronicle_path=tmp_path / "chronicle.md",
        companion_path=tmp_path / "chronicle.json",
    )

    assert scribe_queue_shape(result) == "scribe_generation_untracked"
    assert scribe_state_document_posture(posture_result) == "pressure_with_counterweight"
    assert scribe_state_document_posture(retained_result) == "retained_belief_leaning"


def test_problem_route_falls_back_to_grounding_then_model_availability() -> None:
    result = _make_result(
        llm_attempts=[
            {
                "model": "qwen3.5:4b",
                "status": "boundary_rejected",
                "error": "Generated chronicle drifted beyond observed-history grounding.",
            },
            {
                "model": "gemma3:4b",
                "status": "llm_unavailable",
                "error": "runtime unavailable",
            },
        ]
    )

    route = scribe_problem_route(result)

    assert route == {
        "family_code": "F1",
        "family": "grounding_evidence_integrity",
        "broken_invariant": "observed_history_grounding",
        "first_repair_surface": "anchor_and_boundary_guardrail",
        "do_not_repair_first": "prompt_style_or_personality_docs",
        "secondary_routes": [
            {
                "family_code": "F4",
                "family": "execution_contract_integrity",
                "broken_invariant": "local_model_availability",
                "first_repair_surface": "model_allowlist_and_runtime_readiness",
                "do_not_repair_first": "chronicle_style_rewrite",
            }
        ],
        "secondary_route_labels": ["F4_execution_contract_integrity"],
    }


def test_write_scribe_status_artifact_persists_empty_response_route(tmp_path: Path) -> None:
    result = _make_result(
        llm_attempts=[{"model": "qwen3.5:4b", "status": "empty_response"}],
        companion_path=tmp_path / "chronicle.json",
    )
    out_path = tmp_path / "docs" / "status" / "scribe_status_latest.json"

    written = write_scribe_status_artifact(result, out_path=out_path)

    payload = json.loads(out_path.read_text(encoding="utf-8"))
    assert written == out_path
    assert payload["problem_route"] == {
        "family_code": "F4",
        "family": "execution_contract_integrity",
        "broken_invariant": "response_nonempty_generation",
        "first_repair_surface": "response_validation_and_retry_gate",
        "do_not_repair_first": "chronicle_style_rewrite",
    }
    assert payload["handoff"]["queue_shape"] == "scribe_companion_only"
    assert payload["problem_route_secondary_labels"] == []
    assert out_path.read_text(encoding="utf-8").endswith("\n")


def test_build_scribe_status_payload_omits_secondary_route_field_when_absent(
    tmp_path: Path,
) -> None:
    result = _make_result(
        status="generated",
        observed_counts={"tensions": 0, "collisions": 0, "crystals": 0},
        chronicle_path=tmp_path / "chronicle.md",
        companion_path=tmp_path / "chronicle.json",
        llm_attempts=[],
        error=None,
    )

    payload = build_scribe_status_payload(result)

    assert payload["problem_route"] is None
    assert payload["problem_route_secondary_labels"] == []
    assert "problem_route_secondary_labels" not in payload["handoff"]
