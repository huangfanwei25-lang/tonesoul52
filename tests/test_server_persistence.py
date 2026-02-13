from __future__ import annotations

import apps.api.server as server


def _client():
    server.app.config["TESTING"] = True
    return server.app.test_client()


class _FakePersistence:
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.calls: list[tuple[str, dict]] = []

    def status_dict(self):
        return {
            "provider": "supabase",
            "enabled": self.enabled,
            "configured": self.enabled,
            "last_error": None,
        }

    def list_conversations(self, limit: int, offset: int, session_id: str | None = None):
        self.calls.append(
            ("list_conversations", {"limit": limit, "offset": offset, "session_id": session_id})
        )
        return {
            "conversations": [
                {
                    "id": "conv_abc",
                    "title": "conv_abc",
                    "internal_id": "uuid-1",
                    "created_at": "2026-02-11T00:00:00Z",
                    "updated_at": "2026-02-11T00:00:05Z",
                }
            ],
            "total": 1,
        }

    def get_conversation(self, conversation_id: str):
        self.calls.append(("get_conversation", {"conversation_id": conversation_id}))
        if conversation_id == "missing":
            return None
        return {
            "id": conversation_id,
            "title": conversation_id,
            "internal_id": "uuid-1",
            "messages": [{"role": "user", "content": "hello"}],
        }

    def delete_conversation(self, conversation_id: str):
        self.calls.append(("delete_conversation", {"conversation_id": conversation_id}))
        if conversation_id == "missing":
            return None
        return True

    def list_audit_logs(
        self,
        limit: int,
        offset: int,
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

    def list_memories(self, limit: int, session_id: str | None = None):
        self.calls.append(("list_memories", {"limit": limit, "session_id": session_id}))
        return [{"id": "m1", "source": "session_report"}]

    def get_counts(self):
        self.calls.append(("get_counts", {}))
        return {
            "memory_count": 11,
            "conversation_count": 12,
            "audit_log_count": 13,
            "message_count": 14,
        }


def test_list_conversations_route_returns_supabase_page(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/conversations?limit=20&offset=5")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["total"] == 1
    assert payload["conversations"][0]["id"] == "conv_abc"
    assert payload["persistence_enabled"] is True
    assert ("list_conversations", {"limit": 20, "offset": 5, "session_id": None}) in fake.calls


def test_list_conversations_route_forwards_session_id_filter(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/conversations?limit=20&offset=0&session_id=session_demo")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["session_id"] == "session_demo"
    assert (
        "list_conversations",
        {"limit": 20, "offset": 0, "session_id": "session_demo"},
    ) in fake.calls


def test_get_conversation_route_returns_404_when_missing(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/conversations/missing")
    payload = response.get_json()

    assert response.status_code == 404
    assert payload["error"] == "Conversation not found"


def test_delete_conversation_route_success(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.delete("/api/conversations/conv_abc")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["success"] is True
    assert payload["deleted"] is True


def test_audit_logs_route_returns_data(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/audit-logs?limit=10&offset=0")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["total"] == 1
    assert payload["logs"][0]["id"] == "a1"
    assert (
        "list_audit_logs",
        {"limit": 10, "offset": 0, "conversation_id": None, "session_id": None},
    ) in fake.calls


def test_audit_logs_route_forwards_session_id_filter(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/audit-logs?limit=10&offset=0&session_id=session_demo")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["session_id"] == "session_demo"
    assert (
        "list_audit_logs",
        {
            "limit": 10,
            "offset": 0,
            "conversation_id": None,
            "session_id": "session_demo",
        },
    ) in fake.calls


def test_audit_logs_route_forwards_conversation_id_filter(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/audit-logs?limit=10&offset=0&conversation_id=conv_abc")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["conversation_id"] == "conv_abc"
    assert (
        "list_audit_logs",
        {
            "limit": 10,
            "offset": 0,
            "conversation_id": "conv_abc",
            "session_id": None,
        },
    ) in fake.calls


def test_status_route_exposes_counts_and_backend(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)
    monkeypatch.setattr(server, "llm_backend", "Gemini API")
    monkeypatch.setattr(server, "llm_last_error", None)
    monkeypatch.setattr(server, "get_llm_client", lambda: None)

    client = _client()
    response = client.get("/api/status")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["persistence"]["enabled"] is True
    assert payload["llm_backend"] == "Gemini API"
    assert "llm_error" in payload
    assert payload["memory_count"] == 11
    assert payload["conversation_count"] == 12
    assert payload["audit_log_count"] == 13


def test_memories_route_uses_supabase_when_enabled(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    def _fail_local_loader(*args, **kwargs):
        raise AssertionError("local memory loader should not be called when persistence is enabled")

    monkeypatch.setattr(server, "load_recent_memory", _fail_local_loader)

    client = _client()
    response = client.get("/api/memories?limit=7")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["memories"][0]["id"] == "m1"
    assert ("list_memories", {"limit": 7, "session_id": None}) in fake.calls


def test_memories_route_forwards_session_id_filter(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    response = client.get("/api/memories?limit=7&session_id=session_demo")
    payload = response.get_json()

    assert response.status_code == 200
    assert payload["session_id"] == "session_demo"
    assert ("list_memories", {"limit": 7, "session_id": "session_demo"}) in fake.calls


def test_routes_return_empty_page_when_persistence_disabled(monkeypatch):
    fake = _FakePersistence(enabled=False)
    monkeypatch.setattr(server, "supabase_persistence", fake)

    client = _client()
    conversations = client.get("/api/conversations")
    logs = client.get("/api/audit-logs")
    convo_detail = client.get("/api/conversations/conv_abc")

    assert conversations.status_code == 200
    assert conversations.get_json()["persistence_enabled"] is False
    assert logs.status_code == 200
    assert logs.get_json()["persistence_enabled"] is False
    assert convo_detail.status_code == 503


def test_read_routes_require_token_when_configured(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)
    monkeypatch.setenv("TONESOUL_READ_API_TOKEN", "secret-read-token")

    client = _client()
    conversations = client.get("/api/conversations")
    logs = client.get("/api/audit-logs")
    memories = client.get("/api/memories")

    assert conversations.status_code == 401
    assert logs.status_code == 401
    assert memories.status_code == 401
    assert conversations.get_json()["error"] == "Unauthorized read access"


def test_read_routes_accept_valid_bearer_token(monkeypatch):
    fake = _FakePersistence(enabled=True)
    monkeypatch.setattr(server, "supabase_persistence", fake)
    monkeypatch.setenv("TONESOUL_READ_API_TOKEN", "secret-read-token")

    client = _client()
    headers = {"Authorization": "Bearer secret-read-token"}
    conversations = client.get("/api/conversations?limit=20&offset=0", headers=headers)
    logs = client.get("/api/audit-logs?limit=10&offset=0", headers=headers)
    memories = client.get("/api/memories?limit=5", headers=headers)

    assert conversations.status_code == 200
    assert logs.status_code == 200
    assert memories.status_code == 200
