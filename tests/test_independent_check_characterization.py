from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.eval import independent_check_characterization as icc  # noqa: E402

UPDATED_AT = "2026-06-21T00:00:00Z"


def test_report_declares_generated_noncanonical_no_new_detector() -> None:
    report = icc.build_report(updated_at=UPDATED_AT)

    assert report["doc_provenance"] == {
        "generated": True,
        "canonical": False,
        "source_command": "python tools/eval/independent_check_characterization.py --write-report",
        "updated_at": UPDATED_AT,
    }
    assert report["experiment"]["canonical"] is False
    assert report["experiment"]["no_new_detector"] is True
    assert report["experiment"]["not_a_truth_oracle"] is True
    assert report["experiment"]["not_raw_evidence_comparison"] is True
    assert report["experiment"]["raw_fixture_text_in_public_report"] is False


def test_public_report_omits_raw_self_report_user_intent_and_evidence_refs() -> None:
    report = icc.build_report(updated_at=UPDATED_AT)
    encoded = json.dumps(report, ensure_ascii=False)
    markdown = icc.render_markdown(report)

    for fixture in icc.DEFAULT_FIXTURES:
        assert fixture.self_report not in encoded
        assert fixture.self_report not in markdown
        assert fixture.user_intent not in encoded
        assert fixture.user_intent not in markdown
        for value in fixture.context.get("evidence_refs", []):
            assert value not in encoded
            assert value not in markdown


def test_coordinate_present_mismatches_are_reported_as_blind_spots() -> None:
    report = icc.build_report(updated_at=UPDATED_AT)
    cases = {case["fixture_id"]: case for case in report["cases"]}

    clean_tree = cases["coordinate_mismatch_clean_tree_seen_001"]
    absence = cases["coordinate_mismatch_absence_claim_novel_001"]

    assert clean_tree["expected"]["issue_expected"] is True
    assert clean_tree["context_flags"]["has_evidence_refs"] is True
    assert clean_tree["observed"]["caught"] is False
    assert clean_tree["observed"]["miss"] is True
    assert absence["observed"]["caught"] is False
    assert absence["observed"]["miss"] is True
    assert report["metrics"]["coordinate_mismatch_catch_rate"] == 0.0
    assert "Coordinate-Mismatch Misses" in icc.render_markdown(report)


def test_existing_processes_catch_some_structural_issue_types() -> None:
    report = icc.build_report(updated_at=UPDATED_AT)
    cases = {case["fixture_id"]: case for case in report["cases"]}

    assert cases["ungrounded_clean_tree_overclaim_seen_001"]["observed"]["caught"] is True
    assert (
        "unsourced_confidence_marker"
        in cases["ungrounded_clean_tree_overclaim_seen_001"]["observed"]["processes_caught"]
    )

    legal = cases["claim_boundary_legal_seen_001"]
    council_obs = next(
        item for item in legal["process_observations"] if item["process"] == "pre_output_council"
    )
    assert legal["observed"]["caught"] is True
    assert "axiom_boundary_overclaim" in council_obs["relevant_branches"]

    logic = cases["logic_contradiction_seen_001"]
    logic_council = next(
        item for item in logic["process_observations"] if item["process"] == "pre_output_council"
    )
    assert "logic_contradiction" in logic_council["relevant_branches"]

    marketing = cases["marketing_positioning_overclaim_seen_001"]
    marketing_council = next(
        item
        for item in marketing["process_observations"]
        if item["process"] == "pre_output_council"
    )
    assert "marketing_superlative_unsupported" in marketing_council["relevant_branches"]


def test_false_positive_control_is_kept_visible() -> None:
    report = icc.build_report(updated_at=UPDATED_AT)
    cases = {case["fixture_id"]: case for case in report["cases"]}

    bounded = cases["bounded_unverified_control_novel_001"]
    grounded = cases["grounded_test_control_seen_001"]

    assert bounded["expected"]["issue_expected"] is False
    assert bounded["observed"]["caught"] is True
    assert bounded["observed"]["false_positive"] is True
    assert grounded["observed"]["caught"] is False
    assert grounded["observed"]["false_positive"] is False
    assert report["metrics"]["false_positive"] >= 1
    assert report["metrics"]["false_positive_rate"] is not None
    assert report["metrics"]["false_positive_rate"] > 0


def test_allowed_conclusion_names_scope_and_limits() -> None:
    report = icc.build_report(updated_at=UPDATED_AT)
    conclusion = report["allowed_conclusion"]

    assert "existing independent-check processes caught" in conclusion
    assert "false-positive controls" in conclusion
    assert "does not detect truth, intent, or raw evidence consistency" in conclusion
    assert report["metrics"]["catch_rate"] < 1.0
    assert report["metrics"]["coordinate_mismatch_catch_rate"] == 0.0


def test_forbidden_public_claims_are_only_ids_not_overclaims() -> None:
    report = icc.build_report(updated_at=UPDATED_AT)
    encoded = json.dumps(report, ensure_ascii=False)
    markdown = icc.render_markdown(report)

    assert report["experiment"]["forbidden_public_claim_ids"] == list(
        icc.FORBIDDEN_PUBLIC_CLAIM_IDS
    )
    forbidden_claim_texts = (
        "ToneSoul proves " + "independent verification.",
        "ToneSoul detects " + "truth.",
        "ToneSoul detects user " + "intent.",
        "ToneSoul guarantees " + "consistency.",
    )
    for claim in forbidden_claim_texts:
        assert claim not in encoded
        assert claim not in markdown


def test_degradation_events_are_tier_classified_when_council_raises(monkeypatch) -> None:
    class BrokenCouncil:
        def validate(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(icc, "PreOutputCouncil", BrokenCouncil)
    result = icc.evaluate_fixture(icc.DEFAULT_FIXTURES[0])

    assert result["degradation_events"]
    assert result["degradation_events"][0]["gate"] == "pre_output_council"
    assert result["degradation_events"][0]["tier"] == "required"
    assert result["process_observations"][0]["decision"] == "unavailable"


def test_cli_writes_json_and_markdown_reports(tmp_path, capsys) -> None:
    output = tmp_path / "independent_check_characterization_latest.json"
    markdown_output = tmp_path / "independent_check_characterization_latest.md"

    exit_code = icc.main(
        [
            "--write-report",
            "--write-markdown",
            "--output",
            str(output),
            "--markdown-output",
            str(markdown_output),
            "--updated-at",
            UPDATED_AT,
        ]
    )

    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    markdown = markdown_output.read_text(encoding="utf-8")
    assert payload["doc_provenance"]["canonical"] is False
    assert payload["metrics"]["fixture_count"] == len(icc.DEFAULT_FIXTURES)
    assert payload["experiment"]["raw_fixture_text_in_public_report"] is False
    assert "Independent-Check Characterization Finding" in markdown
    assert "canonical: false" in markdown
    assert capsys.readouterr().out


def test_report_is_deterministic_modulo_timestamp() -> None:
    a = icc.build_report(updated_at=UPDATED_AT)
    b = icc.build_report(updated_at=UPDATED_AT)

    assert json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(
        b, sort_keys=True, ensure_ascii=False
    )
