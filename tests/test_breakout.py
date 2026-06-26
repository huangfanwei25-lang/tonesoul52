"""Tests for BreakoutMomentumFilter_v1 (apps/stocklens/breakout.py)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "breakout_mod", Path(__file__).resolve().parents[1] / "apps" / "stocklens" / "breakout.py"
)
breakout = importlib.util.module_from_spec(_SPEC)
assert _SPEC and _SPEC.loader
sys.modules[_SPEC.name] = breakout  # @dataclass needs the module registered
_SPEC.loader.exec_module(breakout)


def _bar(close, vol, high=None):
    return {
        "high": high if high is not None else close + 0.5,
        "low": close - 0.5,
        "close": close,
        "volume": vol,
    }


def _passing_series():
    # 30 gently rising bars, then a breakout bar (price jump + volume spike + new high)
    bars = [_bar(100 + i, 1000) for i in range(30)]
    bars.append(_bar(134, 2000, high=134.5))
    return bars


def test_passing_series_is_candidate():
    r = breakout.evaluate(_passing_series())
    assert r["candidate"] is True
    assert r["insufficient_data"] is False
    assert all(c["passed"] for c in r["conditions"] if c["id"] in ("1", "2", "3", "4", "5"))


def test_flat_series_not_candidate():
    bars = [_bar(100, 1000) for _ in range(40)]
    r = breakout.evaluate(bars)
    assert r["candidate"] is False  # no breakout, no volume spike, no MA alignment


def test_insufficient_data_flags_and_blocks_candidate():
    r = breakout.evaluate([_bar(100, 1000) for _ in range(10)])
    assert r["insufficient_data"] is True
    assert r["candidate"] is False


def test_boundary_and_caveats_baked_in():
    r = breakout.evaluate([])
    assert "候選" in r["not_a"] and "假設" in r["not_a"]
    joined = " ".join(r["caveats"]).lower()
    assert "backtest" in joined and "overfit" in joined


def test_liquidity_gate_can_reject():
    r = breakout.evaluate(_passing_series(), liquidity_threshold=10**15)
    c6 = next(c for c in r["conditions"] if c["id"] == "6")
    assert c6["passed"] is False
    assert r["candidate"] is False


def test_execution_rules_are_documented_not_screened():
    r = breakout.evaluate(_passing_series())
    ids = {c["id"] for c in r["conditions"]}
    assert "7" not in ids and "8" not in ids  # 7/8 are execution rules, not screen conditions
    assert len(r["execution_rules"]) == 2


def test_deterministic():
    bars = _passing_series()
    assert breakout.evaluate(bars) == breakout.evaluate(bars)
