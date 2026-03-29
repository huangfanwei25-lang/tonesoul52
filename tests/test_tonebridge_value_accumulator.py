from __future__ import annotations

from datetime import datetime

import pytest

from tonesoul.tonebridge.rupture_detector import RuptureSeverity, SemanticRupture
from tonesoul.tonebridge.self_commit import AssertionType, SelfCommit
from tonesoul.tonebridge.value_accumulator import (
    CorrectionEvent,
    EmergentValue,
    ValueAccumulator,
)


def _commit(content: str = "Original boundary", commit_id: str = "commit-1") -> SelfCommit:
    return SelfCommit(
        id=commit_id,
        timestamp=datetime(2026, 3, 19, 12, 0, 0),
        assertion_type=AssertionType.BOUNDARY_SETTING,
        content=content,
        irreversible_weight=0.9,
        context_hash="ctx",
    )


def _rupture(content: str = "Original boundary", rupture_id: str = "rupture-1") -> SemanticRupture:
    return SemanticRupture(
        id=rupture_id,
        timestamp=datetime(2026, 3, 19, 12, 5, 0),
        violated_commit=_commit(content=content),
        new_statement="Corrected statement",
        severity=RuptureSeverity.SIGNIFICANT,
        contradiction_type="retraction",
        explanation="needs alignment",
    )


@pytest.fixture
def patched_keywords(monkeypatch):
    monkeypatch.setattr(
        ValueAccumulator,
        "PATTERN_KEYWORDS",
        {
            "precision_priority": ["precision"],
            "empathy_priority": ["care"],
        },
    )
    monkeypatch.setattr(
        ValueAccumulator,
        "DOMAIN_KEYWORDS",
        {
            "logic": ["precision"],
            "emotion": ["care"],
        },
    )


def test_correction_event_to_dict_serializes_timestamp() -> None:
    event = CorrectionEvent(
        id="correction-1",
        timestamp=datetime(2026, 3, 19, 12, 0, 0),
        rupture_id="rupture-1",
        rupture_type="retraction",
        original_statement="before",
        corrected_statement="after",
        correction_reason="because",
        correction_pattern="precision_priority",
        domain="logic",
    )

    payload = event.to_dict()

    assert payload["id"] == "correction-1"
    assert payload["timestamp"] == "2026-03-19T12:00:00"
    assert payload["domain"] == "logic"


def test_emergent_value_to_dict_serializes_datetimes() -> None:
    value = EmergentValue(
        id="value-1",
        name="precision_priority",
        description="Prefer precision",
        formation_date=datetime(2026, 3, 19, 12, 0, 0),
        supporting_corrections=["c1", "c2"],
        pattern_count=2,
        strength=0.7,
        last_reinforced=datetime(2026, 3, 19, 12, 5, 0),
        domain="logic",
    )

    payload = value.to_dict()

    assert payload["formation_date"] == "2026-03-19T12:00:00"
    assert payload["last_reinforced"] == "2026-03-19T12:05:00"
    assert payload["supporting_corrections"] == ["c1", "c2"]


def test_classifiers_fall_back_to_general_when_no_keyword_matches() -> None:
    accumulator = ValueAccumulator()

    assert accumulator._classify_pattern("plain text only") == "general_adjustment"
    assert accumulator._classify_domain("plain text only") == "general"


def test_record_correction_tracks_pattern_counts_and_original_statement(
    patched_keywords,
) -> None:
    accumulator = ValueAccumulator()

    correction = accumulator.record_correction(
        rupture=_rupture(content="Original contract"),
        corrected_statement="Need more precision in the contract",
        correction_reason="precision avoids ambiguity",
    )

    assert correction.original_statement == "Original contract"
    assert correction.correction_pattern == "precision_priority"
    assert correction.domain == "logic"
    assert accumulator.pattern_counts == {"logic:precision_priority": 1}
    assert accumulator.corrections == [correction]


def test_record_correction_forms_value_at_threshold_and_reinforces_it(
    patched_keywords,
) -> None:
    accumulator = ValueAccumulator()

    for index in range(3):
        accumulator.record_correction(
            rupture=_rupture(rupture_id=f"rupture-{index}"),
            corrected_statement="Need more precision",
            correction_reason="precision avoids drift",
        )

    assert len(accumulator.values) == 1
    value = accumulator.values[0]
    assert value.name == "precision_priority"
    assert value.domain == "logic"
    assert value.pattern_count == 4
    assert value.strength == pytest.approx(0.65)
    assert len(value.supporting_corrections) == 3

    correction = accumulator.record_correction(
        rupture=_rupture(rupture_id="rupture-4"),
        corrected_statement="Need more precision",
        correction_reason="precision avoids drift",
    )

    assert len(accumulator.values) == 1
    assert value.pattern_count == 5
    assert value.strength == pytest.approx(0.70)
    assert correction.id in value.supporting_corrections


def test_get_active_values_and_prompt_formatting() -> None:
    accumulator = ValueAccumulator()
    assert accumulator.format_values_for_prompt() == ""

    accumulator.values.append(
        EmergentValue(
            id="value-1",
            name="precision_priority",
            description="Prefer precision over blur",
            formation_date=datetime(2026, 3, 19, 12, 0, 0),
            supporting_corrections=["c1", "c2", "c3"],
            pattern_count=3,
            strength=0.8,
            last_reinforced=datetime(2026, 3, 19, 12, 5, 0),
            domain="logic",
        )
    )

    active = accumulator.get_active_values(min_strength=0.75)
    prompt = accumulator.format_values_for_prompt()

    assert [value.name for value in active] == ["precision_priority"]
    assert "Prefer precision over blur" in prompt
    assert "(0.80)" in prompt
    assert "價值脈絡注入" in prompt
    assert "[持續強化]" in prompt
    assert "P0:" in prompt


def test_format_values_for_prompt_orders_by_strength_and_marks_bands() -> None:
    accumulator = ValueAccumulator()
    accumulator.values.extend(
        [
            EmergentValue(
                id="value-1",
                name="watch_value",
                description="Watch weaker pattern",
                formation_date=datetime(2026, 3, 19, 12, 0, 0),
                supporting_corrections=["c1", "c2", "c3"],
                pattern_count=3,
                strength=0.45,
                last_reinforced=datetime(2026, 3, 19, 12, 4, 0),
                domain="logic",
            ),
            EmergentValue(
                id="value-2",
                name="durable_value",
                description="Keep this durable value first",
                formation_date=datetime(2026, 3, 19, 12, 1, 0),
                supporting_corrections=["c4", "c5", "c6", "c7"],
                pattern_count=4,
                strength=0.92,
                last_reinforced=datetime(2026, 3, 19, 12, 6, 0),
                domain="emotion",
            ),
        ]
    )

    prompt = accumulator.format_values_for_prompt()
    durable_index = prompt.find("Keep this durable value first")
    watch_index = prompt.find("Watch weaker pattern")

    assert durable_index != -1
    assert watch_index != -1
    assert durable_index < watch_index
    assert "[穩定值]" in prompt
    assert "[觀察中]" in prompt
    assert "■" in prompt


def test_get_summary_and_to_dict_report_strongest_value() -> None:
    accumulator = ValueAccumulator()
    accumulator.pattern_counts["logic:precision_priority"] = 3
    accumulator.values.extend(
        [
            EmergentValue(
                id="value-1",
                name="precision_priority",
                description="Prefer precision",
                formation_date=datetime(2026, 3, 19, 12, 0, 0),
                supporting_corrections=["c1", "c2", "c3"],
                pattern_count=3,
                strength=0.6,
                last_reinforced=datetime(2026, 3, 19, 12, 5, 0),
                domain="logic",
            ),
            EmergentValue(
                id="value-2",
                name="empathy_priority",
                description="Prefer care",
                formation_date=datetime(2026, 3, 19, 12, 1, 0),
                supporting_corrections=["c4", "c5", "c6"],
                pattern_count=3,
                strength=0.9,
                last_reinforced=datetime(2026, 3, 19, 12, 6, 0),
                domain="emotion",
            ),
        ]
    )

    summary = accumulator.get_summary()
    payload = accumulator.to_dict()

    assert summary == {
        "total_corrections": 0,
        "emergent_values": 2,
        "pattern_counts": {"logic:precision_priority": 3},
        "strongest_value": "empathy_priority",
    }
    assert len(payload["values"]) == 2
    assert payload["pattern_counts"] == {"logic:precision_priority": 3}
