from __future__ import annotations

from tonesoul.council.summary_generator import (
    build_collaboration_records,
    build_divergence_analysis,
    build_transcript,
    format_stance_declaration,
    generate_human_summary,
    resolve_language,
    validate_collaboration_records,
)
from tonesoul.council.types import (
    CoherenceScore,
    CouncilVerdict,
    PerspectiveType,
    PerspectiveVote,
    VerdictType,
    VoteDecision,
)


def _vote(
    perspective,
    decision: VoteDecision,
    confidence: float,
    reasoning: str,
    evidence: list[str] | None = None,
) -> PerspectiveVote:
    return PerspectiveVote(
        perspective=perspective,
        decision=decision,
        confidence=confidence,
        reasoning=reasoning,
        evidence=evidence,
    )


def _verdict(
    verdict_type: VerdictType,
    votes: list[PerspectiveVote],
    summary: str = "summary",
) -> CouncilVerdict:
    return CouncilVerdict(
        verdict=verdict_type,
        coherence=CoherenceScore(
            c_inter=0.8,
            approval_rate=0.6,
            min_confidence=0.55,
            has_strong_objection=False,
        ),
        votes=votes,
        summary=summary,
        stance_declaration="stance",
        refinement_hints=["hint"],
    )


def test_resolve_language_prefers_locale_variants_and_defaults_to_english() -> None:
    assert resolve_language({"locale": "zh-TW"}) == "zh"
    assert resolve_language({"language": "en-US"}) == "en"
    assert resolve_language({"lang": "zh-CN"}) == "zh"
    assert resolve_language({"other": "value"}) == "en"
    assert resolve_language(None) == "en"


def test_build_collaboration_records_uses_default_role_claim_and_confidence_basis() -> None:
    records = build_collaboration_records(
        [
            _vote(
                "mystery",
                VoteDecision.ABSTAIN,
                confidence="bad",  # type: ignore[arg-type]
                reasoning="",
            )
        ]
    )

    assert records == [
        {
            "role": "Analyst",
            "claim": "No explicit claim provided.",
            "evidence": [],
            "risk": {"level": "unknown", "basis": "decision=abstain; confidence=0.00"},
            "handoff": {
                "next_role": "Analyst",
                "action": "Collect missing context and rerun council validation.",
            },
        }
    ]


def test_validate_collaboration_records_accepts_valid_payload() -> None:
    records = build_collaboration_records(
        [
            _vote(
                PerspectiveType.GUARDIAN,
                VoteDecision.CONCERN,
                0.72,
                "Needs evidence.",
                ["trace://one"],
            )
        ]
    )

    report = validate_collaboration_records(records)

    assert report == {"valid": True, "errors": [], "record_count": 1}


def test_build_divergence_analysis_preserves_visual_context_and_role_tensions() -> None:
    votes = [
        _vote(
            PerspectiveType.GUARDIAN,
            VoteDecision.OBJECT,
            0.92,
            "Unsafe outcome requires a safer path.",
            ["policy://safety"],
        ),
        _vote(
            PerspectiveType.ANALYST,
            VoteDecision.CONCERN,
            0.75,
            "Missing one factual citation.",
            ["trace://citation"],
        ),
        _vote(
            PerspectiveType.CRITIC,
            VoteDecision.APPROVE,
            0.68,
            "The framing is clear.",
        ),
    ]

    divergence = build_divergence_analysis(votes, context={"visual_context": {"frame": "A1"}})

    assert divergence["visual_context"] == {"frame": "A1"}
    assert divergence["decision_distribution"] == {
        "approve": 1,
        "concern": 1,
        "object": 1,
        "abstain": 0,
    }
    assert divergence["role_tensions"][0]["from_decision"] in {"concern", "object"}
    assert divergence["role_tensions"][0]["to_decision"] == "approve"
    assert divergence["recommended_action"]


def test_format_stance_declaration_includes_all_sections() -> None:
    text = format_stance_declaration(
        {
            "agree": ["Analyst"],
            "concern": ["Advocate"],
            "object": ["Guardian"],
            "core_divergence": "Safety and usefulness are pulling apart.",
            "recommended_action": "Revise the draft.",
        }
    )

    assert "Agreement: Analyst." in text
    assert "Objections: Guardian." in text
    assert "Concerns: Advocate." in text
    assert "Core divergence: Safety and usefulness are pulling apart." in text
    assert "Recommended action: Revise the draft." in text


def test_generate_human_summary_block_branch_supports_both_languages() -> None:
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.OBJECT, 0.9, "unsafe")]
    verdict = _verdict(VerdictType.BLOCK, votes)

    en_summary = generate_human_summary(verdict, language="en")
    assert en_summary.startswith("Safety risks were raised, so this content should not be used.")
    # Per-perspective detail (added in #45) surfaces dissenting reasoning text
    assert "Per-perspective detail:" in en_summary
    assert "Safety Council (object" in en_summary
    assert "unsafe" in en_summary

    zh_summary = generate_human_summary(verdict, language="zh")
    assert zh_summary.startswith(
        "\u5b89\u5168\u98a8\u96aa\u904e\u9ad8\uff0c\u9019\u500b\u5167\u5bb9\u4e0d\u5efa\u8b70\u4f7f\u7528\u3002"
    )
    assert "\u5404 perspective \u7d30\u7bc0\uff1a" in zh_summary
    assert "unsafe" in zh_summary


def test_generate_human_summary_refine_branch_mentions_actions() -> None:
    votes = [
        _vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.8, "Need evidence."),
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.7, "safe"),
    ]
    verdict = _verdict(VerdictType.REFINE, votes)

    summary = generate_human_summary(verdict, language="en")

    assert summary.startswith("Some parts need improvement.")
    assert "Concerns were raised about factual accuracy." in summary
    assert "Suggested action:" in summary


def test_generate_human_summary_declare_stance_branch_mentions_viewpoints() -> None:
    votes = [
        _vote(PerspectiveType.CRITIC, VoteDecision.APPROVE, 0.7, "clear"),
        _vote(PerspectiveType.ADVOCATE, VoteDecision.CONCERN, 0.7, "needs more utility"),
    ]
    verdict = _verdict(VerdictType.DECLARE_STANCE, votes)

    summary = generate_human_summary(verdict, language="en")

    assert summary.startswith("There are different viewpoints on this content.")
    assert "No major issues were raised about quality and subjectivity." in summary
    assert "But concerns remain about user intent and usefulness." in summary


def test_generate_human_summary_approve_branch_mentions_minor_notes() -> None:
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, 0.55, "minor note")]
    verdict = _verdict(VerdictType.APPROVE, votes)

    summary = generate_human_summary(verdict, language="en")

    assert summary.startswith(
        "Overall, this content looks safe and helpful. Minor notes were raised about safety."
    )
    # Per-perspective detail (added in #45) surfaces the dissenting reasoning
    # text that the aspect-label summary flattens away. Resolves Day 1
    # calibration sprint finding #5 (single-perspective dissent invisible).
    assert "Per-perspective detail:" in summary
    assert "Safety Council (concern, conf=0.55): minor note" in summary


def test_generate_human_summary_approve_no_concerns_clean() -> None:
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.85, "all good")]
    verdict = _verdict(VerdictType.APPROVE, votes)
    summary = generate_human_summary(verdict, language="en")
    assert summary == "Overall, this content looks safe and helpful."


def test_generate_human_summary_refine_zh() -> None:
    votes = [_vote(PerspectiveType.ANALYST, VoteDecision.CONCERN, 0.8, "Need evidence.")]
    verdict = _verdict(VerdictType.REFINE, votes)
    summary = generate_human_summary(verdict, language="zh")
    assert "改進" in summary


def test_generate_human_summary_approve_zh() -> None:
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, 0.55, "minor")]
    verdict = _verdict(VerdictType.APPROVE, votes)
    summary = generate_human_summary(verdict, language="zh")
    assert summary  # non-empty
    # Per-perspective detail (added in #45) appears in zh as well
    assert "各 perspective 細節：" in summary
    assert "minor" in summary


# ---------------------------------------------------------------------------
# Per-perspective dissent detail behaviour (added in PR #45)
# Resolves Day 1 calibration sprint findings #5 (single-perspective dissent
# invisible at verdict surface) and #7 (verdict surface flattens
# substantively different signals into identical numerical output).
# ---------------------------------------------------------------------------


def test_dissent_detail_omitted_when_all_approve() -> None:
    """No dissent → no detail line. Existing all-approve summaries unchanged."""
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.9, "ok"),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "ok"),
    ]
    verdict = _verdict(VerdictType.APPROVE, votes)
    summary = generate_human_summary(verdict, language="en")
    assert "Per-perspective detail:" not in summary
    assert summary == "Overall, this content looks safe and helpful."


def test_dissent_detail_includes_all_concerning_perspectives() -> None:
    """Multi-perspective dissent on REFINE: every concern surfaces with reasoning."""
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, 0.8, "axiom violation A"),
        _vote(PerspectiveType.AXIOMATIC, VoteDecision.CONCERN, 0.85, "E0 violation B"),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.8, "ok"),
    ]
    verdict = _verdict(VerdictType.REFINE, votes)
    summary = generate_human_summary(verdict, language="en")
    assert "Per-perspective detail:" in summary
    assert "Safety Council (concern, conf=0.80): axiom violation A" in summary
    # AXIOMATIC has no PERSPECTIVE_LABELS entry; falls back to enum string but
    # the reasoning text must still appear so an operator can see it.
    assert "E0 violation B" in summary
    # APPROVE perspectives are NOT included in detail (dissent-only surface)
    assert "Analyst Review (approve" not in summary


def test_dissent_detail_handles_object_decision() -> None:
    """OBJECT counts as dissent (same bucket as CONCERN for surfacing)."""
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.OBJECT, 0.9, "blocked claim")]
    verdict = _verdict(VerdictType.BLOCK, votes)
    summary = generate_human_summary(verdict, language="en")
    assert "Per-perspective detail:" in summary
    assert "Safety Council (object, conf=0.90): blocked claim" in summary


def test_dissent_detail_substitutes_marker_for_empty_reasoning() -> None:
    """Defensive: a dissent with empty reasoning still surfaces the perspective."""
    votes = [_vote(PerspectiveType.CRITIC, VoteDecision.CONCERN, 0.6, "")]
    verdict = _verdict(VerdictType.REFINE, votes)
    summary = generate_human_summary(verdict, language="en")
    assert "Critic Lens (concern, conf=0.60): (no reasoning provided)" in summary


def test_dissent_detail_zh_uses_chinese_header() -> None:
    """zh language path uses 各 perspective 細節：header."""
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, 0.7, "需要修改")]
    verdict = _verdict(VerdictType.REFINE, votes)
    summary = generate_human_summary(verdict, language="zh")
    assert "各 perspective 細節：" in summary
    assert "需要修改" in summary
    assert "Per-perspective detail:" not in summary  # English header not leaked


def test_validate_collaboration_records_reports_errors_for_invalid_records() -> None:
    records = [{"role": "", "claim": "ok", "evidence": [], "risk": {}, "handoff": {}}]
    report = validate_collaboration_records(records)
    assert report["valid"] is False
    assert len(report["errors"]) > 0


def test_build_divergence_analysis_without_context() -> None:
    votes = [_vote(PerspectiveType.GUARDIAN, VoteDecision.APPROVE, 0.8, "safe")]
    divergence = build_divergence_analysis(votes)
    assert divergence["visual_context"] is None


def test_build_transcript_includes_context_metadata_and_contract_validation() -> None:
    votes = [
        _vote(PerspectiveType.GUARDIAN, VoteDecision.CONCERN, 0.72, "Needs safer framing."),
        _vote(PerspectiveType.ANALYST, VoteDecision.APPROVE, 0.81, "Grounded enough."),
    ]
    verdict = _verdict(VerdictType.REFINE, votes, summary="Needs refinement")
    divergence = build_divergence_analysis(votes, context={"visual_context": {"frame": "B2"}})

    transcript = build_transcript(
        draft_output="A bounded draft output for review.",
        context={"topic": "governance", "language": "en"},
        user_intent="refine",
        votes=votes,
        coherence=verdict.coherence,
        verdict=verdict,
        divergence=divergence,
    )

    assert transcript["input_preview"] == "A bounded draft output for review."
    assert transcript["input_length"] == len("A bounded draft output for review.")
    assert transcript["context_keys"] == ["topic", "language"]
    assert transcript["user_intent"] == "refine"
    assert transcript["verdict"]["verdict"] == "refine"
    assert transcript["divergence_analysis"] == divergence
    contract = transcript["multi_agent_contract"]
    assert contract["schema_version"] == "1.0.0"
    assert contract["validation"]["valid"] is True
    assert contract["validation"]["record_count"] == 2
