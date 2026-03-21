from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from tonesoul.dream_engine import DreamCollision, DreamCycleResult
from tonesoul.memory.soul_db import MemorySource, SqliteSoulDB
from tonesoul.scribe.scribe_engine import ScribeDraftResult
from tonesoul.wakeup_loop import AutonomousWakeupLoop


class DummyEngine:
    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def run_cycle(self, **kwargs):
        self.calls.append(kwargs)
        return self.results.pop(0)


def _build_collision(
    *,
    topic: str,
    friction_score: float,
    should_convene_council: bool,
    breaker_status: str = "stable",
    lyapunov_proxy: float = 0.0,
    llm: dict[str, object] | None = None,
    reflection_generated: bool | None = None,
) -> DreamCollision:
    observability = {"lyapunov_proxy": lyapunov_proxy}
    if llm is not None:
        observability["llm"] = llm
    if reflection_generated is None:
        reflection_generated = llm is not None
    return DreamCollision(
        stimulus_record_id=f"stimulus-{topic}",
        topic=topic,
        source_url="https://example.com",
        priority_score=0.8,
        relevance_score=0.7,
        novelty_score=0.6,
        resonance_score=0.4,
        friction_score=friction_score,
        should_convene_council=should_convene_council,
        council_reason="test",
        llm_backend=None,
        reflection="fallback",
        reflection_generated=reflection_generated,
        resistance={"circuit_breaker": {"status": breaker_status}},
        observability=observability,
    )


def _build_result(
    *collisions: DreamCollision,
    llm_preflight: dict[str, object] | None = None,
    stimuli_considered: int | None = None,
    write_gateway: dict[str, object] | None = None,
) -> DreamCycleResult:
    return DreamCycleResult(
        generated_at="2026-03-07T17:00:00Z",
        dream_cycle_id="dream-cycle-test",
        stimuli_considered=(
            max(1, len(collisions)) if stimuli_considered is None else stimuli_considered
        ),
        stimuli_selected=len(collisions),
        llm_backend=None,
        collisions=list(collisions),
        llm_preflight=dict(llm_preflight or {}),
        write_gateway=dict(
            write_gateway
            or {
                "written": len(collisions),
                "skipped": 0,
                "rejected": 0,
                "record_ids": [f"memory-{index}" for index, _ in enumerate(collisions, start=1)],
                "reject_reasons": [],
            }
        ),
    )


def test_emit_once_returns_idle_status_when_no_stimuli_selected() -> None:
    dummy_engine = DummyEngine([_build_result()])
    loop = AutonomousWakeupLoop(
        dream_engine=dummy_engine,
        interval_seconds=60.0,
        sleep_func=lambda _: None,
    )

    result = loop.emit_once(cycle=1, dream_kwargs={"limit": 2, "generate_reflection": False})

    assert result.status == "idle"
    assert result.summary["stimuli_selected"] == 0
    assert result.summary["collision_count"] == 0
    assert result.summary["collision_success_rate"] == 0.0
    assert dummy_engine.calls == [{"limit": 2, "generate_reflection": False}]


def test_run_repeats_cycles_and_sleeps_between_iterations() -> None:
    dummy_engine = DummyEngine(
        [
            _build_result(
                _build_collision(topic="first", friction_score=0.4, should_convene_council=False)
            ),
            _build_result(
                _build_collision(topic="second", friction_score=0.5, should_convene_council=True)
            ),
            _build_result(
                _build_collision(topic="third", friction_score=0.6, should_convene_council=False)
            ),
        ]
    )
    sleep_calls: list[float] = []
    loop = AutonomousWakeupLoop(
        dream_engine=dummy_engine,
        interval_seconds=12.5,
        sleep_func=lambda seconds: sleep_calls.append(seconds),
    )

    results = loop.run(max_cycles=3, dream_kwargs={"limit": 1})

    assert [result.cycle for result in results] == [1, 2, 3]
    assert sleep_calls == [12.5, 12.5]
    assert dummy_engine.calls == [{"limit": 1}, {"limit": 1}, {"limit": 1}]


def test_emit_once_summarizes_council_breaker_and_friction() -> None:
    dummy_engine = DummyEngine(
        [
            _build_result(
                _build_collision(
                    topic="stable",
                    friction_score=0.42,
                    should_convene_council=False,
                    breaker_status="stable",
                    lyapunov_proxy=0.18,
                    llm={
                        "backend": "ollama",
                        "usage": {
                            "prompt_tokens": 12,
                            "completion_tokens": 5,
                            "total_tokens": 17,
                        },
                    },
                ),
                _build_collision(
                    topic="frozen",
                    friction_score=0.91,
                    should_convene_council=True,
                    breaker_status="frozen",
                    lyapunov_proxy=0.77,
                    llm={
                        "backend": "ollama",
                        "usage": {
                            "prompt_tokens": 9,
                            "completion_tokens": 4,
                            "total_tokens": 13,
                        },
                    },
                ),
                stimuli_considered=4,
            )
        ]
    )
    loop = AutonomousWakeupLoop(
        dream_engine=dummy_engine,
        interval_seconds=30.0,
        sleep_func=lambda _: None,
    )

    result = loop.emit_once(cycle=1)

    assert result.status == "ok"
    assert result.summary["collision_count"] == 2
    assert result.summary["council_count"] == 1
    assert result.summary["frozen_count"] == 1
    assert result.summary["avg_friction_score"] == 0.665
    assert result.summary["max_friction_score"] == 0.91
    assert result.summary["max_lyapunov_proxy"] == 0.77
    assert result.summary["collision_success_rate"] == 0.5
    assert result.summary["write_gateway_written"] == 2
    assert result.summary["write_gateway_skipped"] == 0
    assert result.summary["write_gateway_rejected"] == 0
    assert result.summary["llm_call_count"] == 2
    assert result.summary["llm_prompt_tokens_total"] == 21
    assert result.summary["llm_completion_tokens_total"] == 9
    assert result.summary["llm_total_tokens"] == 30
    assert result.summary["llm_backends"] == ["ollama"]


def test_emit_once_ignores_llm_observability_when_reflection_not_generated() -> None:
    dummy_engine = DummyEngine(
        [
            _build_result(
                _build_collision(
                    topic="preflight-skipped",
                    friction_score=0.52,
                    should_convene_council=True,
                    breaker_status="stable",
                    lyapunov_proxy=0.22,
                    llm={"backend": "lmstudio"},
                    reflection_generated=False,
                )
            )
        ]
    )
    loop = AutonomousWakeupLoop(
        dream_engine=dummy_engine,
        interval_seconds=15.0,
        sleep_func=lambda _: None,
    )

    result = loop.emit_once(cycle=1)

    assert result.summary["llm_call_count"] == 0
    assert result.summary["llm_total_tokens"] == 0
    assert result.summary["llm_backends"] == []
    assert result.summary["llm_models"] == []


def test_emit_once_includes_llm_preflight_latency_summary() -> None:
    dummy_engine = DummyEngine(
        [
            _build_result(
                _build_collision(
                    topic="timeout",
                    friction_score=0.52,
                    should_convene_council=True,
                    breaker_status="stable",
                    lyapunov_proxy=0.22,
                    reflection_generated=False,
                ),
                llm_preflight={
                    "ok": False,
                    "reason": "timeout",
                    "latency_ms": 2002,
                    "selection_latency_ms": 759,
                    "probe_latency_ms": 1243,
                },
            )
        ]
    )
    loop = AutonomousWakeupLoop(
        dream_engine=dummy_engine,
        interval_seconds=15.0,
        sleep_func=lambda _: None,
    )

    result = loop.emit_once(cycle=1)

    assert result.summary["llm_preflight_latency_ms"] == 2002
    assert result.summary["llm_preflight_selection_latency_ms"] == 759
    assert result.summary["llm_preflight_probe_latency_ms"] == 1243
    assert result.summary["llm_preflight_timeout_count"] == 1
    assert result.summary["llm_preflight_reason"] == "timeout"


@dataclass
class DummySleepResult:
    promoted_count: int
    cleared_count: int
    gated_count: int
    subjectivity_summary: dict[str, object] = field(default_factory=dict)


class DummyScribe:
    def __init__(self, result: ScribeDraftResult) -> None:
        self.result = result
        self.calls: list[dict[str, object]] = []

    def draft_chronicle(self, db, title_hint="A Day in the Dream Engine", source_db_path=None):
        self.calls.append(
            {
                "title_hint": title_hint,
                "source_db_path": None if source_db_path is None else str(source_db_path),
            }
        )
        return self.result


def test_run_triggers_periodic_sleep_consolidation() -> None:
    class ConsolidatingEngine(DummyEngine):
        def __init__(self, results):
            super().__init__(results)
            self.soul_db = object()

    dummy_engine = ConsolidatingEngine(
        [
            _build_result(
                _build_collision(topic="first", friction_score=0.2, should_convene_council=False)
            ),
            _build_result(
                _build_collision(topic="second", friction_score=0.3, should_convene_council=False)
            ),
            _build_result(
                _build_collision(topic="third", friction_score=0.4, should_convene_council=True)
            ),
        ]
    )
    consolidate_calls: list[tuple[object, object]] = []
    loop = AutonomousWakeupLoop(
        dream_engine=dummy_engine,
        interval_seconds=12.0,
        sleep_func=lambda _: None,
        consolidate_every_cycles=2,
        consolidate_source=MemorySource.CUSTOM,
        consolidate_func=lambda soul_db, source: (
            consolidate_calls.append((soul_db, source))
            or DummySleepResult(
                promoted_count=2,
                cleared_count=1,
                gated_count=0,
                subjectivity_summary={
                    "unresolved_tension_count": 1,
                    "by_subjectivity_layer": {"vow": 2},
                },
            )
        ),
    )

    results = loop.run(max_cycles=3, dream_kwargs={"limit": 1})

    assert consolidate_calls == [(dummy_engine.soul_db, MemorySource.CUSTOM)]
    assert results[0].summary["consolidation_ran"] is False
    assert results[1].summary["consolidation_ran"] is True
    assert results[1].summary["consolidation_promoted_count"] == 2
    assert results[1].summary["consolidation_cleared_count"] == 1
    assert results[1].summary["consolidation_gated_count"] == 0
    assert results[1].summary["consolidation_unresolved_tension_count"] == 1
    assert results[1].summary["consolidation_vow_count"] == 2
    assert results[1].dream_result["consolidation"]["promoted_count"] == 2


def test_run_triggers_scribe_after_material_cycle(tmp_path: Path) -> None:
    class ScribeEngine(DummyEngine):
        def __init__(self, results, soul_db) -> None:
            super().__init__(results)
            self.soul_db = soul_db

    soul_db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    chronicle_path = tmp_path / "chronicles" / "chronicle.md"
    companion_path = tmp_path / "chronicles" / "chronicle.json"
    scribe = DummyScribe(
        ScribeDraftResult(
            generated_at="2026-03-13T15:20:00Z",
            status="generated",
            source_db_path=str(soul_db.db_path),
            observed_counts={"tensions": 1, "collisions": 0, "crystals": 0},
            lead_anchor_summary="[T1] tension: scribe-worthy collision...",
            fallback_mode="observed_history",
            generation_mode="template_assist",
            title_hint="The Weight of Unresolved Tensions",
            llm_model="gemma3:4b",
            llm_attempts=[
                {"model": "qwen3.5:4b", "status": "timeout"},
                {
                    "model": "gemma3:4b",
                    "status": "boundary_rejected",
                    "error": "data streams, the user",
                },
                {"model": "template_assist", "status": "generated"},
            ],
            chronicle_path=chronicle_path,
            companion_path=companion_path,
        )
    )
    status_path = tmp_path / "status" / "scribe_status_latest.json"
    scribe_state_path = tmp_path / "state" / "scribe_state.json"
    loop = AutonomousWakeupLoop(
        dream_engine=ScribeEngine(
            [
                _build_result(
                    _build_collision(
                        topic="scribe-worthy",
                        friction_score=0.58,
                        should_convene_council=True,
                    )
                )
            ],
            soul_db,
        ),
        interval_seconds=0.0,
        sleep_func=lambda _: None,
        consolidate_every_cycles=0,
        scribe=scribe,
        scribe_status_path=status_path,
        scribe_state_path=scribe_state_path,
    )

    results = loop.run(max_cycles=1, dream_kwargs={"limit": 1})

    assert len(scribe.calls) == 1
    assert scribe.calls[0]["title_hint"] == "After the Wake-Up Collisions"
    assert results[0].summary["scribe_triggered"] is True
    assert results[0].summary["scribe_status"] == "generated"
    assert results[0].summary["scribe_generation_mode"] == "template_assist"
    assert results[0].summary["scribe_state_document_posture"] == "pressure_without_counterweight"
    assert (
        results[0].summary["scribe_anchor_status_line"]
        == "anchor | [T1] tension: scribe-worthy collision..."
    )
    assert (
        results[0].summary["scribe_problem_route_status_line"]
        == "route | family=F6_semantic_role_boundary_integrity "
        "invariant=chronicle_self_scope "
        "repair=semantic_boundary_guardrail "
        "secondary=F4_execution_contract_integrity"
    )
    assert (
        results[0].summary["scribe_problem_route_secondary_labels"]
        == "F4_execution_contract_integrity"
    )
    assert (
        results[0].dream_result["scribe"]["result"]["latest_available_source"] == "chronicle_pair"
    )
    assert status_path.exists()
    assert scribe_state_path.exists()


def test_run_suppresses_duplicate_scribe_signal_across_invocations(tmp_path: Path) -> None:
    class ScribeEngine(DummyEngine):
        def __init__(self, results, soul_db) -> None:
            super().__init__(results)
            self.soul_db = soul_db

    soul_db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    status_path = tmp_path / "status" / "scribe_status_latest.json"
    scribe_state_path = tmp_path / "state" / "scribe_state.json"
    scribe = DummyScribe(
        ScribeDraftResult(
            generated_at="2026-03-13T15:25:00Z",
            status="generated",
            source_db_path=str(soul_db.db_path),
            observed_counts={"tensions": 1, "collisions": 0, "crystals": 0},
            fallback_mode="observed_history",
            generation_mode="template_assist",
            title_hint="The Weight of Unresolved Tensions",
            llm_model="gemma3:4b",
            llm_attempts=[{"model": "gemma3:4b", "status": "generated"}],
            chronicle_path=tmp_path / "chronicles" / "chronicle.md",
            companion_path=tmp_path / "chronicles" / "chronicle.json",
        )
    )

    first_loop = AutonomousWakeupLoop(
        dream_engine=ScribeEngine(
            [
                _build_result(
                    _build_collision(
                        topic="duplicate-topic",
                        friction_score=0.61,
                        should_convene_council=True,
                    )
                )
            ],
            soul_db,
        ),
        interval_seconds=0.0,
        sleep_func=lambda _: None,
        consolidate_every_cycles=0,
        scribe=scribe,
        scribe_status_path=status_path,
        scribe_state_path=scribe_state_path,
    )
    second_loop = AutonomousWakeupLoop(
        dream_engine=ScribeEngine(
            [
                _build_result(
                    _build_collision(
                        topic="duplicate-topic",
                        friction_score=0.61,
                        should_convene_council=True,
                    )
                )
            ],
            soul_db,
        ),
        interval_seconds=0.0,
        sleep_func=lambda _: None,
        consolidate_every_cycles=0,
        scribe=scribe,
        scribe_status_path=status_path,
        scribe_state_path=scribe_state_path,
    )

    first_results = first_loop.run(max_cycles=1, dream_kwargs={"limit": 1})
    second_results = second_loop.run(max_cycles=1, dream_kwargs={"limit": 1})

    assert len(scribe.calls) == 1
    assert first_results[0].summary["scribe_triggered"] is True
    assert second_results[0].summary["scribe_triggered"] is False
    assert second_results[0].summary["scribe_skip_reason"] == "duplicate_signal_signature"


def test_run_keeps_cycle_ok_when_scribe_runtime_fails(tmp_path: Path) -> None:
    class ScribeEngine(DummyEngine):
        def __init__(self, results, soul_db) -> None:
            super().__init__(results)
            self.soul_db = soul_db

    class FailingScribe:
        def draft_chronicle(self, db, title_hint="A Day in the Dream Engine", source_db_path=None):
            raise RuntimeError("scribe boom")

    soul_db = SqliteSoulDB(db_path=tmp_path / "soul.db")
    loop = AutonomousWakeupLoop(
        dream_engine=ScribeEngine(
            [
                _build_result(
                    _build_collision(
                        topic="scribe-fails",
                        friction_score=0.55,
                        should_convene_council=True,
                    )
                )
            ],
            soul_db,
        ),
        interval_seconds=0.0,
        sleep_func=lambda _: None,
        consolidate_every_cycles=0,
        scribe=FailingScribe(),
        scribe_status_path=tmp_path / "status" / "scribe_status_latest.json",
        scribe_state_path=tmp_path / "state" / "scribe_state.json",
    )

    results = loop.run(max_cycles=1, dream_kwargs={"limit": 1})

    assert results[0].status == "ok"
    assert results[0].summary["scribe_triggered"] is False
    assert results[0].summary["scribe_skip_reason"] == "scribe_runtime_failed"
    assert results[0].dream_result["scribe"]["error"]["message"] == "scribe boom"


def test_run_pauses_after_three_consecutive_failures() -> None:
    class FailingEngine:
        def __init__(self) -> None:
            self.calls = 0

        def run_cycle(self, **kwargs):
            self.calls += 1
            raise RuntimeError("boom")

    sleep_calls: list[float] = []
    loop = AutonomousWakeupLoop(
        dream_engine=FailingEngine(),
        interval_seconds=10.0,
        sleep_func=lambda seconds: sleep_calls.append(seconds),
        failure_threshold=3,
        failure_pause_seconds=3600.0,
        consolidate_every_cycles=0,
    )

    results = loop.run(max_cycles=4, dream_kwargs={"limit": 1})

    assert [result.status for result in results] == ["error", "error", "error", "error"]
    assert sleep_calls == [10.0, 10.0, 3600.0]
    assert results[2].summary["circuit_breaker_paused"] is True
    assert results[2].summary["failure_pause_seconds"] == 3600.0
    assert results[2].summary["consecutive_failure_count"] == 3
    assert results[3].summary["consecutive_failure_count"] == 1
    assert results[0].summary["error_type"] == "RuntimeError"
    assert results[0].summary["error_message"] == "boom"


def test_run_persists_runtime_session_state_across_invocations(tmp_path: Path) -> None:
    state_path = tmp_path / "dream_wakeup_state.json"

    first_loop = AutonomousWakeupLoop(
        dream_engine=DummyEngine(
            [
                _build_result(
                    _build_collision(
                        topic="first",
                        friction_score=0.4,
                        should_convene_council=False,
                    )
                )
            ]
        ),
        interval_seconds=0.0,
        sleep_func=lambda _: None,
        state_path=state_path,
    )
    first_results = first_loop.run(max_cycles=1, dream_kwargs={"limit": 1})

    second_loop = AutonomousWakeupLoop(
        dream_engine=DummyEngine(
            [
                _build_result(
                    _build_collision(
                        topic="second",
                        friction_score=0.6,
                        should_convene_council=True,
                    )
                )
            ]
        ),
        interval_seconds=0.0,
        sleep_func=lambda _: None,
        state_path=state_path,
    )
    second_results = second_loop.run(max_cycles=1, dream_kwargs={"limit": 1})

    persisted_state = json.loads(state_path.read_text(encoding="utf-8"))

    assert first_results[0].cycle == 1
    assert second_results[0].cycle == 2
    assert first_results[0].summary["session_resumed"] is False
    assert second_results[0].summary["session_resumed"] is True
    assert first_results[0].summary["session_id"] == second_results[0].summary["session_id"]
    assert persisted_state["next_cycle"] == 3
    assert persisted_state["last_status"] == "ok"
    assert persisted_state["consecutive_failures"] == 0


def test_run_resumes_consecutive_failures_from_persisted_state(tmp_path: Path) -> None:
    state_path = tmp_path / "dream_wakeup_state.json"
    sleep_calls: list[float] = []

    class FailingEngine:
        def run_cycle(self, **kwargs):
            raise RuntimeError("boom")

    first_loop = AutonomousWakeupLoop(
        dream_engine=FailingEngine(),
        interval_seconds=10.0,
        sleep_func=lambda seconds: sleep_calls.append(seconds),
        failure_threshold=3,
        failure_pause_seconds=3600.0,
        consolidate_every_cycles=0,
        state_path=state_path,
    )
    first_results = first_loop.run(max_cycles=2, dream_kwargs={"limit": 1})

    second_loop = AutonomousWakeupLoop(
        dream_engine=FailingEngine(),
        interval_seconds=10.0,
        sleep_func=lambda seconds: sleep_calls.append(seconds),
        failure_threshold=3,
        failure_pause_seconds=3600.0,
        consolidate_every_cycles=0,
        state_path=state_path,
    )
    second_results = second_loop.run(max_cycles=2, dream_kwargs={"limit": 1})
    persisted_state = json.loads(state_path.read_text(encoding="utf-8"))

    assert [result.cycle for result in first_results] == [1, 2]
    assert [result.cycle for result in second_results] == [3, 4]
    assert first_results[1].summary["consecutive_failure_count"] == 2
    assert second_results[0].summary["consecutive_failure_count"] == 3
    assert second_results[0].summary["circuit_breaker_paused"] is True
    assert second_results[1].summary["consecutive_failure_count"] == 1
    assert second_results[0].summary["session_resumed"] is True
    assert sleep_calls == [10.0, 3600.0]
    assert persisted_state["consecutive_failures"] == 1
