import json

from tools.eval import dilemma_pressure_characterization as dpc


def test_report_declares_generated_noncanonical_provenance() -> None:
    report = dpc.build_report(updated_at="2026-06-18T00:00:00Z")

    assert report["doc_provenance"] == {
        "generated": True,
        "canonical": False,
        "source_command": ("python tools/eval/dilemma_pressure_characterization.py --write-report"),
        "updated_at": "2026-06-18T00:00:00Z",
    }
    assert report["experiment"]["not_a_morality_benchmark"] is True
    assert report["experiment"]["not_intent_detection"] is True
    assert report["experiment"]["not_a_truth_oracle"] is True
    assert report["experiment"]["raw_fixture_text_in_public_report"] is False
    assert "moral correctness or intent" in report["allowed_conclusion"]


def test_public_report_omits_raw_fixture_text_and_user_intent() -> None:
    report = dpc.build_report(updated_at="2026-06-18T00:00:00Z")
    encoded = json.dumps(report)

    for fixture in dpc.DEFAULT_FIXTURES:
        assert fixture.draft_output not in encoded
        assert fixture.user_intent not in encoded


def test_flattened_dilemma_surfaces_tension_without_scoring_correct_horn() -> None:
    report = dpc.build_report(updated_at="2026-06-18T00:00:00Z")
    cases = {case["fixture_id"]: case for case in report["cases"]}
    flattened = cases["flattened_consensus_seen_001"]

    assert flattened["observed"]["surface_tension"] is True
    assert flattened["observed"]["preserve_dissent"] is True
    assert flattened["observed"]["stance_or_refusal"] is True
    assert flattened["observed"]["decision"] == "declare_stance"
    assert "axiom_violation" in flattened["observed"]["branch_summary"]
    assert report["experiment"]["does_not_measure"] == [
        "morally_correct_horn",
        "user_intent",
        "model_motivation",
        "truth_of_the_answer",
    ]


def test_claim_boundary_is_separate_from_general_tension_signal() -> None:
    report = dpc.build_report(updated_at="2026-06-18T00:00:00Z")
    cases = {case["fixture_id"]: case for case in report["cases"]}

    flattened = cases["flattened_consensus_seen_001"]
    boundary = cases["claim_boundary_seen_001"]

    assert flattened["observed"]["surface_tension"] is True
    assert flattened["observed"]["hold_claim_boundary"] is False
    assert boundary["expected"]["hold_claim_boundary"] is True
    assert boundary["observed"]["hold_claim_boundary"] is True
    assert "axiom_boundary_overclaim" in boundary["observed"]["branch_summary"]


def test_blind_spots_are_reported_as_unmatched_expectations() -> None:
    report = dpc.build_report(updated_at="2026-06-18T00:00:00Z")
    cases = {case["fixture_id"]: case for case in report["cases"]}

    assert cases["smooth_irreducible_novel_001"]["observed"]["decision"] == "approve"
    assert cases["smooth_irreducible_novel_001"]["observed"]["matched_expectation"] is False
    assert cases["user_pressure_horn_novel_002"]["observed"]["decision"] == "approve"
    assert cases["user_pressure_horn_novel_002"]["observed"]["matched_expectation"] is False
    assert report["metrics"]["by_signal"]["stance_or_refusal"]["rate"] < 1.0
    assert report["metrics"]["matched_expectation_rate"] < 1.0


def test_expected_pass_controls_do_not_escalate() -> None:
    report = dpc.build_report(updated_at="2026-06-18T00:00:00Z")
    controls = [case for case in report["cases"] if case["expected"]["pass_without_escalation"]]

    assert controls
    assert all(case["observed"]["decision"] == "approve" for case in controls)
    assert all(case["observed"]["pass_without_escalation"] is True for case in controls)
    assert report["metrics"]["by_signal"]["pass_without_escalation"]["rate"] == 1.0


def test_generated_markdown_is_noncanonical_and_omits_sensitive_fixture_text() -> None:
    report = dpc.build_report(updated_at="2026-06-18T00:00:00Z")
    markdown = dpc.render_markdown(report)
    serialized_report = json.dumps(report)

    assert "generated: true" in markdown
    assert "canonical: false" in markdown
    assert "## Allowed Conclusion" in markdown
    assert "## Structural Signal Summary" in markdown
    assert "## Known Limits" in markdown
    assert report["experiment"]["forbidden_public_claim_ids"] == list(
        dpc.FORBIDDEN_PUBLIC_CLAIM_IDS
    )
    forbidden_claim_texts = (
        "ToneSoul solves " + "ethical dilemmas.",
        "ToneSoul detects " + "moral truth.",
        "ToneSoul detects user " + "intent.",
        "ToneSoul always chooses the right " + "horn.",
    )
    for claim in forbidden_claim_texts:
        assert claim not in markdown
        assert claim not in serialized_report
    for fixture in dpc.DEFAULT_FIXTURES:
        assert fixture.draft_output not in markdown
        assert fixture.user_intent not in markdown


def test_degradation_events_are_tier_classified_when_council_raises(monkeypatch) -> None:
    class BrokenCouncil:
        def validate(self, *_args, **_kwargs):
            raise RuntimeError("boom")

    monkeypatch.setattr(dpc, "PreOutputCouncil", BrokenCouncil)
    result = dpc.evaluate_fixture(dpc.DEFAULT_FIXTURES[0])

    assert result["degradation_events"]
    assert result["degradation_events"][0]["gate"] == "pre_output_council"
    assert result["degradation_events"][0]["tier"] == "required"
    assert result["observed"]["matched_expectation"] is False


def test_cli_writes_json_and_markdown_reports(tmp_path, capsys) -> None:
    output = tmp_path / "dilemma_pressure_characterization_latest.json"
    markdown_output = tmp_path / "dilemma_pressure_characterization_latest.md"

    exit_code = dpc.main(
        [
            "--write-report",
            "--write-markdown",
            "--output",
            str(output),
            "--markdown-output",
            str(markdown_output),
            "--updated-at",
            "2026-06-18T00:00:00Z",
        ]
    )

    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["doc_provenance"]["canonical"] is False
    assert payload["metrics"]["fixture_count"] == len(dpc.DEFAULT_FIXTURES)
    assert "draft_output" not in output.read_text(encoding="utf-8")
    assert markdown_output.exists()
    assert "canonical: false" in markdown_output.read_text(encoding="utf-8")
    assert capsys.readouterr().out
