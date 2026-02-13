from __future__ import annotations

import apps.api.server as server


def _client():
    server.app.config["TESTING"] = True
    return server.app.test_client()


class _FakeEvolutionPersistence:
    def __init__(self):
        self.enabled = True

    def status_dict(self):
        return {"provider": "supabase", "enabled": True, "configured": True, "last_error": None}

    def get_counts(self):
        return {
            "memory_count": 2,
            "conversation_count": 2,
            "audit_log_count": 2,
            "message_count": 6,
        }

    def list_conversations(self, limit: int = 20, offset: int = 0, session_id: str | None = None):
        return {"conversations": [{"id": "conv_1"}, {"id": "conv_2"}], "total": 2}

    def get_conversation(self, conversation_id: str):
        if conversation_id == "conv_1":
            return {
                "id": "conv_1",
                "messages": [
                    {"role": "user", "content": "I am upset", "created_at": "2026-02-12T00:00:00Z"},
                    {
                        "role": "assistant",
                        "content": "I will clarify limits and next actions.",
                        "created_at": "2026-02-12T00:00:01Z",
                        "deliberation": {
                            "self_commits": ["clarify limits"],
                            "ruptures": ["tone mismatch"],
                            "emergent_values": ["honesty"],
                        },
                    },
                    {"role": "user", "content": "Thanks, better now", "created_at": "2026-02-12T00:00:02Z"},
                ],
            }
        return {
            "id": "conv_2",
            "messages": [
                {"role": "user", "content": "Can we do this safely?", "created_at": "2026-02-12T01:00:00Z"},
                {
                    "role": "assistant",
                    "content": "Yes, with constraints.",
                    "created_at": "2026-02-12T01:00:01Z",
                    "deliberation": {"self_commits": ["bounded help"], "emergent_values": ["safety"]},
                },
            ],
        }

    def list_audit_logs(
        self,
        limit: int = 20,
        offset: int = 0,
        conversation_id: str | None = None,
        session_id: str | None = None,
    ):
        logs = [
            {
                "id": "a1",
                "conversation_id": "conv_1",
                "gate_decision": "block",
                "delta_t": 0.83,
                "created_at": "2026-02-12T00:00:01Z",
            },
            {
                "id": "a2",
                "conversation_id": "conv_2",
                "gate_decision": "approve",
                "delta_t": 0.32,
                "created_at": "2026-02-12T01:00:01Z",
            },
        ]
        if conversation_id:
            logs = [row for row in logs if row["conversation_id"] == conversation_id]
        return {"logs": logs[:limit], "total": len(logs)}


def test_evolution_summary_endpoint_before_and_after_distill(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    fake = _FakeEvolutionPersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)
    monkeypatch.setattr(server, "_context_distiller", None)

    client = _client()

    before = client.get("/api/evolution/summary")
    before_payload = before.get_json()
    assert before.status_code == 200
    assert before_payload["total_patterns"] == 0

    distill = client.post("/api/evolution/distill", json={"limit": 50})
    distill_payload = distill.get_json()
    assert distill.status_code == 200
    assert distill_payload["success"] is True
    assert distill_payload["conversations_analyzed"] == 2
    assert len(distill_payload["patterns"]) >= 1

    after = client.get("/api/evolution/summary")
    after_payload = after.get_json()
    assert after.status_code == 200
    assert after_payload["total_patterns"] >= 1
    assert after_payload["conversations_analyzed"] == 2


def test_evolution_patterns_endpoint_supports_filter(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    fake = _FakeEvolutionPersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)
    monkeypatch.setattr(server, "_context_distiller", None)

    client = _client()
    response = client.post("/api/evolution/distill", json={"limit": 20})
    assert response.status_code == 200

    filtered = client.get("/api/evolution/patterns?pattern_type=value")
    payload = filtered.get_json()
    assert filtered.status_code == 200
    assert payload["pattern_type"] == "value"
    assert payload["total"] >= 1
    assert all(row["pattern_type"] == "value" for row in payload["patterns"])


def test_evolution_distill_rejects_invalid_limit(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    fake = _FakeEvolutionPersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)
    monkeypatch.setattr(server, "_context_distiller", None)

    client = _client()
    response = client.post("/api/evolution/distill", json={"limit": "bad"})
    payload = response.get_json()

    assert response.status_code == 400
    assert payload["error"] == "Invalid limit"


def test_status_includes_evolution_summary(monkeypatch):
    monkeypatch.delenv("TONESOUL_READ_API_TOKEN", raising=False)
    fake = _FakeEvolutionPersistence()
    monkeypatch.setattr(server, "supabase_persistence", fake)
    monkeypatch.setattr(server, "_context_distiller", None)

    client = _client()
    client.post("/api/evolution/distill", json={"limit": 20})

    status = client.get("/api/status")
    payload = status.get_json()
    assert status.status_code == 200
    assert "evolution" in payload
    assert payload["evolution"]["total_patterns"] >= 1
