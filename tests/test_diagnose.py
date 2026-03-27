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
        "recent_compactions": [
            {
                "agent": "claude",
                "updated_at": "2026-03-27T01:20:00Z",
                "summary": "captured current boundary decisions",
            }
        ],
        "parallel_lanes": {
            "canonical_commit_serialized": True,
            "perspectives_surface": "ts:perspectives:{agent_id}",
            "checkpoints_surface": "ts:checkpoints:*",
        },
        "project_memory_summary": {
            "focus_topics": ["shared-memory", "runtime"],
            "recent_agents": ["codex", "claude"],
            "active_claim_count": 1,
            "pending_paths": ["docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md"],
            "carry_forward": ["keep packet first"],
            "next_actions": ["integrate risk posture into packet"],
            "summary_text": "近期焦點：shared-memory, runtime | 下一步：integrate risk posture into packet",
        },
    }


def test_compact_diagnostic_reports_shared_runtime_counts(monkeypatch) -> None:
    store = _FakeStore()
    monkeypatch.setattr("tonesoul.store.get_store", lambda: store)
    monkeypatch.setattr("tonesoul.runtime_adapter.load", lambda agent_id, source="diagnose": _fake_posture())
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.r_memory_packet",
        lambda posture=None, store=None, trace_limit=5, visitor_limit=5: _fake_packet(),
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    text = compact_diagnostic(agent_id="codex")

    assert "claims=1" in text
    assert "compactions=1" in text
    assert "R=0.67/high" in text
    assert "aegis=intact" in text


def test_full_diagnostic_is_cp950_safe_and_includes_shared_runtime(monkeypatch) -> None:
    store = _FakeStore()
    monkeypatch.setattr("tonesoul.store.get_store", lambda: store)
    monkeypatch.setattr("tonesoul.runtime_adapter.load", lambda agent_id, source="diagnose": _fake_posture())
    monkeypatch.setattr(
        "tonesoul.runtime_adapter.r_memory_packet",
        lambda posture=None, store=None, trace_limit=5, visitor_limit=5: _fake_packet(),
    )
    monkeypatch.setattr("tonesoul.aegis_shield.AegisShield", _FakeShield)

    report = full_diagnostic(agent_id="codex")

    assert "[Shared Runtime] claims=1 visitors=1 compactions=1" in report
    assert "Risk Posture:" in report
    assert "[Project Memory Summary]" in report
    assert "coord-contract" in report
    assert "diagnose/load -> packet -> claim" in report
    report.encode("cp950", errors="strict")
