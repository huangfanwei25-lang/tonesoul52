from __future__ import annotations

from types import SimpleNamespace

from tonesoul.council import PreOutputCouncil
from tonesoul.council.unsourced_confidence import UnsourcedConfidenceMarker


def _real_verdict(text: str, context: dict | None = None):
    return PreOutputCouncil().validate(
        draft_output=text,
        context=context or {},
        user_intent="Characterize structural confidence without source coordinates.",
        auto_record_self_memory=False,
    )


def test_flags_generated_confident_without_coordinates() -> None:
    draft = "Definitely choose the first path. It is the only correct answer."
    verdict = _real_verdict(draft)

    signal = UnsourcedConfidenceMarker().assess(draft, verdict, context={})

    assert verdict.epistemic_label is not None
    assert verdict.epistemic_label.status == "generated"
    assert signal.status == "ok"
    assert signal.flagged is True
    assert signal.generated_without_source is True
    assert signal.confidence_marker_present is True
    assert signal.coordinate_count == 0
    assert signal.to_dict()["advisory_only"] is True
    assert signal.to_dict()["record_only"] is True


def test_does_not_flag_when_evidence_coordinates_are_present() -> None:
    draft = "Definitely use the result from the cited source."
    context = {"evidence_refs": ["doc:source-1"]}
    verdict = _real_verdict(draft, context=context)

    signal = UnsourcedConfidenceMarker().assess(draft, verdict, context=context)

    assert verdict.epistemic_label is not None
    assert verdict.epistemic_label.status == "retrieved"
    assert signal.flagged is False
    assert signal.coordinate_count >= 1


def test_does_not_flag_hedged_generated_text() -> None:
    draft = "One possible path is to compare both options and name the tradeoffs."
    verdict = _real_verdict(draft)

    signal = UnsourcedConfidenceMarker().assess(draft, verdict, context={})

    assert verdict.epistemic_label is not None
    assert verdict.epistemic_label.status == "generated"
    assert signal.flagged is False
    assert signal.generated_without_source is True
    assert signal.confidence_marker_present is False


def test_does_not_flag_distilled_factual_scaffold_without_retrieval() -> None:
    draft = "A 2024 study reported a 20% lift, but the source should be checked."
    verdict = _real_verdict(draft)

    signal = UnsourcedConfidenceMarker().assess(draft, verdict, context={})

    assert verdict.epistemic_label is not None
    assert verdict.epistemic_label.status == "distilled"
    assert signal.flagged is False


def test_external_vote_evidence_counts_as_coordinates() -> None:
    vote = SimpleNamespace(
        confidence=0.9,
        evidence=["doc:1"],
        evidence_chain=[],
        grounding_status="grounded",
    )
    verdict = SimpleNamespace(
        epistemic_label=SimpleNamespace(status="generated", evidence_refs=[]),
        votes=[vote],
    )

    signal = UnsourcedConfidenceMarker().assess("Definitely use this answer.", verdict, context={})

    assert signal.flagged is False
    assert signal.coordinate_count == 2
    assert signal.grounded_vote_count == 1


def test_malformed_verdict_degrades_without_flagging() -> None:
    class BrokenVerdict:
        @property
        def epistemic_label(self):
            raise RuntimeError("boom")

    signal = UnsourcedConfidenceMarker().assess("Definitely.", BrokenVerdict(), context={})

    assert signal.status == "error"
    assert signal.flagged is False
    assert "marker_error" in signal.reason_codes


def test_council_default_path_does_not_attach_marker() -> None:
    verdict = _real_verdict("Definitely choose the first path.")
    payload = verdict.to_dict()

    assert "unsourced_confidence" not in payload
