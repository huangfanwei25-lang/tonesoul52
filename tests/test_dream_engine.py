from __future__ import annotations

import json
from pathlib import Path

from tonesoul.dream_engine import DreamEngine
from tonesoul.memory.crystallizer import Crystal, MemoryCrystallizer
from tonesoul.memory.reviewed_promotion import (
    apply_reviewed_promotion,
    build_reviewed_promotion_decision,
)
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.memory.write_gateway import MemoryWriteGateway
from tonesoul.perception.stimulus import EnvironmentStimulus
from tonesoul.schemas import LLMCallMetrics


class DummyRouter:
    def __init__(self, client=None, backend=None, metrics=None, readiness=None) -> None:
        self._client = client
        self.active_backend = backend
        self.last_metrics = metrics
        self.readiness = readiness
        self.readiness_calls = []

    def get_client(self):
        return self._client

    def inference_check(self, timeout_seconds: float = 10.0):
        self.readiness_calls.append(timeout_seconds)
        if self.readiness is None:
            return {
                "ok": True,
                "supported": False,
                "backend": self.active_backend,
                "reason": "probe_unsupported",
                "timeout_seconds": timeout_seconds,
            }
        return dict(self.readiness, timeout_seconds=timeout_seconds)


class DummyClient:
    def __init__(
        self,
        text: str,
        *,
        model: str = "qwen3.5:4b",
        metrics: LLMCallMetrics | None = None,
    ) -> None:
        self.text = text
        self.model = model
        self.last_metrics = metrics
        self.prompts = []

    def generate(self, prompt: str, system: str | None = None) -> str:
        self.prompts.append({"prompt": prompt, "system": system})
        return self.text


def _write_crystals(path: Path) -> MemoryCrystallizer:
    entries = [
        Crystal(
            rule="prefer governance checks when memory and architecture are involved",
            source_pattern="manual",
            weight=0.92,
            created_at="2026-03-07T12:00:00Z",
            tags=["governance", "memory", "architecture"],
        ),
        Crystal(
            rule="preserve durable memory boundaries before autonomous execution",
            source_pattern="manual",
            weight=0.88,
            created_at="2026-03-07T12:01:00Z",
            tags=["memory", "autonomous"],
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
    return MemoryCrystallizer(crystal_path=path, min_frequency=1)


def _build_stimulus(
    *,
    topic: str,
    summary: str,
    content_hash: str,
    relevance_score: float,
    novelty_score: float,
    tags: list[str],
    source_url: str = "https://example.com/article",
    ingested_at: str = "2026-03-07T12:00:00Z",
) -> EnvironmentStimulus:
    return EnvironmentStimulus(
        source_url=source_url,
        topic=topic,
        summary=summary,
        content_hash=content_hash,
        ingested_at=ingested_at,
        relevance_score=relevance_score,
        novelty_score=novelty_score,
        tags=tags,
        raw_excerpt=summary,
    )


def test_select_stimuli_prefers_high_priority_records(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="High Governance Signal",
                summary="governance memory architecture",
                content_hash="stim-1",
                relevance_score=0.9,
                novelty_score=0.7,
                tags=["governance", "memory"],
            ),
            _build_stimulus(
                topic="Low Signal",
                summary="small unrelated note",
                content_hash="stim-2",
                relevance_score=0.1,
                novelty_score=0.1,
                tags=["misc"],
            ),
            _build_stimulus(
                topic="Medium Signal",
                summary="memory architecture pipeline",
                content_hash="stim-3",
                relevance_score=0.65,
                novelty_score=0.55,
                tags=["memory", "architecture"],
            ),
        ]
    )

    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(),
    )
    selected = engine.select_stimuli(limit=2, min_priority=0.35)

    assert [record.payload["topic"] for record in selected] == [
        "High Governance Signal",
        "Medium Signal",
    ]


def test_run_cycle_collides_stimulus_with_memory_and_crystals(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    db.append(
        MemorySource.SELF_JOURNAL,
        {
            "timestamp": "2026-03-07T10:00:00Z",
            "title": "Governance checkpoint",
            "summary": "memory architecture governance note",
            "tags": ["governance", "memory", "architecture"],
            "layer": "factual",
        },
    )
    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="Governance collision",
                summary="governance memory architecture signal",
                content_hash="stim-collision",
                relevance_score=0.82,
                novelty_score=0.61,
                tags=["governance", "memory", "architecture"],
            )
        ]
    )

    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(),
    )
    result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)

    assert result.stimuli_selected == 1
    assert result.write_gateway["written"] == 1
    assert result.write_gateway["rejected"] == 0
    collision = result.collisions[0]
    assert collision.related_memories
    assert collision.crystal_rules
    assert collision.friction_score is not None
    assert isinstance(collision.should_convene_council, bool)
    assert collision.resistance["prior_tension"]["constraint_kind"] == "core_rule"
    assert collision.persisted_record_id == result.write_gateway["record_ids"][0]


def test_run_cycle_uses_deterministic_fallback_without_model(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="Fallback case",
                summary="governance memory",
                content_hash="stim-fallback",
                relevance_score=0.74,
                novelty_score=0.52,
                tags=["governance", "memory"],
            )
        ]
    )

    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(client=None, backend=None),
    )
    result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=True)

    collision = result.collisions[0]
    assert collision.reflection_generated is False
    assert "Dream collision examined" in collision.reflection
    assert collision.llm_backend is None


def test_run_cycle_uses_llm_when_available(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="Model case",
                summary="architecture memory governance",
                content_hash="stim-llm",
                relevance_score=0.8,
                novelty_score=0.6,
                tags=["architecture", "memory", "governance"],
            )
        ]
    )
    metrics = LLMCallMetrics(
        model="qwen3.5:8b",
        prompt_tokens=14,
        completion_tokens=6,
        total_tokens=20,
    )
    client = DummyClient("model reflection", model="qwen3.5:8b", metrics=metrics)
    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(client=client, backend="ollama", metrics=metrics),
    )

    result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=True)

    collision = result.collisions[0]
    assert collision.reflection_generated is True
    assert collision.reflection == "model reflection"
    assert collision.llm_backend == "ollama"
    assert collision.observability["llm"] == {
        "backend": "ollama",
        "model": "qwen3.5:8b",
        "usage": {
            "prompt_tokens": 14,
            "completion_tokens": 6,
            "total_tokens": 20,
            "cost_usd": 0.0,
        },
    }
    assert client.prompts


def test_run_cycle_skips_reflection_when_readiness_probe_fails(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="Timeout case",
                summary="governance memory architecture",
                content_hash="stim-timeout",
                relevance_score=0.8,
                novelty_score=0.6,
                tags=["governance", "memory", "architecture"],
            )
        ]
    )
    client = DummyClient("slow reflection", model="qwen3.5:9b")
    router = DummyRouter(
        client=client,
        backend="lmstudio",
        readiness={
            "ok": False,
            "supported": True,
            "backend": "lmstudio",
            "model": "qwen3.5:9b",
            "reason": "timeout",
        },
    )
    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=router,
    )

    result = engine.run_cycle(
        limit=1,
        min_priority=0.1,
        generate_reflection=True,
        require_inference_ready=True,
        inference_timeout_seconds=7.5,
    )

    collision = result.collisions[0]
    assert result.llm_backend == "lmstudio"
    assert result.llm_preflight["ok"] is False
    assert result.llm_preflight["reason"] == "timeout"
    assert router.readiness_calls == [7.5]
    assert collision.reflection_generated is False
    assert collision.observability.get("llm") is None
    assert client.prompts == []


def test_run_cycle_persists_collision_via_write_gateway_with_provenance(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="Persistence case",
                summary="governance memory architecture signal",
                content_hash="stim-persist",
                relevance_score=0.88,
                novelty_score=0.57,
                tags=["governance", "memory", "architecture"],
            )
        ]
    )
    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(),
    )

    result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)

    assert result.dream_cycle_id.startswith("dream-cycle-")
    assert result.write_gateway == {
        "written": 1,
        "skipped": 0,
        "rejected": 0,
        "record_ids": [result.collisions[0].persisted_record_id],
        "skip_reasons": [],
        "reject_reasons": [],
    }

    persisted = list(db.stream(MemorySource.CUSTOM))
    collision_payloads = [
        record.payload
        for record in persisted
        if str(record.payload.get("type") or "").strip() == "dream_collision"
    ]
    assert len(collision_payloads) == 1
    payload = collision_payloads[0]
    assert payload["layer"] == "working"
    assert payload["subjectivity_layer"] == "tension"
    assert payload["dream_cycle_id"] == result.dream_cycle_id
    assert payload["source_record_ids"] == [result.collisions[0].stimulus_record_id]
    assert payload["promotion_gate"] == {
        "status": "candidate",
        "source": "dream_engine",
    }
    assert payload["decay_policy"] == {"policy": "adaptive"}
    assert payload["provenance"]["dream_cycle_id"] == result.dream_cycle_id
    assert payload["provenance"]["source_url"] == "https://example.com/article"
    assert payload["provenance"]["stimulus_record_id"] == result.collisions[0].stimulus_record_id
    assert payload["evidence"]


def test_run_cycle_skips_duplicate_collision_when_same_source_loop_is_still_unresolved(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(),
    )

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="A distributed vulnerability database for Open Source",
                summary="governance memory architecture signal",
                content_hash="stim-initial",
                relevance_score=0.88,
                novelty_score=0.57,
                tags=["governance", "memory", "architecture"],
                source_url="https://osv.dev/",
                ingested_at="2026-03-07T12:00:00Z",
            )
        ]
    )
    first_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)
    first_record_id = str(first_result.collisions[0].persisted_record_id or "")
    persisted_record = next(
        record
        for record in db.stream(MemorySource.CUSTOM)
        if str(record.record_id or "") == first_record_id
    )
    decision = build_reviewed_promotion_decision(
        persisted_record.payload,
        review_actor="operator",
        review_basis="Still one source loop; defer instead of promoting.",
        reviewed_record_id=first_record_id,
        source_record_ids=persisted_record.payload.get("source_record_ids"),
        promotion_source="test_review",
        status="deferred",
        notes="Wake this up only after a second source loop appears.",
    )
    apply_reviewed_promotion(
        db,
        source=MemorySource.CUSTOM,
        payload=persisted_record.payload,
        decision=decision,
    )

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="A distributed vulnerability database for Open Source",
                summary="governance memory architecture signal refreshed",
                content_hash="stim-followup",
                relevance_score=0.91,
                novelty_score=0.59,
                tags=["governance", "memory", "architecture"],
                source_url="https://osv.dev/",
                ingested_at="2026-03-07T12:05:00Z",
            )
        ]
    )
    second_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)

    assert second_result.write_gateway == {
        "written": 0,
        "skipped": 1,
        "rejected": 0,
        "record_ids": [],
        "skip_reasons": ["active_unresolved_signature"],
        "reject_reasons": [],
    }
    assert second_result.collisions[0].persisted_record_id is None
    assert second_result.collisions[0].observability["write_status"] == "skipped"
    assert second_result.collisions[0].observability["write_skip_reason"] == (
        "active_unresolved_signature"
    )

    collision_payloads = [
        record.payload
        for record in db.stream(MemorySource.CUSTOM)
        if str(record.payload.get("type") or "").strip() == "dream_collision"
    ]
    assert len(collision_payloads) == 1


def test_run_cycle_still_writes_when_same_topic_appears_from_new_source_loop(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(),
    )

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="A distributed vulnerability database for Open Source",
                summary="governance memory architecture signal",
                content_hash="stim-primary",
                relevance_score=0.88,
                novelty_score=0.57,
                tags=["governance", "memory", "architecture"],
                source_url="https://osv.dev/",
                ingested_at="2026-03-07T12:00:00Z",
            )
        ]
    )
    first_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)
    assert first_result.write_gateway["written"] == 1

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="A distributed vulnerability database for Open Source",
                summary="governance memory architecture signal mirrored elsewhere",
                content_hash="stim-secondary",
                relevance_score=0.9,
                novelty_score=0.6,
                tags=["governance", "memory", "architecture"],
                source_url="https://mirror.example/osv/",
                ingested_at="2026-03-07T12:05:00Z",
            )
        ]
    )
    second_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)

    assert second_result.write_gateway["written"] == 1
    assert second_result.write_gateway["skipped"] == 0
    assert second_result.collisions[0].persisted_record_id

    collision_payloads = [
        record.payload
        for record in db.stream(MemorySource.CUSTOM)
        if str(record.payload.get("type") or "").strip() == "dream_collision"
    ]
    assert len(collision_payloads) == 2


def test_run_cycle_skips_same_lineage_after_latest_reviewed_rejection(tmp_path: Path) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(),
    )

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="[](https://google.github.io/osv.dev/data/#data-sources) Data sources",
                summary="governance memory architecture signal",
                content_hash="stim-primary",
                relevance_score=0.91,
                novelty_score=0.59,
                tags=["governance", "memory", "architecture"],
                source_url="https://google.github.io/osv.dev/data/",
                ingested_at="2026-03-07T12:00:00Z",
            )
        ]
    )
    first_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)
    first_record_id = str(first_result.collisions[0].persisted_record_id or "")
    persisted_record = next(
        record
        for record in db.stream(MemorySource.CUSTOM)
        if str(record.record_id or "") == first_record_id
    )
    decision = build_reviewed_promotion_decision(
        persisted_record.payload,
        review_actor="operator",
        review_basis=(
            "Repeated same-source governance friction remains visible, but it still comes from "
            "one source loop and one lineage; reject commitment weight while preserving the tension trace."
        ),
        reviewed_record_id=first_record_id,
        source_record_ids=persisted_record.payload.get("source_record_ids"),
        promotion_source="test_review",
        status="rejected",
        notes="Revisit only if the same direction appears across materially different source contexts or a second independent lineage cluster.",
    )
    apply_reviewed_promotion(
        db,
        source=MemorySource.CUSTOM,
        payload=persisted_record.payload,
        decision=decision,
    )

    second_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)

    assert second_result.write_gateway == {
        "written": 0,
        "skipped": 1,
        "rejected": 0,
        "record_ids": [],
        "skip_reasons": ["prior_rejected_signature"],
        "reject_reasons": [],
    }
    assert second_result.collisions[0].persisted_record_id is None
    assert second_result.collisions[0].observability["write_status"] == "skipped"
    assert second_result.collisions[0].observability["write_skip_reason"] == (
        "prior_rejected_signature"
    )

    collision_payloads = [
        record.payload
        for record in db.stream(MemorySource.CUSTOM)
        if str(record.payload.get("type") or "").strip() == "dream_collision"
    ]
    assert len(collision_payloads) == 1


def test_run_cycle_still_writes_when_rejected_same_source_reappears_from_new_lineage(
    tmp_path: Path,
) -> None:
    db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    gateway = MemoryWriteGateway(db)
    crystallizer = _write_crystals(tmp_path / "crystals.jsonl")
    engine = DreamEngine(
        soul_db=db,
        write_gateway=gateway,
        crystallizer=crystallizer,
        router=DummyRouter(),
    )

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="[](https://google.github.io/osv.dev/data/#data-sources) Data sources",
                summary="governance memory architecture signal",
                content_hash="stim-primary",
                relevance_score=0.91,
                novelty_score=0.59,
                tags=["governance", "memory", "architecture"],
                source_url="https://google.github.io/osv.dev/data/",
                ingested_at="2026-03-07T12:00:00Z",
            )
        ]
    )
    first_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)
    first_record_id = str(first_result.collisions[0].persisted_record_id or "")
    persisted_record = next(
        record
        for record in db.stream(MemorySource.CUSTOM)
        if str(record.record_id or "") == first_record_id
    )
    decision = build_reviewed_promotion_decision(
        persisted_record.payload,
        review_actor="operator",
        review_basis=(
            "Repeated same-source governance friction remains visible, but it still comes from "
            "one source loop and one lineage; reject commitment weight while preserving the tension trace."
        ),
        reviewed_record_id=first_record_id,
        source_record_ids=persisted_record.payload.get("source_record_ids"),
        promotion_source="test_review",
        status="rejected",
        notes="Revisit only if the same direction appears across materially different source contexts or a second independent lineage cluster.",
    )
    apply_reviewed_promotion(
        db,
        source=MemorySource.CUSTOM,
        payload=persisted_record.payload,
        decision=decision,
    )

    gateway.write_environment_stimuli(
        [
            _build_stimulus(
                topic="[](https://google.github.io/osv.dev/data/#data-sources) Data sources",
                summary="governance memory architecture signal from a second lineage",
                content_hash="stim-secondary-lineage",
                relevance_score=0.93,
                novelty_score=0.61,
                tags=["governance", "memory", "architecture"],
                source_url="https://google.github.io/osv.dev/data/",
                ingested_at="2026-03-07T12:05:00Z",
            )
        ]
    )
    second_result = engine.run_cycle(limit=1, min_priority=0.1, generate_reflection=False)

    assert second_result.write_gateway["written"] == 1
    assert second_result.write_gateway["skipped"] == 0
    assert second_result.collisions[0].persisted_record_id

    collision_payloads = [
        record.payload
        for record in db.stream(MemorySource.CUSTOM)
        if str(record.payload.get("type") or "").strip() == "dream_collision"
    ]
    assert len(collision_payloads) == 2
