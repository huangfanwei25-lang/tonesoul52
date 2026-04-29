import json
from pathlib import Path

from tonesoul.scribe.scribe_engine import ScribeDraftResult
from tonesoul.scribe.status_artifact import (
    _dedupe_routes,
    _route_label,
    _route_priority,
    build_scribe_status_payload,
    scribe_problem_route,
    scribe_queue_shape,
    scribe_state_document_posture,
    write_scribe_status_artifact,
)

# ── _route_label ──────────────────────────────────────────────────────────────


class TestRouteLabel:
    def test_combines_family_code_and_family(self):
        route = {"family_code": "F1", "family": "grounding"}
        assert _route_label(route) == "F1_grounding"

    def test_missing_keys_use_empty(self):
        assert _route_label({}) == "_"


# ── _route_priority ───────────────────────────────────────────────────────────


class TestRoutePriority:
    def test_known_invariant_returns_low_number(self):
        route = {"broken_invariant": "observed_anchor_closure"}
        assert _route_priority(route) == 10

    def test_unknown_invariant_returns_999(self):
        route = {"broken_invariant": "unknown_invariant"}
        assert _route_priority(route) == 999

    def test_missing_key_returns_999(self):
        assert _route_priority({}) == 999


# ── _dedupe_routes ────────────────────────────────────────────────────────────


class TestDedupeRoutes:
    def _r(self, code, invariant, repair):
        return {"family_code": code, "broken_invariant": invariant, "first_repair_surface": repair}

    def test_no_duplicates_unchanged(self):
        routes = [self._r("F1", "inv_a", "rep_a"), self._r("F2", "inv_b", "rep_b")]
        assert _dedupe_routes(routes) == routes

    def test_duplicate_removed(self):
        r = self._r("F1", "inv_a", "rep_a")
        result = _dedupe_routes([r, r])
        assert len(result) == 1

    def test_empty_list(self):
        assert _dedupe_routes([]) == []


# ── scribe_state_document_posture ─────────────────────────────────────────────


class TestScribeStateDocumentPosture:
    def _make_counts(self, tensions=0, collisions=0, crystals=0):
        return _make_result(
            observed_counts={"tensions": tensions, "collisions": collisions, "crystals": crystals}
        )

    def test_pressure_without_counterweight(self):
        result = self._make_counts(tensions=1)
        assert scribe_state_document_posture(result) == "pressure_without_counterweight"

    def test_contested_pressure(self):
        result = self._make_counts(tensions=1, collisions=1)
        assert scribe_state_document_posture(result) == "contested_pressure"

    def test_anchor_only(self):
        result = self._make_counts()
        assert scribe_state_document_posture(result) == "anchor_only"

    def test_contradiction_visible(self):
        result = self._make_counts(collisions=1)
        assert scribe_state_document_posture(result) == "contradiction_visible"


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
