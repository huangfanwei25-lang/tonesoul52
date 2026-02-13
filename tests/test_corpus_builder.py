from __future__ import annotations

from pathlib import Path

from tonesoul.evolution.corpus_builder import CorpusBuilder


class _FakePersistence:
    def list_conversations(self, limit: int = 20, offset: int = 0):
        return {
            "conversations": [
                {"id": "conv_with_audit"},
                {"id": "conv_without_audit"},
            ],
            "total": 2,
        }

    def get_conversation(self, conversation_id: str):
        if conversation_id == "conv_without_audit":
            return {
                "id": conversation_id,
                "messages": [
                    {"role": "user", "content": "hello"},
                    {"role": "assistant", "content": "hi"},
                ],
            }

        return {
            "id": conversation_id,
            "messages": [
                {
                    "role": "user",
                    "content": "Please help me with a safer plan",
                    "created_at": "2026-02-11T01:00:00Z",
                },
                {
                    "role": "assistant",
                    "content": "I can provide a bounded step-by-step option.",
                    "created_at": "2026-02-11T01:00:02Z",
                    "deliberation": {
                        "verdict": "approve",
                        "summary": "Proceed with bounded scope.",
                        "delta_t": 0.64,
                        "self_commits": ["bounded guidance"],
                        "ruptures": ["overclaim risk"],
                        "emergent_values": ["safety", "clarity"],
                        "transcript": {
                            "votes": [
                                {
                                    "perspective": "Philosopher",
                                    "reasoning": "Stay honest about limits.",
                                },
                                {
                                    "perspective": "Engineer",
                                    "reasoning": "Use incremental implementation.",
                                },
                                {
                                    "perspective": "Guardian",
                                    "reasoning": "Avoid unsafe escalation.",
                                },
                            ]
                        },
                    },
                },
                {
                    "role": "user",
                    "content": "Great, this is helpful.",
                    "created_at": "2026-02-11T01:00:10Z",
                },
            ],
        }

    def list_audit_logs(
        self,
        limit: int = 20,
        offset: int = 0,
        conversation_id: str | None = None,
        **_kwargs,
    ):
        if conversation_id == "conv_without_audit":
            return {"logs": [], "total": 0}
        if conversation_id:
            return {
                "logs": [
                    {
                        "conversation_id": conversation_id,
                        "gate_decision": "approve",
                        "delta_t": 0.64,
                        "created_at": "2026-02-11T01:00:02Z",
                    }
                ],
                "total": 1,
            }
        return {"logs": [], "total": 0}


def test_build_from_conversation_creates_structured_entries():
    builder = CorpusBuilder(_FakePersistence())
    entries = builder.build_from_conversation("conv_with_audit")

    assert len(entries) == 1
    entry = entries[0]
    assert entry.conversation_id == "conv_with_audit"
    assert entry.philosopher_stance == "Stay honest about limits."
    assert entry.engineer_approach == "Use incremental implementation."
    assert entry.guardian_risk == "Avoid unsafe escalation."
    assert entry.tension_level == 0.64
    assert "bounded guidance" in entry.commitments_made
    assert "safety" in entry.values_invoked
    assert entry.user_satisfaction == "positive"
    assert "resolved" in entry.tags


def test_build_batch_only_keeps_conversations_with_audit_logs():
    builder = CorpusBuilder(_FakePersistence())
    entries = builder.build_batch(limit=10)
    conversation_ids = {entry.conversation_id for entry in entries}

    assert conversation_ids == {"conv_with_audit"}


def test_export_jsonl_writes_serialized_entries(tmp_path: Path):
    builder = CorpusBuilder(_FakePersistence())
    entries = builder.build_from_conversation("conv_with_audit")
    output = tmp_path / "corpus" / "sample.jsonl"

    builder.export_jsonl(entries, str(output))

    assert output.exists()
    lines = output.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == len(entries)
    assert "conv_with_audit" in lines[0]


def test_build_from_conversation_aligns_descending_audit_logs_by_timestamp():
    class _DescendingAuditPersistence:
        def get_conversation(self, conversation_id: str):
            return {
                "id": conversation_id,
                "messages": [
                    {"role": "user", "content": "u1", "created_at": "2026-02-11T01:00:00Z"},
                    {
                        "role": "assistant",
                        "content": "a1",
                        "created_at": "2026-02-11T01:00:02Z",
                        "deliberation": {},
                    },
                    {"role": "user", "content": "u2", "created_at": "2026-02-11T01:01:00Z"},
                    {
                        "role": "assistant",
                        "content": "a2",
                        "created_at": "2026-02-11T01:01:02Z",
                        "deliberation": {},
                    },
                ],
            }

        def list_audit_logs(
            self,
            limit: int = 20,
            offset: int = 0,
            conversation_id: str | None = None,
            **_kwargs,
        ):
            return {
                "logs": [
                    {
                        "conversation_id": conversation_id,
                        "delta_t": 0.9,
                        "created_at": "2026-02-11T01:01:02Z",
                    },
                    {
                        "conversation_id": conversation_id,
                        "delta_t": 0.2,
                        "created_at": "2026-02-11T01:00:02Z",
                    },
                ],
                "total": 2,
            }

    builder = CorpusBuilder(_DescendingAuditPersistence())
    entries = builder.build_from_conversation("conv_desc")

    assert len(entries) == 2
    assert entries[0].tension_level == 0.2
    assert entries[1].tension_level == 0.9
