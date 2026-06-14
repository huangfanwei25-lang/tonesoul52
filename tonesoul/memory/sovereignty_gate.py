"""Axiom 8 (Memory Sovereignty) enforcement gate.

A8: memory is non-replicable; transfer requires explicit consent; training
requires de-identification. Until now `SOUL.memory` (MemoryConfig) had **zero
consumers** — A8 was aspirational. This gate makes it a real, fail-closed
consumer at the two points where memory actually LEAVES the user↔AI
relationship: agent-to-agent **transfer** (handoff) and **training export**.

Scope discipline (deliberately narrow): this does NOT gate first-party memory
writes (journal, dream collisions, crystallization) — those create the
relationship's OWN memory and flow through `write_gateway` untouched. The gate
fires only on egress that crosses an ownership boundary, so the revived Phase 7
dream cycle and normal sessions are unaffected. (This is why the gate is wired at
the handoff/export edges, NOT at the central `write_payload` choke point.)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from tonesoul.soul_config import SOUL, MemoryConfig

__ts_layer__ = "memory"
__ts_purpose__ = (
    "Memory sovereignty gate: enforce Axiom 8 at memory egress (transfer + training export)."
)

LOCAL_OWNER = "self"  # the user↔AI relationship is the default memory owner

# Free-text fields that may carry user PII (redacted on de-identification).
PII_TEXT_FIELDS = (
    "user_message",
    "final_response",
    "conversation_context",
    "content",
    "raw_excerpt",
    "summary",
)
# Identifier fields (SHA256-hashed on de-identification).
PII_ID_FIELDS = ("conversation_id", "session_id", "user_id", "author")


def _hash(value: str) -> str:
    """SHA256 (truncated) — the same de-id primitive used by corpus/consent.py."""
    if not value:
        return ""
    return "sha256:" + hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:32]


@dataclass
class SovereigntyVerdict:
    allowed: bool
    reasons: List[str] = field(default_factory=list)
    stamp: Dict[str, object] = field(default_factory=dict)


class MemorySovereigntyError(Exception):
    """Raised when an egress operation violates Axiom 8 (fail-closed)."""


class MemorySovereigntyGate:
    """Fail-closed enforcement of Axiom 8 (Memory Sovereignty)."""

    def __init__(
        self,
        *,
        config: Optional[MemoryConfig] = None,
        consent_lookup: Optional[Callable[[str], bool]] = None,
        owner: str = LOCAL_OWNER,
    ) -> None:
        # config injectable for testability; defaults to the live SOUL singleton.
        self.config = config or SOUL.memory
        self._consent_lookup = consent_lookup
        self._owner = owner

    def _has_consent(self, meta: Dict[str, object]) -> bool:
        """A consent token must be present AND, if a registry is wired, verified."""
        token = str(meta.get("consent_token") or "").strip()
        if not token:
            return False
        if self._consent_lookup is not None:
            try:
                return bool(self._consent_lookup(token))
            except Exception:
                return False  # fail-closed: a broken registry is not consent
        return True

    def evaluate_transfer(self, meta: Dict[str, object]) -> SovereigntyVerdict:
        """Evaluate a memory TRANSFER (e.g. a handoff) against Axiom 8.

        First-party transfer (``memory_owner`` == local owner, or unspecified) is
        allowed and stamped — this keeps existing intra-relationship handoffs and
        session boot working. A transfer that declares a DIFFERENT memory owner,
        or is flagged as a replica, requires a consent token; without one it is
        blocked (fail-closed).
        """
        owner = str(meta.get("memory_owner") or self._owner).strip() or self._owner
        is_replica = bool(meta.get("is_replica") or meta.get("replicate"))
        external = owner != self._owner
        consent = self._has_consent(meta)

        reasons: List[str] = []
        allowed = True

        if is_replica and not self.config.replication_allowed and not consent:
            allowed = False
            reasons.append(
                "replication_blocked: Axiom 8 memory is non-replicable and no consent token was provided"
            )
        if external and self.config.transfer_requires_consent and not consent:
            allowed = False
            reasons.append(
                f"transfer_blocked: Axiom 8 transfer of {owner!r} memory requires explicit consent (none provided)"
            )

        stamp = {
            "axiom": 8,
            "memory_owner": owner,
            "external_transfer": external,
            "is_replica": is_replica,
            "consent": consent,
            "transfer_requires_consent": self.config.transfer_requires_consent,
            "replication_allowed": self.config.replication_allowed,
            "verdict": "allow" if allowed else "block",
        }
        return SovereigntyVerdict(allowed=allowed, reasons=reasons, stamp=stamp)

    def deidentify(
        self,
        record: Dict[str, object],
        *,
        text_fields: Sequence[str] = PII_TEXT_FIELDS,
        id_fields: Sequence[str] = PII_ID_FIELDS,
    ) -> Dict[str, object]:
        """Return a de-identified COPY when ``training_requires_deidentification``.

        Free-text PII fields are redacted to a hash marker; identifier fields are
        SHA256-hashed. No-op (returns the record unchanged) when the flag is off,
        so de-identification is opt-out by policy, not silent.
        """
        if not self.config.training_requires_deidentification:
            return record
        out = dict(record)
        for name in text_fields:
            value = out.get(name)
            if isinstance(value, str) and value.strip():
                out[name] = f"[redacted:{_hash(value)}]"
        for name in id_fields:
            value = out.get(name)
            if value:
                out[name] = _hash(str(value))
        out["deidentified"] = True
        return out
