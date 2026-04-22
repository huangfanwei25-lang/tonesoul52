from __future__ import annotations

import json
from pathlib import Path

from tonesoul.zone_registry import (
    _compute_mood,
    _compute_weather,
    _match_topic_to_zone,
    rebuild_from_traces,
)


def test_rebuild_from_traces_ignores_missing_timestamp_for_last_seen(tmp_path: Path) -> None:
    traces_path = tmp_path / "session_traces.jsonl"
    governance_path = tmp_path / "governance_state.json"

    traces_path.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "session_id": "real-1",
                        "timestamp": "2026-03-26T10:00:00+00:00",
                        "topics": ["governance"],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "session_id": "test-001",
                        "topics": ["governance"],
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    governance_path.write_text("{}", encoding="utf-8")

    world = rebuild_from_traces(
        traces_path=traces_path,
        governance_path=governance_path,
    )

    governance_zone = next(zone for zone in world.zones if zone.zone_id == "governance")
    assert governance_zone.visit_count == 2
    assert governance_zone.first_seen == "2026-03-26T10:00:00+00:00"
    assert governance_zone.last_seen == "2026-03-26T10:00:00+00:00"


# ─────────────────────────────────────────────
# Pure function coverage
# ─────────────────────────────────────────────


class TestMatchTopicToZone:
    def test_english_key_matches(self):
        assert _match_topic_to_zone("governance discussion") == "governance"

    def test_chinese_governance_keyword(self):
        assert _match_topic_to_zone("治理框架") == "governance"

    def test_chinese_council_keyword(self):
        assert _match_topic_to_zone("議會推演") == "governance"

    def test_memory_english(self):
        assert _match_topic_to_zone("memory management") == "memory"

    def test_architecture_chinese(self):
        assert _match_topic_to_zone("系統架構設計") == "architecture"

    def test_testing_english(self):
        assert _match_topic_to_zone("test coverage") == "testing"

    def test_debug_chinese(self):
        assert _match_topic_to_zone("修復除錯") == "debug"

    def test_unknown_topic_returns_none(self):
        assert _match_topic_to_zone("random unrelated xyz") is None

    def test_case_insensitive(self):
        assert _match_topic_to_zone("GOVERNANCE") == "governance"


class TestComputeMood:
    def test_high_integral_high_tension_is_tense(self):
        assert _compute_mood(0.9, 5) == "tense"

    def test_high_integral_low_tension_is_alert(self):
        assert _compute_mood(0.6, 1) == "alert"

    def test_zero_tension_is_serene(self):
        assert _compute_mood(0.0, 0) == "serene"

    def test_moderate_integral_some_tension_is_calm(self):
        assert _compute_mood(0.3, 2) == "calm"

    def test_boundary_integral_below_threshold_is_serene(self):
        # soul_integral=0.0, tension=0 → serene
        assert _compute_mood(0.0, 0) == "serene"


class TestComputeWeather:
    def test_high_caution_is_storm(self):
        assert _compute_weather(0.8, 0.0) == "storm"

    def test_high_innovation_is_aurora(self):
        assert _compute_weather(0.0, 0.9) == "aurora"

    def test_moderate_caution_is_cloudy(self):
        assert _compute_weather(0.6, 0.2) == "cloudy"

    def test_low_caution_low_innovation_is_clear(self):
        assert _compute_weather(0.2, 0.2) == "clear"

    def test_caution_at_boundary_storm(self):
        # caution > 0.7 → storm
        assert _compute_weather(0.71, 0.0) == "storm"
