#!/usr/bin/env python3
"""
ToneSoul Quickstart Demo
========================
Run this to see the core governance loop in action — zero external services needed.

    python examples/quickstart.py

What it demonstrates:
    1. Load governance state (Soul Integral, vows, tension history)
    2. TSR semantic tension scoring
    3. POAV output quality scoring
    4. Vow enforcement (honesty / hedging / harm checks)
    5. Council deliberation (4 perspectives vote on draft output)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pathlib import Path


def divider(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main() -> None:
    sample_text = (
        "Based on the server logs from 2026-04-13, the API latency increased by 23% "
        "after the v2.1 deployment. I recommend rolling back to v2.0 until we identify "
        "the root cause. However, I'm not fully certain whether the latency spike is "
        "correlated with the deployment or the concurrent DDoS mitigation."
    )

    print("ToneSoul / 語魂 — Governance Demo")
    print(f'Input: "{sample_text[:80]}..."')

    # ── Step 1: Load governance state ──────────────────────────
    divider("Step 1: Governance State")
    from tonesoul.runtime_adapter import load

    posture = load(state_path=Path("governance_state.json"))
    print(f"  Soul Integral:    {posture.soul_integral:.4f}")
    print(f"  Active Vows:      {len(posture.active_vows)}")
    print(f"  Session Count:    {posture.session_count}")
    print(
        f"  Risk Posture:     {posture.risk_posture.get('level', 'unknown') if isinstance(posture.risk_posture, dict) else posture.risk_posture}"
    )

    # ── Step 2: TSR tension scoring ────────────────────────────
    divider("Step 2: TSR (Tension / Sentiment / Range)")
    from tonesoul.tsr_metrics import score as tsr_score

    tsr = tsr_score(sample_text)
    t = tsr["tsr"]
    print(f"  Tension  (T):     {t['T']:.3f}  (0=calm, 1=high conflict)")
    print(f"  Sentiment(S):     {t['S']:.3f}  (-1=negative, +1=positive)")
    print(f"  Range    (R):     {t['R']:.3f}  (semantic variability)")
    print(f"  Energy Radius:    {t['energy_radius']:.3f}")

    # ── Step 3: POAV quality scoring ───────────────────────────
    divider("Step 3: POAV (Parsimony / Orthogonality / Audibility / Verifiability)")
    from tonesoul.poav import score as poav_score

    poav = poav_score(sample_text)
    print(f"  Parsimony:        {poav['parsimony']:.3f}  (brevity)")
    print(f"  Orthogonality:    {poav['orthogonality']:.3f}  (non-redundancy)")
    print(f"  Audibility:       {poav['audibility']:.3f}  (clarity)")
    print(f"  Verifiability:    {poav['verifiability']:.3f}  (evidence density)")
    print(f"  Total:            {poav['total']:.3f}")

    # ── Step 4: Vow enforcement ────────────────────────────────
    divider("Step 4: Vow Enforcement")
    from tonesoul.vow_system import check_vows

    vow_result = check_vows(sample_text)
    status = "PASS" if vow_result.all_passed else "BLOCKED"
    print(f"  Result:           {status}")
    print(f"  Blocked:          {vow_result.blocked}")
    print(f"  Repair Needed:    {vow_result.repair_needed}")
    for r in vow_result.results:
        icon = "o" if r.passed else "x"
        print(
            f"    [{icon}] {r.vow_id}: score={r.score:.2f} (threshold={r.threshold}) → {r.action.value}"
        )

    # ── Step 5: Council deliberation ───────────────────────────
    divider("Step 5: Council Deliberation (4 perspectives)")
    from tonesoul.council.pre_output_council import PreOutputCouncil

    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output=sample_text,
        context={"language": "en", "topic": "incident-response"},
        user_intent="diagnose API latency issue",
        auto_record_self_memory=False,
    )
    print(f"  Verdict:          {verdict.verdict.value}")
    print(f"  Coherence:        {verdict.coherence.overall:.3f}")
    if verdict.human_summary:
        print(f"  Summary:          {verdict.human_summary[:120]}")
    for vote in verdict.votes:
        print(
            f"    [{vote.perspective.value}] {vote.decision.value} (confidence={vote.confidence:.2f})"
        )

    # ── Summary ────────────────────────────────────────────────
    divider("Summary")
    print(f"  Governance loaded:  SI={posture.soul_integral:.4f}")
    print(f"  Tension detected:   T={t['T']:.3f}")
    print(f"  Output quality:     POAV={poav['total']:.3f}")
    print(f"  Vow check:          {'PASS' if vow_result.all_passed else 'FAIL'}")
    print(f"  Council verdict:    {verdict.verdict.value}")
    print()
    print("Every decision is traceable. Every output is auditable.")
    print("That is ToneSoul.")


if __name__ == "__main__":
    main()
