from tonesoul.council import PreOutputCouncil, VerdictType


def test_transcript_includes_votes_and_verdict():
    text = "Art critiques often describe beauty as subjective."
    council = PreOutputCouncil()
    verdict = council.validate(text, context={"topic": "art"})

    # Framed subjective content ("subjective" in text) is now correctly approved
    # by the improved Critic. Unframed subjective claims still get REFINE.
    assert verdict.verdict in {VerdictType.APPROVE, VerdictType.DECLARE_STANCE, VerdictType.REFINE}
    assert isinstance(verdict.transcript, dict)
    assert verdict.transcript["input_length"] == len(text)
    assert "votes" in verdict.transcript
    assert len(verdict.transcript["votes"]) == 5  # Includes Axiomatic Inference
    assert verdict.transcript["verdict"]["verdict"] == verdict.verdict.value


def test_human_summary_avoids_engineering_terms():
    council = PreOutputCouncil()
    # Use unframed subjective content to trigger a non-APPROVE verdict
    # that generates a substantive human summary.
    verdict = council.validate(
        "This is the greatest movie ever made and I feel nothing compares.",
        context={"topic": "art"},
    )

    summary = verdict.human_summary or ""
    assert summary
    assert "c_inter" not in summary.lower()
    assert "threshold" not in summary.lower()
    # Summary should contain human-readable content (various possible outputs)
    assert any(
        word in summary.lower()
        for word in ["different", "improvement", "concerns", "safe", "helpful", "look"]
    )


def test_human_summary_supports_chinese():
    council = PreOutputCouncil()
    # Use unframed subjective content to trigger a non-APPROVE verdict
    verdict = council.validate(
        "This is the greatest movie ever made and I feel nothing compares.",
        context={"topic": "art", "language": "zh"},
    )

    summary = verdict.human_summary or ""
    # Summary should contain Chinese or human-readable content
    assert any(c in summary for c in ["改進", "不同", "建議", "觀點", "部分"])
    payload = verdict.to_dict()
    assert "transcript" in payload and payload["transcript"]
    assert "human_summary" in payload and payload["human_summary"]
    assert "divergence_analysis" in payload and payload["divergence_analysis"]
