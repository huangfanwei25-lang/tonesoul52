"""ToneSoul StockLens — a forced bull/bear honesty layer for stock reasoning (台股 MVP).

WHAT THIS IS NOT (baked-in boundary, NOT a disclaimer footnote):
  - NOT financial advice. It returns NO buy/sell verdict — `verdict` is always None by design.
  - NOT a predictor. It cannot predict price or the future.
  - It does not fetch market data, read insider/non-public info, or know what will happen.

WHAT IT DOES: takes *your* analysis points and forces honesty on them —
  (1) forces both sides — flags a dimension you argued one-sidedly (or skipped);
  (2) flags overclaims in your own wording (保證 / 穩賺 / 必漲 / 零風險 ...);
  (3) flags claims whose language outruns their stated evidence level (篤定措辭 + 低證據);
  (4) states what *neither* side can know.

The decision and the money are yours. This is the ToneSoul claim-boundary discipline
applied to the domain most full of "保證 / 穩賺 / 必漲" overclaims — it helps you think,
it does not think for you.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List

try:  # reuse ToneSoul's evidence ladder when available; stay runnable standalone otherwise
    from tonesoul.reviewer.evidence_levels import EVIDENCE_LEVELS
except Exception:  # pragma: no cover - fallback only
    EVIDENCE_LEVELS = None

DIMENSIONS = ("基本面", "技術面", "籌碼面", "消息面")
SIDES = ("bull", "bear")

# The AXIOMS forbidden-claim class ("保證/穩賺/必漲"), in this domain. Lexical by design —
# like the rest of ToneSoul it flags phrasings, it does not comprehend; paraphrase evades.
_OVERCLAIM = re.compile(
    r"保證|穩賺不賠|穩賺|包賺|必賺|必漲|必跌|一定(漲|跌|賺|會賺)|零風險|無風險|"
    r"絕對(會|不會|穩|賺)|百分之百|百分百|穩的|閉著眼|全壓|all[\s-]?in|穩贏|躺著賺|"
    r"輕鬆翻倍|穩定獲利|包你|穩穩賺",
    re.IGNORECASE,
)
# certainty language, used to detect "language outruns evidence"
_STRONG = re.compile(
    r"保證|必|一定|絕對|百分|零風險|無風險|穩賺|穩贏|包賺|包你|穩的|鐵定|肯定會",
    re.IGNORECASE,
)

CANNOT_VERIFY = (
    "未來價格走勢——沒有人能預測",
    "總體經濟 / 政策 / 利率的轉向",
    "黑天鵝、突發事件",
    "你拿不到的內線 / 未公開資訊",
    "市場情緒,以及其他參與者接下來會怎麼做",
)


@dataclass(frozen=True)
class Point:
    """One analysis point the user supplies."""

    dimension: str
    side: str  # "bull" | "bear"
    claim: str
    evidence_level: str = "E1"  # E0 demo-only ... E4 independently replicated


def _normalize(points: List[Any]) -> List[Point]:
    return [p if isinstance(p, Point) else Point(**p) for p in points]


def _input_problems(points: List[Point]) -> List[str]:
    problems: List[str] = []
    for i, p in enumerate(points):
        if p.dimension not in DIMENSIONS:
            problems.append(f"point[{i}]: 未知面向 {p.dimension!r}(應為 {'/'.join(DIMENSIONS)})")
        if p.side not in SIDES:
            problems.append(f"point[{i}]: side 應為 bull/bear,得到 {p.side!r}")
        if EVIDENCE_LEVELS is not None and p.evidence_level not in EVIDENCE_LEVELS:
            problems.append(f"point[{i}]: 未知證據等級 {p.evidence_level!r}(應為 E0–E4)")
    return problems


def _dissent_coverage_gaps(points: List[Point]) -> List[str]:
    """The core of 強制拆多空對照: every dimension must show BOTH sides."""
    gaps: List[str] = []
    for dim in DIMENSIONS:
        sides = {p.side for p in points if p.dimension == dim}
        if not sides:
            gaps.append(f"{dim}:你完全沒給(你說你會看這面)——多空各補一個最強論點。")
            continue
        if "bull" not in sides:
            gaps.append(f"{dim}:只有空方。多方最強的反駁是什麼?")
        if "bear" not in sides:
            gaps.append(f"{dim}:只有多方。空方 / 最大的風險是什麼?")
    return gaps


def _overclaim_flags(points: List[Point]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for p in points:
        m = _OVERCLAIM.search(p.claim)
        if m:
            out.append(
                {
                    "dimension": p.dimension,
                    "side": p.side,
                    "claim": p.claim,
                    "matched": m.group(0),
                    "why": "AXIOMS 禁止的『保證/穩賺』類 claim——股市沒有保證。改成可被反駁的措辭。",
                }
            )
    return out


def _evidence_mismatches(points: List[Point]) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for p in points:
        if _STRONG.search(p.claim) and p.evidence_level in ("E0", "E1"):
            out.append(
                {
                    "claim": p.claim,
                    "evidence_level": p.evidence_level,
                    "why": f"措辭很篤定,但證據只到 {p.evidence_level}——語言超過了證據。",
                }
            )
    return out


def review(stock_id: str, points: List[Any]) -> Dict[str, Any]:
    """Return a structured honesty report. Never a buy/sell verdict (by design)."""
    pts = _normalize(points)
    return {
        "stock": stock_id,
        "verdict": None,  # by design: StockLens never recommends buy/sell
        "no_verdict_note": (
            "StockLens 不給買賣判定。這是把多空分歧、你自己的 overclaim、和兩邊都不可知的事"
            "攤開的結構——決定和錢是你的。"
        ),
        "input_problems": _input_problems(pts),
        "dissent_coverage_gaps": _dissent_coverage_gaps(pts),
        "overclaim_flags": _overclaim_flags(pts),
        "evidence_mismatches": _evidence_mismatches(pts),
        "cannot_verify": list(CANNOT_VERIFY),
        "point_count": len(pts),
    }


def format_report(report: Dict[str, Any]) -> str:
    lines = [f"# StockLens · {report['stock']} · 多空誠實框(非投資建議)", ""]
    lines.append(f"（{report['point_count']} 個分析點;StockLens 不給買賣判定）")

    def block(title: str, items: List[Any], empty: str) -> None:
        lines.append("")
        lines.append(f"## {title}")
        if not items:
            lines.append(f"  ✓ {empty}")
            return
        for it in items:
            if isinstance(it, dict):
                if "matched" in it:
                    lines.append(
                        f"  ⚑ [{it['dimension']}/{it['side']}] 「{it['matched']}」 — {it['claim']}"
                    )
                    lines.append(f"      → {it['why']}")
                elif "evidence_level" in it:
                    lines.append(f"  ⚑ ({it['evidence_level']}) {it['claim']}")
                    lines.append(f"      → {it['why']}")
                else:
                    lines.append(f"  ⚑ {it}")
            else:
                lines.append(f"  ⚑ {it}")

    if report["input_problems"]:
        block("輸入問題(先修)", report["input_problems"], "")
    block("強制對照:缺的另一邊", report["dissent_coverage_gaps"], "四個面向都有多空兩邊。")
    block("你自己的 overclaim", report["overclaim_flags"], "沒抓到『保證/穩賺/必漲』類措辭。")
    block("語言超過證據", report["evidence_mismatches"], "沒有篤定措辭配低證據的情形。")
    lines.append("")
    lines.append("## 兩邊都不可知(別假裝知道)")
    for c in report["cannot_verify"]:
        lines.append(f"  · {c}")
    lines.append("")
    lines.append(f"— {report['no_verdict_note']}")
    return "\n".join(lines)


def main(argv: List[str] | None = None) -> int:  # pragma: no cover - thin CLI
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        prog="stocklens",
        description="Forced bull/bear honesty frame for a stock analysis (台股). Not advice.",
    )
    parser.add_argument(
        "points_json", help="JSON file: {stock, points:[{dimension,side,claim,evidence_level}]}"
    )
    parser.add_argument("--json", action="store_true", help="emit the structured report as JSON")
    args = parser.parse_args(argv)

    with open(args.points_json, encoding="utf-8-sig") as fh:
        data = json.load(fh)
    report = review(data.get("stock", "?"), data.get("points", []))

    out = json.dumps(report, ensure_ascii=False, indent=2) if args.json else format_report(report)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((out + "\n").encode("utf-8", errors="replace"))
    else:
        print(out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
