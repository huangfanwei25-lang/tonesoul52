from __future__ import annotations

from pathlib import Path

from tools.handoff_builder import (
    ContextSummary,
    DriftEntry,
    HandoffBuilder,
    PendingTask,
    Phase,
)


def test_handoff_builder_uses_env_secret(monkeypatch):
    monkeypatch.setenv("HANDOFF_SECRET", "custom_secret")
    builder = HandoffBuilder()
    assert builder.secret_key == "custom_secret"


def test_handoff_builder_without_env_uses_non_default_secret(monkeypatch):
    monkeypatch.delenv("HANDOFF_SECRET", raising=False)
    builder = HandoffBuilder()
    assert builder.secret_key != "default_dev_secret"
    assert len(builder.secret_key) == 64


def test_handoff_builder_detects_tampered_packet(monkeypatch):
    monkeypatch.setenv("HANDOFF_SECRET", "tamper_secret")
    builder = HandoffBuilder()
    packet = builder.build(
        source_model="gpt-5.4",
        target_model="gpt-5.4-mini",
        phase=Phase(current="implement", reason="security hardening"),
        pending_tasks=[PendingTask(id="1", description="finish tests", status="pending")],
        drift_log=[
            DriftEntry(timestamp="2026-03-20T12:00:00Z", choice="a", toward="b", away_from="c")
        ],
        context_summary=ContextSummary(
            user_goal="ship secure handoff",
            key_concepts=["security", "handoff"],
            current_files=["tools/handoff_builder.py"],
        ),
    )

    assert builder.verify(packet) is True
    packet.context_summary.user_goal = "tampered goal"
    assert builder.verify(packet) is False


def test_handoff_builder_persist_and_load_round_trip(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HANDOFF_SECRET", "persist_secret")
    builder = HandoffBuilder()
    packet = builder.build(
        source_model="gpt-5.4",
        target_model="gpt-5.4-mini",
        phase=Phase(current="handoff", reason="save packet"),
        pending_tasks=[PendingTask(id="2", description="verify packet", status="in_progress")],
        drift_log=[],
        context_summary=ContextSummary(
            user_goal="persist signed packet",
            key_concepts=["handoff"],
            current_files=["memory/handoff"],
        ),
    )

    saved = builder.persist(packet, path=tmp_path)
    loaded = builder.load(saved)

    assert saved.parent == tmp_path
    assert loaded.signature == packet.signature
    assert builder.verify(loaded) is True
