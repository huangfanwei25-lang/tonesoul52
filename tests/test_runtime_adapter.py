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
    claim_task,
    commit,
    decay_tensions,
    drift_baseline,
    list_active_claims,
    list_checkpoints,
    list_compactions,
    list_perspectives,
    load,
    r_memory_packet,
    release_task_claim,
    summary,
    update_soul_integral,
    write_checkpoint,
    write_compaction,
    write_perspective,
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
    trace = SessionTrace(agent="claude", key_decisions=["test"])
    commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    lines = tmp_traces.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["agent"] == "claude"
    assert "test" in record["key_decisions"]


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


def test_r_memory_packet_exposes_runtime_dominance_and_recent_trace(
    tmp_state: Path,
    tmp_traces: Path,
) -> None:
    trace = SessionTrace(
        agent="codex",
        topics=["runtime", "redis"],
        tension_events=[{"topic": "safety vs speed", "severity": 0.7}],
        key_decisions=["emit packet"],
    )
    commit(trace, state_path=tmp_state, traces_path=tmp_traces)

    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_state,
        traces_path=tmp_traces,
        zones_path=tmp_traces.parent / "zone_registry.json",
    )
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
    assert (
        "docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"
        in packet["canonical_sources"]
    )
    assert packet["posture"]["session_count"] == 1
    assert set(packet["posture"]["risk_posture"]) >= {"score", "level", "recommended_action"}
    assert "project_memory_summary" in packet
    assert "summary_text" in packet["project_memory_summary"]
    assert "repo_progress" in packet["project_memory_summary"]
    assert packet["operator_guidance"]["backend_mode"] == "file"
    assert packet["operator_guidance"]["session_start"][0].startswith("python -m tonesoul.diagnose")
    assert packet["operator_guidance"]["session_end"][0].startswith("python scripts/save_checkpoint.py")
    assert "claim" in packet["operator_guidance"]["coordination_commands"]
    assert "checkpoint or compaction" in packet["operator_guidance"]["completion_rule"]
    assert packet["recent_traces"][0]["agent"] == "codex"
    assert packet["recent_traces"][0]["topics"] == ["runtime", "redis"]


def test_task_claims_prevent_collisions_and_appear_in_packet(tmp_path: Path) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        claims_path=tmp_path / "task_claims.json",
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
    assert "project_memory_summary" in packet
    assert packet["project_memory_summary"]["next_actions"][0] == "use packet consumption in UI"
    assert "repo_progress" in packet["project_memory_summary"]
    assert (
        "Prefer recent_compactions and project_memory_summary before older recent_traces."
        in packet["operator_guidance"]["current_reminders"]
    )
    assert packet["operator_guidance"]["session_end"][2].startswith(
        "python scripts/run_task_claim.py release"
    )


def test_r_memory_packet_surfaces_fresh_compaction_even_when_traces_are_older(
    tmp_path: Path,
) -> None:
    from tonesoul.backends.file_store import FileStore

    store = FileStore(
        gov_path=tmp_path / "governance_state.json",
        traces_path=tmp_path / "session_traces.jsonl",
        zones_path=tmp_path / "zone_registry.json",
        compactions_path=tmp_path / "compacted.json",
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
    result = update_soul_integral(0.0, now, [{"severity": 0.7}])
    assert result == pytest.approx(0.7, abs=0.01)


def test_soul_integral_decays_old() -> None:
    result = update_soul_integral(10.0, "2020-01-01T00:00:00+00:00", [])
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
