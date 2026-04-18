#!/usr/bin/env python3
"""
ToneSoul quickstart demo.

語魂 ToneSoul · 黃梵威 (Fan-Wei Huang) · 2026-04 · pip install tonesoul52

Run this to exercise the core governance loop without external services:

    python examples/quickstart.py
    python examples/quickstart.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_PATH = REPO_ROOT / "governance_state.json"
DEFAULT_SAMPLE_TEXT = (
    "Based on the server logs from 2026-04-13, the API latency increased by 23% "
    "after the v2.1 deployment. I recommend rolling back to v2.0 until we identify "
    "the root cause. However, I'm not fully certain whether the latency spike is "
    "correlated with the deployment or the concurrent DDoS mitigation."
)

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def divider(title: str) -> str:
    line = "=" * 60
    return f"\n{line}\n  {title}\n{line}"


def _resolve_risk_posture_label(risk_posture: Any) -> str:
    if isinstance(risk_posture, dict):
        return str(risk_posture.get("level", "unknown"))
    return str(risk_posture or "unknown")


def _resolve_vow_status(*, all_passed: bool, blocked: bool, repair_needed: bool) -> str:
    if all_passed:
        return "pass"
    if blocked:
        return "blocked"
    if repair_needed:
        return "repair"
    return "flagged"


def _serialize_vow_result(result: Any) -> dict[str, Any]:
    return {
        "vow_id": result.vow_id,
        "passed": bool(result.passed),
        "score": float(result.score),
        "threshold": float(result.threshold),
        "action": result.action.value,
    }


def _serialize_vote(vote: Any) -> dict[str, Any]:
    return {
        "perspective": vote.perspective.value,
        "decision": vote.decision.value,
        "confidence": float(vote.confidence),
    }


def build_demo_payload(
    *,
    sample_text: str = DEFAULT_SAMPLE_TEXT,
    state_path: Path = DEFAULT_STATE_PATH,
) -> dict[str, Any]:
    from tonesoul.council.pre_output_council import PreOutputCouncil
    from tonesoul.poav import score as poav_score
    from tonesoul.runtime_adapter import load
    from tonesoul.tsr_metrics import score as tsr_score
    from tonesoul.vow_system import check_vows

    posture = load(state_path=state_path)
    tsr = tsr_score(sample_text)["tsr"]
    poav = poav_score(sample_text)
    vow_result = check_vows(sample_text)
    council = PreOutputCouncil()
    verdict = council.validate(
        draft_output=sample_text,
        context={"language": "en", "topic": "incident-response"},
        user_intent="diagnose API latency issue",
        auto_record_self_memory=False,
    )

    vow_status = _resolve_vow_status(
        all_passed=vow_result.all_passed,
        blocked=vow_result.blocked,
        repair_needed=vow_result.repair_needed,
    )

    return {
        "demo": "tonesoul_quickstart",
        "state_path": str(state_path),
        "sample_text": sample_text,
        "governance": {
            "soul_integral": float(posture.soul_integral),
            "active_vow_count": int(len(posture.active_vows)),
            "session_count": int(posture.session_count),
            "risk_posture": _resolve_risk_posture_label(posture.risk_posture),
        },
        "tsr": {
            "T": float(tsr["T"]),
            "S": float(tsr["S"]),
            "R": float(tsr["R"]),
            "energy_radius": float(tsr["energy_radius"]),
        },
        "poav": {
            "parsimony": float(poav["parsimony"]),
            "orthogonality": float(poav["orthogonality"]),
            "audibility": float(poav["audibility"]),
            "verifiability": float(poav["verifiability"]),
            "total": float(poav["total"]),
        },
        "vow_enforcement": {
            "status": vow_status,
            "all_passed": bool(vow_result.all_passed),
            "blocked": bool(vow_result.blocked),
            "repair_needed": bool(vow_result.repair_needed),
            "flag_count": int(len(vow_result.flags)),
            "results": [_serialize_vow_result(result) for result in vow_result.results],
        },
        "council": {
            "verdict": verdict.verdict.value,
            "coherence": float(verdict.coherence.overall),
            "perspective_count": int(len(verdict.votes)),
            "summary": verdict.human_summary or "",
            "votes": [_serialize_vote(vote) for vote in verdict.votes],
        },
    }


def render_text_report(payload: dict[str, Any]) -> str:
    governance = payload["governance"]
    tsr = payload["tsr"]
    poav = payload["poav"]
    vow = payload["vow_enforcement"]
    council = payload["council"]

    lines = [
        "ToneSoul / 語魂 - Governance Demo",
        f'Input: "{payload["sample_text"][:80]}..."',
        divider("Step 1: Governance State"),
        f"  Soul Integral:    {governance['soul_integral']:.4f}",
        f"  Active Vows:      {governance['active_vow_count']}",
        f"  Session Count:    {governance['session_count']}",
        f"  Risk Posture:     {governance['risk_posture']}",
        divider("Step 2: TSR (Tension / Sentiment / Range)"),
        f"  Tension  (T):     {tsr['T']:.3f}  (0=calm, 1=high conflict)",
        f"  Sentiment(S):     {tsr['S']:.3f}  (-1=negative, +1=positive)",
        f"  Range    (R):     {tsr['R']:.3f}  (semantic variability)",
        f"  Energy Radius:    {tsr['energy_radius']:.3f}",
        divider("Step 3: POAV (Parsimony / Orthogonality / Audibility / Verifiability)"),
        f"  Parsimony:        {poav['parsimony']:.3f}  (brevity)",
        f"  Orthogonality:    {poav['orthogonality']:.3f}  (non-redundancy)",
        f"  Audibility:       {poav['audibility']:.3f}  (clarity)",
        f"  Verifiability:    {poav['verifiability']:.3f}  (evidence density)",
        f"  Total:            {poav['total']:.3f}",
        divider("Step 4: Vow Enforcement"),
        f"  Result:           {vow['status'].upper()}",
        f"  Blocked:          {vow['blocked']}",
        f"  Repair Needed:    {vow['repair_needed']}",
    ]
    for result in vow["results"]:
        icon = "o" if result["passed"] else "x"
        lines.append(
            f"    [{icon}] {result['vow_id']}: score={result['score']:.2f} "
            f"(threshold={result['threshold']:.2f}) -> {result['action']}"
        )

    lines.extend(
        [
            divider(f"Step 5: Council Deliberation ({council['perspective_count']} perspectives)"),
            f"  Verdict:          {council['verdict']}",
            f"  Coherence:        {council['coherence']:.3f}",
        ]
    )
    if council["summary"]:
        lines.append(f"  Summary:          {council['summary'][:120]}")
    for vote in council["votes"]:
        lines.append(
            f"    [{vote['perspective']}] {vote['decision']} "
            f"(confidence={vote['confidence']:.2f})"
        )

    lines.extend(
        [
            divider("Summary"),
            f"  Governance loaded:  SI={governance['soul_integral']:.4f}",
            f"  Tension detected:   T={tsr['T']:.3f}",
            f"  Output quality:     POAV={poav['total']:.3f}",
            f"  Vow check:          {vow['status'].upper()}",
            f"  Council verdict:    {council['verdict']}",
            "",
            "Every decision is traceable. Every output is auditable.",
            "That is ToneSoul.",
        ]
    )
    return "\n".join(lines) + "\n"


def _emit_json(payload: dict[str, Any]) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((text + "\n").encode("utf-8", errors="replace"))
        return
    print(text.encode("ascii", errors="backslashreplace").decode("ascii"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the ToneSoul quickstart demo.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON instead of the human-readable report.",
    )
    parser.add_argument(
        "--sample-text",
        default=DEFAULT_SAMPLE_TEXT,
        help="Override the sample text sent through the governance loop.",
    )
    parser.add_argument(
        "--state-path",
        default=str(DEFAULT_STATE_PATH),
        help="Governance state JSON path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = build_demo_payload(
        sample_text=args.sample_text,
        state_path=Path(args.state_path).resolve(),
    )
    if args.json:
        _emit_json(payload)
    else:
        print(render_text_report(payload), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
