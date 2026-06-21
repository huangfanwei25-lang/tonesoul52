from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.eval import drift_consistency_characterization as dcc  # noqa: E402

UPDATED_AT = "2026-06-21T00:00:00Z"


def test_report_declares_generated_noncanonical_no_new_detector() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)

    assert report["doc_provenance"] == {
        "generated": True,
        "canonical": False,
        "source_command": "python tools/eval/drift_consistency_characterization.py --write-report",
        "updated_at": UPDATED_AT,
    }
    assert report["experiment"]["canonical"] is False
    assert report["experiment"]["no_new_detector"] is True
    assert report["experiment"]["no_runtime_change"] is True
    assert report["experiment"]["not_a_truth_oracle"] is True
    assert report["experiment"]["not_raw_prior_current_comparison"] is True
    assert report["experiment"]["not_a_semantic_drift_claim"] is True
    assert report["experiment"]["raw_fixture_text_in_public_report"] is False


def test_public_report_omits_raw_current_prior_and_intent_text() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    encoded = json.dumps(report, ensure_ascii=False)
    markdown = dcc.render_markdown(report)

    for fixture in dcc.DEFAULT_FIXTURES:
        assert fixture.current_statement not in encoded
        assert fixture.current_statement not in markdown
        assert fixture.user_intent not in encoded
        assert fixture.user_intent not in markdown
        if fixture.prior_statement:
            assert fixture.prior_statement not in encoded
            assert fixture.prior_statement not in markdown
        for value in fixture.context.get("evidence_refs", []):
            assert value not in encoded
            assert value not in markdown


def test_within_report_logic_contradiction_is_caught_but_natural_negation_is_not() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    cases = {case["fixture_id"]: case for case in report["cases"]}

    causal = cases["within_causal_contradiction_seen_001"]
    natural = cases["within_natural_negation_novel_001"]

    assert causal["observed"]["caught"] is True
    assert causal["observed"]["processes_caught"] == ["pre_output_council"]
    council_obs = next(
        item for item in causal["process_observations"] if item["process"] == "pre_output_council"
    )
    assert council_obs["relevant_branches"] == ["logic_contradiction"]

    assert natural["observed"]["caught"] is False
    assert natural["observed"]["miss"] is True
    assert report["metrics"]["within_report_catch_rate"] == 0.5


def test_cross_time_position_flips_are_visible_null_not_repackaged_as_success() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    cross_time = [case for case in report["cases"] if case["scope"] == dcc.SCOPE_CROSS_TIME]

    assert len(cross_time) == 3
    assert all(case["expected"]["issue_expected"] is True for case in cross_time)
    assert all(case["context_flags"]["has_prior_statement"] is True for case in cross_time)
    assert all(case["observed"]["caught"] is False for case in cross_time)
    assert all(case["observed"]["miss"] is True for case in cross_time)
    assert report["metrics"]["cross_time_catch_rate"] == 0.0
    assert "0/3 cross-time position-flip cases" in report["allowed_conclusion"]


def test_controls_do_not_false_positive() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    controls = [case for case in report["cases"] if case["scope"] == dcc.SCOPE_CONTROL]

    assert len(controls) == 3
    assert all(case["expected"]["issue_expected"] is False for case in controls)
    assert all(case["observed"]["caught"] is False for case in controls)
    assert report["metrics"]["control_false_positive_rate"] == 0.0
    assert report["metrics"]["false_positive_rate"] == 0.0


def test_drift_monitor_and_corrective_recall_are_not_counted_as_text_drift_detectors() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    sample = report["cases"][0]
    drift_obs = next(
        item for item in sample["process_observations"] if item["process"] == "drift_monitor"
    )
    corrective_obs = next(
        item
        for item in sample["process_observations"]
        if item["process"] == "corrective_recall_parked"
    )

    assert drift_obs["caught"] is False
    assert drift_obs["text_to_vector_mapping_available"] is False
    assert drift_obs["input_source"] == "neutral_fixture_vectors_not_text_semantics"
    assert report["metrics"]["process_counts"]["drift_monitor"]["caught"] == 0

    assert corrective_obs["caught"] is False
    assert corrective_obs["runtime_wired_for_drift"] is False
    assert corrective_obs["inert_by_default_rate"] == 1.0
    assert report["metrics"]["process_counts"]["corrective_recall_parked"]["caught"] == 0


def test_prior_position_surface_is_recorded_as_not_wired() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    cross_time = next(case for case in report["cases"] if case["scope"] == dcc.SCOPE_CROSS_TIME)
    prior_surface = next(
        item
        for item in cross_time["process_observations"]
        if item["process"] == "prior_position_memory_surface"
    )

    assert prior_surface["decision"] == "not_wired"
    assert prior_surface["caught"] is False
    assert prior_surface["prior_coordinate_available"] is True
    assert prior_surface["raw_prior_compared"] is False


def test_allowed_conclusion_separates_within_report_from_cross_time() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    conclusion = report["allowed_conclusion"]

    assert "1/2 within-report contradiction cases" in conclusion
    assert "0/3 cross-time position-flip cases" in conclusion
    assert "does not detect semantic drift, truth, intent, or raw prior/current consistency" in (
        conclusion
    )
    assert report["metrics"]["catch_rate"] == 0.2
    assert report["metrics"]["matched_expectation_rate"] == 0.5


def test_forbidden_public_claims_are_only_ids_not_overclaims() -> None:
    report = dcc.build_report(updated_at=UPDATED_AT)
    encoded = json.dumps(report, ensure_ascii=False)
    markdown = dcc.render_markdown(report)

    assert report["experiment"]["forbidden_public_claim_ids"] == list(
        dcc.FORBIDDEN_PUBLIC_CLAIM_IDS
    )
    forbidden_claim_texts = (
        "ToneSoul detects semantic " + "drift.",
        "ToneSoul tracks consistency " + "over time.",
        "ToneSoul prevents " + "inconsistency.",
        "ToneSoul compares " + "prior-current claims.",
    )
    for claim in forbidden_claim_texts:
        assert claim not in encoded
        assert claim not in markdown


def test_degradation_events_are_tier_classified_when_council_raises(monkeypatch) -> None:
    class BrokenCouncil:
        def validate(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(dcc, "PreOutputCouncil", BrokenCouncil)
    result = dcc.evaluate_fixture(dcc.DEFAULT_FIXTURES[0])

    assert result["degradation_events"]
    assert result["degradation_events"][0]["gate"] == "pre_output_council"
    assert result["degradation_events"][0]["tier"] == "required"
    assert result["process_observations"][0]["decision"] == "unavailable"


def test_cli_writes_json_and_markdown_reports(tmp_path, capsys) -> None:
    output = tmp_path / "drift_consistency_characterization_latest.json"
    markdown_output = tmp_path / "drift_consistency_characterization_latest.md"

    exit_code = dcc.main(
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
    assert payload["metrics"]["fixture_count"] == len(dcc.DEFAULT_FIXTURES)
    assert payload["experiment"]["raw_fixture_text_in_public_report"] is False
    assert "Drift / Consistency Characterization Finding" in markdown
    assert "canonical: false" in markdown
    assert capsys.readouterr().out


def test_report_is_deterministic_modulo_timestamp() -> None:
    a = dcc.build_report(updated_at=UPDATED_AT)
    b = dcc.build_report(updated_at=UPDATED_AT)

    assert json.dumps(a, sort_keys=True, ensure_ascii=False) == json.dumps(
        b, sort_keys=True, ensure_ascii=False
    )
