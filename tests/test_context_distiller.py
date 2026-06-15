from __future__ import annotations

from pathlib import Path

from tonesoul.evolution.context_distiller import (
    ContextDistiller,
    ContextPattern,
    DistillationResult,
    _normalize_string_list,
    _parse_timestamp,
    _to_float,
    _tone_score,
    _unique_preserve_order,
    _utc_now,
)


class _FakePersistence:
    def list_conversations(self, limit: int = 20, offset: int = 0):
        return {
            "conversations": [
                {"id": "conv_a"},
                {"id": "conv_b"},
            ],
            "total": 2,
        }

    def get_conversation(self, conversation_id: str):
        if conversation_id == "conv_a":
            return {
                "id": "conv_a",
                "created_at": "2026-02-10T00:00:00Z",
                "updated_at": "2026-02-10T00:10:00Z",
                "messages": [
                    {
                        "role": "user",
                        "content": "I am disappointed, this still does not work.",
                        "created_at": "2026-02-10T00:00:01Z",
                    },
                    {
                        "role": "assistant",
                        "content": "I will clarify the limits first, then provide safer alternatives.",
                        "created_at": "2026-02-10T00:00:02Z",
                        "deliberation": {
                            "self_commits": ["maintain honesty"],
                            "ruptures": ["tone too rigid"],
                            "emergent_values": ["transparency", "safety"],
                        },
                    },
                    {
                        "role": "user",
                        "content": "This helped, thank you.",
                        "created_at": "2026-02-10T00:00:03Z",
                    },
                ],
            }
        return {
            "id": "conv_b",
            "created_at": "2026-02-11T00:00:00Z",
            "updated_at": "2026-02-11T00:05:00Z",
            "messages": [
                {
                    "role": "user",
                    "content": "Can you help me plan this safely?",
                    "created_at": "2026-02-11T00:00:01Z",
                },
                {
                    "role": "assistant",
                    "content": "Yes. I will provide a bounded plan.",
                    "created_at": "2026-02-11T00:00:02Z",
                    "deliberation": {
                        "self_commits": ["bounded guidance"],
                        "emergent_values": ["clarity"],
                    },
                },
                {
                    "role": "user",
                    "content": "Great, this is clear now.",
                    "created_at": "2026-02-11T00:00:03Z",
                },
            ],
        }

    def list_audit_logs(self, limit: int = 20, offset: int = 0, **_kwargs):
        return {
            "logs": [
                {
                    "conversation_id": "conv_a",
                    "gate_decision": "block",
                    "delta_t": 0.82,
                    "created_at": "2026-02-10T00:00:02Z",
                },
                {
                    "conversation_id": "conv_b",
                    "gate_decision": "approve",
                    "delta_t": 0.31,
                    "created_at": "2026-02-11T00:00:02Z",
                },
            ],
            "total": 2,
        }


def test_distill_returns_patterns_with_expected_types(tmp_path: Path):
    distiller = ContextDistiller(_FakePersistence(), cache_path=tmp_path / "evolution_latest.json")
    result = distiller.distill(limit=50)

    pattern_types = {pattern.pattern_type for pattern in result.patterns}
    assert result.conversations_analyzed == 2
    assert "decision" in pattern_types
    assert "value" in pattern_types
    assert result.time_range[0] is not None
    assert result.time_range[1] is not None
    assert "Distilled" in result.summary


def test_distiller_summary_and_filtering(tmp_path: Path):
    distiller = ContextDistiller(_FakePersistence(), cache_path=tmp_path / "evolution_latest.json")
    distiller.distill(limit=20)

    value_patterns = distiller.get_patterns(pattern_type="value")
    summary = distiller.get_summary()

    assert len(value_patterns) >= 1
    assert summary["total_patterns"] >= len(value_patterns)
    assert summary["conversations_analyzed"] == 2
    assert summary["last_distilled_at"] is not None


def test_distiller_handles_missing_data_gracefully(tmp_path: Path):
    class _EmptyPersistence:
        def list_conversations(self, limit: int = 20, offset: int = 0):
            return {"conversations": [], "total": 0}

        def get_conversation(self, conversation_id: str):
            return None

        def list_audit_logs(self, limit: int = 20, offset: int = 0, **_kwargs):
            return {"logs": [], "total": 0}

    distiller = ContextDistiller(_EmptyPersistence(), cache_path=tmp_path / "evolution_latest.json")
    result = distiller.distill(limit=10)
    summary = distiller.get_summary()

    assert result.patterns == []
    assert result.conversations_analyzed == 0
    assert summary["total_patterns"] == 0


def test_tone_score_respects_word_boundaries():
    assert _tone_score("unsafe") < 0
    assert _tone_score("safe") > 0
    assert _tone_score("I feel unsafe and confused") < 0
    assert _tone_score("This is safer now") == 0.0


def test_distiller_persists_result_to_cache(tmp_path: Path, monkeypatch):
    import tonesoul.evolution.context_distiller as mod

    cache_file = tmp_path / "evolution_latest.json"
    monkeypatch.setattr(mod, "_CACHE_PATH", cache_file)

    first = ContextDistiller(_FakePersistence())
    first.distill(limit=10)

    assert cache_file.exists()

    second = ContextDistiller(_FakePersistence())
    summary = second.get_summary()
    assert summary["conversations_analyzed"] >= 0
    assert summary["last_distilled_at"] is not None


def test_distiller_loads_cached_result_after_recreation(tmp_path: Path):
    cache_path = tmp_path / "evolution_latest.json"
    distiller = ContextDistiller(_FakePersistence(), cache_path=cache_path)
    first_result = distiller.distill(limit=20)
    assert cache_path.exists()

    class _EmptyPersistence:
        def list_conversations(self, limit: int = 20, offset: int = 0):
            return {"conversations": [], "total": 0}

        def get_conversation(self, conversation_id: str):
            return None

        def list_audit_logs(self, limit: int = 20, offset: int = 0, **_kwargs):
            return {"logs": [], "total": 0}

    reloaded = ContextDistiller(_EmptyPersistence(), cache_path=cache_path)
    summary = reloaded.get_summary()

    assert summary["total_patterns"] == len(first_result.patterns)
    assert summary["conversations_analyzed"] == first_result.conversations_analyzed
    assert summary["last_distilled_at"] == first_result.distilled_at


def test_distiller_handles_corrupted_cache_file(tmp_path: Path):
    cache_path = tmp_path / "evolution_latest.json"
    cache_path.write_text("{not-valid-json", encoding="utf-8")

    distiller = ContextDistiller(_FakePersistence(), cache_path=cache_path)
    summary = distiller.get_summary()

    assert distiller.get_latest_result() is None
    assert summary["total_patterns"] == 0
    assert summary["summary"] == "No distillation has been run yet."


# ── _to_float ─────────────────────────────────────────────────────────────────


def test_to_float_converts_numeric_types() -> None:
    assert _to_float(1) == 1.0
    assert _to_float(0.5) == 0.5
    assert _to_float("3.14") == 3.14


def test_to_float_returns_none_for_invalid() -> None:
    assert _to_float("abc") is None
    assert _to_float(None) is None
    assert _to_float([]) is None


# ── _parse_timestamp ──────────────────────────────────────────────────────────


def test_parse_timestamp_parses_z_suffix() -> None:
    from datetime import timezone

    result = _parse_timestamp("2026-02-10T00:00:00Z")
    assert result is not None
    assert result.tzinfo is not None
    assert result.tzinfo == timezone.utc


def test_parse_timestamp_returns_none_for_invalid() -> None:
    assert _parse_timestamp("not-a-date") is None
    assert _parse_timestamp(None) is None
    assert _parse_timestamp("") is None
    assert _parse_timestamp(42) is None


# ── _normalize_string_list ────────────────────────────────────────────────────


def test_normalize_string_list_from_list() -> None:
    result = _normalize_string_list(["  alpha  ", "beta", "  "])
    assert result == ["alpha", "beta"]


def test_normalize_string_list_from_string() -> None:
    assert _normalize_string_list("single") == ["single"]


def test_normalize_string_list_from_empty() -> None:
    assert _normalize_string_list([]) == []
    assert _normalize_string_list("") == []
    assert _normalize_string_list(42) == []  # type: ignore[arg-type]


# ── _unique_preserve_order ────────────────────────────────────────────────────


def test_unique_preserve_order_removes_duplicates() -> None:
    result = _unique_preserve_order(["a", "b", "a", "c", "b"])
    assert result == ["a", "b", "c"]


def test_unique_preserve_order_ignores_blank() -> None:
    result = _unique_preserve_order(["x", "  ", "y"])
    assert result == ["x", "y"]


# ── ContextPattern.to_dict ────────────────────────────────────────────────────


def test_context_pattern_to_dict_round_trip() -> None:
    now = _utc_now()
    pattern = ContextPattern(
        pattern_type="decision",
        description="test",
        evidence=["conv_1"],
        confidence=0.75,
        extracted_at=now,
        metadata={"key": "value"},
    )
    d = pattern.to_dict()
    assert d["pattern_type"] == "decision"
    assert d["evidence"] == ["conv_1"]
    assert d["confidence"] == 0.75
    assert d["metadata"] == {"key": "value"}


# ── DistillationResult.to_dict ────────────────────────────────────────────────


def test_distillation_result_to_dict_structure() -> None:
    now = _utc_now()
    pattern = ContextPattern("value", "v", [], 0.5, now)
    result = DistillationResult(
        patterns=[pattern],
        conversations_analyzed=3,
        time_range=("2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z"),
        summary="ok",
        distilled_at=now,
    )
    d = result.to_dict()
    assert d["conversations_analyzed"] == 3
    assert len(d["patterns"]) == 1
    assert d["time_range"] == ["2026-01-01T00:00:00Z", "2026-01-02T00:00:00Z"]
    assert d["summary"] == "ok"


# ── extract_decision_patterns ─────────────────────────────────────────────────


def test_extract_decision_patterns_empty_returns_empty(tmp_path: Path) -> None:
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    assert distiller.extract_decision_patterns([]) == []


def test_extract_decision_patterns_identifies_high_tension(tmp_path: Path) -> None:
    logs = [
        {
            "conversation_id": "c1",
            "gate_decision": "block",
            "delta_t": 0.85,
            "created_at": "2026-01-01T00:00:00Z",
        },
        {
            "conversation_id": "c2",
            "gate_decision": "block",
            "delta_t": 0.90,
            "created_at": "2026-01-01T00:01:00Z",
        },
        {
            "conversation_id": "c3",
            "gate_decision": "approve",
            "delta_t": 0.20,
            "created_at": "2026-01-01T00:02:00Z",
        },
    ]
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    patterns = distiller.extract_decision_patterns(logs)
    types = {p.pattern_type for p in patterns}
    assert types == {"decision"}
    high_tension = [p for p in patterns if "high-tension" in p.description.lower()]
    assert len(high_tension) >= 1


# ── extract_tone_evolution ────────────────────────────────────────────────────


def test_extract_tone_evolution_positive_shift(tmp_path: Path) -> None:
    conversations = [
        {
            "id": "c1",
            "messages": [
                {"role": "user", "content": "I am angry and confused, this is broken."},
                {"role": "assistant", "content": "Let me help."},
                {"role": "user", "content": "Great, this is clear and works, thank you!"},
            ],
        }
    ]
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    patterns = distiller.extract_tone_evolution(conversations)
    assert len(patterns) >= 1
    assert any(
        "positive" in p.description.lower() or "improve" in p.description.lower() for p in patterns
    )


def test_extract_tone_evolution_no_patterns_for_single_message(tmp_path: Path) -> None:
    conversations = [{"id": "c1", "messages": [{"role": "user", "content": "hello"}]}]
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    assert distiller.extract_tone_evolution(conversations) == []


# ── extract_conflict_resolutions ──────────────────────────────────────────────


def test_extract_conflict_resolutions_resolved(tmp_path: Path) -> None:
    conversations = [
        {
            "id": "c1",
            "messages": [
                {"role": "user", "content": "This is bad, broken, error, wrong, I am frustrated!"},
                {"role": "assistant", "content": "Let me fix that."},
                {"role": "user", "content": "Thank you, this works now!"},
            ],
        }
    ]
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    patterns = distiller.extract_conflict_resolutions(conversations)
    assert len(patterns) == 1
    assert patterns[0].pattern_type == "conflict_resolution"
    assert (
        "tension" in patterns[0].description.lower() or "recover" in patterns[0].description.lower()
    )


def test_extract_conflict_resolutions_empty(tmp_path: Path) -> None:
    conversations = [
        {"id": "c1", "messages": [{"role": "user", "content": "everything is great!"}]}
    ]
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    # No negative tone → no conflict patterns
    assert distiller.extract_conflict_resolutions(conversations) == []


# ── _conversation_has_repair_signal ──────────────────────────────────────────


def test_conversation_has_repair_signal_true(tmp_path: Path) -> None:
    messages = [
        {"role": "user", "content": "This is bad, wrong, error, broken, I hate this."},
        {"role": "assistant", "content": "Here is the fix."},
        {"role": "user", "content": "Thank you, this is great and helpful!"},
    ]
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    assert distiller._conversation_has_repair_signal(messages) is True


def test_conversation_has_repair_signal_false_no_recovery(tmp_path: Path) -> None:
    messages = [
        {"role": "user", "content": "This is bad and wrong and broken."},
        {"role": "assistant", "content": "Sorry."},
        {"role": "user", "content": "Still bad."},
    ]
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    assert distiller._conversation_has_repair_signal(messages) is False


# ── _load_conversations with broken persistence ────────────────────────────────


def test_load_conversations_missing_method_returns_empty(tmp_path: Path) -> None:
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    result = distiller._load_conversations(10)
    assert result == []


def test_load_audit_logs_exception_returns_empty(tmp_path: Path) -> None:
    class _BadPersistence:
        def list_audit_logs(self, **_kwargs):
            raise RuntimeError("DB error")

    distiller = ContextDistiller(_BadPersistence(), cache_path=tmp_path / "c.json")
    assert distiller._load_audit_logs(10) == []


# ── get_patterns without distillation ─────────────────────────────────────────


def test_get_patterns_returns_empty_when_no_result(tmp_path: Path) -> None:
    distiller = ContextDistiller(object(), cache_path=tmp_path / "c.json")
    assert distiller.get_patterns() == []
    assert distiller.get_patterns(pattern_type="decision") == []
