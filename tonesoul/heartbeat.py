from __future__ import annotations

import asyncio
import inspect
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Mapping, Optional
from uuid import uuid4

from memory.genesis import Genesis
from tonesoul.gateway import GatewayClient, GatewaySession
from tonesoul.openclaw_auditor import OpenClawAuditor, OpenClawAuditReport

__ts_layer__ = "observability"
__ts_purpose__ = (
    "Periodic heartbeat probe to validate AI session continuity."
)

CouncilCheck = Callable[[Mapping[str, Any]], Any]
SleepFunc = Callable[[float], Awaitable[None]]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _default_council_check(payload: Mapping[str, Any]) -> dict[str, Any]:
    from integrations.openclaw.skills.tonesoul import invoke_skill

    return invoke_skill("council_deliberate", payload)


@dataclass(slots=True)
class HeartbeatResult:
    cycle: int
    status: str
    heartbeat: dict[str, Any]
    gateway_envelope: dict[str, Any]
    audit: OpenClawAuditReport
    council_result: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle": self.cycle,
            "status": self.status,
            "heartbeat": self.heartbeat,
            "gateway_envelope": self.gateway_envelope,
            "audit": self.audit.to_dict(),
            "council_result": self.council_result,
        }


class ResponsibilityHeartbeat:
    """
    Heartbeat protocol runner for scheduled responsibility audits.

    Each cycle emits:
    - OpenClaw auditor report (attribute/shadow/benevolence)
    - Council periodic self-check result
    - Heartbeat envelope routed to gateway heartbeat channel
    """

    def __init__(
        self,
        *,
        node_id: str = "tonesoul52",
        interval_seconds: float = 60.0,
        protocol_version: str = "1.0",
        gateway_client: Optional[GatewayClient] = None,
        auditor: Optional[OpenClawAuditor] = None,
        council_check: Optional[CouncilCheck] = None,
        sleep_func: SleepFunc = asyncio.sleep,
    ) -> None:
        self.node_id = node_id
        self.interval_seconds = max(0.0, float(interval_seconds))
        self.protocol_version = protocol_version
        self.gateway_client = gateway_client or GatewayClient()
        self.auditor = auditor or OpenClawAuditor(persist_to_ledger=True)
        self.council_check = council_check or _default_council_check
        self._sleep = sleep_func

    async def emit_once(
        self,
        *,
        cycle: int,
        session: Optional[GatewaySession | Mapping[str, Any]] = None,
        proposed_action: str = "Scheduled responsibility audit ping.",
        context_fragments: Optional[list[str]] = None,
        council_payload: Optional[Mapping[str, Any]] = None,
    ) -> HeartbeatResult:
        heartbeat_session = self._normalize_session(session)
        effective_context = (
            [str(item) for item in context_fragments]
            if isinstance(context_fragments, list) and context_fragments
            else [proposed_action, "scheduled_task", "responsibility_audit"]
        )
        audit = self.auditor.audit(
            proposed_action,
            context_fragments=effective_context,
            action_basis="Inference",
            current_layer="L2",
            session=heartbeat_session,
            genesis_id=f"heartbeat_{cycle}",
        )
        council_result = await self._run_council_check(council_payload)
        status = self._derive_status(audit, council_result)
        heartbeat_payload = self._build_payload(
            cycle=cycle,
            status=status,
            session=heartbeat_session,
            audit=audit,
            council_result=council_result,
        )
        envelope = await self.gateway_client.send("heartbeat", heartbeat_payload)
        return HeartbeatResult(
            cycle=cycle,
            status=status,
            heartbeat=heartbeat_payload,
            gateway_envelope=envelope,
            audit=audit,
            council_result=council_result,
        )

    async def run(
        self,
        *,
        max_cycles: Optional[int] = None,
        session: Optional[GatewaySession | Mapping[str, Any]] = None,
        proposed_action: str = "Scheduled responsibility audit ping.",
        context_fragments: Optional[list[str]] = None,
        council_payload: Optional[Mapping[str, Any]] = None,
    ) -> list[HeartbeatResult]:
        if max_cycles is not None and max_cycles <= 0:
            return []
        results: list[HeartbeatResult] = []
        cycle = 0
        while True:
            cycle += 1
            result = await self.emit_once(
                cycle=cycle,
                session=session,
                proposed_action=proposed_action,
                context_fragments=context_fragments,
                council_payload=council_payload,
            )
            results.append(result)
            if max_cycles is not None and cycle >= max_cycles:
                break
            await self._sleep(self.interval_seconds)
        return results

    async def close(self) -> None:
        await self.gateway_client.close()

    def _normalize_session(
        self, session: Optional[GatewaySession | Mapping[str, Any]]
    ) -> GatewaySession:
        if isinstance(session, GatewaySession):
            return session
        if isinstance(session, Mapping):
            return GatewaySession.from_payload(session, default_genesis=Genesis.MANDATORY)
        return GatewaySession(
            session_id=f"hb_{uuid4().hex[:12]}",
            channel="heartbeat",
            genesis=Genesis.MANDATORY,
            metadata={"source": "heartbeat_cron"},
        )

    async def _run_council_check(self, payload: Optional[Mapping[str, Any]]) -> dict[str, Any]:
        request = (
            dict(payload)
            if isinstance(payload, Mapping)
            else {
                "draft_output": "Heartbeat scheduled self-check.",
                "context": {"trigger": "scheduled_task", "source": "heartbeat"},
                "user_intent": "periodic governance verification",
            }
        )
        result = self.council_check(request)
        if inspect.isawaitable(result):
            resolved = await result
        else:
            resolved = result
        return (
            resolved
            if isinstance(resolved, dict)
            else {"ok": False, "error": "invalid council result"}
        )

    def _derive_status(self, audit: OpenClawAuditReport, council_result: dict[str, Any]) -> str:
        if not audit.passed:
            return "degraded"
        if council_result.get("ok") is False:
            return "degraded"
        return "ok"

    def _build_payload(
        self,
        *,
        cycle: int,
        status: str,
        session: GatewaySession,
        audit: OpenClawAuditReport,
        council_result: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "type": "heartbeat",
            "protocol_version": self.protocol_version,
            "node_id": self.node_id,
            "timestamp": _utc_now(),
            "cycle": cycle,
            "status": status,
            "session": {
                "session_id": session.session_id,
                "channel": session.channel,
                "genesis": session.genesis.value,
                "responsibility_tier": session.responsibility_tier,
            },
            "checks": {
                "auditor_passed": audit.passed,
                "council_ok": bool(council_result.get("ok", False)),
                "requires_confirmation": audit.requires_confirmation,
            },
            "audit": audit.to_dict(),
            "council": council_result,
        }


class Heartbeat:
    """Lightweight file-backed heartbeat — works without Redis or gateway.

    Writes a pulse record to a local JSONL file on each call to `pulse()` and
    reads it back in `status()` so the result survives session restart.
    """

    import json as _json
    import os as _os
    import pathlib as _pathlib

    _DEFAULT_PATH = ".aegis/heartbeat.jsonl"

    def __init__(self, path: Optional[str] = None) -> None:
        import os
        import pathlib
        self._path = pathlib.Path(path or self._DEFAULT_PATH)
        os.makedirs(str(self._path.parent), exist_ok=True)

    def pulse(self, agent: str = "unknown", note: str = "") -> dict[str, Any]:
        import json
        record: dict[str, Any] = {
            "ts": _utc_now(),
            "agent": agent,
            "note": note,
            "id": str(uuid4()),
        }
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        return record

    def status(self) -> dict[str, Any]:
        import json
        if not self._path.exists():
            return {"alive": False, "last_pulse": None, "pulse_count": 0}
        records: list[dict[str, Any]] = []
        try:
            for line in self._path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        except Exception:
            return {"alive": False, "last_pulse": None, "pulse_count": 0, "error": "read_failed"}
        if not records:
            return {"alive": False, "last_pulse": None, "pulse_count": 0}
        last = records[-1]
        return {"alive": True, "last_pulse": last["ts"], "pulse_count": len(records), "last_agent": last.get("agent")}


__all__ = ["HeartbeatResult", "ResponsibilityHeartbeat", "Heartbeat"]
