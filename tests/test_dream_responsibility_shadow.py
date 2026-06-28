from __future__ import annotations

from pathlib import Path

from tonesoul.dream_engine import DreamCollision, DreamEngine
from tonesoul.dream_responsibility_shadow import (
    ShadowGateOutcome,
    ShadowLedger,
    collision_payload_to_intent,
    run_shadow_gate,
)
from tonesoul.memory.crystallizer import MemoryCrystallizer
from tonesoul.memory.soul_db import SqliteSoulDB
from tonesoul.memory.write_gateway import MemoryWriteRejectedError

# ── helpers ──────────────────────────────────────────────────────────────────


class _DummyRouter:
    active_backend = None
    last_metrics = None

    def get_client(self):
        return None

    def inference_check(self, timeout_seconds: float = 10.0):
        return {"ok": False}


class _StubGateway:
    """Deterministic stand-in for MemoryWriteGateway: records writes, rejects chosen topics."""

    def __init__(self, reject_topics: set[str] | None = None) -> None:
        self.calls: list[tuple[object, dict]] = []
        self.reject_topics = set(reject_topics or set())

    def write_payload(self, source, payload):
        self.calls.append((source, dict(payload)))
        topic = str(payload.get("topic") or "")
        if topic in self.reject_topics:
            raise MemoryWriteRejectedError([f"stub reject: {topic}"])
        return f"rec-{len(self.calls)}"


def _make_collision(
    topic: str, *, reflection: str = "A grounded dream reflection."
) -> DreamCollision:
    return DreamCollision(
        stimulus_record_id="stim-1",
        topic=topic,
        source_url="https://example.org/x",
        priority_score=0.5,
        relevance_score=0.5,
        novelty_score=0.5,
        resonance_score=0.5,
        friction_score=0.4,
        should_convene_council=False,
        council_reason="no convene",
        llm_backend=None,
        reflection=reflection,
        reflection_generated=False,
    )


def _make_engine(base: Path, *, gateway: _StubGateway, shadow: bool) -> DreamEngine:
    base.mkdir(parents=True, exist_ok=True)
    (base / "crystals.jsonl").write_text("", encoding="utf-8")
    return DreamEngine(
        soul_db=SqliteSoulDB(db_path=base / "soul.db"),
        write_gateway=gateway,
        crystallizer=MemoryCrystallizer(crystal_path=base / "crystals.jsonl", min_frequency=1),
        router=_DummyRouter(),
        responsibility_shadow=shadow,
    )


# ── translation ──────────────────────────────────────────────────────────────


def test_collision_payload_to_intent_shape() -> None:
    intent = collision_payload_to_intent(
        {
            "summary": "S",
            "topic": "T",
            "source_url": "u",
            "evidence": ["e1", "e2"],
            "stimulus_record_id": "sid",
            "source_record_ids": ["r1"],
        }
    )

    assert intent["intent"] == "memory.write.propose"
    assert intent["requested_scope"] == "long_term_memory"
    assert intent["claim"] == "S"
    assert "e1" in intent["evidence_refs"]
    assert "stimulus:sid" in intent["evidence_refs"]
    assert "source:r1" in intent["evidence_refs"]


def test_collision_payload_to_intent_falls_back_for_claim() -> None:
    intent = collision_payload_to_intent({"reflection": "R only", "evidence": ["e"]})
    assert intent["claim"] == "R only"


# ── run_shadow_gate ──────────────────────────────────────────────────────────


def test_run_shadow_gate_allows_valid_payload() -> None:
    outcome = run_shadow_gate({"summary": "A grounded claim", "evidence": ["because of X"]})

    assert outcome.ran is True
    assert outcome.would_execute is True
    assert outcome.error is None


def test_run_shadow_gate_denies_without_evidence() -> None:
    outcome = run_shadow_gate({"summary": "A claim with no evidence", "evidence": []})

    assert outcome.ran is True
    assert outcome.would_execute is False


def test_run_shadow_gate_denies_without_claim() -> None:
    outcome = run_shadow_gate(
        {"summary": "", "reflection": "", "title": "", "topic": "", "evidence": ["e"]}
    )

    assert outcome.would_execute is False


def test_run_shadow_gate_swallows_errors(monkeypatch) -> None:
    # Isolation guarantee: even if the gate explodes, the shadow returns an outcome and never
    # raises, so the caller's real write path can never be affected.
    import tonesoul.dream_responsibility_shadow as mod

    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(mod, "validate_intent", boom)
    outcome = mod.run_shadow_gate({"summary": "x", "evidence": ["e"]})

    assert outcome.ran is False
    assert outcome.would_execute is None
    assert "RuntimeError" in (outcome.error or "")


# ── ledger ───────────────────────────────────────────────────────────────────


def test_shadow_ledger_counts_and_divergence() -> None:
    ledger = ShadowLedger()
    allow = ShadowGateOutcome(
        ran=True,
        would_execute=True,
        request_id="r",
        intent="memory.write.propose",
        reason="ok",
        issue_codes=(),
    )
    deny = ShadowGateOutcome(
        ran=True,
        would_execute=False,
        request_id="r2",
        intent="memory.write.propose",
        reason="deny",
        issue_codes=("missing_evidence_refs",),
    )
    ledger.record(allow, actual_written=True, topic="A")  # gate allow, real wrote
    ledger.record(
        deny, actual_written=True, topic="B"
    )  # gate would deny, real wrote -> enforce signal

    summary = ledger.summary()
    assert summary["total"] == 2
    assert summary["would_allow_and_written"] == 1
    # the enforce-relevant cell: a write an enforcing gate would have blocked
    assert summary["would_deny_but_written"] == 1
    assert summary["would_deny_but_written_cases"][0]["topic"] == "B"
    assert summary["would_allow_but_rejected"] == 0


# ── dream_engine integration ─────────────────────────────────────────────────


def test_shadow_does_not_change_write_counts(tmp_path: Path) -> None:
    # Isolation: turning the shadow ON must not change WHAT gets written.
    gw_off = _StubGateway()
    gw_on = _StubGateway()
    engine_off = _make_engine(tmp_path / "off", gateway=gw_off, shadow=False)
    engine_on = _make_engine(tmp_path / "on", gateway=gw_on, shadow=True)

    res_off = engine_off._persist_collisions(
        [_make_collision("Topic A"), _make_collision("Topic B")],
        generated_at="2026-06-29T00:00:00Z",
        dream_cycle_id="dc-1",
    )
    res_on = engine_on._persist_collisions(
        [_make_collision("Topic A"), _make_collision("Topic B")],
        generated_at="2026-06-29T00:00:00Z",
        dream_cycle_id="dc-1",
    )

    for key in ("written", "skipped", "rejected"):
        assert res_off[key] == res_on[key]
    assert res_off["written"] == 2
    assert "responsibility_shadow" not in res_off
    assert "responsibility_shadow" in res_on


def test_shadow_annotates_persisted_record_and_ledger(tmp_path: Path) -> None:
    gw = _StubGateway()
    engine = _make_engine(tmp_path, gateway=gw, shadow=True)
    collisions = [_make_collision("Topic A")]

    res = engine._persist_collisions(
        collisions, generated_at="2026-06-29T00:00:00Z", dream_cycle_id="dc-1"
    )

    # the annotation travels WITH the persisted record's observability
    written_payload = gw.calls[0][1]
    shadow_obs = written_payload["observability"]["responsibility_shadow"]
    assert shadow_obs["mode"] == "shadow"
    assert shadow_obs["would_execute"] is True
    # and rides on the in-memory collision
    assert collisions[0].observability["responsibility_shadow"]["would_execute"] is True
    # and the cycle ledger summarizes it
    summary = res["responsibility_shadow"]
    assert summary["total"] == 1
    assert summary["would_allow_and_written"] == 1


def test_shadow_records_would_allow_but_rejected_when_real_write_rejected(tmp_path: Path) -> None:
    # responsibility gate would allow (valid intent) but the write_gateway rejects -> the cross-tab
    # cell would_allow_but_rejected (NOT would_deny_but_written, which is the enforce signal).
    gw = _StubGateway(reject_topics={"Topic A"})
    engine = _make_engine(tmp_path, gateway=gw, shadow=True)

    res = engine._persist_collisions(
        [_make_collision("Topic A")], generated_at="2026-06-29T00:00:00Z", dream_cycle_id="dc-1"
    )

    assert res["written"] == 0
    assert res["rejected"] == 1
    summary = res["responsibility_shadow"]
    assert summary["total"] == 1
    assert summary["would_allow_but_rejected"] == 1
    assert summary["would_deny_but_written"] == 0
