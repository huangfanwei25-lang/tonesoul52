"""BreakoutMomentumFilter_v1 — deterministic momentum-breakout CANDIDATE screener.

WHAT THIS IS NOT (baked-in boundary, not a disclaimer footnote):
  - NOT a buy/sell signal, NOT a trading system, NOT backtested or validated here.
  - It answers ONE mechanical question: does this OHLCV series currently meet a fixed set of
    momentum-breakout conditions? **PASS ≠ a good trade.**

Momentum breakouts have high false-breakout rates. Whether THIS filter has any *edge* is an
EMPIRICAL question only an honest out-of-sample backtest (with costs, slippage, survivorship
bias controlled) can answer — and until that backtest exists and publishes its hit-rate /
expectancy INCLUDING the nulls, the filter is an **untested hypothesis**. (ToneSoul discipline:
claim ≤ evidence; a screen finds *candidates*, not winners. The numeric parameters are
reasonable *priors*, not validated values — tuning them to fit past data is overfitting, the
same Goodhart trap as a fixed self-evaluator.)

Conditions 1–6 are evaluated deterministically at the latest bar. 7 (entry-gap) needs the NEXT
bar's open, so it is an *execution-time* rule, not a screen condition; 8 (exit) is position
management. Both are documented, not screened.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

__ts_purpose__ = "Deterministic momentum-breakout candidate screener; not a signal, not backtested."

# Reasonable priors — NOT validated. Backtest before trusting any of these numbers.
PARAMS = {
    "ma_fast": 5,
    "ma_mid": 10,
    "ma_slow": 20,
    "vol_window": 20,
    "vol_mult": 1.5,
    "breakout_window": 30,
    "overheat_lookback": 20,
    "overheat_max": 0.30,
    "entry_gap_max": 0.05,
}

CAVEATS = (
    "PASS = mechanically meets the conditions, NOT a profitable trade.",
    "Momentum breakouts have a high false-breakout rate; most breakouts fail.",
    "Whether this filter has edge is UNKNOWN until an honest out-of-sample backtest "
    "(with costs/slippage/survivorship) measures its hit-rate AND publishes the nulls.",
    "The parameters are priors, not validated; tuning them to past data is overfitting.",
    "Indicators are lagging and regime-dependent (trend-following dies in chop/bear).",
    "It cannot know WHY a breakout happened (news / 籌碼 / manipulation).",
)


@dataclass(frozen=True)
class Bar:
    high: float
    low: float
    close: float
    volume: float


def _sma(values: List[float], n: int) -> Optional[float]:
    if len(values) < n or n <= 0:
        return None
    return sum(values[-n:]) / n


def _to_bars(bars: List[Any]) -> List[Bar]:
    return [
        b if isinstance(b, Bar) else Bar(**{k: b[k] for k in ("high", "low", "close", "volume")})
        for b in bars
    ]


def evaluate(bars: List[Any], liquidity_threshold: Optional[float] = None) -> Dict[str, Any]:
    """Evaluate BreakoutMomentumFilter_v1 conditions at the latest bar. Deterministic."""
    bs = _to_bars(bars)
    closes = [b.close for b in bs]
    highs = [b.high for b in bs]
    vols = [b.volume for b in bs]
    p = PARAMS
    conds: List[Dict[str, Any]] = []

    def add(cid: str, name: str, passed: Optional[bool], detail: str) -> None:
        conds.append({"id": cid, "name": name, "passed": passed, "detail": detail})

    ma_slow = _sma(closes, p["ma_slow"])
    ma_mid = _sma(closes, p["ma_mid"])
    ma_fast = _sma(closes, p["ma_fast"])
    close = closes[-1] if closes else None

    # 1. Close > MA20
    if ma_slow is None or close is None:
        add("1", "Close > MA20", None, "資料不足(需≥20根)")
    else:
        add("1", "Close > MA20", close > ma_slow, f"close {close:.2f} vs MA20 {ma_slow:.2f}")

    # 2. MA5 > MA10 > MA20
    if None in (ma_fast, ma_mid, ma_slow):
        add("2", "MA5 > MA10 > MA20", None, "資料不足(需≥20根)")
    else:
        ok = ma_fast > ma_mid > ma_slow
        add(
            "2",
            "MA5 > MA10 > MA20",
            ok,
            f"MA5 {ma_fast:.2f} / MA10 {ma_mid:.2f} / MA20 {ma_slow:.2f}",
        )

    # 3. Volume > VolMA20 * 1.5
    vol_ma = _sma(vols, p["vol_window"])
    if vol_ma is None or not vols:
        add("3", "Volume > VolMA20 × 1.5", None, "資料不足(需≥20根)")
    else:
        thr = vol_ma * p["vol_mult"]
        add(
            "3",
            "Volume > VolMA20 × 1.5",
            vols[-1] > thr,
            f"vol {vols[-1]:.0f} vs {p['vol_mult']}×VolMA20 {thr:.0f}",
        )

    # 4. Close > Highest(High, 30)[1]  — prior-30-bar high, excluding today
    need4 = p["breakout_window"] + 1
    if len(highs) < need4 or close is None:
        add("4", "Close > 前30日最高(不含今日)", None, f"資料不足(需≥{need4}根)")
    else:
        prior_high = max(highs[-(p["breakout_window"] + 1) : -1])
        add(
            "4",
            "Close > 前30日最高(不含今日)",
            close > prior_high,
            f"close {close:.2f} vs 前高 {prior_high:.2f}",
        )

    # 5. Close/Close[20] - 1 < 0.3 (not overheated)
    need5 = p["overheat_lookback"] + 1
    if len(closes) < need5:
        add("5", "20日漲幅 < 30%(尚未過熱)", None, f"資料不足(需≥{need5}根)")
    else:
        chg = close / closes[-need5] - 1
        add("5", "20日漲幅 < 30%(尚未過熱)", chg < p["overheat_max"], f"20日漲幅 {chg*100:.1f}%")

    # 6. AvgTurnover20 > threshold (optional liquidity gate)
    if liquidity_threshold is None:
        add("6", "流動性(AvgTurnover20 > 門檻)", None, "未提供 liquidity_threshold,略過")
    else:
        turn = _sma([b.close * b.volume for b in bs], p["vol_window"])
        if turn is None:
            add("6", "流動性(AvgTurnover20 > 門檻)", None, "資料不足(需≥20根)")
        else:
            add(
                "6",
                "流動性(AvgTurnover20 > 門檻)",
                turn > liquidity_threshold,
                f"AvgTurnover20 {turn:.0f} vs 門檻 {liquidity_threshold:.0f}",
            )

    screen = [c for c in conds if c["id"] in ("1", "2", "3", "4", "5")]
    insufficient = any(c["passed"] is None for c in screen)
    # candidate = all screened (1-5) pass; 6 only counts against if a threshold was given
    cand_conds = screen + ([c for c in conds if c["id"] == "6" and c["passed"] is not None])
    candidate = (not insufficient) and all(c["passed"] for c in cand_conds)

    return {
        "candidate": candidate,
        "insufficient_data": insufficient,
        "conditions": conds,
        "execution_rules": [
            "7 · 進場跳空限制:NextOpen/Close - 1 < 0.05 — 需『隔日開盤』,屬執行期檢查,非篩選條件。",
            "8 · 出場規則:跌破突破日低點 / 跌破 MA10 / 固定停損 — 屬部位管理,非篩選條件。",
        ],
        "caveats": list(CAVEATS),
        "not_a": "候選篩選器,不是買賣訊號、不是交易系統;在誠實回測量出 edge(含 null)之前,它是未驗證的假設。",
    }


def format_report(r: Dict[str, Any]) -> str:
    mark = {True: "✓", False: "✗", None: "—"}
    lines = ["# BreakoutMomentumFilter_v1 · 候選篩選(非買賣訊號)", ""]
    for c in r["conditions"]:
        lines.append(f"  {mark[c['passed']]} 條件{c['id']} {c['name']}：{c['detail']}")
    verdict = (
        "候選成立(符合機械條件)"
        if r["candidate"]
        else ("資料不足" if r["insufficient_data"] else "不符合(非候選)")
    )
    lines += ["", f"→ {verdict}", "", "## 執行規則(非篩選條件)"]
    lines += [f"  · {x}" for x in r["execution_rules"]]
    lines += ["", "## 誠實 caveat(讀之前先看)"]
    lines += [f"  · {x}" for x in r["caveats"]]
    lines += ["", f"— {r['not_a']}"]
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:  # pragma: no cover - thin CLI
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(prog="breakout", description=__doc__)
    parser.add_argument(
        "bars_json", help="JSON: {bars:[{high,low,close,volume}], liquidity_threshold?}"
    )
    args = parser.parse_args(argv)
    with open(args.bars_json, encoding="utf-8") as fh:
        data = json.load(fh)
    r = evaluate(data.get("bars", []), data.get("liquidity_threshold"))
    out = format_report(r)
    if hasattr(sys.stdout, "buffer"):
        sys.stdout.buffer.write((out + "\n").encode("utf-8", errors="replace"))
    else:
        print(out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
