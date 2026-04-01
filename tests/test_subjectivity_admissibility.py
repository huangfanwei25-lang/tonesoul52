import pytest

from tonesoul.memory import subjectivity_admissibility as subject_mod


@pytest.mark.parametrize(
    ("text", "direction"),
    [
        ("need better audit provenance", "provenance_discipline"),
        ("tighten boundary guardrail scope", "boundary_discipline"),
        ("critical harm risk block", "safety_boundary"),
        ("resource budget latency pressure", "resource_discipline"),
        ("governance threshold council breaker", "governance_escalation"),
        ("unclear mood", "undifferentiated_tension"),
    ],
)
def test_direction_from_text_maps_known_signal_buckets(text, direction):
    assert subject_mod._direction_from_text(text) == direction


def test_direction_focus_returns_focus_tags_and_questions():
    focus, tags, questions = subject_mod._direction_focus("resource_discipline")
    fallback_focus, fallback_tags, fallback_questions = subject_mod._direction_focus("")

    assert focus == "resource_tradeoff_honesty"
    assert tags == ["cost_shift_check", "tradeoff_honesty"]
    assert len(questions) == 2
    assert fallback_focus == "maturity_before_admissibility"
    assert fallback_tags == ["semantic_maturity_gap"]
    assert len(fallback_questions) == 2


def test_build_axiomatic_admissibility_checklist_sets_posture_and_risk_tags():
    checklist = subject_mod.build_axiomatic_admissibility_checklist(
        topic="Budget guardrail",
        direction="resource_discipline",
        triage_recommendation="candidate_for_manual_review",
        same_source_loop=True,
        source_url_count=1,
        lineage_count=1,
        cycle_count=3,
    )

    assert checklist["gate_name"] == "axiomatic_admissibility"
    assert checklist["required_for_approved"] is True
    assert checklist["gate_posture"] == "manual_review_candidate"
    assert checklist["focus"] == "resource_tradeoff_honesty"
    assert checklist["risk_tags"] == [
        "cost_shift_check",
        "cross_cycle_persistence",
        "low_context_diversity",
        "single_lineage_pressure",
        "tradeoff_honesty",
    ]
    assert "Budget guardrail" in checklist["operator_prompt"]
    assert "Goal function:" in checklist["operator_prompt"]
    assert "P0:" in checklist["operator_prompt"]
    assert "[資料不足]" in checklist["operator_prompt"]
    assert "focus=resource_tradeoff_honesty" in checklist["status_line"]


def test_build_record_axiomatic_admissibility_checklist_derives_direction():
    checklist = subject_mod.build_record_axiomatic_admissibility_checklist(
        {
            "topic": "Traceability",
            "summary": "Need stronger audit provenance for this branch",
            "source_url": "https://example.com",
            "source_record_ids": ["a", "b"],
        }
    )

    assert checklist["derived_direction"] == "provenance_discipline"
    assert checklist["gate_posture"] == "manual_admissibility_review"
    assert "traceability_not_enough" in checklist["risk_tags"]
    assert checklist["focus"] == "traceability_and_accountability"


def test_build_axiomatic_admissibility_status_line_handles_optional_tags():
    assert (
        subject_mod.build_axiomatic_admissibility_status_line(
            gate_posture="manual",
            focus="focus",
            risk_tags=["a", "b"],
        )
        == "manual | focus=focus | tags=a, b"
    )
    assert (
        subject_mod.build_axiomatic_admissibility_status_line(
            gate_posture="manual",
            focus="focus",
        )
        == "manual | focus=focus"
    )


def test_build_operator_prompt_uses_bounded_review_shape():
    prompt = subject_mod._build_operator_prompt("Traceability", "traceability_and_accountability")

    assert "Before approving `Traceability`" in prompt
    assert "Goal function:" in prompt
    assert "Focus: traceability_and_accountability." in prompt
    assert "[資料不足]" in prompt
