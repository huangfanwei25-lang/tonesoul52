from __future__ import annotations

import json
import sys
from pathlib import Path

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
