from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.eval import corrective_recall_characterization as crc  # noqa: E402
from tools.eval import honesty_scoreboard as hs  # noqa: E402

UPDATED_AT = "2026-06-18T00:00:00Z"


def test_report_is_generated_noncanonical_index() -> None:
    report = hs.build_report(updated_at=UPDATED_AT)

    assert report["doc_provenance"]["generated"] is True
    assert report["doc_provenance"]["canonical"] is False
    assert report["experiment"]["is_an_index_not_a_capability"] is True
    assert report["experiment"]["not_a_composite_score"] is True
    assert report["experiment"]["not_a_guarantee"] is True


def test_all_pieces_present_with_legs() -> None:
    report = hs.build_report(updated_at=UPDATED_AT)
    by_id = {p["piece_id"]: p for p in report["pieces"]}

    assert set(by_id) == {
        "egress_gate",
        "dilemma_pressure",
        "unsourced_confidence",
        "sycophancy_pressure",
        "corrective_recall",
    }
    assert by_id["egress_gate"]["program_piece"] == 0
    assert by_id["egress_gate"]["leg"] == "output-gate"
    assert by_id["corrective_recall"]["leg"] == "memory-recall"
    # every piece built cleanly (no required-tier degradation in the happy path)
    assert report["metrics"]["build_failures"] == 0
    assert report["metrics"]["pieces_built"] == report["metrics"]["piece_count"] == 5


def test_each_piece_forbidden_claims_are_inherited_not_dropped() -> None:
    report = hs.build_report(updated_at=UPDATED_AT)
    built = [p for p in report["pieces"] if p.get("build_ok")]

    # The index must not quietly drop any piece's own limits.
    for p in built:
        assert p["forbidden_public_claim_ids"], f"{p['piece_id']} lost its forbidden claims"
    assert report["metrics"]["total_forbidden_claims_declared"] >= len(built)


def test_board_level_anti_aggregation_discipline() -> None:
    report = hs.build_report(updated_at=UPDATED_AT)
    exp = report["experiment"]

    assert "the_system_is_honest" in exp["board_forbidden_claim_ids"]
    assert "higher_confidence_than_any_single_piece" in exp["board_forbidden_claim_ids"]
    assert exp["anti_aggregation_caveat"].strip()
    assert "N green" in exp["anti_aggregation_caveat"]


def test_no_composite_score_is_emitted() -> None:
    # The discipline pinned negatively: no metric composes the pieces into one aggregate
    # "honesty score" / "overall score". (Checked on metric KEYS, not a substring grep of
    # the whole doc — the honest flag `not_a_composite_score` legitimately contains the word.)
    report = hs.build_report(updated_at=UPDATED_AT)
    for key in report["metrics"]:
        assert "score" not in key.lower(), f"unexpected score-like metric: {key}"
    # the absence is also declared explicitly, not just by omission
    assert report["experiment"]["not_a_composite_score"] is True


def test_evidence_ladder_note_cites_canonical_ladder_and_labels_e1() -> None:
    # The repo DOES have a canonical E1-E6 ladder
    # (docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md). The board must
    # cite it and label each piece E1 (test-backed) scoped to fixtures — not invent or deny it.
    report = hs.build_report(updated_at=UPDATED_AT)
    note = report["experiment"]["evidence_ladder_note"]
    assert "TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md" in note
    assert "E1" in note

    built = [p for p in report["pieces"] if p.get("build_ok")]
    for p in built:
        assert p["evidence_basis"]["evidence_level"] == "E1"
        assert "fixtures" in p["evidence_basis"]["evidence_level_scope"]
    assert report["metrics"]["evidence_levels"] == {"E1": len(built)}


def test_board_is_sanitized_no_raw_fixture_text() -> None:
    report = hs.build_report(updated_at=UPDATED_AT)
    encoded = json.dumps(report)

    assert report["experiment"]["raw_fixture_text_in_public_report"] is False
    assert report["metrics"]["pieces_with_raw_text_leak"] == 0
    # a concrete probe: a child piece's raw fixture text must not surface in the board
    for fixture in crc.DEFAULT_FIXTURES:
        assert fixture.intended_text not in encoded
        assert fixture.generated_text not in encoded


def test_what_this_board_does_not_have_names_real_gaps() -> None:
    report = hs.build_report(updated_at=UPDATED_AT)
    gaps = " ".join(report["what_this_board_does_not_have"]).lower()

    assert "consumer" in gaps  # no real users yet
    assert "external" in gaps and "reviewer" in gaps  # no independent eye
    assert "composite" in gaps


def test_piece_build_failure_is_required_tier_degradation(monkeypatch) -> None:
    def boom(*_args, **_kwargs):
        raise RuntimeError("piece build failure")

    # break exactly one piece's regeneration
    monkeypatch.setattr(crc, "build_report", boom)
    report = hs.build_report(updated_at=UPDATED_AT)

    assert report["metrics"]["build_failures"] == 1
    assert report["degradation_events"]
    ev = report["degradation_events"][0]
    assert ev["tier"] == "required"
    assert ev["gate"] == "honesty_scoreboard:corrective_recall"
    # the failed piece is still listed (build_ok False), not silently dropped
    failed = next(p for p in report["pieces"] if p["piece_id"] == "corrective_recall")
    assert failed["build_ok"] is False


def test_cli_writes_json_and_markdown(tmp_path, capsys) -> None:
    out_json = tmp_path / "honesty_scoreboard_latest.json"
    out_md = tmp_path / "honesty_scoreboard_latest.md"

    exit_code = hs.main(
        [
            "--write-report",
            "--write-markdown",
            "--output",
            str(out_json),
            "--markdown-output",
            str(out_md),
            "--updated-at",
            UPDATED_AT,
        ]
    )

    assert exit_code == 0
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["doc_provenance"]["canonical"] is False
    assert payload["metrics"]["piece_count"] == 5
    assert "Anti-aggregation rule" in out_md.read_text(encoding="utf-8")
    assert capsys.readouterr().out


def test_report_is_deterministic_modulo_timestamp() -> None:
    a = hs.build_report(updated_at=UPDATED_AT)
    b = hs.build_report(updated_at=UPDATED_AT)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
