from __future__ import annotations

from pathlib import Path

from tonesoul.evolution.context_distiller import ContextDistiller, _tone_score


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
