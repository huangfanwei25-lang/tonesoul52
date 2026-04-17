"""Tests for tonesoul.runtime_adapter — the session load/commit bridge."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from tonesoul.runtime_adapter import (
    CommitConcurrencyError,
    GovernancePosture,
    SessionTrace,
    acknowledge_observer_cursor,
    apply_subject_refresh,
    claim_task,
    commit,
    decay_tensions,
    drift_baseline,
    get_observer_cursor,
    list_active_claims,
    list_checkpoints,
    list_compactions,
    list_perspectives,
    list_routing_events,
    list_subject_snapshots,
    load,
    r_memory_packet,
    record_routing_event,
    release_task_claim,
    route_r_memory_signal,
    summary,
    update_soul_integral,
    write_checkpoint,
    write_compaction,
    write_perspective,
    write_routed_signal,
    write_subject_snapshot,
)


@pytest.fixture()
def tmp_state(tmp_path: Path) -> Path:
    return tmp_path / "governance_state.json"


@pytest.fixture()
def tmp_traces(tmp_path: Path) -> Path:
    return tmp_path / "traces.jsonl"


# ── load() ──────────────────────────────────────────────────────


def test_load_missing_file_returns_default(tmp_path: Path) -> None:
    posture = load(state_path=tmp_path / "nonexistent.json")
    assert posture.session_count == 0
    assert posture.soul_integral == 0.0
    assert len(posture.active_vows) == 0


def test_load_existing_file(tmp_state: Path) -> None:
    state = {
        "version": "0.1.0",
        "last_updated": "2026-03-25T00:00:00+00:00",
        "soul_integral": 1.5,
        "tension_history": [],
        "active_vows": [{"id": "v1", "content": "test vow", "created": "2026-03-25"}],
        "aegis_vetoes": [],
        "baseline_drift": {"caution_bias": 0.6, "innovation_bias": 0.4, "autonomy_level": 0.3},
        "session_count": 5,
    }
    tmp_state.write_text(json.dumps(state), encoding="utf-8")
    posture = load(state_path=tmp_state)
    assert posture.session_count == 5
    assert posture.soul_integral == 1.5
    assert len(posture.active_vows) == 1


# ── commit() ────────────────────────────────────────────────────


def test_commit_increments_session_count(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(agent="test", key_decisions=["did a thing"])
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    assert posture.session_count == 1
    assert set(posture.risk_posture) >= {"score", "level", "recommended_action"}

    trace2 = SessionTrace(agent="test", key_decisions=["did another thing"])
    posture2 = commit(trace2, state_path=tmp_state, traces_path=tmp_traces)
    assert posture2.session_count == 2
    assert set(posture2.risk_posture) >= {"score", "level", "recommended_action"}


def test_commit_writes_trace_jsonl(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(
        agent="claude",
        key_decisions=["test"],
        council_dossier={
            "dossier_version": "v1",
            "final_verdict": "approve",
            "confidence_posture": "moderate",
            "coherence_score": 0.71,
            "dissent_ratio": 0.0,
            "minority_report": [],
            "vote_summary": [],
            "deliberation_mode": "standard_council",
            "change_of_position": [],
            "evidence_refs": [],
            "grounding_summary": {
                "has_ungrounded_claims": False,
                "total_evidence_sources": 0,
            },
            "confidence_decomposition": {
                "calibration_status": "descriptive_only",
                "agreement_score": 1.0,
                "coverage_posture": "partial",
                "distinct_perspectives": 2,
                "evidence_density": 0.0,
                "evidence_posture": "none",
                "grounding_posture": "not_required",
                "adversarial_posture": "not_tested",
            },
            "evolution_suppression_flag": True,
            "opacity_declaration": "partially_observable",
        },
    )
    commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    lines = tmp_traces.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["agent"] == "claude"
    assert "test" in record["key_decisions"]
    assert record["council_dossier"]["final_verdict"] == "approve"
    assert record["council_dossier"]["confidence_posture"] == "moderate"
    assert (
        record["council_dossier"]["confidence_decomposition"]["calibration_status"]
        == "descriptive_only"
    )
    assert record["council_dossier"]["evolution_suppression_flag"] is True


def test_commit_merges_tension_events(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(
        agent="test",
        tension_events=[{"topic": "scope creep", "severity": 0.6}],
        key_decisions=["kept it small"],
    )
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    assert len(posture.tension_history) == 1
    assert posture.tension_history[0]["topic"] == "scope creep"


def test_commit_creates_vow(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(
        agent="test",
        vow_events=[{"vow_id": "v-new", "action": "created", "detail": "always test"}],
        key_decisions=["added vow"],
    )
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    ids = [v["id"] for v in posture.active_vows]
    assert "v-new" in ids


def test_commit_retires_vow(tmp_state: Path, tmp_traces: Path) -> None:
    # Seed with a vow
    state = {
        "version": "0.1.0",
        "last_updated": "2026-03-25T00:00:00+00:00",
        "soul_integral": 0.0,
        "tension_history": [],
        "active_vows": [{"id": "v-old", "content": "obsolete", "created": "2026-01-01"}],
        "aegis_vetoes": [],
        "baseline_drift": {"caution_bias": 0.5, "innovation_bias": 0.5, "autonomy_level": 0.5},
        "session_count": 0,
    }
    tmp_state.write_text(json.dumps(state), encoding="utf-8")

    trace = SessionTrace(
        agent="test",
        vow_events=[{"vow_id": "v-old", "action": "retired"}],
        key_decisions=["retired old vow"],
    )
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)
    ids = [v["id"] for v in posture.active_vows]
    assert "v-old" not in ids


def test_commit_blocked_trace_does_not_mutate_state(
    tmp_state: Path,
    tmp_traces: Path,
    monkeypatch,
) -> None:
    state = {
        "version": "0.1.0",
        "last_updated": "2026-03-25T00:00:00+00:00",
        "soul_integral": 0.0,
        "tension_history": [],
        "active_vows": [],
        "aegis_vetoes": [],
        "baseline_drift": {"caution_bias": 0.5, "innovation_bias": 0.5, "autonomy_level": 0.5},
        "session_count": 2,
    }
    tmp_state.write_text(json.dumps(state), encoding="utf-8")

    class _BlockedShield:
        @classmethod
        def load(cls, store=None):
            return cls()

        def protect_trace(self, trace_dict, agent_id):
            return trace_dict, SimpleNamespace(
                severity="blocked",
                violations=["prompt_injection"],
            )

        def save(self, store) -> None:
            return None

    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _BlockedShield)

    trace = SessionTrace(
        agent="test",
        tension_events=[{"topic": "scope creep", "severity": 0.9}],
        vow_events=[{"vow_id": "v-new", "action": "created", "detail": "should never land"}],
    )
    posture = commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    assert posture.session_count == 2
    assert posture.tension_history == []
    assert posture.active_vows == []
    assert len(posture.aegis_vetoes) == 1
    assert posture.aegis_vetoes[0]["type"] == "memory_poisoning"
    assert not tmp_traces.exists()

    saved = json.loads(tmp_state.read_text(encoding="utf-8"))
    assert saved["session_count"] == 2
    assert saved["tension_history"] == []
    assert saved["active_vows"] == []
    assert len(saved["aegis_vetoes"]) == 1


def test_commit_rebuilds_zone_registry_with_same_explicit_paths(
    tmp_state: Path,
    tmp_traces: Path,
    monkeypatch,
) -> None:
    calls = {}

    def fake_rebuild_and_save(
        traces_path=None,
        governance_path=None,
        registry_path=None,
        store=None,
    ):
        calls["traces_path"] = traces_path
        calls["governance_path"] = governance_path
        calls["registry_path"] = registry_path
        calls["store"] = store
        return None

    monkeypatch.setattr("tonesoul.zone_registry.rebuild_and_save", fake_rebuild_and_save)

    trace = SessionTrace(agent="test", key_decisions=["rebuild zones"])
    commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    assert calls["store"] is None
    assert calls["traces_path"] == tmp_traces
    assert calls["governance_path"] == tmp_state
    assert calls["registry_path"] is not None
    assert calls["registry_path"].name == "zone_registry.json"


def test_commit_raises_when_canonical_lock_is_unavailable(
    tmp_state: Path,
    tmp_traces: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "tonesoul.backends.file_store.FileStore.acquire_commit_lock",
        lambda self, owner, ttl_seconds=30: None,
    )

    trace = SessionTrace(agent="codex", key_decisions=["should conflict"])
    with pytest.raises(CommitConcurrencyError):
        commit(trace, state_path=tmp_state, traces_path=tmp_traces)


def test_commit_lock_file_is_released_after_success(tmp_state: Path, tmp_traces: Path) -> None:
    trace = SessionTrace(agent="codex", key_decisions=["release lock"])
    commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    lock_path = tmp_state.parent / ".aegis" / "commit.lock.json"
    assert not lock_path.exists()


def test_commit_lock_file_is_released_after_state_write_failure(
    tmp_state: Path,
    tmp_traces: Path,
    monkeypatch,
) -> None:
    from tonesoul.backends.file_store import FileStore

    def _boom(self, data) -> None:
        raise RuntimeError("boom in set_state")

    monkeypatch.setattr(FileStore, "set_state", _boom)

    trace = SessionTrace(agent="codex", key_decisions=["fail after lock"])
    with pytest.raises(RuntimeError, match="boom in set_state"):
        commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    lock_path = tmp_state.parent / ".aegis" / "commit.lock.json"
    assert not lock_path.exists()


def test_r_memory_packet_exposes_runtime_dominance_and_recent_trace(
    tmp_state: Path,
    tmp_traces: Path,
) -> None:
    trace = SessionTrace(
        agent="codex",
        topics=["runtime", "redis"],
        tension_events=[{"topic": "safety vs speed", "severity": 0.7}],
        key_decisions=["emit packet"],
        council_dossier={
            "dossier_version": "v1",
            "final_verdict": "approve",
            "confidence_posture": "contested",
            "coherence_score": 0.62,
            "dissent_ratio": 0.35,
            "minority_report": [
                {
                    "perspective": "critic",
                    "decision": "concern",
                    "confidence": 0.75,
                    "reasoning": "migration path missing",
                    "evidence": ["docs/spec.md"],
                }
            ],
            "vote_summary": [],
            "deliberation_mode": "standard_council",
            "change_of_position": [],
            "evidence_refs": ["docs/spec.md"],
            "grounding_summary": {
                "has_ungrounded_claims": False,
                "total_evidence_sources": 1,
            },
            "confidence_decomposition": {
                "calibration_status": "descriptive_only",
                "agreement_score": 0.5,
                "coverage_posture": "partial",
                "distinct_perspectives": 2,
                "evidence_density": 0.5,
                "evidence_posture": "moderate",
                "grounding_posture": "not_required",
                "adversarial_posture": "survived_dissent",
            },
            "evolution_suppression_flag": True,
            "opacity_declaration": "partially_observable",
        },
    )
    commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_state,
        traces_path=tmp_traces,
        zones_path=tmp_traces.parent / "zone_registry.json",
        claims_path=tmp_traces.parent / "task_claims.json",
        perspectives_path=tmp_traces.parent / "perspectives.json",
        checkpoints_path=tmp_traces.parent / "checkpoints.json",
        compactions_path=tmp_traces.parent / "compacted.json",
        subject_snapshots_path=tmp_traces.parent / "subject_snapshots.json",
        observer_cursors_path=tmp_traces.parent / "observer_cursors.json",
    )
    route = route_r_memory_signal(
        agent_id="codex",
        summary="resume packet cleanup",
        pending_paths=["tonesoul/diagnose.py"],
        next_action="finish delta formatting",
    )
    record_routing_event(route, action="preview", written=False, store=store)
    posture = load(state_path=tmp_state)
    packet = r_memory_packet(posture=posture, store=store, trace_limit=3, visitor_limit=3)

    assert packet["contract_version"] == "v1"
    assert packet["backend"] == "file"
    assert packet["dominance_order"][0] == "hard_constraints"
    assert packet["session_end_order"][3] == "persist_governance_posture"
    assert packet["trace_integrity"]["hash_chain_required"] is True
    assert packet["parallel_lanes"]["canonical_commit_serialized"] is True
    assert packet["parallel_lanes"]["perspectives_surface"] == "ts:perspectives:{agent_id}"
    assert packet["parallel_lanes"]["compaction_surface"] == "ts:compacted"
    assert packet["parallel_lanes"]["subject_snapshot_surface"] == "ts:subject_snapshots"
    assert packet["parallel_lanes"]["observer_cursor_surface"] == "ts:observer_cursors:{agent_id}"
    assert packet["parallel_lanes"]["routing_events_surface"] == "ts:routing_events"
    assert (
        "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"
        in packet["canonical_sources"]
    )
    assert packet["posture"]["session_count"] == 1
    assert set(packet["posture"]["risk_posture"]) >= {"score", "level", "recommended_action"}
    assert packet["posture"]["freshness_hours"] >= 0.0
    assert "project_memory_summary" in packet
    assert "summary_text" in packet["project_memory_summary"]
    assert "repo_progress" in packet["project_memory_summary"]
    assert packet["project_memory_summary"]["routing_summary"]["total_events"] == 1
    assert packet["project_memory_summary"]["routing_summary"]["dominant_surface"] == "checkpoint"
    assert packet["project_memory_summary"]["subject_refresh"]["status"] == "no_snapshot"
    assert packet["project_memory_summary"]["subject_refresh"]["refresh_recommended"] is False
    assert packet["coordination_mode"]["mode"] == "file-backed"
    assert packet["coordination_mode"]["live_surfaces_available"] is False
    assert packet["coordination_mode"]["surface_modes"]["claims"] == "file-backed"
    assert packet["coordination_mode"]["surface_modes"]["visitors"] == "unavailable"
    assert packet["coordination_mode"]["launch_default_mode"] == "file-backed"
    assert packet["coordination_mode"]["launch_alignment"] == "aligned_with_launch_default"
    assert "launch-default coordination story" in packet["coordination_mode"]["launch_posture_note"]
    assert packet["recent_routing_events"][0]["surface"] == "checkpoint"
    assert packet["recent_routing_events"][0]["freshness_hours"] >= 0.0
    assert (
        packet["recent_traces"][0]["council_dossier_summary"]["confidence_posture"] == "contested"
    )
    assert packet["recent_traces"][0]["council_dossier_summary"]["has_minority_report"] is True
    assert (
        packet["recent_traces"][0]["council_dossier_summary"]["confidence_decomposition"][
            "adversarial_posture"
        ]
        == "survived_dissent"
    )
    assert (
        packet["recent_traces"][0]["council_dossier_summary"]["evolution_suppression_flag"] is True
    )
    assert (
        "Descriptive agreement record only"
        in packet["recent_traces"][0]["council_dossier_summary"]["realism_note"]
    )
    assert packet["recent_traces"][0]["freshness_hours"] >= 0.0
    assert packet["operator_guidance"]["backend_mode"] == "file"
    assert packet["operator_guidance"]["session_start"][0].startswith(
        "python scripts/start_agent_session.py --agent"
    )
    assert packet["operator_guidance"]["session_start"][1].startswith("python -m tonesoul.diagnose")
    assert packet["operator_guidance"]["session_start"][2].startswith(
        "python scripts/run_r_memory_packet.py --agent"
    )
    assert packet["operator_guidance"]["preflight_chain"]["present"] is True
    assert packet["operator_guidance"]["preflight_chain"]["stages"][0]["name"] == (
        "shared_edit_path_overlap"
    )
    assert packet["operator_guidance"]["preflight_chain"]["stages"][2]["command"].startswith(
        "python scripts/run_task_board_preflight.py --agent"
    )
    assert packet["operator_guidance"]["preflight_chain"]["hooks"][0]["status"] == "available"
    assert (
        packet["operator_guidance"]["preflight_chain"]["current_recommendation"]["present"] is False
    )
    assert packet["operator_guidance"]["session_end"][0].startswith(
        "python scripts/end_agent_session.py --agent"
    )
    assert "--closeout-status complete" in packet["operator_guidance"]["session_end"][0]
    assert packet["operator_guidance"]["session_end"][1].startswith(
        "python scripts/end_agent_session.py --agent"
    )
    assert "--closeout-status partial" in packet["operator_guidance"]["session_end"][1]
    assert packet["operator_guidance"]["session_end"][2].startswith(
        "python scripts/save_checkpoint.py"
    )
    assert "claim" in packet["operator_guidance"]["coordination_commands"]
    assert "signal_router" in packet["operator_guidance"]["coordination_commands"]
    assert "subject_snapshot" in packet["operator_guidance"]["coordination_commands"]
    assert "apply_subject_refresh" in packet["operator_guidance"]["coordination_commands"]
    assert "checkpoint or compaction" in packet["operator_guidance"]["completion_rule"]
    assert (
        "omit pending paths and next_action when the session truly ends cleanly"
        in packet["operator_guidance"]["completion_rule"]
    )
    assert packet["consumer_contract"]["present"] is True
    assert packet["consumer_contract"]["required_read_order"][0]["surface"] == "readiness"
    assert (
        packet["consumer_contract"]["priority_misread_guard"]["name"]
        == "observer_stable_not_verified"
    )
    assert (
        packet["operator_guidance"]["consumer_contract"]["source_precedence_summary"]
        == packet["consumer_contract"]["source_precedence_summary"]
    )
    assert packet["surface_versioning"]["present"] is True
    assert packet["surface_versioning"]["runtime_surfaces"][2]["surface"] == "r_memory_packet"
    assert (
        packet["operator_guidance"]["surface_versioning"]["consumer_shells"][0]["consumer"]
        == "codex_cli"
    )
    assert any(
        reminder.startswith("Council realism: Descriptive agreement record only")
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Consumer contract: consumer_order=")
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert packet["recent_traces"][0]["agent"] == "codex"
    assert packet["recent_traces"][0]["topics"] == ["runtime", "redis"]
    assert packet["recent_checkpoints"] == []


def test_record_routing_event_persists_telemetry_summary(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / "task_claims.json",
    )

    route = route_r_memory_signal(
        agent_id="codex",
        summary="force a compaction lane despite checkpoint cues",
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="review lane choice",
        carry_forward=["preserve the observer baseline"],
        prefer_surface="compaction",
    )

    event = record_routing_event(route, action="write", written=True, store=store)
    events = list_routing_events(store=store)

    assert event["surface"] == "compaction"
    assert event["forced"] is True
    assert event["overlap"] is True
    assert event["misroute_signal"] is True
    assert events[0]["event_id"] == event["event_id"]


def test_task_claims_prevent_collisions_and_appear_in_packet(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / "task_claims.json",
        subject_snapshots_path=tmp_path / "subject_snapshots.json",
    )

    first = claim_task(
        "launch-world-dedupe",
        agent_id="codex",
        summary="dedupe redis refresh",
        paths=["scripts/launch_world.py"],
        store=store,
    )
    second = claim_task(
        "launch-world-dedupe",
        agent_id="gemini",
        summary="should conflict",
        paths=["scripts/launch_world.py"],
        store=store,
    )

    assert first["ok"] is True
    assert second["ok"] is False

    claims = list_active_claims(store=store)
    assert len(claims) == 1
    assert claims[0]["agent"] == "codex"

    packet = r_memory_packet(posture=GovernancePosture(), store=store)
    assert packet["active_claims"][0]["task_id"] == "launch-world-dedupe"
    assert packet["active_claims"][0]["agent"] == "codex"
    assert packet["active_claims"][0]["freshness_hours"] >= 0.0

    released = release_task_claim("launch-world-dedupe", agent_id="codex", store=store)
    assert released["ok"] is True
    assert list_active_claims(store=store) == []


def test_perspectives_and_checkpoints_use_noncanonical_lanes(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / "task_claims.json",
        perspectives_path=tmp_path / "perspectives.json",
        checkpoints_path=tmp_path / "checkpoints.json",
        commit_lock_path=tmp_path / "commit.lock.json",
        subject_snapshots_path=tmp_path / "subject_snapshots.json",
    )

    perspective = write_perspective(
        "codex",
        session_id="sess-42",
        summary="guardian leans cautious, analyst wants evidence",
        stance="divergent_but_productive",
        tensions=["safety vs speed"],
        proposed_drift={"caution_bias": 0.58},
        proposed_vows=["trace-before-promotion"],
        evidence_refs=["docs/architecture/TONESOUL_MULTI_AGENT_SEMANTIC_FIELD_CONTRACT.md"],
        store=store,
    )
    checkpoint = write_checkpoint(
        "cp-42",
        agent_id="codex",
        session_id="sess-42",
        summary="mutex implemented, field lane pending",
        pending_paths=["tonesoul/runtime_adapter.py", "tonesoul/backends/redis_store.py"],
        next_action="add field synthesis evaluator",
        store=store,
    )

    assert perspective["agent"] == "codex"
    assert checkpoint["checkpoint_id"] == "cp-42"

    perspectives = list_perspectives(store=store)
    checkpoints = list_checkpoints(store=store)

    assert perspectives[0]["stance"] == "divergent_but_productive"
    assert perspectives[0]["proposed_vows"] == ["trace-before-promotion"]
    assert checkpoints[0]["next_action"] == "add field synthesis evaluator"


def test_compactions_use_noncanonical_resumability_lane(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / "task_claims.json",
        compactions_path=tmp_path / "compacted.json",
        subject_snapshots_path=tmp_path / "subject_snapshots.json",
    )

    first = write_compaction(
        agent_id="codex",
        session_id="sess-42",
        summary="Session condensed into a resumability handoff.",
        carry_forward=["keep canonical commit serialized"],
        pending_paths=["scripts/gateway.py"],
        evidence_refs=[
            "docs/architecture/TONESOUL_RUNTIME_COMPACTION_AND_GAMIFICATION_CONTRACT.md"
        ],
        next_action="surface compaction in the packet only",
        limit=2,
        store=store,
    )
    second = write_compaction(
        agent_id="gemini",
        session_id="sess-43",
        summary="Second summary should appear first.",
        carry_forward=["do not mutate governance posture"],
        pending_paths=["apps/dashboard/world.html"],
        next_action="use packet consumption in UI",
        limit=2,
        store=store,
    )

    compactions = list_compactions(store=store, n=5)

    assert first["agent"] == "codex"
    assert second["agent"] == "gemini"
    assert len(compactions) == 2
    assert compactions[0]["summary"] == "Second summary should appear first."
    assert compactions[1]["carry_forward"] == ["keep canonical commit serialized"]

    packet = r_memory_packet(posture=GovernancePosture(), store=store)
    assert packet["recent_compactions"][0]["agent"] == "gemini"
    assert packet["recent_compactions"][1]["agent"] == "codex"
    assert packet["recent_compactions"][0]["freshness_hours"] >= 0.0
    assert packet["recent_compactions"][0]["closeout"]["status"] == "partial"
    assert "project_memory_summary" in packet
    assert packet["project_memory_summary"]["next_actions"][0] == "use packet consumption in UI"
    assert "repo_progress" in packet["project_memory_summary"]
    assert (
        "Prefer recent_compactions and project_memory_summary before older recent_traces."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "Latest compaction closeout is partial; do not read the handoff as completed work."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "Use --path and --next-action only for unresolved carry-forward; omit them when the session truly closes cleanly."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert packet["operator_guidance"]["session_end"][4].startswith(
        "python scripts/run_task_claim.py release"
    )


def test_subject_snapshots_surface_durable_subject_anchor(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / ".aegis" / "task_claims.json",
        checkpoints_path=tmp_path / ".aegis" / "checkpoints.json",
        compactions_path=tmp_path / ".aegis" / "compacted.json",
        subject_snapshots_path=tmp_path / "subject_snapshots.json",
        routing_events_path=tmp_path / ".aegis" / "routing_events.json",
    )

    snapshot = write_subject_snapshot(
        agent_id="codex",
        session_id="sess-44",
        summary="Operate as a packet-first runtime steward with explicit boundaries.",
        stable_vows=["never smuggle theory into runtime truth"],
        durable_boundaries=["do not edit protected human-managed files"],
        decision_preferences=["prefer packet before broad repo scan"],
        verified_routines=["end sessions with checkpoint or compaction before release"],
        active_threads=["subject snapshot hardening"],
        evidence_refs=["docs/AI_QUICKSTART.md"],
        refresh_signals=["refresh when durable boundaries change"],
        store=store,
    )
    write_checkpoint(
        "cp-refresh",
        agent_id="codex",
        session_id="sess-45",
        summary="Packet-first rollout remains active.",
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="refresh active threads after compaction review",
        store=store,
    )
    write_compaction(
        agent_id="codex",
        session_id="sess-45",
        summary="Runtime adapter and redis coordination remain active threads.",
        carry_forward=["keep packet-first session cadence stable"],
        pending_paths=["tonesoul/runtime_adapter.py"],
        evidence_refs=["docs/AI_QUICKSTART.md"],
        next_action="refresh subject snapshot active threads",
        store=store,
    )
    route = route_r_memory_signal(
        agent_id="codex",
        summary="checkpoint still dominates bounded hot-state notes",
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="refresh subject threads",
    )
    record_routing_event(route, action="preview", written=False, store=store)
    store.append_trace(
        SessionTrace(
            agent="codex",
            session_id="sess-45",
            timestamp="2026-03-28T00:06:00+00:00",
            topics=["runtime_adapter", "redis"],
            key_decisions=["refresh active threads after compaction review"],
        ).to_dict()
    )

    snapshots = list_subject_snapshots(store=store, n=5)
    packet = r_memory_packet(posture=GovernancePosture(), store=store)

    assert snapshot["agent"] == "codex"
    assert snapshots[0]["summary"].startswith("Operate as a packet-first runtime steward")
    assert packet["recent_subject_snapshots"][0]["snapshot_id"] == snapshot["snapshot_id"]
    assert packet["recent_subject_snapshots"][0]["freshness_hours"] >= 0.0
    assert (
        packet["project_memory_summary"]["subject_anchor"]["summary"]
        == "Operate as a packet-first runtime steward with explicit boundaries."
    )
    working_style_anchor = packet["project_memory_summary"]["working_style_anchor"]
    assert working_style_anchor["summary"].startswith("prefs=prefer packet before broad repo scan")
    assert working_style_anchor["decision_preferences"] == ["prefer packet before broad repo scan"]
    assert working_style_anchor["verified_routines"] == [
        "end sessions with checkpoint or compaction before release"
    ]
    assert working_style_anchor["guardrail_boundaries"] == [
        "do not edit protected human-managed files"
    ]
    assert working_style_anchor["receiver_posture"] == "advisory_apply_not_promote"
    assert "render-layer noise" in working_style_anchor["render_caveat"]
    working_style_observability = packet["project_memory_summary"]["working_style_observability"]
    assert working_style_observability["status"] == "reinforced"
    assert working_style_observability["drift_risk"] == "low"
    assert working_style_observability["reinforced_item_count"] == 2
    assert (
        "decision_preferences: prefer packet before broad repo scan"
        in working_style_observability["reinforced_items"]
    )
    assert (
        "verified_routines: end sessions with checkpoint or compaction before release"
        in working_style_observability["reinforced_items"]
    )
    working_style_import_limits = packet["project_memory_summary"]["working_style_import_limits"]
    assert working_style_import_limits["apply_posture"] == "bounded_default"
    assert any(item.startswith("scan_order:") for item in working_style_import_limits["safe_apply"])
    assert any(
        item.startswith("durable_identity:")
        for item in working_style_import_limits["must_not_import"]
    )
    evidence_readout = packet["project_memory_summary"]["evidence_readout_posture"]
    assert evidence_readout["classification_counts"]["tested"] == 2
    assert evidence_readout["classification_counts"]["runtime_present"] == 1
    assert any(
        lane["lane"] == "continuity_effectiveness" and lane["classification"] == "runtime_present"
        for lane in evidence_readout["lanes"]
    )
    assert any(
        lane["lane"] == "council_decision_quality" and lane["classification"] == "descriptive_only"
        for lane in evidence_readout["lanes"]
    )
    launch_claim_posture = packet["project_memory_summary"]["launch_claim_posture"]
    assert launch_claim_posture["current_tier"] == "collaborator_beta"
    assert launch_claim_posture["next_target_tier"] == "public_launch"
    assert launch_claim_posture["public_launch_ready"] is False
    assert any(
        item.startswith("coordination_backend=file-backed:")
        for item in launch_claim_posture["safe_now"]
    )
    assert any(
        item["claim"] == "continuity_effectiveness"
        and item["current_classification"] == "runtime_present"
        for item in launch_claim_posture["blocked_overclaims"]
    )
    assert any(
        item["claim"] == "live_shared_memory"
        and item["current_classification"] == "not_launch_default"
        for item in launch_claim_posture["blocked_overclaims"]
    )
    launch_health_trend_posture = packet["project_memory_summary"]["launch_health_trend_posture"]
    assert launch_health_trend_posture["current_state"]["current_tier"] == "collaborator_beta"
    assert launch_health_trend_posture["current_state"]["launch_default_mode"] == "file-backed"
    assert any(
        item["metric"] == "coordination_backend_alignment" and item["classification"] == "trendable"
        for item in launch_health_trend_posture["metric_classes"]
    )
    assert any(
        item["metric"] == "public_launch_forecast" and item["classification"] == "forecast_later"
        for item in launch_health_trend_posture["metric_classes"]
    )
    assert (
        launch_health_trend_posture["trend_watch_cues"][0]["metric"]
        == "coordination_backend_alignment"
    )
    assert (
        launch_health_trend_posture["forecast_blockers"][0]["metric"] == "continuity_effectiveness"
    )
    assert launch_health_trend_posture["operator_actions"][2] == (
        "Do not emit predictive launch numbers or success probabilities."
    )
    internal_state_observability = packet["project_memory_summary"]["internal_state_observability"]
    assert internal_state_observability["current_state"]["coordination_strain"] == "low"
    assert internal_state_observability["current_state"]["continuity_drift"] == "low"
    assert internal_state_observability["current_state"]["deliberation_conflict"] == "clear"
    assert internal_state_observability["current_state"]["stop_reason_pressure"] == "medium"
    assert internal_state_observability["pressure_watch_cues"][0]["signal"] == "coordination_strain"
    assert (
        internal_state_observability["pressure_watch_cues"][2]["signal"] == "stop_reason_pressure"
    )
    assert internal_state_observability["operator_actions"][1] == (
        "Keep continuity cues subordinate to current runtime truth."
    )
    assert packet["project_memory_summary"]["subject_refresh"]["status"] == "refresh_candidate"
    assert packet["project_memory_summary"]["subject_refresh"]["refresh_recommended"] is True
    active_thread_guidance = next(
        item
        for item in packet["project_memory_summary"]["subject_refresh"]["field_guidance"]
        if item["field"] == "active_threads"
    )
    assert active_thread_guidance["action"] == "may_refresh_directly"
    assert "runtime_adapter" in active_thread_guidance["candidate_values"]
    assert packet["project_memory_summary"]["subject_refresh"]["recommended_command"].startswith(
        "python scripts/apply_subject_refresh.py --agent"
    )
    assert packet["coordination_mode"]["mode"] == "file-backed"
    assert packet["coordination_mode"]["delta_feed_enabled"] is False
    assert packet["coordination_mode"]["launch_default_mode"] == "file-backed"
    assert (
        "A recent subject snapshot is visible; treat it as durable working identity, but still non-canonical."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "A working-style playbook is visible; apply it as advisory workflow, not as durable identity or policy."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "Working-style: Preference: prefer packet before broad repo scan"
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "Working-style: Routine: end sessions with checkpoint or compaction before release"
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "Working-style import stays bounded to scan order, evidence handling, prompt shape, session cadence, and render interpretation."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith(
            "Evidence posture: evidence=tested(session_control_and_handoff,council_mechanics)"
        )
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Launch claim posture: launch_claims=current:collaborator_beta")
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Launch health posture: launch_health current=collaborator_beta")
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Internal state posture: internal_state coordination=low")
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Receiver posture: receiver_parity council=unflagged")
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert any(
        reminder.startswith("Receiver ladder: ack is safe visibility only")
        for reminder in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "Subject-refresh heuristics found low-risk updates; review subject_refresh before writing the next snapshot."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "File-backed coordination is not push-driven; re-read packet before touching shared paths after longer work or after another agent reports progress."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert (
        "Launch coordination default: Current runtime matches the launch-default coordination story: file-backed continuity with receiver guards."
        in packet["operator_guidance"]["current_reminders"]
    )


def test_apply_subject_refresh_updates_active_threads_when_compaction_backed_and_clean(
    tmp_path: Path,
) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / ".aegis" / "task_claims.json",
        compactions_path=tmp_path / ".aegis" / "compacted.json",
        subject_snapshots_path=tmp_path / ".aegis" / "subject_snapshots.json",
        routing_events_path=tmp_path / ".aegis" / "routing_events.json",
    )

    original_snapshot = write_subject_snapshot(
        agent_id="codex",
        session_id="sess-44",
        summary="Operate as a packet-first runtime steward with explicit boundaries.",
        stable_vows=["never smuggle theory into runtime truth"],
        durable_boundaries=["do not edit protected human-managed files"],
        decision_preferences=["prefer packet before broad repo scan"],
        verified_routines=["end sessions with checkpoint or compaction before release"],
        active_threads=["subject snapshot hardening"],
        evidence_refs=["docs/AI_QUICKSTART.md"],
        refresh_signals=["refresh when durable boundaries change"],
        store=store,
    )
    store.append_trace(
        SessionTrace(
            agent="codex",
            session_id="sess-45",
            timestamp="2026-03-28T00:06:00+00:00",
            topics=["runtime_adapter", "redis"],
            key_decisions=["refresh active threads after compaction review"],
        ).to_dict()
    )
    compaction = write_compaction(
        agent_id="codex",
        session_id="sess-45",
        summary="Runtime adapter and redis coordination remain active threads.",
        carry_forward=["keep packet-first session cadence stable"],
        pending_paths=["tonesoul/runtime_adapter.py"],
        evidence_refs=["docs/AI_QUICKSTART.md"],
        next_action="refresh subject snapshot active threads",
        store=store,
    )

    packet = r_memory_packet(posture=GovernancePosture(), store=store)

    assert packet["project_memory_summary"]["subject_refresh"]["recommended_command"].startswith(
        "python scripts/apply_subject_refresh.py --agent"
    )

    result = apply_subject_refresh(
        agent_id="codex",
        field="active_threads",
        summary="Refresh bounded active threads from clean compaction-backed evidence.",
        session_id="sess-45",
        source="test",
        refresh_signals=["manual review complete"],
        store=store,
    )

    assert result["ok"] is True
    assert result["reason"] == "applied"
    assert result["candidate_values"] == ["runtime_adapter", "redis"]
    applied = result["applied_snapshot"]
    assert applied is not None
    assert applied["summary"].startswith("Refresh bounded active threads")
    assert applied["stable_vows"] == original_snapshot["stable_vows"]
    assert applied["durable_boundaries"] == original_snapshot["durable_boundaries"]
    assert applied["decision_preferences"] == original_snapshot["decision_preferences"]
    assert applied["verified_routines"] == original_snapshot["verified_routines"]
    assert applied["active_threads"] == ["subject snapshot hardening", "runtime_adapter", "redis"]
    assert f"compaction:{compaction['compaction_id']}" in applied["evidence_refs"]
    assert "manual review complete" in applied["refresh_signals"]
    assert "active_threads compaction-backed refresh applied" in applied["refresh_signals"]

    snapshots = list_subject_snapshots(store=store, n=5)
    assert snapshots[0]["snapshot_id"] == applied["snapshot_id"]
    assert snapshots[1]["snapshot_id"] == original_snapshot["snapshot_id"]


def test_apply_subject_refresh_rejects_when_promotion_hazards_are_present(
    tmp_path: Path,
) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / ".aegis" / "task_claims.json",
        compactions_path=tmp_path / ".aegis" / "compacted.json",
        subject_snapshots_path=tmp_path / ".aegis" / "subject_snapshots.json",
        routing_events_path=tmp_path / ".aegis" / "routing_events.json",
    )

    write_subject_snapshot(
        agent_id="codex",
        session_id="sess-44",
        summary="Operate as a packet-first runtime steward with explicit boundaries.",
        stable_vows=["never smuggle theory into runtime truth"],
        durable_boundaries=["do not edit protected human-managed files"],
        decision_preferences=["prefer packet before broad repo scan"],
        verified_routines=["end sessions with checkpoint or compaction before release"],
        active_threads=["subject snapshot hardening"],
        store=store,
    )
    store.append_trace(
        SessionTrace(
            agent="codex",
            session_id="sess-45",
            timestamp="2026-03-28T00:06:00+00:00",
            topics=["runtime_adapter", "redis"],
            key_decisions=["refresh active threads after compaction review"],
        ).to_dict()
    )
    write_compaction(
        agent_id="codex",
        session_id="sess-45",
        summary="Runtime adapter and redis coordination remain active threads.",
        carry_forward=["keep packet-first session cadence stable"],
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="refresh subject snapshot active threads",
        store=store,
    )
    claim_task(
        "runtime-lane",
        agent_id="claude",
        summary="hold the runtime lane",
        paths=["tonesoul/runtime_adapter.py"],
        store=store,
    )

    result = apply_subject_refresh(
        agent_id="codex",
        field="active_threads",
        summary="Do not apply when hazards remain visible.",
        session_id="sess-45",
        source="test",
        store=store,
    )

    assert result["ok"] is False
    assert result["reason"] == "promotion_hazards_present"
    assert result["applied_snapshot"] is None
    assert (
        "Do not promote active claims into durable identity"
        in result["subject_refresh"]["promotion_hazards"][0]
    )


def test_apply_subject_refresh_rejects_recycled_carry_forward_without_new_evidence(
    tmp_path: Path,
) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / ".aegis" / "task_claims.json",
        compactions_path=tmp_path / ".aegis" / "compacted.json",
        subject_snapshots_path=tmp_path / ".aegis" / "subject_snapshots.json",
        routing_events_path=tmp_path / ".aegis" / "routing_events.json",
    )

    write_subject_snapshot(
        agent_id="codex",
        session_id="sess-44",
        summary="Operate as a packet-first runtime steward with explicit boundaries.",
        stable_vows=["never smuggle theory into runtime truth"],
        durable_boundaries=["do not edit protected human-managed files"],
        decision_preferences=["prefer packet before broad repo scan"],
        verified_routines=["end sessions with checkpoint or compaction before release"],
        active_threads=["subject snapshot hardening"],
        store=store,
    )
    store.append_trace(
        SessionTrace(
            agent="codex",
            session_id="sess-45",
            timestamp="2026-03-28T00:06:00+00:00",
            topics=["runtime_adapter", "redis"],
            key_decisions=["refresh active threads after compaction review"],
        ).to_dict()
    )
    write_compaction(
        agent_id="codex",
        session_id="sess-45",
        summary="First bounded handoff for the runtime lane.",
        carry_forward=["keep packet-first session cadence stable"],
        pending_paths=["tonesoul/runtime_adapter.py"],
        evidence_refs=["docs/AI_QUICKSTART.md"],
        next_action="refresh subject snapshot active threads",
        store=store,
    )
    write_compaction(
        agent_id="codex",
        session_id="sess-46",
        summary="Repeated bounded handoff with no new backing evidence.",
        carry_forward=["keep packet-first session cadence stable"],
        pending_paths=["tonesoul/runtime_adapter.py"],
        evidence_refs=["docs/AI_QUICKSTART.md"],
        next_action="refresh subject snapshot active threads",
        store=store,
    )

    packet = r_memory_packet(posture=GovernancePosture(), store=store)

    assert packet["project_memory_summary"]["subject_refresh"]["refresh_recommended"] is True
    assert not packet["project_memory_summary"]["subject_refresh"][
        "recommended_command"
    ].startswith("python scripts/apply_subject_refresh.py --agent")
    assert any(
        "recycled carry_forward" in hazard
        for hazard in packet["project_memory_summary"]["subject_refresh"]["promotion_hazards"]
    )

    result = apply_subject_refresh(
        agent_id="codex",
        field="active_threads",
        summary="Do not promote recycled carry-forward without new evidence.",
        session_id="sess-46",
        source="test",
        store=store,
    )

    assert result["ok"] is False
    assert result["reason"] == "promotion_hazards_present"
    assert any(
        "recycled carry_forward" in hazard
        for hazard in result["subject_refresh"]["promotion_hazards"]
    )


def test_r_memory_packet_surfaces_fresh_compaction_even_when_traces_are_older(
    tmp_path: Path,
) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / "task_claims.json",
        compactions_path=tmp_path / "compacted.json",
        subject_snapshots_path=tmp_path / "subject_snapshots.json",
    )

    legacy_trace = SessionTrace(
        agent="claude-opus-4-6",
        session_id="trace-legacy",
        timestamp="2026-03-25T05:09:48+00:00",
        topics=["governance", "memory", "testing"],
        key_decisions=["older trace should remain visible but not dominate handoff"],
    )
    store.append_trace(legacy_trace.to_dict())

    compaction = write_compaction(
        agent_id="codex",
        session_id="2026-03-27-rmemory-refresh",
        summary=(
            "2026-03-27: bounded POAV gate is live on high-risk runtime paths; "
            "repo_progress now surfaces current branch/head/dirty posture."
        ),
        carry_forward=["Prefer packet-first handoff before broad repo scans."],
        pending_paths=["tonesoul/unified_pipeline.py", "scripts/run_r_memory_packet.py"],
        evidence_refs=["docs/status/claim_authority_latest.md"],
        next_action="Verify a fresh AI cites recent_compactions before stale traces.",
        source="codex-r-memory-refresh",
        store=store,
    )

    packet = r_memory_packet(posture=GovernancePosture(), store=store, trace_limit=5)

    assert packet["recent_traces"][0]["session_id"] == "trace-legacy"
    assert packet["recent_compactions"][0]["compaction_id"] == compaction["compaction_id"]
    assert packet["recent_compactions"][0]["summary"].startswith("2026-03-27: bounded POAV gate")
    assert packet["project_memory_summary"]["carry_forward"] == [
        "Prefer packet-first handoff before broad repo scans."
    ]
    assert packet["project_memory_summary"]["next_actions"] == [
        "Verify a fresh AI cites recent_compactions before stale traces."
    ]
    assert "tonesoul/unified_pipeline.py" in packet["project_memory_summary"]["pending_paths"]
    assert (
        "No active claims are visible; claim shared paths before editing them."
        in packet["operator_guidance"]["current_reminders"]
    )


def test_r_memory_packet_surfaces_since_last_seen_delta_and_ack(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / ".aegis" / "task_claims.json",
        checkpoints_path=tmp_path / ".aegis" / "checkpoints.json",
        compactions_path=tmp_path / ".aegis" / "compacted.json",
        subject_snapshots_path=tmp_path / ".aegis" / "subject_snapshots.json",
        observer_cursors_path=tmp_path / ".aegis" / "observer_cursors.json",
    )

    store.append_trace(
        SessionTrace(
            agent="codex",
            session_id="sess-first",
            timestamp="2026-03-28T00:00:00+00:00",
            topics=["delta-feed"],
            key_decisions=["establish observer baseline"],
        ).to_dict()
    )
    claim_task(
        "delta-lane",
        agent_id="codex",
        summary="wire since-last-seen observer cursor",
        paths=["tonesoul/runtime_adapter.py"],
        store=store,
    )
    write_checkpoint(
        "cp-first",
        agent_id="codex",
        session_id="sess-first",
        summary="packet now exposes recent checkpoints",
        pending_paths=["tonesoul/diagnose.py"],
        next_action="add ack-aware CLI",
        store=store,
    )
    first_compaction = write_compaction(
        agent_id="codex",
        session_id="sess-first",
        summary="Observer cursor lane is ready for first-baseline acknowledgement.",
        carry_forward=["ack after review, not before"],
        pending_paths=["scripts/run_r_memory_packet.py"],
        next_action="teach the CLI to persist observer baselines",
        store=store,
    )
    write_subject_snapshot(
        agent_id="codex",
        session_id="sess-first",
        summary="Operate as a packet-first observer and advance baselines deliberately.",
        stable_vows=["do not treat unread packet data as inherited"],
        durable_boundaries=["observer cursor stays non-canonical"],
        decision_preferences=["prefer deltas over broad rescans when possible"],
        verified_routines=["ack only after reviewing the packet"],
        active_threads=["delta-feed rollout"],
        store=store,
    )

    first_packet = r_memory_packet(
        posture=GovernancePosture(),
        store=store,
        observer_id="claude-observer",
    )

    assert first_packet["delta_feed"]["first_observation"] is True
    assert first_packet["delta_feed"]["ack_command"] == (
        "python scripts/run_r_memory_packet.py --agent claude-observer --ack"
    )
    assert (
        first_packet["delta_feed"]["new_compactions"][0]["compaction_id"]
        == first_compaction["compaction_id"]
    )
    assert (
        "No since-last-seen baseline exists yet; ack the packet after review to establish one."
        in first_packet["operator_guidance"]["current_reminders"]
    )

    cursor = acknowledge_observer_cursor(
        "claude-observer",
        packet=first_packet,
        store=store,
    )
    stored_cursor = get_observer_cursor("claude-observer", store=store)

    assert cursor["latest_compaction_id"] == first_compaction["compaction_id"]
    assert stored_cursor["latest_checkpoint_id"] == "cp-first"
    assert stored_cursor["active_claim_ids"] == ["delta-lane"]

    release_task_claim("delta-lane", agent_id="codex", store=store)
    second_checkpoint = write_checkpoint(
        "cp-second",
        agent_id="codex",
        session_id="sess-second",
        summary="Ack path landed; re-read packet and observe only the new delta.",
        pending_paths=["tonesoul/diagnose.py"],
        next_action="show delta feed in diagnose",
        store=store,
    )

    second_packet = r_memory_packet(
        posture=GovernancePosture(),
        store=store,
        observer_id="claude-observer",
    )

    assert second_packet["delta_feed"]["first_observation"] is False
    assert second_packet["delta_feed"]["has_updates"] is True
    assert (
        second_packet["delta_feed"]["new_checkpoints"][0]["checkpoint_id"]
        == second_checkpoint["checkpoint_id"]
    )
    assert second_packet["delta_feed"]["released_claim_ids"] == ["delta-lane"]
    assert (
        "A delta feed is visible for this agent; ack after review to advance the observer baseline."
        in second_packet["operator_guidance"]["current_reminders"]
    )


def test_route_r_memory_signal_classifies_surfaces() -> None:
    claim_route = route_r_memory_signal(
        agent_id="codex",
        summary="claim the runtime adapter lane",
        task_id="runtime-adapter-lane",
        paths=["tonesoul/runtime_adapter.py"],
    )
    checkpoint_route = route_r_memory_signal(
        agent_id="codex",
        summary="pause for handoff",
        pending_paths=["tonesoul/diagnose.py"],
        next_action="resume packet output cleanup",
    )
    compaction_route = route_r_memory_signal(
        agent_id="codex",
        summary="handoff across sessions",
        carry_forward=["keep packet-first discipline"],
        evidence_refs=["docs/AI_QUICKSTART.md"],
    )
    perspective_route = route_r_memory_signal(
        agent_id="codex",
        summary="temporary stance while evidence is incomplete",
        stance="provisional",
        tensions=["safety vs speed"],
    )
    subject_route = route_r_memory_signal(
        agent_id="codex",
        summary="durable operating boundary changed",
        durable_boundaries=["do not bypass packet-first startup"],
        decision_preferences=["route summary-only state into checkpoints first"],
    )

    assert claim_route["surface"] == "claim"
    assert checkpoint_route["surface"] == "checkpoint"
    assert compaction_route["surface"] == "compaction"
    assert perspective_route["surface"] == "perspective"
    assert subject_route["surface"] == "subject_snapshot"


def test_write_routed_signal_persists_to_selected_surface(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / ".aegis" / "task_claims.json",
        checkpoints_path=tmp_path / ".aegis" / "checkpoints.json",
        compactions_path=tmp_path / ".aegis" / "compacted.json",
        subject_snapshots_path=tmp_path / ".aegis" / "subject_snapshots.json",
    )

    route = route_r_memory_signal(
        agent_id="codex",
        summary="resume packet delta follow-up",
        pending_paths=["tonesoul/runtime_adapter.py"],
        next_action="finish router integration",
        source="test",
    )
    written = write_routed_signal(route, store=store)
    packet = r_memory_packet(posture=GovernancePosture(), store=store)

    assert route["surface"] == "checkpoint"
    assert written["checkpoint_id"].startswith("cp-")
    assert packet["recent_checkpoints"][0]["checkpoint_id"] == written["checkpoint_id"]
    assert packet["recent_checkpoints"][0]["next_action"] == "finish router integration"


# ── decay_tensions() ────────────────────────────────────────────


def test_decay_prunes_old_tensions() -> None:
    old = [{"timestamp": "2020-01-01T00:00:00+00:00", "severity": 0.5, "topic": "ancient"}]
    result = decay_tensions(old)
    assert len(result) == 0  # years old, fully decayed


def test_decay_preserves_recent_tensions() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    recent = [{"timestamp": now, "severity": 0.8, "topic": "just happened"}]
    result = decay_tensions(recent)
    assert len(result) == 1
    assert result[0]["severity"] >= 0.79  # barely decayed


# ── drift_baseline() ────────────────────────────────────────────


def test_drift_no_tensions_returns_same() -> None:
    base = {"caution_bias": 0.5, "innovation_bias": 0.5, "autonomy_level": 0.5}
    assert drift_baseline(base, []) == base


def test_drift_high_tension_nudges_caution_up() -> None:
    base = {"caution_bias": 0.5, "innovation_bias": 0.5, "autonomy_level": 0.5}
    tensions = [{"severity": 0.9}]
    result = drift_baseline(base, tensions)
    assert result["caution_bias"] > 0.5


# ── update_soul_integral() ──────────────────────────────────────


def test_soul_integral_accumulates() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    # blend_rate=0.3: 0.0 * decay + 0.3 * 0.7 = 0.21
    result = update_soul_integral(0.0, now, [{"severity": 0.7}])
    assert result == pytest.approx(0.21, abs=0.01)


def test_soul_integral_accumulates_over_sessions() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    # Multiple high-tension sessions should build up, but stay bounded
    si = 0.0
    for _ in range(10):
        si = update_soul_integral(si, now, [{"severity": 0.9}])
    assert 0.0 < si <= 1.0
    # After 10 consecutive 0.9-severity sessions (no decay), should be high but capped
    assert si <= 1.0


def test_soul_integral_clamped_to_unit() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    # Even with very high current + high tension, stays at 1.0
    result = update_soul_integral(0.95, now, [{"severity": 1.0}])
    assert result <= 1.0


def test_soul_integral_decays_old() -> None:
    result = update_soul_integral(1.0, "2020-01-01T00:00:00+00:00", [])
    assert result < 0.01  # years of decay


# ── summary() ───────────────────────────────────────────────────


def test_summary_contains_key_sections() -> None:
    posture = GovernancePosture(
        soul_integral=1.23,
        session_count=5,
        active_vows=[{"id": "v1", "content": "be good"}],
    )
    text = summary(posture)
    assert "Soul Integral" in text
    assert "Sessions: 5" in text
    assert "be good" in text
    assert "Active Vows (1)" in text


# ── GovernancePosture round-trip ────────────────────────────────


def test_posture_round_trip() -> None:
    p = GovernancePosture(soul_integral=3.14, session_count=7)
    d = p.to_dict()
    p2 = GovernancePosture.from_dict(d)
    assert p2.soul_integral == 3.14
    assert p2.session_count == 7


# ── SessionTrace ────────────────────────────────────────────────


def test_session_trace_auto_id() -> None:
    t = SessionTrace(agent="test")
    assert len(t.session_id) > 0
    assert t.timestamp != ""
