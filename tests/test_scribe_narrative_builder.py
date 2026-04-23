import pytest

from tonesoul.scribe.narrative_builder import (
    ScribeCollisionRecord,
    ScribeCrystalRecord,
    ScribeNarrativeBuilder,
    ScribeObservationSummary,
    ScribeTensionRecord,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _tension(
    tension_id: str = "T1",
    topic: str = "Market Pullback",
    description: str = "A visible tension.",
    friction_score: float | None = 0.5,
    status: str = "recorded",
) -> ScribeTensionRecord:
    return ScribeTensionRecord(
        tension_id=tension_id,
        topic=topic,
        friction_score=friction_score,
        status=status,
        created_at="2026-01-01T00:00:00Z",
        description=description,
    )


def _collision(
    collision_id: str = "K1",
    nature_of_conflict: str = "Two interpretations diverge.",
    resolved: bool | None = False,
) -> ScribeCollisionRecord:
    return ScribeCollisionRecord(
        collision_id=collision_id,
        memory_a_text=None,
        memory_b_text=None,
        nature_of_conflict=nature_of_conflict,
        resolved=resolved,
    )


def _crystal(
    crystal_id: str = "C1",
    core_belief: str = "Trust the ledger.",
    formation_date: str = "2026-01-01",
    underlying_tensions_resolved: int | None = 1,
) -> ScribeCrystalRecord:
    return ScribeCrystalRecord(
        crystal_id=crystal_id,
        core_belief=core_belief,
        formation_date=formation_date,
        underlying_tensions_resolved=underlying_tensions_resolved,
    )


# ── _clean_fragment ───────────────────────────────────────────────────────────

class TestCleanFragment:
    def test_empty_returns_empty(self):
        assert ScribeNarrativeBuilder._clean_fragment(None) == ""
        assert ScribeNarrativeBuilder._clean_fragment("") == ""
        assert ScribeNarrativeBuilder._clean_fragment("   ") == ""

    def test_short_text_returned_unchanged(self):
        text = "short text"
        assert ScribeNarrativeBuilder._clean_fragment(text) == text

    def test_long_text_truncated_with_ellipsis(self):
        long_text = "a" * 200
        result = ScribeNarrativeBuilder._clean_fragment(long_text, limit=50)
        assert result.endswith("...")
        assert len(result) <= 53

    def test_collapses_internal_whitespace(self):
        result = ScribeNarrativeBuilder._clean_fragment("hello   world")
        assert result == "hello world"

    def test_truncates_at_word_boundary(self):
        text = "one two three four five six seven eight nine ten"
        result = ScribeNarrativeBuilder._clean_fragment(text, limit=20)
        assert "..." in result
        assert len(result) <= 23


# ── _is_generic_tension_topic ─────────────────────────────────────────────────

class TestIsGenericTensionTopic:
    def test_empty_string_is_generic(self):
        assert ScribeNarrativeBuilder._is_generic_tension_topic("") is True

    def test_tension_word_is_generic(self):
        assert ScribeNarrativeBuilder._is_generic_tension_topic("tension") is True

    def test_subjectivity_event_is_generic(self):
        assert ScribeNarrativeBuilder._is_generic_tension_topic("subjectivity_event") is True

    def test_specific_topic_is_not_generic(self):
        assert ScribeNarrativeBuilder._is_generic_tension_topic("Market Pullback") is False

    def test_none_treated_as_generic(self):
        assert ScribeNarrativeBuilder._is_generic_tension_topic(None) is True


# ── _fragments_overlap ────────────────────────────────────────────────────────

class TestFragmentsOverlap:
    def test_empty_strings_do_not_overlap(self):
        assert ScribeNarrativeBuilder._fragments_overlap("", "") is False
        assert ScribeNarrativeBuilder._fragments_overlap("abc", "") is False

    def test_identical_strings_overlap(self):
        assert ScribeNarrativeBuilder._fragments_overlap("market pullback", "market pullback") is True

    def test_one_contains_other(self):
        assert ScribeNarrativeBuilder._fragments_overlap("market", "the market pullback") is True

    def test_disjoint_strings_do_not_overlap(self):
        assert ScribeNarrativeBuilder._fragments_overlap("alpha", "beta gamma") is False

    def test_case_insensitive(self):
        assert ScribeNarrativeBuilder._fragments_overlap("ALPHA", "alpha beta") is True


# ── _posture_line ─────────────────────────────────────────────────────────────

class TestPostureLine:
    def _summary(self, tc=0, cc=0, xc=0) -> ScribeObservationSummary:
        return ScribeObservationSummary(
            tension_count=tc,
            collision_count=cc,
            crystal_count=xc,
            fallback_mode="observed_history",
            title_hint="test",
        )

    def test_tension_only_reads_pressure_present(self):
        result = ScribeNarrativeBuilder._posture_line(self._summary(tc=2))
        assert "pressure is present" in result

    def test_tension_plus_collision_reads_contested(self):
        result = ScribeNarrativeBuilder._posture_line(self._summary(tc=1, cc=1))
        assert "contested" in result

    def test_tension_plus_crystal(self):
        result = ScribeNarrativeBuilder._posture_line(self._summary(tc=1, xc=1))
        assert "counterweight" in result

    def test_collision_without_tension(self):
        result = ScribeNarrativeBuilder._posture_line(self._summary(cc=1))
        assert "unsettled" in result

    def test_all_zero_returns_default(self):
        result = ScribeNarrativeBuilder._posture_line(self._summary())
        assert "only the recorded anchors" in result


# ── format helpers ────────────────────────────────────────────────────────────

class TestFormatTensions:
    def test_empty_returns_no_tensions_message(self):
        assert ScribeNarrativeBuilder.format_tensions([]) == "No significant tensions recorded."

    def test_single_tension_includes_id_and_friction(self):
        result = ScribeNarrativeBuilder.format_tensions([_tension("T99", friction_score=0.75)])
        assert "T99" in result
        assert "0.75" in result

    def test_none_friction_shown_as_unknown(self):
        result = ScribeNarrativeBuilder.format_tensions([_tension(friction_score=None)])
        assert "unknown" in result


class TestFormatCrystals:
    def test_empty_returns_no_crystals_message(self):
        assert ScribeNarrativeBuilder.format_crystals([]) == "No crystallized beliefs formed yet."

    def test_none_tensions_resolved_shows_unavailable(self):
        result = ScribeNarrativeBuilder.format_crystals([_crystal(underlying_tensions_resolved=None)])
        assert "unavailable" in result

    def test_crystal_with_resolved_count(self):
        result = ScribeNarrativeBuilder.format_crystals([_crystal(underlying_tensions_resolved=3)])
        assert "3 resolved tensions" in result


class TestFormatCollisions:
    def test_empty_returns_no_collisions_message(self):
        assert ScribeNarrativeBuilder.format_collisions([]) == "No recent memory collisions."

    def test_resolved_true_shows_resolved(self):
        result = ScribeNarrativeBuilder.format_collisions([_collision(resolved=True)])
        assert "RESOLVED" in result

    def test_resolved_false_shows_unresolved(self):
        result = ScribeNarrativeBuilder.format_collisions([_collision(resolved=False)])
        assert "UNRESOLVED" in result


class TestFormatObservationSummary:
    def test_includes_all_fields(self):
        summary = ScribeObservationSummary(
            tension_count=3,
            collision_count=1,
            crystal_count=2,
            fallback_mode="observed_history",
            title_hint="Governance Test",
        )
        result = ScribeNarrativeBuilder.format_observation_summary(summary)
        assert "3" in result
        assert "1" in result
        assert "observed_history" in result
        assert "Governance Test" in result


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
