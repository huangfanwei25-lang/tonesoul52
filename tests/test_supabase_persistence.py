from __future__ import annotations

from typing import Any

from tonesoul.supabase_persistence import SupabasePersistence


class _FakeResponse:
    def __init__(
        self,
        status_code: int = 200,
        payload: Any = None,
        text: str | None = None,
        headers: dict[str, str] | None = None,
    ):
        self.status_code = status_code
        self._payload = payload
        self._text = text
        self.headers = headers or {}

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def text(self) -> str:
        if self._text is not None:
            return self._text
        if self._payload is None:
            return ""
        return "json"

    def json(self) -> Any:
        return self._payload


class _FakeSession:
    def __init__(self, responses: list[_FakeResponse]):
        self.responses = responses
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        url: str,
        params: dict[str, str] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> _FakeResponse:
        self.calls.append(
            {
                "method": method,
                "url": url,
                "params": params or {},
                "json": json,
                "headers": headers or {},
                "timeout": timeout,
            }
        )
        if not self.responses:
            raise AssertionError("No fake response configured for request")
        return self.responses.pop(0)


def test_disabled_when_env_missing():
    store = SupabasePersistence(url="", key="")
    assert store.enabled is False
    status = store.status_dict()
    assert status["enabled"] is False
    assert status["provider"] == "supabase"


def test_ensure_conversation_creates_mapping_and_session_link():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(payload=[]),  # lookup conversation
            _FakeResponse(payload=[{"id": "uuid-1", "title": "conv_abc"}]),  # create
            _FakeResponse(payload=None),  # append memory
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    internal = store.ensure_conversation("conv_abc", session_id="session_1")

    assert internal == "uuid-1"
    assert len(fake_session.calls) == 3
    assert fake_session.calls[0]["method"] == "GET"
    assert fake_session.calls[1]["method"] == "POST"
    assert fake_session.calls[2]["url"].endswith("/rest/v1/soul_memories")


def test_record_chat_exchange_writes_two_messages_and_touches_conversation():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(payload=[{"id": "uuid-1", "title": "conv_abc"}]),  # lookup conversation
            _FakeResponse(payload=None),  # user message
            _FakeResponse(payload=None),  # assistant message
            _FakeResponse(payload=None),  # touch conversation
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    ok = store.record_chat_exchange(
        conversation_id="conv_abc",
        user_message="u",
        assistant_message="a",
        deliberation={"verdict": "approve"},
    )

    assert ok is True
    message_calls = [
        call for call in fake_session.calls if call["url"].endswith("/rest/v1/messages")
    ]
    assert len(message_calls) == 2
    assert message_calls[0]["json"]["role"] == "user"
    assert message_calls[1]["json"]["role"] == "assistant"


def test_withdraw_consent_deletes_all_tracked_conversations():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(  # session mapping list
                payload=[
                    {"payload": {"session_id": "s1", "conversation_id": "conv_a"}},
                    {"payload": {"session_id": "s1", "conversation_id": "conv_b"}},
                ]
            ),
            _FakeResponse(payload=[{"id": "uuid-a", "title": "conv_a"}]),  # resolve conv_a
            _FakeResponse(payload=None),  # delete audit conv_a
            _FakeResponse(payload=None),  # delete conversation conv_a
            _FakeResponse(payload=[{"id": "uuid-b", "title": "conv_b"}]),  # resolve conv_b
            _FakeResponse(payload=None),  # delete audit conv_b
            _FakeResponse(payload=None),  # delete conversation conv_b
            _FakeResponse(payload=None),  # append withdrawal memory
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    report = store.withdraw_consent("s1")

    assert report["tracked_conversations"] == 2
    assert report["deleted_conversations"] == 2


def test_list_conversations_returns_paged_rows_and_total():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(
                payload=[
                    {
                        "id": "uuid-1",
                        "title": "conv_abc",
                        "created_at": "2026-02-11T00:00:00Z",
                        "updated_at": "2026-02-11T00:00:05Z",
                    }
                ]
            ),
            _FakeResponse(payload=[{"id": "uuid-1"}], headers={"Content-Range": "0-0/42"}),
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    result = store.list_conversations(limit=20, offset=0)

    assert result["total"] == 42
    assert len(result["conversations"]) == 1
    assert result["conversations"][0]["id"] == "conv_abc"


def test_list_conversations_can_filter_by_session_id():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(
                payload=[
                    {"payload": {"session_id": "session_demo", "conversation_id": "conv_abc"}},
                    {"payload": {"session_id": "session_demo", "conversation_id": "conv_xyz"}},
                    {"payload": {"session_id": "other", "conversation_id": "conv_ignored"}},
                ]
            ),
            _FakeResponse(
                payload=[
                    {
                        "id": "uuid-1",
                        "title": "conv_abc",
                        "created_at": "2026-02-11T00:00:00Z",
                        "updated_at": "2026-02-11T00:00:05Z",
                    }
                ]
            ),
            _FakeResponse(payload=[{"id": "uuid-1"}], headers={"Content-Range": "0-0/1"}),
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    result = store.list_conversations(limit=20, offset=0, session_id="session_demo")

    assert result["total"] == 1
    assert len(result["conversations"]) == 1
    assert result["conversations"][0]["id"] == "conv_abc"
    assert "title" in fake_session.calls[1]["params"]
    assert fake_session.calls[2]["params"]["title"] == fake_session.calls[1]["params"]["title"]


def test_get_conversation_returns_messages():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(payload=[{"id": "uuid-1", "title": "conv_abc"}]),
            _FakeResponse(
                payload=[
                    {
                        "id": "uuid-1",
                        "title": "conv_abc",
                        "created_at": "2026-02-11T00:00:00Z",
                        "updated_at": "2026-02-11T00:00:05Z",
                    }
                ]
            ),
            _FakeResponse(
                payload=[
                    {
                        "id": "msg-1",
                        "role": "user",
                        "content": "hello",
                        "deliberation": None,
                        "created_at": "2026-02-11T00:00:01Z",
                    },
                    {
                        "id": "msg-2",
                        "role": "assistant",
                        "content": "hi",
                        "deliberation": {"verdict": "approve"},
                        "created_at": "2026-02-11T00:00:02Z",
                    },
                ]
            ),
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    conversation = store.get_conversation("conv_abc")

    assert conversation is not None
    assert conversation["id"] == "conv_abc"
    assert len(conversation["messages"]) == 2
    assert conversation["messages"][0]["role"] == "user"


def test_delete_conversation_removes_conversation_and_audit():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(payload=[{"id": "uuid-1", "title": "conv_abc"}]),  # resolve
            _FakeResponse(payload=None),  # delete audit_logs
            _FakeResponse(payload=None),  # delete conversations
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    deleted = store.delete_conversation("conv_abc")

    assert deleted is True
    assert fake_session.calls[-1]["url"].endswith("/rest/v1/conversations")


def test_list_audit_logs_returns_rows_and_total():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(payload=[{"id": "a1", "gate_decision": "approve"}]),
            _FakeResponse(payload=[{"id": "a1"}], headers={"Content-Range": "0-0/7"}),
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    result = store.list_audit_logs(limit=20, offset=0)

    assert result["total"] == 7
    assert len(result["logs"]) == 1
    assert result["logs"][0]["id"] == "a1"


def test_list_audit_logs_can_filter_by_conversation_id():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(payload=[{"id": "uuid-1", "title": "conv_abc"}]),  # resolve external id
            _FakeResponse(payload=[{"id": "a1", "gate_decision": "approve"}]),  # logs
            _FakeResponse(payload=[{"id": "a1"}], headers={"Content-Range": "0-0/1"}),  # count
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    result = store.list_audit_logs(limit=10, offset=0, conversation_id="conv_abc")

    assert result["total"] == 1
    assert len(result["logs"]) == 1
    assert result["logs"][0]["id"] == "a1"
    assert fake_session.calls[1]["params"]["conversation_id"] == "eq.uuid-1"
    assert fake_session.calls[2]["params"]["conversation_id"] == "eq.uuid-1"


def test_list_audit_logs_can_filter_by_session_id():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(  # list session conversation links
                payload=[
                    {"payload": {"session_id": "session_demo", "conversation_id": "conv_a"}},
                    {"payload": {"session_id": "session_demo", "conversation_id": "conv_b"}},
                    {"payload": {"session_id": "other", "conversation_id": "conv_ignored"}},
                ]
            ),
            _FakeResponse(payload=[{"id": "uuid-a", "title": "conv_a"}]),  # resolve conv_a
            _FakeResponse(payload=[{"id": "uuid-b", "title": "conv_b"}]),  # resolve conv_b
            _FakeResponse(payload=[{"id": "a1", "gate_decision": "approve"}]),  # logs
            _FakeResponse(payload=[{"id": "a1"}], headers={"Content-Range": "0-0/1"}),  # count
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    result = store.list_audit_logs(limit=10, offset=0, session_id="session_demo")

    assert result["total"] == 1
    assert len(result["logs"]) == 1
    assert result["logs"][0]["id"] == "a1"
    logs_filter = fake_session.calls[3]["params"]["conversation_id"]
    count_filter = fake_session.calls[4]["params"]["conversation_id"]
    assert logs_filter.startswith("in.(")
    assert "uuid-a" in logs_filter and "uuid-b" in logs_filter
    assert count_filter == logs_filter


def test_list_memories_can_filter_by_session_id():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(
                payload=[
                    {
                        "id": "m1",
                        "source": "consent_event",
                        "payload": {"session_id": "session_demo"},
                        "tags": ["session:session_demo"],
                        "created_at": "2026-02-11T00:00:00Z",
                    }
                ]
            )
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    memories = store.list_memories(limit=5, session_id="session_demo")

    assert len(memories) == 1
    assert memories[0]["id"] == "m1"
    assert fake_session.calls[0]["params"]["tags"] == "cs.{session:session_demo}"


def test_list_memories_and_get_counts():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(
                payload=[
                    {
                        "id": "m1",
                        "source": "session_report",
                        "payload": {"ok": True},
                        "tags": ["x"],
                        "created_at": "2026-02-11T00:00:00Z",
                    }
                ]
            ),
            _FakeResponse(payload=[{"id": "x"}], headers={"Content-Range": "0-0/9"}),
            _FakeResponse(payload=[{"id": "x"}], headers={"Content-Range": "0-0/8"}),
            _FakeResponse(payload=[{"id": "x"}], headers={"Content-Range": "0-0/7"}),
            _FakeResponse(payload=[{"id": "x"}], headers={"Content-Range": "0-0/6"}),
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    memories = store.list_memories(limit=5)
    counts = store.get_counts()

    assert len(memories) == 1
    assert memories[0]["id"] == "m1"
    assert counts["memory_count"] == 9
    assert counts["conversation_count"] == 8
    assert counts["audit_log_count"] == 7
    assert counts["message_count"] == 6


def test_record_evolution_result_writes_payload_to_evolution_results():
    fake_session = _FakeSession(
        responses=[
            _FakeResponse(payload=[{"id": "uuid-1", "title": "conv_abc"}]),  # resolve conversation
            _FakeResponse(payload=None),  # insert evolution_results row
        ]
    )
    store = SupabasePersistence(url="https://example.supabase.co", key="k", session=fake_session)

    ok = store.record_evolution_result(
        conversation_id="conv_abc",
        result_type="chat_semantic_state",
        payload={"semantic_contradictions": [], "semantic_graph_summary": {"nodes": 2}},
    )

    assert ok is True
    insert_call = fake_session.calls[-1]
    assert insert_call["url"].endswith("/rest/v1/evolution_results")
    assert insert_call["json"]["conversation_id"] == "uuid-1"
    assert insert_call["json"]["result_type"] == "chat_semantic_state"
    assert insert_call["json"]["payload"]["semantic_graph_summary"] == {"nodes": 2}
