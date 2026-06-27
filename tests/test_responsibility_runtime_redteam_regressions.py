"""Regression tests for red-team findings (2026-06-27) against the responsibility runtime.

Bypass 1 (rt:evidence): an evidence ref / claim / scope / query made only of invisible code
points (U+200B zero-width space, U+FEFF, U+2060, U+180E) passed the strip()-only non-empty
check and reached executed — fooling the audit trail with an invisible "citation". Fixed by
_has_visible_content. These tests fail on the pre-fix validator and pass after.
"""

from __future__ import annotations

import pytest

from tonesoul.responsibility_runtime import (
    Enforcer,
    FakePolicyEngine,
    InMemoryTraceStore,
    RecordingMemoryAdapter,
    validate_intent,
)

# invisible / zero-width / format code points that str.strip() does NOT remove
INVISIBLE = ["​", "﻿", "⁠", "᠎", "‌", "‍"]


def _write(**over: object) -> dict[str, object]:
    base = {
        "intent": "memory.write.propose",
        "claim": "使用者偏好繁體中文",
        "evidence_refs": ["turn_2026_06_27_001"],
        "requested_scope": "long_term_memory",
    }
    base.update(over)
    return base


@pytest.mark.parametrize("ch", INVISIBLE)
def test_invisible_evidence_ref_is_rejected(ch: str) -> None:
    result = validate_intent(_write(evidence_refs=[ch]))
    assert result.accepted is False  # was True pre-fix (the bypass)


@pytest.mark.parametrize("ch", INVISIBLE)
def test_invisible_claim_is_rejected(ch: str) -> None:
    # the claim field had the same strip()-only weakness (red-team coverage gap)
    assert validate_intent(_write(claim=ch)).accepted is False


@pytest.mark.parametrize("ch", INVISIBLE)
def test_invisible_query_is_rejected(ch: str) -> None:
    result = validate_intent(
        {"intent": "memory.read.request", "query": ch, "requested_scope": "session_memory"}
    )
    assert result.accepted is False


def test_invisible_evidence_does_not_reach_executed_end_to_end() -> None:
    # the full-chain version of the bypass: it must now be blocked before the adapter is called
    validation = validate_intent(_write(evidence_refs=["​"]))
    decision = FakePolicyEngine().decide(validation)
    adapter = RecordingMemoryAdapter()
    enforcer = Enforcer(memory_adapter=adapter, trace_store=InMemoryTraceStore())
    result = enforcer.enforce(validation, decision)
    assert result.executed is False
    assert adapter.call_count == 0


def test_mixed_visible_and_invisible_ref_still_accepted() -> None:
    # a ref with real content plus an incidental zero-width char is fine — we reject only
    # refs that are ENTIRELY invisible, not refs that merely contain an invisible char
    assert validate_intent(_write(evidence_refs=["turn_001​"])).accepted is True


def test_no_oracle_boundary_preserved_weak_but_visible_ref_accepted() -> None:
    # the fix must NOT become a sufficiency check: a visible-but-weak ref ('x', '.') still
    # passes the FORM gate. Phase 1 validates form, never whether evidence supports the claim.
    assert validate_intent(_write(evidence_refs=["x"])).accepted is True
    assert validate_intent(_write(evidence_refs=["."])).accepted is True
