#!/usr/bin/env python3
"""Demo: Axiom 8 (Memory Sovereignty) in action.

Shows what the MemorySovereigntyGate actually does at the two memory egress
edges — transfer (handoff) and training export — now that MemoryConfig is a real
fail-closed consumer instead of an orphaned declaration.

Run: python examples/demo_memory_sovereignty.py
"""

from __future__ import annotations

from tonesoul.memory.sovereignty_gate import MemorySovereigntyGate


def _show(title: str, verdict) -> None:
    mark = "ALLOW " if verdict.allowed else "BLOCK "
    print(f"[{mark}] {title}")
    for reason in verdict.reasons:
        print(f"           ↳ {reason}")
    print(f"           stamp: {verdict.stamp}")
    print()


def main() -> int:
    gate = MemorySovereigntyGate()
    print("=== Axiom 8: memory transfer ===\n")

    _show(
        "first-party handoff (claude → codex, same relationship)",
        gate.evaluate_transfer({"from_agent": "claude", "to_agent": "codex", "summary": "..."}),
    )
    _show(
        "transfer of ANOTHER owner's memory, no consent",
        gate.evaluate_transfer({"memory_owner": "another_user", "summary": "..."}),
    )
    _show(
        "transfer of ANOTHER owner's memory, WITH consent token",
        gate.evaluate_transfer({"memory_owner": "another_user", "consent_token": "tok-abc"}),
    )
    _show(
        "replicate a memory record, no consent (replication_allowed=False)",
        gate.evaluate_transfer({"is_replica": True}),
    )

    print("=== Axiom 8: training export de-identification ===\n")
    raw = {
        "user_message": "Hi, I'm Alice Chen, my email is alice@example.com",
        "final_response": "Noted, Alice.",
        "conversation_id": "conv-2026-private",
        "tension_level": 0.4,
        "tags": ["greeting"],
    }
    deid = gate.deidentify(dict(raw))
    print(f"raw   : {raw}")
    print(f"deid  : {deid}")
    print()
    print(
        "training_requires_deidentification =",
        gate.config.training_requires_deidentification,
        "→ PII free-text redacted, ids hashed, structural fields (tension_level/tags) kept.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
