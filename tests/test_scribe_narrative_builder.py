from tonesoul.scribe.narrative_builder import (
    ScribeCollisionRecord,
    ScribeCrystalRecord,
    ScribeNarrativeBuilder,
    ScribeObservationSummary,
    ScribeTensionRecord,
)


def test_description_clause_strips_marker_and_trailing_segments() -> None:
    clause = ScribeNarrativeBuilder._description_clause(
        "Context. Tension: Anchor remains visible; extra clause that should be trimmed.",
        marker="Tension:",
        limit=80,
    )

    assert clause == "Anchor remains visible"


def test_observed_anchor_line_returns_empty_slice_message() -> None:
    line = ScribeNarrativeBuilder._observed_anchor_line(
        tensions=[],
        collisions=[],
        crystals=[],
    )

    assert line == "Observed anchors: no named anchor is recorded in this slice."


def test_weight_line_uses_numeric_friction_without_duplicate_detail() -> None:
    line = ScribeNarrativeBuilder._weight_line(
        tensions=[
            ScribeTensionRecord(
                tension_id="T7",
                topic="Market Pullback",
                friction_score=0.63,
                status="recorded",
                created_at="2026-03-19T00:00:00Z",
                description="Market Pullback remains visible in the latest observed record.",
            )
        ],
        collisions=[],
        crystals=[],
    )

    assert line.startswith("Weight carried now: [T7] Market Pullback.")
    assert "Recorded friction remains 0.63 in this slice." in line
    assert "(" not in line


def test_primary_anchor_summary_falls_back_from_collision_to_crystal() -> None:
    collision_summary = ScribeNarrativeBuilder.primary_anchor_summary(
        tensions=[],
        collisions=[
            ScribeCollisionRecord(
                collision_id="K2",
                memory_a_text=None,
                memory_b_text=None,
                nature_of_conflict="Two readings refuse to settle.",
                resolved=False,
            )
        ],
        crystals=[],
    )
    crystal_summary = ScribeNarrativeBuilder.primary_anchor_summary(
        tensions=[],
        collisions=[],
        crystals=[
            ScribeCrystalRecord(
                crystal_id="C9",
                core_belief="Keep the contradiction visible until better evidence arrives.",
                formation_date="2026-03-19",
                underlying_tensions_resolved=2,
            )
        ],
    )

    assert collision_summary == "[K2] collision: Two readings refuse to settle."
    assert crystal_summary.startswith("[C9] crystal: Keep the contradiction visible")


def test_posture_absence_collision_and_crystal_formatting_cover_remaining_branches() -> None:
    posture = ScribeNarrativeBuilder._posture_line(
        ScribeObservationSummary(
            tension_count=0,
            collision_count=0,
            crystal_count=1,
            fallback_mode="observed_history",
            title_hint="Retained Belief",
        )
    )
    absence = ScribeNarrativeBuilder._absence_line(collisions=[], crystals=[])
    collisions_text = ScribeNarrativeBuilder.format_collisions(
        [
            ScribeCollisionRecord(
                collision_id="K3",
                memory_a_text=None,
                memory_b_text="Memory B remains explicit.",
                nature_of_conflict="Interpretations diverge.",
                resolved=None,
            )
        ]
    )
    crystals_text = ScribeNarrativeBuilder.format_crystals(
        [
            ScribeCrystalRecord(
                crystal_id="C3",
                core_belief="Trust the observed ledger first.",
                formation_date="2026-03-18",
                underlying_tensions_resolved=2,
            )
        ]
    )

    assert "leans more on retained belief" in posture
    assert absence == (
        "No recent collision is recorded in this slice. "
        "No crystallized belief is recorded in this slice."
    )
    assert "[COLLISION K3] (UNKNOWN)" in collisions_text
    assert "Memory A:" not in collisions_text
    assert "Memory B: Memory B remains explicit." in collisions_text
    assert "Built upon 2 resolved tensions." in crystals_text
