from __future__ import annotations

from types import SimpleNamespace

import apps.api.server as server
from tonesoul.memory.soul_db import MemorySource


def _client():
    server.app.config["TESTING"] = True
    return server.app.test_client()


class _FakePersistence:
    def __init__(self):
        self.enabled = True
        self.calls: list[tuple[str, tuple, dict]] = []

    def status_dict(self):
        return {"provider": "supabase", "enabled": True, "configured": True, "last_error": None}

    def ensure_conversation(self, conversation_id: str, session_id: str | None = None):
        self.calls.append(("ensure_conversation", (conversation_id, session_id), {}))
        return "uuid-demo"

    def record_consent(self, session_id: str, consent_type: str):
        self.calls.append(("record_consent", (session_id, consent_type), {}))
        return True

    def withdraw_consent(self, session_id: str):
        self.calls.append(("withdraw_consent", (session_id,), {}))
        return {"tracked_conversations": 1, "deleted_conversations": 1}

    def record_chat_exchange(self, **kwargs):
        self.calls.append(("record_chat_exchange", tuple(), kwargs))
        return True

    def record_chat_audit(self, **kwargs):
        self.calls.append(("record_chat_audit", tuple(), kwargs))
        return True

    def list_audit_logs(
        self,
        limit: int,
        offset: int,
        conversation_id: str | None = None,
    ):
        self.calls.append(
            (
                "list_audit_logs",
                tuple(),
                {
                    "limit": limit,
                    "offset": offset,
                    "conversation_id": conversation_id,
                },
            )
        )
        return {
            "logs": [
                {
                    "delta_t": 0.41,
                    "gate_decision": "refine",
                    "rationale": "low tension",
                    "created_at": "2026-02-12T00:00:00Z",
                },
                {
                    "delta_t": 0.87,
                    "gate_decision": "block",
                    "rationale": "high tension memory",
                    "created_at": "2026-02-12T00:05:00Z",
                },
            ],
            "total": 2,
        }

    def record_session_report(self, **kwargs):
        self.calls.append(("record_session_report", tuple(), kwargs))
        return True

    def record_evolution_result(self, **kwargs):
        self.calls.append(("record_evolution_result", tuple(), kwargs))
        return True


def test_conversation_endpoint_calls_persistence(monkeypatch):
    fake = _FakePersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.post("/api/conversation", json={"session_id": "session_x"})

    assert response.status_code == 200
    assert any(name == "ensure_conversation" for name, _, _ in fake.calls)


def test_chat_endpoint_records_exchange_and_audit(monkeypatch):
    import tonesoul.unified_pipeline as unified_pipeline

    fake = _FakePersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)
    captured: dict = {}

    class _Pipeline:
        def process(self, **kwargs):
            captured["kwargs"] = kwargs
            return SimpleNamespace(
                response="ok",
                council_verdict={"verdict": "approve", "summary": "ok", "transcript": {}},
                tonebridge_analysis={},
                inner_narrative="",
                intervention_strategy="",
                internal_monologue="",
                persona_mode="",
                trajectory_analysis={},
                self_commits=[],
                ruptures=[],
                emergent_values=[],
            )

    monkeypatch.setattr(unified_pipeline, "create_unified_pipeline", lambda: _Pipeline())

    client = _client()
    response = client.post(
        "/api/chat",
        json={
            "conversation_id": "conv_demo",
            "session_id": "session_demo",
            "message": "hello",
            "history": [],
            "full_analysis": False,
        },
    )

    assert response.status_code == 200
    assert any(name == "record_chat_exchange" for name, _, _ in fake.calls)
    assert any(name == "record_chat_audit" for name, _, _ in fake.calls)
    assert any(name == "record_evolution_result" for name, _, _ in fake.calls)
    assert any(name == "list_audit_logs" for name, _, _ in fake.calls)
    assert captured["kwargs"]["prior_tension"]["delta_t"] == 0.87
    assert captured["kwargs"]["prior_tension"]["gate_decision"] == "block"


def test_session_report_endpoint_records_persistence(monkeypatch):
    import tonesoul.tonebridge.session_reporter as session_reporter

    fake = _FakePersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)

    class _Summary:
        def to_dict(self):
            return {"summary_text": "ok"}

    class _Reporter:
        def analyze(self, history):
            return _Summary()

    monkeypatch.setattr(session_reporter, "SessionReporter", _Reporter)

    client = _client()
    response = client.post(
        "/api/session-report",
        json={
            "conversation_id": "conv_demo",
            "history": [{"role": "user", "content": "hello"}],
        },
    )

    assert response.status_code == 200
    assert any(name == "record_session_report" for name, _, _ in fake.calls)


def test_session_report_endpoint_runs_decay_cleanup(monkeypatch):
    import tonesoul.tonebridge.session_reporter as session_reporter

    fake = _FakePersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)
    cleaned: dict[str, object] = {}

    class _Summary:
        def to_dict(self):
            return {"summary_text": "ok"}

    class _Reporter:
        def analyze(self, history):
            return _Summary()

    class _FakeSoulDB:
        def cleanup_decayed(self, source, *, forget_threshold=None):
            cleaned["source"] = source
            cleaned["forget_threshold"] = forget_threshold
            return 1

    monkeypatch.setattr(session_reporter, "SessionReporter", _Reporter)
    monkeypatch.setattr(server, "_get_soul_db", lambda: _FakeSoulDB())

    client = _client()
    response = client.post(
        "/api/session-report",
        json={
            "conversation_id": "conv_demo",
            "history": [{"role": "user", "content": "hello"}],
        },
    )

    assert response.status_code == 200
    assert cleaned["source"] == MemorySource.SELF_JOURNAL


def test_evolution_distill_records_result_when_persistence_enabled(monkeypatch):
    fake = _FakePersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)

    class _DistillResult:
        def to_dict(self):
            return {
                "patterns": [{"pattern_type": "decision", "description": "x"}],
                "conversations_analyzed": 1,
                "time_range": ["2026-02-10T00:00:00Z", "2026-02-10T00:05:00Z"],
                "summary": "ok",
                "distilled_at": "2026-02-10T00:06:00Z",
            }

    class _Distiller:
        def distill(self, limit):
            assert limit == 5
            return _DistillResult()

    monkeypatch.setattr(server, "_get_context_distiller", lambda: _Distiller())

    client = _client()
    response = client.post("/api/evolution/distill", json={"limit": 5})

    assert response.status_code == 200
    assert any(name == "record_evolution_result" for name, _, _ in fake.calls)


def test_withdraw_consent_includes_deletion_report_when_enabled(monkeypatch):
    fake = _FakePersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.delete("/api/consent/session_demo")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["deletion_report"]["deleted_conversations"] == 1
    assert any(name == "withdraw_consent" for name, _, _ in fake.calls)
