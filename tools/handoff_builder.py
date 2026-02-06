"""
HandoffBuilder

Builds signed handoff packets for cross-agent session transfer.
"""

import json
import hmac
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import os
import sys

# Ensure we can import from repository root when executed directly.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory.genesis import Genesis
from tools.schema import ToolErrorCode, tool_error, tool_success


@dataclass
class DriftEntry:
    """Drift entry."""

    timestamp: str
    choice: str
    toward: str
    away_from: str


@dataclass
class PendingTask:
    """Pending task."""

    id: str
    description: str
    status: str  # "pending", "in_progress", "blocked"


@dataclass
class Phase:
    """Phase descriptor."""

    current: str  # e.g. "init", "plan", "implement", "test", "refactor", "handoff"
    reason: str


@dataclass
class ContextSummary:
    """Context summary."""

    user_goal: str
    key_concepts: List[str]
    current_files: List[str]
    recent_memory: Optional[List[Dict[str, Any]]] = None


@dataclass
class HandoffPacket:
    """Handoff packet."""

    version: str
    timestamp: str
    source_model: str
    target_model: str
    phase: Phase
    pending_tasks: List[PendingTask]
    drift_log: List[DriftEntry]
    context_summary: ContextSummary
    signature: Optional[Dict[str, str]] = None


class HandoffBuilder:
    """Builds and validates handoff packets."""

    VERSION = "1.0"

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize a handoff builder.

        Args:
            secret_key: Optional HMAC secret for signing packets.
        """
        self.secret_key = secret_key or self._load_secret()

    def _load_secret(self) -> str:
        """
        Load signing secret from environment.

        Uses `HANDOFF_SECRET` when provided. Otherwise falls back to a
        per-process high-entropy secret to avoid predictable signatures.
        """
        secret = os.environ.get("HANDOFF_SECRET")
        if secret:
            return secret
        print(
            "[WARN] HANDOFF_SECRET is not set; using ephemeral in-memory secret.",
            file=sys.stderr,
        )
        return secrets.token_hex(32)

    def build(
        self,
        source_model: str,
        target_model: str,
        phase: Phase,
        pending_tasks: List[PendingTask],
        drift_log: List[DriftEntry],
        context_summary: ContextSummary,
    ) -> HandoffPacket:
        """
        Build a handoff packet.

        Returns:
            HandoffPacket with computed signature.
        """
        packet = HandoffPacket(
            version=self.VERSION,
            timestamp=datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            source_model=source_model,
            target_model=target_model,
            phase=phase,
            pending_tasks=pending_tasks,
            drift_log=drift_log,
            context_summary=context_summary,
        )

        # Sign packet
        packet.signature = self._sign(packet)

        return packet

    def _sign(self, packet: HandoffPacket) -> Dict[str, str]:
        """Sign packet using HMAC-SHA256."""
        # Remove signature for canonical hashing
        packet_dict = asdict(packet)
        packet_dict.pop("signature", None)

        # Serialize canonical JSON for hashing
        canonical = json.dumps(packet_dict, sort_keys=True, ensure_ascii=False)

        # Compute HMAC
        signature = hmac.new(
            self.secret_key.encode(), canonical.encode(), hashlib.sha256
        ).hexdigest()

        return {"algorithm": "HMAC-SHA256", "hash": signature}

    def verify(self, packet: HandoffPacket) -> bool:
        """Verify packet signature."""
        if not packet.signature:
            return False

        expected = self._sign(packet)
        return hmac.compare_digest(expected["hash"], packet.signature.get("hash", ""))

    def persist(self, packet: HandoffPacket, path: Optional[Path] = None) -> Path:
        """
        Persist handoff packet to disk.

        Args:
            packet: Packet to persist.
            path: Optional directory (default: memory/handoff/).

        Returns:
            Path to saved packet.
        """
        if path is None:
            path = Path("memory/handoff")

        path.mkdir(parents=True, exist_ok=True)

        filename = f"handoff_{packet.timestamp.replace(':', '-').replace('.', '-')}.json"
        filepath = path / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(asdict(packet), f, ensure_ascii=False, indent=2)

        return filepath

    def load(self, filepath: Path) -> HandoffPacket:
        """Load a handoff packet from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        return HandoffPacket(
            version=data["version"],
            timestamp=data["timestamp"],
            source_model=data["source_model"],
            target_model=data["target_model"],
            phase=Phase(**data["phase"]),
            pending_tasks=[PendingTask(**t) for t in data["pending_tasks"]],
            drift_log=[DriftEntry(**d) for d in data["drift_log"]],
            context_summary=ContextSummary(**data["context_summary"]),
            signature=data.get("signature"),
        )


# ToolResponse wrappers

def build_tool_response(
    builder: "HandoffBuilder",
    source_model: str,
    target_model: str,
    phase: "Phase",
    pending_tasks: List["PendingTask"],
    drift_log: List["DriftEntry"],
    context_summary: "ContextSummary",
    genesis: Genesis = Genesis.REACTIVE_USER,
) -> Dict[str, Any]:
    try:
        packet = builder.build(
            source_model=source_model,
            target_model=target_model,
            phase=phase,
            pending_tasks=pending_tasks,
            drift_log=drift_log,
            context_summary=context_summary,
        )
        return tool_success(
            data={"packet": asdict(packet)},
            genesis=genesis,
            intent_id=None,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=genesis,
        )


def persist_tool_response(
    builder: "HandoffBuilder",
    packet: "HandoffPacket",
    path: Optional[Path] = None,
    genesis: Genesis = Genesis.REACTIVE_USER,
) -> Dict[str, Any]:
    try:
        filepath = builder.persist(packet, path)
        return tool_success(
            data={"path": str(filepath)},
            genesis=genesis,
            intent_id=None,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=genesis,
        )


def load_tool_response(
    builder: "HandoffBuilder",
    filepath: Path,
    genesis: Genesis = Genesis.REACTIVE_USER,
) -> Dict[str, Any]:
    try:
        packet = builder.load(filepath)
        return tool_success(
            data={"packet": asdict(packet)},
            genesis=genesis,
            intent_id=None,
        )
    except Exception as exc:
        return tool_error(
            code=ToolErrorCode.INTERNAL_ERROR,
            message=str(exc),
            genesis=genesis,
        )

if __name__ == "__main__":
    builder = HandoffBuilder()
    packet = builder.build(
        source_model="antigravity",
        target_model="codex",
        phase=Phase(current="demo", reason="manual run"),
        pending_tasks=[],
        drift_log=[],
        context_summary=ContextSummary(
            user_goal="demo",
            key_concepts=["handoff"],
            current_files=[__file__],
        ),
    )
    print(f"Packet valid: {builder.verify(packet)}")
