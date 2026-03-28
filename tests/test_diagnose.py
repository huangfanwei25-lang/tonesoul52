from __future__ import annotations

from tonesoul.diagnose import compact_diagnostic, full_diagnostic
from tonesoul.runtime_adapter import GovernancePosture


class _FakeRedis:
    def info(self, section: str):
        assert section == "memory"
        return {"used_memory": 2 * 1024 * 1024}

    def dbsize(self) -> int:
        return 17


class _FakeStore:
    backend_name = "redis"
    is_redis = True
    _r = _FakeRedis()

    def get_traces(self, n: int = 999):
        return [
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-27T01:02:03Z",
                "topics": ["shared-memory"],
                "tension_events": [],
                "vow_events": [],
                "aegis_vetoes": [],
                "key_decisions": ["left a claim"],
            }
        ]

    def get_zones(self):
        return {
            "zones": [{"name": "governance", "level": 2, "visit_count": 4}],
            "total_sessions": 9,
            "world_mood": "steady",
            "weather": "clear",
        }


class _FakeShield:
    @classmethod
    def load(cls, store):
        return cls()

    def audit(self, store):
        return {
            "integrity": "intact",
            "chain_valid": True,
            "total_traces": 3,
            "signature_failures": [],
            "chain_errors": [],
        }


def _fake_posture() -> GovernancePosture:
    return GovernancePosture(
        last_updated="2026-03-27T00:00:00Z",
        soul_integral=0.81,
        tension_history=[{"topic": "coordination", "severity": 0.42}],
        active_vows=[{"id": "v1", "content": "be explicit"}],
        baseline_drift={
            "caution_bias": 0.55,
            "innovation_bias": 0.48,
            "autonomy_level": 0.36,
        },
        session_count=9,
    )


def _fake_packet():
    return {
        "posture": {
            "risk_posture": {
                "score": 0.67,
                "level": "high",
                "recommended_action": "review_before_commit",
                "factors": ["high_recent_tension"],
                "inputs": {"tension_pressure": 0.7},
            }
        },
        "recent_traces": [
            {
                "session_id": "sess-1",
                "agent": "codex",
                "timestamp": "2026-03-27T01:02:03Z",
                "topics": ["shared-memory"],
                "key_decision_count": 1,
            }
        ],
        "recent_visitors": [
            {
                "agent": "claude",
                "timestamp": "2026-03-27T01:10:00Z",
                "source": "diagnose",
            }
        ],
        "active_claims": [
            {
                "task_id": "coord-contract",
                "agent": "codex",
                "summary": "write shared ops contract",
                "paths": ["docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"],
            }
        ],
        "recent_checkpoints": [
            {
                "checkpoint_id": "cp-1",
                "agent": "codex",
                "session_id": "sess-1",
                "summary": "Ack path is pending in the packet script.",
                "pending_paths": ["scripts/run_r_memory_packet.py"],
                "next_action": "add --agent and --ack support",
                "source": "cli",
                "updated_at": "2026-03-27T01:15:00Z",
            }
        ],
        "recent_compactions": [
            {
                "agent": "claude",
                "updated_at": "2026-03-27T01:20:00Z",
                "summary": "captured current boundary decisions",
            }
        ],
        "recent_subject_snapshots": [
            {
                "snapshot_id": "subj-1",
                "agent": "codex",
                "session_id": "sess-1",
                "summary": "Stay packet-first and keep theory out of runtime truth.",
                "stable_vows": ["do not smuggle theory into runtime"],
                "durable_boundaries": ["protected files stay human-managed"],
                "decision_preferences": ["prefer packet before broad repo scan"],
                "verified_routines": ["leave compaction before release"],
                "active_threads": ["subject-snapshot rollout"],
                "evidence_refs": ["docs/AI_QUICKSTART.md"],
                "refresh_signals": ["refresh when durable boundaries change"],
                "source": "cli",
                "updated_at": "2026-03-28T00:04:00Z",
            }
        ],
        "parallel_lanes": {
            "canonical_commit_serialized": True,
            "perspectives_surface": "ts:perspectives:{agent_id}",
            "checkpoints_surface": "ts:checkpoints:*",
            "subject_snapshot_surface": "ts:subject_snapshots",
        },
        "project_memory_summary": {
            "focus_topics": ["shared-memory", "runtime"],
            "recent_agents": ["codex", "claude"],
            "active_claim_count": 1,
            "pending_paths": ["docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"],
            "carry_forward": ["keep packet first"],
            "next_actions": ["integrate risk posture into packet"],
            "subject_anchor": {
                "summary": "Stay packet-first and keep theory out of runtime truth.",
                "stable_vows": ["do not smuggle theory into runtime"],
                "durable_boundaries": ["protected files stay human-managed"],
                "decision_preferences": ["prefer packet before broad repo scan"],
                "verified_routines": ["leave compaction before release"],
                "active_threads": ["subject-snapshot rollout"],
            },
            "repo_progress": {
                "available": True,
                "branch": "codex/r-memory-compaction-lane-20260326",
                "head": "04c243d",
                "staged_count": 1,
                "modified_count": 2,
                "untracked_count": 3,
                "dirty_count": 6,
                "path_preview": [
                    "tonesoul/runtime_adapter.py",
                    "tonesoul/diagnose.py",
                ],
            },
            "summary_text": (
                "focus=shared-memory, runtime | next=integrate risk posture into packet | "
                "repo=codex/r-memory-compaction-lane-20260326@04c243d dirty=6"
            ),
        },
        "operator_guidance": {
            "backend_mode": "redis",
            "session_start": [
                "python scripts/start_agent_session.py --agent <your-id>",
                "python -m tonesoul.diagnose --agent <your-id>",
                "python scripts/run_r_memory_packet.py --agent <your-id> --ack",
                "python scripts/run_task_claim.py list",
            ],
            "session_end": [
                'python scripts/end_agent_session.py --agent <your-id> --summary "..." --path "..."',
                'python scripts/save_checkpoint.py --checkpoint-id <id> --agent <your-id> --summary "..." --path "..."',
                'python scripts/save_compaction.py --agent <your-id> --summary "..." --path "..."',
                "python scripts/run_task_claim.py release <task_id> --agent <your-id>",
            ],
            "coordination_commands": {
                "claim": 'python scripts/run_task_claim.py claim <task_id> --agent <your-id> --summary "..."',
                "perspective": 'python scripts/save_perspective.py --agent <your-id> --summary "..." --stance "..."',
                "checkpoint": 'python scripts/save_checkpoint.py --checkpoint-id <id> --agent <your-id> --summary "..." --path "..."',
                "compaction": 'python scripts/save_compaction.py --agent <your-id> --summary "..." --path "..."',
                "signal_router": 'python scripts/route_r_memory_signal.py --agent <your-id> --summary "..." --path "..." --next-action "..." --write',
                "subject_snapshot": 'python scripts/save_subject_snapshot.py --agent <your-id> --summary "..." --boundary "..." --preference "..."',
                "release": "python scripts/run_task_claim.py release <task_id> --agent <your-id>",
            },
            "recommended_order": [
                "diagnose/load",
                "packet",
                "claim",
                "work",
                "perspective/checkpoint/compaction",
                "commit",
                "release",
            ],
            "current_reminders": [
                "Prefer recent_compactions and project_memory_summary before older recent_traces.",
                "Active claims are visible; coordinate before editing overlapping paths.",
                "A recent subject snapshot is visible; treat it as durable working identity, but still non-canonical.",
                "A delta feed is visible for this agent; ack after review to advance the observer baseline.",
            ],
            "completion_rule": (
                "Before ending a session, externalize progress with checkpoint or compaction, "
                "then release any shared claim."
            ),
        },
        "delta_feed": {
            "observer_id": "codex",
            "first_observation": False,
            "has_updates": True,
            "update_count": 3,
            "previous_seen_at": "2026-03-27T00:59:00Z",
            "summary_text": "checkpoints=1 | claims(+0/-1) | repo=03fdabc->04c243d dirty=4->6",
            "new_compactions": [],
            "new_subject_snapshots": [],
            "new_checkpoints": [
                {
                    "checkpoint_id": "cp-1",
                    "agent": "codex",
                    "summary": "Ack path is pending in the packet script.",
                    "next_action": "add --agent and --ack support",
                    "updated_at": "2026-03-27T01:15:00Z",
                }
            ],
            "new_traces": [],
            "new_claims": [],
            "released_claim_ids": ["old-claim"],
            "repo_change": {
                "changed": True,
                "previous_head": "03fdabc",
                "current_head": "04c243d",
                "previous_dirty_count": 4,
                "current_dirty_count": 6,
            },
            "ack_command": "python scripts/run_r_memory_packet.py --agent codex --ack",
        },
    }


def test_compact_diagnostic_reports_shared_runtime_counts(monkeypatch) -> None:
    store = _FakeStore()
    monkeypatch.setattr("tonesoul.store.get_store", lambda: store)
    monkeypatch.setattr("tonesoul.runtime_adapter.load", lambda agent_id, source="diagnose": _fake_posture())
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.r_memory_packet",
        lambda posture=None, store=None, observer_id="", trace_limit=5, visitor_limit=5: _fake_packet(),
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    text = compact_diagnostic(agent_id="codex")

    assert "claims=1" in text
    assert "compactions=1" in text
    assert "subjects=1" in text
    assert "R=0.67/high" in text
    assert "git=04c243d/dirty=6" in text
    assert "aegis=intact" in text


def test_full_diagnostic_is_cp950_safe_and_includes_shared_runtime(monkeypatch) -> None:
    store = _FakeStore()
    monkeypatch.setattr("tonesoul.store.get_store", lambda: store)
    monkeypatch.setattr("tonesoul.runtime_adapter.load", lambda agent_id, source="diagnose": _fake_posture())
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.r_memory_packet",
        lambda posture=None, store=None, observer_id="", trace_limit=5, visitor_limit=5: _fake_packet(),
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    report = full_diagnostic(agent_id="codex")

    assert "[Shared Runtime] claims=1 visitors=1 checkpoints=1 compactions=1 subject_snapshots=1" in report
    assert "Risk Posture:" in report
    assert "[Project Memory Summary]" in report
    assert "[Subject Snapshot] count=1" in report
    assert "[Since Last Seen]" in report
    assert "coord-contract" in report
    assert "diagnose/load -> packet -> claim" in report
    assert "repo=codex/r-memory-compaction-lane-20260326@04c243d dirty=6" in report
    assert "repo_paths=tonesoul/runtime_adapter.py, tonesoul/diagnose.py" in report
    assert "[Operator Guidance]" in report
    assert "start_agent_session.py --agent <your-id>" in report
    assert "end_agent_session.py --agent <your-id>" in report
    assert "run_r_memory_packet.py --agent <your-id> --ack" in report
    assert "save_checkpoint.py" in report
    assert "save_compaction.py" in report
    assert "route_r_memory_signal.py" in report
    assert "save_subject_snapshot.py" in report
    assert "completion_rule=Before ending a session" in report
    assert "subject_anchor:" in report
    assert "Prefer recent_compactions and project_memory_summary before older" in report
    assert "ack_command=python scripts/run_r_memory_packet.py --agent codex --ack" in report
    assert "released_claim_ids=old-claim" in report
    report.encode("cp950", errors="strict")
