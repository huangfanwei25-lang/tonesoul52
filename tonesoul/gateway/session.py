from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from memory.genesis import Genesis, resolve_responsibility_tier


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_genesis(value: str | None, default: Genesis) -> Genesis:
    if not value:
        return default
    candidate = value.strip().lower()
    for genesis in Genesis:
        if genesis.value == candidate:
            return genesis
    return default


@dataclass(slots=True)
class GatewaySession:
    """Session contract exchanged between ToneSoul and OpenClaw gateway."""

    session_id: str
    user_id: str | None = None
    channel: str = "audit"
    genesis: Genesis = Genesis.REACTIVE_USER
    created_at: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def responsibility_tier(self) -> str:
        return resolve_responsibility_tier(self.genesis)

    def to_gateway_payload(self, event_type: str = "session_open") -> dict[str, Any]:
        return {
            "type": event_type,
            "session": {
                "session_id": self.session_id,
                "user_id": self.user_id,
                "channel": self.channel,
                "genesis": self.genesis.value,
                "responsibility_tier": self.responsibility_tier,
                "created_at": self.created_at,
                "metadata": self.metadata,
            },
        }

    @classmethod
    def from_payload(
        cls,
        payload: Mapping[str, Any],
        *,
        default_genesis: Genesis = Genesis.REACTIVE_USER,
    ) -> "GatewaySession":
        session_id = str(payload.get("session_id", "")).strip()
        if not session_id:
            raise ValueError("session_id is required")
        user_id_raw = payload.get("user_id")
        user_id = None if user_id_raw is None else str(user_id_raw)
        channel = str(payload.get("channel", "audit")).strip() or "audit"
        genesis = _parse_genesis(str(payload.get("genesis", "")), default_genesis)
        metadata_raw = payload.get("metadata")
        metadata = metadata_raw if isinstance(metadata_raw, dict) else {}
        created_at = str(payload.get("created_at", _utc_now()))
        return cls(
            session_id=session_id,
            user_id=user_id,
            channel=channel,
            genesis=genesis,
            created_at=created_at,
            metadata=metadata,
        )
