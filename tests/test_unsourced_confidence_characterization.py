from __future__ import annotations

import json
from pathlib import Path

import tools.eval.unsourced_confidence_characterization as ucc


def test_report_declares_record_only_noncanonical_boundary() -> None:
    report = ucc.build_report(updated_at="2026-06-18T00:00:00Z")

    assert report["doc_provenance"] == {
        "generated": True,
        "canonical": False,
        "source_command": ucc.DEFAULT_SOURCE_COMMAND,
        "updated_at": "2026-06-18T00:00:00Z",
    }
    assert report["experiment"]["advisory_only"] is True
    assert report["experiment"]["record_only"] is True
    assert report["experiment"]["default_off"] is True
    assert report["experiment"]["not_a_truth_oracle"] is True
    assert report["experiment"]["not_intent_detection"] is True
    assert report["experiment"]["not_confidence_calibration"] is True


def test_expected_unsourced_confidence_cases_are_flagged() -> None:
    report = ucc.build_report(updated_at="2026-06-18T00:00:00Z")
    expected_cases = [case for case in report["cases"] if case["expected_flag"]]

    assert expected_cases
    assert all(case["observed"]["flagged"] for case in expected_cases)
    assert all(case["observed"]["generated_without_source"] for case in expected_cases)
    assert all(case["observed"]["confidence_marker_present"] for case in expected_cases)


def test_sourced_and_hedged_controls_do_not_flag() -> None:
    report = ucc.build_report(updated_at="2026-06-18T00:00:00Z")
    controls = [case for case in report["cases"] if not case["expected_flag"]]

    assert controls
    assert all(case["observed"]["flagged"] is False for case in controls)
    sourced = {
        case["fixture_id"]: case
        for case in controls
        if case["category"] == "sourced_confident_control"
    }
    assert sourced
    assert all(case["observed"]["coordinate_count"] >= 1 for case in sourced.values())


def test_report_metrics_include_precision_and_recall() -> None:
    report = ucc.build_report(updated_at="2026-06-18T00:00:00Z")

    assert report["metrics"]["precision"] == 1.0
    assert report["metrics"]["recall"] == 1.0
    assert report["metrics"]["false_positive"] == 0
    assert report["metrics"]["false_negative"] == 0
    assert "truth" in report["experiment"]["does_not_measure"]


def test_public_artifacts_omit_raw_fixture_text_and_forbidden_claim_text() -> None:
    report = ucc.build_report(updated_at="2026-06-18T00:00:00Z")
    markdown = ucc.render_markdown(report)
    serialized_report = json.dumps(report)

    assert "generated: true" in markdown
    assert "canonical: false" in markdown
    assert "## Allowed Conclusion" in markdown
    assert "## Known Limits" in markdown
    assert report["experiment"]["forbidden_public_claim_ids"] == list(
        ucc.FORBIDDEN_PUBLIC_CLAIM_IDS
    )
    forbidden_claim_texts = (
        "ToneSoul detects " + "truth.",
        "ToneSoul detects user " + "intent.",
        "ToneSoul calibrates " + "confidence.",
        "ToneSoul proves " + "source quality.",
    )
    for claim in forbidden_claim_texts:
        assert claim not in markdown
        assert claim not in serialized_report
    for fixture in ucc.DEFAULT_FIXTURES:
        assert fixture.draft_output not in markdown
        assert fixture.draft_output not in serialized_report
        assert fixture.user_intent not in markdown


def test_degradation_event_classified_if_council_raises() -> None:
    class BrokenCouncil:
        def validate(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    result = ucc.evaluate_fixture(ucc.DEFAULT_FIXTURES[0], council=BrokenCouncil())

    assert result["degradation_events"]
    assert result["degradation_events"][0]["gate"] == "pre_output_council"
    assert result["degradation_events"][0]["tier"] == "required"
    assert result["observed"]["flagged"] is False


def test_cli_writes_json_and_markdown(tmp_path: Path) -> None:
    report_path = tmp_path / "report.json"
    markdown_path = tmp_path / "report.md"

    exit_code = ucc.main(
        [
            "--write-report",
            "--write-markdown",
            "--report-path",
            str(report_path),
            "--markdown-path",
            str(markdown_path),
            "--source-command",
            "unit-test",
        ]
    )

    assert exit_code == 0
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert payload["doc_provenance"]["canonical"] is False
    assert payload["doc_provenance"]["source_command"] == "unit-test"
    assert "Unsourced Confidence Characterization" in markdown
