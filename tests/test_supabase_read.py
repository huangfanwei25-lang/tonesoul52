from __future__ import annotations

import apps.api.server as server


def _client():
    server.app.config["TESTING"] = True
    return server.app.test_client()


class _FakeReadPersistence:
    def __init__(self):
        self.enabled = True
        self.calls: list[tuple[str, dict]] = []

    def status_dict(self):
        return {"provider": "supabase", "enabled": True, "configured": True, "last_error": None}

    def get_counts(self):
        return {
            "memory_count": 5,
            "conversation_count": 3,
            "audit_log_count": 8,
            "message_count": 12,
        }

    def list_memories(self, limit: int = 10, session_id: str | None = None):
        self.calls.append(("list_memories", {"limit": limit, "session_id": session_id}))
        return [{"id": "m1", "source": "session_report"}]

    def list_conversations(self, limit: int = 20, offset: int = 0, session_id: str | None = None):
        self.calls.append(
            (
                "list_conversations",
                {"limit": limit, "offset": offset, "session_id": session_id},
            )
        )
        return {"conversations": [{"id": "conv_demo"}], "total": 1}

    def get_conversation(self, conversation_id: str):
        self.calls.append(("get_conversation", {"conversation_id": conversation_id}))
        return {
            "id": conversation_id,
            "messages": [{"id": "msg_1", "role": "user", "content": "hello"}],
        }

    def delete_conversation(self, conversation_id: str):
        self.calls.append(("delete_conversation", {"conversation_id": conversation_id}))
        return True

    def list_audit_logs(
        self,
        limit: int = 20,
        offset: int = 0,
        conversation_id: str | None = None,
        session_id: str | None = None,
    ):
        self.calls.append(
            (
                "list_audit_logs",
                {
                    "limit": limit,
                    "offset": offset,
                    "conversation_id": conversation_id,
                    "session_id": session_id,
                },
            )
        )
        return {"logs": [{"id": "a1", "gate_decision": "approve"}], "total": 1}


def test_status_returns_counts_from_persistence(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    fake = _FakeReadPersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["memory_count"] == 5
    assert payload["conversation_count"] == 3
    assert payload["audit_log_count"] == 8
    assert payload["message_count"] == 12


def test_conversation_read_routes_call_persistence(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    fake = _FakeReadPersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    list_response = client.get("/api/conversations?limit=15&offset=5")
    get_response = client.get("/api/conversations/conv_demo")
    delete_response = client.delete("/api/conversations/conv_demo")

    assert list_response.status_code == 200
    assert get_response.status_code == 200
    assert delete_response.status_code == 200
    assert any(name == "list_conversations" for name, _ in fake.calls)
    assert any(name == "get_conversation" for name, _ in fake.calls)
    assert any(name == "delete_conversation" for name, _ in fake.calls)


def test_audit_logs_route_supports_filters(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    fake = _FakeReadPersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/audit-logs?conversation_id=conv_demo&limit=10&offset=0")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["total"] == 1
    assert payload["conversation_id"] == "conv_demo"
    assert any(
        name == "list_audit_logs" and call["conversation_id"] == "conv_demo"
        for name, call in fake.calls
    )


def test_memories_route_falls_back_to_local_when_persistence_disabled(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)

    class _DisabledPersistence:
        enabled = False

        def status_dict(self):
            return {
                "provider": "supabase",
                "enabled": False,
                "configured": False,
                "last_error": None,
            }

    monkeypatch.setattr(server, "supabase_persistence", _DisabledPersistence())
    monkeypatch.setattr(server, "load_recent_memory", lambda limit=10: [{"id": "local_1"}])

    client = _client()
    response = client.get("/api/memories?limit=7")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["memories"] == [{"id": "local_1"}]
