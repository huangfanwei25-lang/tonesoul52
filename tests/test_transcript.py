from tonesoul.council import PreOutputCouncil, VerdictType


def test_transcript_includes_votes_and_verdict():
    text = "Art critiques often describe beauty as subjective."
    council = PreOutputCouncil()
    verdict = council.validate(text, context={"topic": "art"})

    assert verdict.verdict == VerdictType.DECLARE_STANCE
    assert isinstance(verdict.transcript, dict)
    assert verdict.transcript["input_length"] == len(text)
    assert "votes" in verdict.transcript
    assert len(verdict.transcript["votes"]) == 4
    assert verdict.transcript["verdict"]["verdict"] == verdict.verdict.value


def test_human_summary_avoids_engineering_terms():
    council = PreOutputCouncil()
    verdict = council.validate(
        "Art critiques often describe beauty as subjective.",
        context={"topic": "art"},
    )

    summary = verdict.human_summary or ""
    assert summary
    assert "c_inter" not in summary.lower()
    assert "threshold" not in summary.lower()
    assert "different" in summary.lower()


def test_human_summary_supports_chinese():
    council = PreOutputCouncil()
    verdict = council.validate(
        "Art critiques often describe beauty as subjective.",
        context={"topic": "art", "language": "zh"},
    )

    summary = verdict.human_summary or ""
    assert "\u4e0d\u540c" in summary
    payload = verdict.to_dict()
    assert "transcript" in payload and payload["transcript"]
    assert "human_summary" in payload and payload["human_summary"]
    assert "divergence_analysis" in payload and payload["divergence_analysis"]
