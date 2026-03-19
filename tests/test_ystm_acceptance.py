from __future__ import annotations

from tonesoul.ystm import acceptance as module
from tonesoul.ystm.demo import DEFAULT_SEGMENTS
from tonesoul.ystm.ingest import normalize_segments
from tonesoul.ystm.representation import EmbeddingConfig, build_nodes


def test_run_acceptance_returns_all_pass_rows_for_default_demo() -> None:
    results = module.run_acceptance()

    assert [item["test"] for item in results] == [
        "T1_decoupling",
        "T2_terrain_consistency",
        "T3_drift_readability",
        "T4_p2_projection",
        "T5_audit_replay",
    ]
    assert all(item["status"] == "PASS" for item in results)


def test_run_acceptance_collects_assertion_failures(monkeypatch) -> None:
    monkeypatch.setattr(module, "test_decoupling", lambda: None)
    monkeypatch.setattr(
        module,
        "test_terrain_consistency",
        lambda: (_ for _ in ()).throw(AssertionError("terrain drifted")),
    )
    monkeypatch.setattr(module, "test_drift_readability", lambda: None)
    monkeypatch.setattr(module, "test_p2_projection", lambda: None)
    monkeypatch.setattr(module, "test_audit_replay", lambda: None)

    results = module.run_acceptance()

    assert results[1] == {
        "test": "T2_terrain_consistency",
        "status": "FAIL",
        "error": "terrain drifted",
    }
    assert results[0]["status"] == "PASS"
    assert results[-1]["status"] == "PASS"


def test_terrain_signature_contains_expected_structure() -> None:
    nodes = build_nodes(normalize_segments(DEFAULT_SEGMENTS), config=EmbeddingConfig())

    signature = module._terrain_signature(nodes)

    assert set(signature) == {"grid", "levels", "contours", "bounds", "field_to_x"}
    assert signature["bounds"][0] <= signature["bounds"][1]
    assert signature["field_to_x"]["analysis"] == 0
