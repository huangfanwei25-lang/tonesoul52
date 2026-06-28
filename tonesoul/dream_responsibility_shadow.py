"""Shadow-mode responsibility gate for dream-cycle memory writes.

OBSERVE-ONLY. This runs the ``responsibility_runtime`` gate (validate -> policy -> enforce, with a
fake adapter + in-memory trace) against a dream collision payload to RECORD what the gate WOULD
decide for that durable write. It never performs the real write and never blocks it.

This is a measurement surface, not an enforcement boundary. It makes NO claim that memory is
gated, non-bypassable, or that the gate "perceives" anything. The real write keeps flowing through
``MemoryWriteGateway.write_payload`` unchanged (Axiom 8 records that path as intentionally
un-gated); enforce-mode is a separate, owner-authorized decision.

Governance record: docs/plans/responsibility_runtime_dream_shadow_wiring_2026-06-29.md
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    decide_fail_closed,
    validate_intent,
)

__ts_layer__ = "evolution"
__ts_purpose__ = (
    "Observe-only responsibility-gate shadow for dream-cycle memory writes "
    "(measurement, not enforcement)."
)

USES_LLM = False
USES_NETWORK = False

# Dream collisions persist as durable subjectivity records, so the proposed scope is long-term.
_DREAM_SCOPE = "long_term_memory"
# Cap evidence refs so a pathological payload cannot make the shadow intent unbounded.
_MAX_EVIDENCE_REFS = 16


@dataclass(frozen=True)
class ShadowGateOutcome:
    """What the responsibility gate WOULD decide for a real memory write (observe-only).

    ``would_execute is None`` means the gate could not run (translation/gate error); the real
    write is unaffected regardless.
    """

    ran: bool
    would_execute: bool | None
    request_id: str | None
    intent: str
    reason: str
    issue_codes: tuple[str, ...]
    error: str | None = None

    def to_observability(self) -> dict[str, Any]:
        """Annotation that travels WITH the persisted memory record."""

        return {
            "mode": "shadow",
            "note": "observe-only; did not gate or block the real write",
            "ran": self.ran,
            "would_execute": self.would_execute,
            "request_id": self.request_id,
            "intent": self.intent,
            "reason": self.reason,
            "issue_codes": list(self.issue_codes),
            "error": self.error,
        }


def collision_payload_to_intent(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Best-effort (LOSSY) translation of a dream collision payload to a memory.write.propose intent.

    The collision uses a world-facing schema; the gate expects
    ``{intent, claim, evidence_refs, requested_scope}``. Because this translation is lossy, the
    shadow gate judges a *sanitized projection* of the real write — one reason this can only be
    measurement, not enforcement.
    """

    claim = ""
    for key in ("summary", "reflection", "title", "topic"):
        value = str(payload.get(key) or "").strip()
        if value:
            claim = value
            break

    evidence_refs: list[str] = []
    raw_evidence = payload.get("evidence")
    if isinstance(raw_evidence, list):
        for item in raw_evidence:
            text = str(item or "").strip()
            if text:
                evidence_refs.append(text)
    stimulus = str(payload.get("stimulus_record_id") or "").strip()
    if stimulus:
        evidence_refs.append(f"stimulus:{stimulus}")
    source_ids = payload.get("source_record_ids")
    if isinstance(source_ids, list):
        for sid in source_ids:
            text = str(sid or "").strip()
            if text:
                evidence_refs.append(f"source:{text}")

    return {
        "intent": "memory.write.propose",
        "requested_scope": _DREAM_SCOPE,
        "claim": claim,
        "evidence_refs": evidence_refs[:_MAX_EVIDENCE_REFS],
    }


def run_shadow_gate(payload: Mapping[str, Any]) -> ShadowGateOutcome:
    """Run the responsibility gate in observe-only mode over a collision payload.

    Fully isolated: any error is captured into the returned outcome (``ran=False``, ``error=...``)
    and never raised, so the caller's real write path is never affected. Uses a fake adapter and an
    in-memory trace; performs no real write.
    """

    try:
        intent_payload = collision_payload_to_intent(payload)
        validation = validate_intent(intent_payload)
        decision = decide_fail_closed(FakePolicyEngine(), validation)
        enforcer = Enforcer(
            memory_adapter=RecordingMemoryAdapter(),
            trace_store=InMemoryTraceStore(),
        )
        result = enforcer.enforce(validation, decision)
        return ShadowGateOutcome(
            ran=True,
            would_execute=result.executed,
            request_id=result.request_id,
            intent=result.intent,
            reason=result.reason,
            issue_codes=tuple(issue.code for issue in validation.issues),
        )
    except Exception as exc:  # isolation: shadow must NEVER affect the real write
        return ShadowGateOutcome(
            ran=False,
            would_execute=None,
            request_id=None,
            intent="memory.write.propose",
            reason=f"shadow gate error: {type(exc).__name__}",
            issue_codes=(),
            error=f"{type(exc).__name__}: {exc}",
        )


@dataclass
class ShadowLedger:
    """Accumulates shadow outcomes vs. the real write result for a dream cycle (measurement)."""

    entries: list[dict[str, Any]] = field(default_factory=list)

    def record(
        self,
        outcome: ShadowGateOutcome,
        *,
        actual_written: bool,
        topic: str = "",
    ) -> None:
        agrees: bool | None
        if outcome.would_execute is None:
            agrees = None
        else:
            # "perceptual localization": does the gate's judgment match what reality did?
            agrees = outcome.would_execute == actual_written
        self.entries.append(
            {
                "topic": topic,
                "ran": outcome.ran,
                "would_execute": outcome.would_execute,
                "actual_written": actual_written,
                "agrees": agrees,
                "gate_reason": outcome.reason,
                "issue_codes": list(outcome.issue_codes),
            }
        )

    def summary(self) -> dict[str, Any]:
        total = len(self.entries)
        would_allow = sum(1 for e in self.entries if e["would_execute"] is True)
        would_deny = sum(1 for e in self.entries if e["would_execute"] is False)
        errored = sum(1 for e in self.entries if not e["ran"])
        diverged = [e for e in self.entries if e["agrees"] is False]
        return {
            "mode": "shadow",
            "note": "observe-only measurement; the gate did not block any real write",
            "total": total,
            "would_allow": would_allow,
            "would_deny": would_deny,
            "errored": errored,
            "diverged_count": len(diverged),
            "diverged": diverged,
        }
