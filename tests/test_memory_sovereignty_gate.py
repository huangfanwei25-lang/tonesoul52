"""Axiom 8 (Memory Sovereignty) enforcement — gate + egress wiring.

These pin that MemoryConfig is now a REAL fail-closed consumer at the two memory
egress edges (transfer / training export), while first-party memory writes stay
untouched (so the revived dream cycle and boot are unaffected).
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

from tonesoul.memory.sovereignty_gate import MemorySovereigntyGate
from tonesoul.soul_config import SOUL, MemoryConfig


def _cfg(**over) -> MemoryConfig:
    return dataclasses.replace(SOUL.memory, **over)


# ── evaluate_transfer ─────────────────────────────────────────────────────────


def test_first_party_transfer_is_allowed_and_stamped() -> None:
    gate = MemorySovereigntyGate()
    v = gate.evaluate_transfer({"from_agent": "claude", "to_agent": "codex", "summary": "x"})
    assert v.allowed is True
    assert v.stamp["external_transfer"] is False
    assert v.stamp["verdict"] == "allow"


def test_external_transfer_without_consent_is_blocked() -> None:
    gate = MemorySovereigntyGate()
    v = gate.evaluate_transfer({"memory_owner": "another_user", "summary": "x"})
    assert v.allowed is False
    assert any("transfer_blocked" in r for r in v.reasons)
    assert v.stamp["verdict"] == "block"


def test_external_transfer_with_consent_token_is_allowed() -> None:
    gate = MemorySovereigntyGate()
    v = gate.evaluate_transfer({"memory_owner": "another_user", "consent_token": "tok-123"})
    assert v.allowed is True
    assert v.stamp["consent"] is True


def test_replica_without_consent_is_blocked_when_replication_disallowed() -> None:
    gate = MemorySovereigntyGate(config=_cfg(replication_allowed=False))
    v = gate.evaluate_transfer({"is_replica": True})
    assert v.allowed is False
    assert any("replication_blocked" in r for r in v.reasons)


def test_replica_allowed_when_replication_allowed() -> None:
    gate = MemorySovereigntyGate(config=_cfg(replication_allowed=True))
    v = gate.evaluate_transfer({"is_replica": True})
    assert v.allowed is True


def test_consent_lookup_can_refute_a_token_fail_closed() -> None:
    gate = MemorySovereigntyGate(consent_lookup=lambda token: False)
    v = gate.evaluate_transfer({"memory_owner": "other", "consent_token": "forged"})
    assert v.allowed is False  # registry refuted the token


# ── deidentify ────────────────────────────────────────────────────────────────


def test_deidentify_redacts_text_and_hashes_ids_when_required() -> None:
    gate = MemorySovereigntyGate(config=_cfg(training_requires_deidentification=True))
    out = gate.deidentify(
        {
            "user_message": "my name is Alice and my SSN is 123",
            "conversation_id": "conv-9",
            "tags": ["a"],
        }
    )
    assert out["user_message"].startswith("[redacted:sha256:")
    assert out["conversation_id"].startswith("sha256:")
    assert out["deidentified"] is True
    assert out["tags"] == ["a"]  # non-PII structural field preserved


def test_deidentify_is_noop_when_flag_off() -> None:
    gate = MemorySovereigntyGate(config=_cfg(training_requires_deidentification=False))
    record = {"user_message": "raw", "conversation_id": "conv-9"}
    out = gate.deidentify(record)
    assert out == record
    assert "deidentified" not in out


# ── training export wiring (corpus_builder.export_jsonl) ───────────────────────


def test_export_jsonl_deidentifies_by_default(tmp_path: Path) -> None:
    from tonesoul.evolution.corpus_builder import CorpusBuilder
    from tonesoul.evolution.corpus_schema import CorpusEntry

    entry = CorpusEntry(
        user_message="raw user text with PII",
        conversation_context="ctx",
        philosopher_stance="p",
        engineer_approach="e",
        guardian_risk="g",
        synthesizer_decision="s",
        tension_level=0.5,
        final_response="raw assistant text",
        conversation_id="conv-42",
    )
    out = tmp_path / "corpus.jsonl"
    CorpusBuilder(None).export_jsonl([entry], str(out))

    record = json.loads(out.read_text(encoding="utf-8").splitlines()[0])
    assert record["deidentified"] is True
    assert record["user_message"].startswith("[redacted:")
    assert record["final_response"].startswith("[redacted:")
    assert record["conversation_id"].startswith("sha256:")


# ── handoff transfer wiring (live, non-breaking) ──────────────────────────────


def _write_handoff(dir_path: Path, name: str, payload: dict) -> Path:
    p = dir_path / name
    p.write_text(json.dumps(payload), encoding="utf-8")
    return p


def test_first_party_handoff_still_ingests(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    from tonesoul.memory.handoff_ingester import HandoffIngester
    from tonesoul.memory.soul_db import SqliteSoulDB

    path = _write_handoff(
        tmp_path,
        "h.json",
        {"source_model": "claude", "target_model": "codex", "phase": {"reason": "ok"}},
    )
    ing = HandoffIngester(SqliteSoulDB(db_path=tmp_path / "soul.db"))
    assert ing._ingest_json(path, since_dt=None) == "ingested"  # boot path unaffected


def test_external_owner_handoff_without_consent_is_skipped(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    from tonesoul.memory.handoff_ingester import HandoffIngester
    from tonesoul.memory.soul_db import SqliteSoulDB

    path = _write_handoff(
        tmp_path,
        "ext.json",
        {
            "source_model": "x",
            "target_model": "y",
            "memory_owner": "another_user",
            "phase": {"reason": "r"},
        },
    )
    ing = HandoffIngester(SqliteSoulDB(db_path=tmp_path / "soul.db"))
    assert ing._ingest_json(path, since_dt=None) == "skipped"
    assert ing.last_reject_reasons and "transfer_blocked" in ing.last_reject_reasons[0]


def test_external_owner_handoff_with_consent_ingests(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("TONESOUL_MEMORY_EMBEDDER", "hash")
    from tonesoul.memory.handoff_ingester import HandoffIngester
    from tonesoul.memory.soul_db import SqliteSoulDB

    path = _write_handoff(
        tmp_path,
        "ext_ok.json",
        {
            "source_model": "x",
            "target_model": "y",
            "memory_owner": "another_user",
            "consent_token": "tok-abc",
            "phase": {"reason": "r"},
        },
    )
    ing = HandoffIngester(SqliteSoulDB(db_path=tmp_path / "soul.db"))
    assert ing._ingest_json(path, since_dt=None) == "ingested"
