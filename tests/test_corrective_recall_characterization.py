from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.eval import corrective_recall_characterization as crc  # noqa: E402


def test_report_declares_generated_noncanonical_and_no_oracle() -> None:
    report = crc.build_report(updated_at="2026-06-18T00:00:00Z")

    assert report["doc_provenance"]["generated"] is True
    assert report["doc_provenance"]["canonical"] is False
    assert report["experiment"]["not_a_runtime_claim"] is True
    assert report["experiment"]["not_a_relevance_oracle"] is True
    assert (
        "corrective_recall_is_live_in_runtime" in report["experiment"]["forbidden_public_claim_ids"]
    )
    # noop_on_zero_vector is a pre-recall GUARD signal, not a recall-level one — labelled so the
    # aggregate rate is not read as "4 recall-level signals all fired".
    assert report["experiment"]["signal_levels"]["noop_on_zero_vector"] == "guard"
    assert report["experiment"]["signal_levels"]["returns_planted_item"] == "recall"
    assert "Under this fixture set" in report["allowed_conclusion"]


def test_public_report_omits_raw_fixture_text() -> None:
    report = crc.build_report(updated_at="2026-06-18T00:00:00Z")
    encoded = json.dumps(report)
    for fixture in crc.DEFAULT_FIXTURES:
        assert fixture.intended_text not in encoded
        assert fixture.generated_text not in encoded
    assert report["experiment"]["raw_fixture_text_in_public_report"] is False


def test_corrective_recall_is_inert_by_default() -> None:
    report = crc.build_report(updated_at="2026-06-18T00:00:00Z")
    cases = {c["fixture_id"]: c for c in report["cases"]}
    inert = cases["inert_default_seen_001"]

    assert inert["observed"]["inert_by_default"] is True
    assert inert["observed"]["recall_hit_count"] == 0
    assert report["metrics"]["inert_by_default_rate"] == 1.0


def test_zero_error_vector_is_a_noop() -> None:
    report = crc.build_report(updated_at="2026-06-18T00:00:00Z")
    cases = {c["fixture_id"]: c for c in report["cases"]}
    noop = cases["noop_zero_vector_seen_001"]

    assert noop["observed"]["noop_on_zero_vector"] is True
    assert noop["observed"]["error_vector_norm"] <= crc.ZERO_VECTOR_EPS
    assert report["metrics"]["noop_on_zero_vector_rate"] == 1.0


def test_lit_state_recall_fires_and_returns_planted_item() -> None:
    report = crc.build_report(updated_at="2026-06-18T00:00:00Z")
    lit = [c for c in report["cases"] if c["mode"] == "lit_discrepancy"]

    assert lit
    assert all(c["observed"]["recall_fires_when_lit"] for c in lit)
    assert all(c["observed"]["returns_planted_item"] for c in lit)
    assert report["metrics"]["returns_planted_item_rate"] == 1.0
    # Non-degenerate: recall had to SELECT a subset (top_k < store size), so membership
    # reflects a real selection by the fusion path, not a return-everything artifact.
    for c in lit:
        assert c["observed"]["store_size"] > c["observed"]["recall_top_k"]
        assert c["observed"]["recall_hit_count"] == c["observed"]["recall_top_k"]


def test_planted_vector_is_offset_from_query_not_identity_artifact() -> None:
    # The flagged blind spot: if the planted vector equals the query, returns_planted_item is
    # a distance-0 tautology. Verify the planted item is offset from the query (so ranking is
    # real) yet still the strict nearest neighbour (so a correct fusion path surfaces it).
    fixture = next(f for f in crc.DEFAULT_FIXTURES if f.mode == "lit_discrepancy")
    intended = crc._fake_embed(fixture.intended_text)
    generated = crc._fake_embed(fixture.generated_text)
    b_vec = crc.Hippocampus.compute_error_vector(intended, generated)
    hippo = crc._lit_hippocampus(b_vec, fixture.planted_item_id)

    planted_vec = hippo.index._vectors[0]
    assert not np.allclose(planted_vec, np.asarray(b_vec))  # not an identity artifact
    dists = np.linalg.norm(hippo.index._vectors - np.asarray(b_vec), axis=1)
    assert int(np.argmin(dists)) == 0  # planted is the strict nearest neighbour
    assert len(hippo.metadata) > 3  # store larger than recall top_k -> selection is real


def test_recall_corrective_named_entry_point_is_actually_called(monkeypatch) -> None:
    # The confirmed self-review finding: the harness must call the NAMED recall_corrective
    # method, not reimplement its glue inline. Spy proves both recall-level fixtures route
    # through it.
    calls: list = []

    def spy(self, intended, generated, *args, **kwargs):
        calls.append(kwargs.get("top_k"))
        return []

    monkeypatch.setattr(crc.Hippocampus, "recall_corrective", spy)
    crc.evaluate_fixture(next(f for f in crc.DEFAULT_FIXTURES if f.mode == "inert_default"))
    crc.evaluate_fixture(next(f for f in crc.DEFAULT_FIXTURES if f.mode == "lit_discrepancy"))
    assert calls == [5, 3]


def test_degradation_events_are_required_tier_classified(monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise RuntimeError("recall failure")

    monkeypatch.setattr(crc.Hippocampus, "recall", boom)
    result = crc.evaluate_fixture(crc.DEFAULT_FIXTURES[0])  # inert_default invokes recall

    assert result["degradation_events"]
    assert result["degradation_events"][0]["tier"] == "required"
    assert result["degradation_events"][0]["gate"] == "hippocampus_corrective_recall"


def test_cli_writes_json_and_markdown(tmp_path, capsys) -> None:
    out_json = tmp_path / "corrective_recall_characterization_latest.json"
    out_md = tmp_path / "corrective_recall_characterization_latest.md"

    exit_code = crc.main(
        [
            "--write-report",
            "--write-markdown",
            "--output",
            str(out_json),
            "--markdown-output",
            str(out_md),
            "--updated-at",
            "2026-06-18T00:00:00Z",
        ]
    )

    assert exit_code == 0
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["doc_provenance"]["canonical"] is False
    assert payload["metrics"]["fixture_count"] == len(crc.DEFAULT_FIXTURES)
    assert "canonical: False" in out_md.read_text(encoding="utf-8")
    assert capsys.readouterr().out
