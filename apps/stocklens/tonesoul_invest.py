"""語魂投資 v0 — StockLens + an EXTERNAL-EYE prep layer (not its own auditor).

This is StockLens's honesty frame (forced bull/bear, overclaim flags, evidence levels —
see core.py) PLUS two things it deliberately does NOT do alone:

  1. surface the LOAD-BEARING assumption (the lowest-evidence claim the upside rests on);
  2. generate an EXTERNAL-EYE REFUTATION PACKET — the exact adversarial prompt + trap
     checklist you hand to a *separate* reviewer (a different local model, a human, a
     fresh session). It does NOT refute the thesis itself.

Why it does not grade itself: a system auditing its own output is the audit-washing
structure (auditor ≠ auditee); same-source blind spots correlate. So 語魂投資 PREPARES the
thesis for an external eye; the external eye must be genuinely separate. `verdict` is always
None — it never says buy/sell. (ToneSoul claim ≤ evidence; it flags, it does not decide.)
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List

# reuse StockLens core (same directory) without a package import
_core_spec = importlib.util.spec_from_file_location(
    "stocklens_core", Path(__file__).resolve().parent / "core.py"
)
_core = importlib.util.module_from_spec(_core_spec)
sys.modules["stocklens_core"] = _core
_core_spec.loader.exec_module(_core)

# The reasoning-loop trap-catalog, as adversarial questions an external eye should ask.
TRAP_QUESTIONS = (
    "Dropped-if: which claim asserts a conclusion (Y) without keeping its condition (if X) visible?",
    "Activity-as-confirmation: is any signal about risk/volatility/hedging (leverage, CB demand, fund flows) being read as a directional 看好?",
    "Aggregation: are several weak/one-sided points being summed into false confidence?",
    "Base-rate ≠ fate: is a historical/sector frequency being treated as this name's destiny?",
    "Peak extrapolation: is a cyclical-peak number (EPS/margin/price) used as the baseline?",
    "Load-bearing assumption: what single assumption, if false, flips the thesis — and is it verified or just E0/E1?",
    "Refuse both: is the thesis over-claimed (or, defensively, under-claimed) vs the evidence?",
)


def load_bearing(points: List[Any]) -> Dict[str, Any]:
    """The upside's weakest support: bull claims at the lowest evidence levels."""
    pts = _core._normalize(points)
    weak_bull = [
        {"dimension": p.dimension, "claim": p.claim, "evidence_level": p.evidence_level}
        for p in pts
        if p.side == "bull" and p.evidence_level in ("E0", "E1")
    ]
    weak_bull.sort(key=lambda x: x["evidence_level"])  # E0 before E1
    return {
        "weakest_bull_support": weak_bull,
        "note": (
            "你的『上漲』論點裡,證據最弱的就是這些(E0/E1)。整個 thesis 多半吊在其中一兩條上——"
            "把它們當『承重假設』,先驗了再下注。"
            if weak_bull
            else "多方論點沒有落在 E0/E1 的;但仍要問:哪一條若為假會翻盤?(見 external-eye packet)"
        ),
    }


def external_eye_packet(stock: str, points: List[Any]) -> Dict[str, Any]:
    """The packet to HAND TO a separate reviewer/model/human. 語魂投資 does not run it itself."""
    pts = _core._normalize(points)
    thesis = "\n".join(f"- [{p.dimension}/{p.side}|{p.evidence_level}] {p.claim}" for p in pts)
    prompt = (
        f"You are an ADVERSARIAL reviewer of a stock thesis on {stock}. You are NOT the author "
        f"and NOT a cheerleader. Your job is to REFUTE it. Default to 'not established' when "
        f"uncertain. For EACH question below, answer concretely against the thesis; end by naming "
        f"the single load-bearing assumption and whether it is verified.\n\nTHESIS:\n{thesis}\n\n"
        f"QUESTIONS:\n"
        + "\n".join(f"  {i+1}. {q}" for i, q in enumerate(TRAP_QUESTIONS))
        + "\n\nDo NOT give a buy/sell verdict. Output only the refutation + the load-bearing assumption."
    )
    return {
        "hand_this_to": "a SEPARATE reviewer — a different local model (e.g. an Ollama model), a "
        "human, or a fresh session. NOT the same context/model that wrote the thesis.",
        "why": "auditor ≠ auditee: a thesis graded by its own author/source is audit-washing; "
        "same-source blind spots correlate. The external eye must be genuinely separate.",
        "refutation_prompt": prompt,
        "trap_checklist": list(TRAP_QUESTIONS),
    }


def run(stock: str, points: List[Any]) -> Dict[str, Any]:
    """Assemble the 語魂投資 v0 output. Never a verdict."""
    report = _core.review(stock, points)
    return {
        "stocklens": report,
        "load_bearing": load_bearing(points),
        "external_eye": external_eye_packet(stock, points),
        "verdict": None,
        "note": (
            "語魂投資 v0:StockLens 結構 + 承重假設 + 給外部眼睛的駁斥包。它不替自己評分、不給買賣——"
            "把 packet 餵給一個『不同源』的審查官(地端模型/人/另一個 session),讓它來駁你。"
        ),
    }


def format_report(r: Dict[str, Any]) -> str:
    lines = [_core.format_report(r["stocklens"]), "", "## 承重假設(上漲最弱的支撐)"]
    lb = r["load_bearing"]
    for w in lb["weakest_bull_support"]:
        lines.append(f"  ⚑ [{w['dimension']}|{w['evidence_level']}] {w['claim']}")
    lines.append(f"  → {lb['note']}")
    ee = r["external_eye"]
    lines += [
        "",
        "## 外部的眼睛(語魂投資不自己駁——交給不同源的審查官)",
        f"  交給:{ee['hand_this_to']}",
        f"  為什麼:{ee['why']}",
        "",
        "  ── 把下面這段餵給那個審查官 ──",
        ee["refutation_prompt"],
    ]
    lines += ["", f"— {r['note']}"]
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:  # pragma: no cover - thin CLI
    import argparse
    import json

    parser = argparse.ArgumentParser(prog="tonesoul-invest", description=__doc__)
    parser.add_argument(
        "points_json", help="JSON: {stock, points:[{dimension,side,claim,evidence_level}]}"
    )
    parser.add_argument("--json", action="store_true", help="emit structured JSON")
    args = parser.parse_args(argv)
    with open(args.points_json, encoding="utf-8") as fh:
        data = json.load(fh)
    r = run(data.get("stock", "?"), data.get("points", []))
    out = json.dumps(r, ensure_ascii=False, indent=2) if args.json else format_report(r)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((out + "\n").encode("utf-8", errors="replace"))
    else:
        print(out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
