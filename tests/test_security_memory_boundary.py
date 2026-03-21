from __future__ import annotations

from pathlib import Path

import pytest

from tonesoul.corpus.consent import ConsentManager, ConsentType
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.write_gateway import MemoryWriteGateway, MemoryWriteRejectedError
from tonesoul.perception.stimulus import EnvironmentStimulus


def test_write_gateway_rejects_non_mapping_payload(tmp_path: Path) -> None:
    gateway = MemoryWriteGateway(SqliteSoulDB(db_path=tmp_path / "soul.db"))

    with pytest.raises(TypeError, match="dict payload"):
        gateway.write_payload(MemorySource.CUSTOM, "not-a-dict")  # type: ignore[arg-type]


def test_write_gateway_rejects_invalid_source_record_ids_payload(tmp_path: Path) -> None:
    gateway = MemoryWriteGateway(SqliteSoulDB(db_path=tmp_path / "soul.db"))

    with pytest.raises(MemoryWriteRejectedError) as excinfo:
        gateway.write_payload(
            MemorySource.CUSTOM,
            {
                "type": "handoff",
                "summary": "Invalid source_record_ids should fail closed.",
                "evidence": ["artifact excerpt"],
                "provenance": {"source": "handoff"},
                "subjectivity_layer": "tension",
                "source_record_ids": "record-1",
            },
        )

    assert excinfo.value.reasons == ["invalid_source_record_ids"]


def test_environment_stimulus_truncates_excessive_excerpt_before_persisting(tmp_path: Path) -> None:
    gateway = MemoryWriteGateway(SqliteSoulDB(db_path=tmp_path / "soul.db"))
    stimulus = EnvironmentStimulus(
        source_url="https://example.com/security",
        topic="Security",
        summary="Boundary check",
        content_hash="security-hash",
        ingested_at="2026-03-20T12:00:00Z",
        raw_excerpt="x" * 1200,
    )

    gateway.write_environment_stimuli([stimulus], dedupe=False)
    record = gateway.stream_environment_stimuli(limit=1)[0]

    assert len(record.payload["evidence"][0]) == 500
    assert len(record.payload["raw_excerpt"]) == 500


def test_sqlite_soul_db_search_handles_injection_like_query_without_mutation(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    db.append(MemorySource.CUSTOM, {"text": "stable governance memory", "title": "stable note"})

    results = db.search("'; DROP TABLE memories; --", limit=5)
    remaining = list(db.stream(MemorySource.CUSTOM))

    assert isinstance(results, list)
    assert len(remaining) == 1
    assert remaining[0].payload["text"] == "stable governance memory"


def test_consent_manager_defaults_to_invalid_without_authorization(tmp_path: Path) -> None:
    manager = ConsentManager(db_path=str(tmp_path / "users.db"))

    assert manager.get_consent("missing-session") is None
    assert manager.has_valid_consent("missing-session") is False


def test_consent_manager_withdraw_revokes_future_access(tmp_path: Path) -> None:
    manager = ConsentManager(db_path=str(tmp_path / "users.db"))
    manager.record_consent("session-1", ConsentType.RESEARCH)

    assert manager.has_valid_consent("session-1") is True
    assert manager.withdraw_consent("session-1") is True
    assert manager.has_valid_consent("session-1") is False
