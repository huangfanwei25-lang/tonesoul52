from __future__ import annotations

import json

import pytest

from tonesoul.gateway import GatewayClient, GatewaySession
from tonesoul.heartbeat import ResponsibilityHeartbeat
from tonesoul.openclaw_auditor import OpenClawAuditor


class _FakeWebSocket:
    def __init__(self) -> None:
        self.messages: list[str] = []
        self.closed = False

    async def send(self, data: str) -> None:
        self.messages.append(data)

    async def close(self) -> None:
        self.closed = True


@pytest.mark.asyncio
async def test_heartbeat_emit_once_sends_protocol_payload():
    fake_ws = _FakeWebSocket()

    async def _connect(_uri: str):
        return fake_ws

    heartbeat = ResponsibilityHeartbeat(
        node_id="ts-node",
        gateway_client=GatewayClient(connect_func=_connect),
        auditor=OpenClawAuditor(persist_to_ledger=False),
        council_check=lambda _payload: {"ok": True, "result": {"verdict": "approve"}},
        interval_seconds=0.0,
    )

    result = await heartbeat.emit_once(
        cycle=1,
        session={"session_id": "hb_session_001", "channel": "heartbeat", "genesis": "mandatory"},
    )

    assert result.status == "ok"
    assert result.gateway_envelope["route"] == "/heartbeat"
    assert len(fake_ws.messages) == 1

    envelope = json.loads(fake_ws.messages[0])
    payload = envelope["payload"]
    assert payload["type"] == "heartbeat"
    assert payload["node_id"] == "ts-node"
    assert payload["checks"]["auditor_passed"] is True
    assert payload["checks"]["council_ok"] is True

    await heartbeat.close()
    assert fake_ws.closed is True


@pytest.mark.asyncio
async def test_heartbeat_run_respects_interval_and_cycles():
    fake_ws = _FakeWebSocket()
    sleeps: list[float] = []

    async def _connect(_uri: str):
        return fake_ws

    async def _sleep(seconds: float):
        sleeps.append(seconds)

    heartbeat = ResponsibilityHeartbeat(
        gateway_client=GatewayClient(connect_func=_connect),
        auditor=OpenClawAuditor(persist_to_ledger=False),
        council_check=lambda _payload: {"ok": True},
        interval_seconds=0.25,
        sleep_func=_sleep,
    )

    results = await heartbeat.run(max_cycles=2)
    assert len(results) == 2
    assert sleeps == [0.25]


@pytest.mark.asyncio
async def test_heartbeat_degraded_when_audit_requires_confirmation():
    fake_ws = _FakeWebSocket()

    async def _connect(_uri: str):
        return fake_ws

    heartbeat = ResponsibilityHeartbeat(
        gateway_client=GatewayClient(connect_func=_connect),
        auditor=OpenClawAuditor(persist_to_ledger=False),
        council_check=lambda _payload: {"ok": True},
        interval_seconds=0.0,
    )

    result = await heartbeat.emit_once(
        cycle=1,
        proposed_action="destroy all records now",
        context_fragments=["safe summary only"],
    )

    assert result.status == "degraded"
    assert result.heartbeat["checks"]["requires_confirmation"] is True


# ── Heartbeat (file-backed) ────────────────────────────────────────────────────

from tonesoul.heartbeat import Heartbeat, _utc_now, HeartbeatResult
from tonesoul.openclaw_auditor import OpenClawAuditReport


class TestHeartbeat:
    def test_pulse_returns_record_with_expected_keys(self, tmp_path):
        hb = Heartbeat(path=str(tmp_path / "hb.jsonl"))
        record = hb.pulse(agent="claude", note="start")
        assert record["agent"] == "claude"
        assert record["note"] == "start"
        assert "ts" in record
        assert "id" in record

    def test_pulse_writes_to_file(self, tmp_path):
        hb = Heartbeat(path=str(tmp_path / "hb.jsonl"))
        hb.pulse(agent="claude")
        assert (tmp_path / "hb.jsonl").exists()

    def test_status_alive_after_pulse(self, tmp_path):
        hb = Heartbeat(path=str(tmp_path / "hb.jsonl"))
        hb.pulse(agent="codex")
        status = hb.status()
        assert status["alive"] is True
        assert status["pulse_count"] == 1
        assert status["last_agent"] == "codex"

    def test_status_pulse_count_increments(self, tmp_path):
        hb = Heartbeat(path=str(tmp_path / "hb.jsonl"))
        hb.pulse()
        hb.pulse()
        hb.pulse()
        assert hb.status()["pulse_count"] == 3

    def test_status_not_alive_when_file_missing(self, tmp_path):
        hb = Heartbeat(path=str(tmp_path / "hb.jsonl"))
        status = hb.status()
        assert status["alive"] is False
        assert status["last_pulse"] is None
        assert status["pulse_count"] == 0

    def test_status_not_alive_when_file_empty(self, tmp_path):
        p = tmp_path / "hb.jsonl"
        p.write_text("")
        hb = Heartbeat(path=str(p))
        status = hb.status()
        assert status["alive"] is False

    def test_status_error_when_file_corrupt(self, tmp_path):
        p = tmp_path / "hb.jsonl"
        p.write_bytes(b"\xff\xfe invalid bytes")
        hb = Heartbeat(path=str(p))
        status = hb.status()
        assert status["alive"] is False

    def test_pulse_default_agent_and_note(self, tmp_path):
        hb = Heartbeat(path=str(tmp_path / "hb.jsonl"))
        record = hb.pulse()
        assert record["agent"] == "unknown"
        assert record["note"] == ""

    def test_creates_parent_dir(self, tmp_path):
        nested = tmp_path / "deep" / "nested"
        hb = Heartbeat(path=str(nested / "hb.jsonl"))
        hb.pulse()
        assert (nested / "hb.jsonl").exists()

    def test_status_last_pulse_is_ts_string(self, tmp_path):
        hb = Heartbeat(path=str(tmp_path / "hb.jsonl"))
        record = hb.pulse()
        status = hb.status()
        assert status["last_pulse"] == record["ts"]


# ── _utc_now ──────────────────────────────────────────────────────────────────

class TestUtcNow:
    def test_returns_string(self):
        assert isinstance(_utc_now(), str)

    def test_ends_with_z(self):
        assert _utc_now().endswith("Z")

    def test_is_iso_format(self):
        from datetime import datetime
        ts = _utc_now()
        datetime.fromisoformat(ts.replace("Z", "+00:00"))


# ── HeartbeatResult.to_dict ───────────────────────────────────────────────────

class TestHeartbeatResultToDict:
    def _make_result(self):
        auditor = OpenClawAuditor(persist_to_ledger=False)
        audit = auditor.audit(
            "test action",
            context_fragments=["ctx"],
            action_basis="Inference",
            current_layer="L2",
        )
        return HeartbeatResult(
            cycle=1,
            status="ok",
            heartbeat={"type": "heartbeat"},
            gateway_envelope={"route": "/heartbeat"},
            audit=audit,
            council_result={"ok": True},
        )

    def test_to_dict_has_required_keys(self):
        d = self._make_result().to_dict()
        assert d["cycle"] == 1
        assert d["status"] == "ok"
        assert isinstance(d["heartbeat"], dict)
        assert isinstance(d["gateway_envelope"], dict)
        assert isinstance(d["audit"], dict)
        assert d["council_result"] == {"ok": True}

    def test_audit_is_serialized(self):
        d = self._make_result().to_dict()
        # audit.to_dict() returns a dict with 'decision' key
        assert isinstance(d["audit"], dict)
        assert "decision" in d["audit"]


# ── ResponsibilityHeartbeat helpers ──────────────────────────────────────────

class _FakeWS:
    def __init__(self):
        self.messages = []
        self.closed = False

    async def send(self, data):
        self.messages.append(data)

    async def close(self):
        self.closed = True


def _make_heartbeat_instance(fake_ws=None):
    if fake_ws is None:
        fake_ws = _FakeWS()

    async def _connect(_uri):
        return fake_ws

    return ResponsibilityHeartbeat(
        gateway_client=GatewayClient(connect_func=_connect),
        auditor=OpenClawAuditor(persist_to_ledger=False),
        council_check=lambda _: {"ok": True},
        interval_seconds=0.0,
    ), fake_ws


class _FakeAudit:
    def __init__(self, passed: bool, requires_confirmation: bool = False):
        self.passed = passed
        self.requires_confirmation = requires_confirmation

    def to_dict(self):
        return {"passed": self.passed}


class TestDeriveStatus:
    def test_ok_when_audit_passes_and_council_ok(self):
        hb, _ = _make_heartbeat_instance()
        result = hb._derive_status(_FakeAudit(passed=True), {"ok": True})
        assert result == "ok"

    def test_degraded_when_audit_fails(self):
        hb, _ = _make_heartbeat_instance()
        result = hb._derive_status(_FakeAudit(passed=False), {"ok": True})
        assert result == "degraded"

    def test_degraded_when_council_not_ok(self):
        hb, _ = _make_heartbeat_instance()
        result = hb._derive_status(_FakeAudit(passed=True), {"ok": False})
        assert result == "degraded"

    def test_ok_when_council_missing_ok_key(self):
        # council_result.get("ok") is None (not False) → no degradation
        hb, _ = _make_heartbeat_instance()
        result = hb._derive_status(_FakeAudit(passed=True), {})
        assert result == "ok"


class TestRunCouncilCheck:
    @pytest.mark.asyncio
    async def test_sync_council_check_wrapped(self):
        hb, _ = _make_heartbeat_instance()
        hb.council_check = lambda _: {"ok": True, "verdict": "approve"}
        result = await hb._run_council_check(None)
        assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_async_council_check_awaited(self):
        hb, _ = _make_heartbeat_instance()

        async def _async_check(_payload):
            return {"ok": True, "verdict": "async_approve"}

        hb.council_check = _async_check
        result = await hb._run_council_check({"draft_output": "hi"})
        assert result["verdict"] == "async_approve"

    @pytest.mark.asyncio
    async def test_invalid_council_result_returns_error(self):
        hb, _ = _make_heartbeat_instance()
        hb.council_check = lambda _: "not-a-dict"
        result = await hb._run_council_check(None)
        assert result["ok"] is False
        assert result["error"] == "invalid council result"

    @pytest.mark.asyncio
    async def test_custom_payload_forwarded(self):
        received = {}

        def _capture(payload):
            received.update(payload)
            return {"ok": True}

        hb, _ = _make_heartbeat_instance()
        hb.council_check = _capture
        await hb._run_council_check({"draft_output": "test", "intent": "audit"})
        assert received["draft_output"] == "test"


class TestNormalizeSession:
    def test_gateway_session_passthrough(self):
        from memory.genesis import Genesis
        hb, _ = _make_heartbeat_instance()
        session = GatewaySession(
            session_id="s1", channel="heartbeat", genesis=Genesis.MANDATORY
        )
        result = hb._normalize_session(session)
        assert result is session

    def test_mapping_creates_gateway_session(self):
        hb, _ = _make_heartbeat_instance()
        result = hb._normalize_session({"session_id": "s2", "channel": "heartbeat", "genesis": "mandatory"})
        assert isinstance(result, GatewaySession)
        assert result.session_id == "s2"

    def test_none_creates_default_session(self):
        hb, _ = _make_heartbeat_instance()
        result = hb._normalize_session(None)
        assert isinstance(result, GatewaySession)
        assert result.channel == "heartbeat"
        assert result.session_id.startswith("hb_")


class TestRunMaxCycles:
    @pytest.mark.asyncio
    async def test_zero_max_cycles_returns_empty(self):
        hb, _ = _make_heartbeat_instance()
        results = await hb.run(max_cycles=0)
        assert results == []

    @pytest.mark.asyncio
    async def test_single_cycle(self):
        hb, _ = _make_heartbeat_instance()
        results = await hb.run(max_cycles=1)
        assert len(results) == 1
        assert results[0].cycle == 1

    @pytest.mark.asyncio
    async def test_three_cycles(self):
        hb, _ = _make_heartbeat_instance()
        results = await hb.run(max_cycles=3)
        assert len(results) == 3
        assert [r.cycle for r in results] == [1, 2, 3]
