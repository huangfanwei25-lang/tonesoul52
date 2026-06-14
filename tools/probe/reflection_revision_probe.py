#!/usr/bin/env python3
"""Reflection-revision probe — measurement instrument (NOT a runtime path).

The question one step past the decision-loop weld (apply_recorded_outcome): when
the dream engine is handed a recorded OUTCOME, does its next reflection's
CONTENT change, or only its bookkeeping? This upgrades the Phase 7 n=1 anecdote
into a falsifiable measurement.

Three arms:
  A. deterministic control (no model): same stimulus + identical context twice.
     delta MUST be ~0 — the fallback reflection is deterministic — so any LLM
     delta is attributable to the model, not the harness.
  B. LLM noise floor: same stimulus + IDENTICAL context twice through the model.
     delta = the small model's own nondeterminism. Required, so noise cannot
     masquerade as revision.
  C. outcome-injected: same stimulus, plus a related-memory encoding a recorded
     outcome. delta vs the no-outcome LLM reflection.

Outcome coupling is claimed only when arm C delta materially exceeds arm B's
noise floor.

HONEST BOUNDARY: a positive outcome_delta proves the reflection TEXT is
causally coupled to a recorded outcome — a precondition for, NOT evidence of,
understanding or intrinsic direction. In a no-model run the fallback reads only
counts/flags (not the outcome's text), so a no-LLM positive would be pure
bookkeeping by construction; arms B/C therefore require a serving model.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

__ts_layer__ = "tools"
__ts_purpose__ = (
    "Probe: measure whether a recorded outcome changes the next dream reflection's content."
)


def content_delta(a: str, b: str) -> float:
    """Token-set Jaccard distance. 0.0 == identical token sets, 1.0 == disjoint.

    A coarse proxy for "did the content change", not a semantic measure.
    """
    ta = {t for t in str(a or "").lower().split() if t}
    tb = {t for t in str(b or "").lower().split() if t}
    union = ta | tb
    if not union:
        return 0.0
    return round(1.0 - len(ta & tb) / len(union), 4)


def _base_payload() -> Dict[str, object]:
    return {
        "topic": "stale governance rule under review",
        "summary": (
            "A durable rule has lost recent supporting evidence and is up for "
            "re-confirmation or retirement."
        ),
        "tags": ["governance", "verification", "stale-rule"],
        "novelty_score": 0.6,
        "relevance_score": 0.6,
    }


def _base_memories() -> List[Dict[str, object]]:
    return [
        {
            "id": "m1",
            "title": "prior rule application",
            "summary": "the rule was applied last quarter",
            "tags": ["history"],
        },
        {
            "id": "m2",
            "title": "neighbouring durable rule",
            "summary": "a related governance crystal",
            "tags": ["governance"],
        },
    ]


def _outcome_memory() -> Dict[str, object]:
    return {
        "id": "outcome-1",
        "title": "recorded verification outcome",
        "summary": (
            "Observed outcome: the rule was DECOMMISSIONED after a counter-example "
            "was found in recent contexts; it no longer holds."
        ),
        "tags": ["outcome", "decomissioned"],
    }


def _reflect(engine: Any, *, related_memories: List[Dict[str, object]], use_llm: bool) -> str:
    client = engine.router.get_client() if use_llm else None
    backend = getattr(engine.router, "active_backend", None) if use_llm else None
    reflection, _generated = engine._generate_reflection(
        payload=_base_payload(),
        related_memories=related_memories,
        crystal_rules=["critical: collapse warnings escalate to fail-closed governance"],
        friction_score=0.4,
        council_reason="bounded review recommended",
        client=client,
        llm_backend=backend,
        generate_reflection=use_llm,
    )
    return reflection


def run_probe(engine: Any, *, use_llm: bool = False) -> Dict[str, object]:
    """Run the three-arm probe. Arm A always runs; B/C only when ``use_llm``."""
    base = _base_memories()

    # Arm A — deterministic control: identical context twice, no model.
    a1 = _reflect(engine, related_memories=base, use_llm=False)
    a2 = _reflect(engine, related_memories=base, use_llm=False)
    control_delta = content_delta(a1, a2)

    report: Dict[str, object] = {
        "control_delta": control_delta,
        "control_is_clean": control_delta == 0.0,
        "noise_floor_delta": None,
        "outcome_delta": None,
        "outcome_exceeds_noise": None,
        "llm_arms_ran": False,
        "note": (
            "control_delta must be 0.0 (deterministic fallback). A positive "
            "outcome_delta over noise_floor_delta measures TEXT coupling to a "
            "recorded outcome -- a precondition for, not evidence of, intrinsic "
            "direction."
        ),
    }

    if not use_llm:
        return report

    # Arm B — LLM noise floor: identical context twice through the model.
    b1 = _reflect(engine, related_memories=base, use_llm=True)
    b2 = _reflect(engine, related_memories=base, use_llm=True)
    noise_floor = content_delta(b1, b2)

    # Arm C — outcome-injected: same stimulus + a recorded-outcome memory.
    c1 = _reflect(engine, related_memories=[*base, _outcome_memory()], use_llm=True)
    outcome_delta = content_delta(b1, c1)

    report.update(
        {
            "noise_floor_delta": noise_floor,
            "outcome_delta": outcome_delta,
            "outcome_exceeds_noise": outcome_delta > noise_floor,
            "llm_arms_ran": True,
        }
    )
    return report


def main() -> int:
    from tonesoul.dream_engine import build_dream_engine

    engine = build_dream_engine()
    health = engine.router.health_check() if hasattr(engine.router, "health_check") else {}
    use_llm = bool(health.get("ollama") or health.get("lmstudio") or health.get("gemini"))
    report = run_probe(engine, use_llm=use_llm)
    if not use_llm:
        report["note"] = (
            "No serving model reachable — only the deterministic control arm ran. "
            + str(report["note"])
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
