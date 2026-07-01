"""Accountability / co-observation panel — render the "what I claimed, who caught it" ledger.

§0 Orientation
--------------
This is NOT a hero dashboard. Per the ToneSoul thesis + Fan-Wei's co-observation principle
(see memory: co-observer / dual-calibration, "show misses not an aggregate score"), the panel shows
MISSES — claims that did not hold and WHO caught them — graded by the project's own evidence ladder
(tonesoul/reviewer/evidence_levels.py: E0 demo-only .. E4 independent replication). It is
BIDIRECTIONAL: one lane is "I check myself" (self / test / a different model), the other is "the
human checks me" (co-observer). The product is the catching, not a green score. A few held claims are
shown too, for honesty — so it is not only failures — but misses lead.

Pure: events in -> a self-contained HTML string out. No I/O, no network, no framework
(inline CSS, dependency-free). The generator (tools/accountability_panel/generate.py) does the I/O.
"""

from __future__ import annotations

import html
from collections.abc import Sequence
from dataclasses import dataclass

__ts_layer__ = "surface"
__ts_purpose__ = (
    "Render the accountability / co-observation ledger (claims -> who caught them) as static HTML."
)

USES_LLM = False
USES_NETWORK = False

_LANES = ("self-check", "co-observer")
_TIERS = ("E0", "E1", "E2", "E3", "E4", "—")


@dataclass(frozen=True)
class AccountabilityEvent:
    """One accountability event. `lane` ∈ {self-check, co-observer}; `evidence_at_claim` is an E-tier
    (or '—' when not applicable); `held` is whether the claim survived scrutiny."""

    claim: str
    evidence_at_claim: str
    held: bool
    caught_by: str
    correction: str
    lane: str

    def __post_init__(self) -> None:
        if self.lane not in _LANES:
            raise ValueError(f"lane must be one of {_LANES}, got {self.lane!r}")
        if self.evidence_at_claim not in _TIERS:
            raise ValueError(
                f"evidence_at_claim must be one of {_TIERS}, got {self.evidence_at_claim!r}"
            )


def _esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def _tier_badge(tier: str) -> str:
    # weaker evidence = warmer/redder; stronger = greener. This is a claim-confidence cue, not a score.
    colors = {
        "E0": "#c0392b",
        "E1": "#d35400",
        "E2": "#b7950b",
        "E3": "#1e8449",
        "E4": "#0e6251",
        "—": "#566573",
    }
    return (
        f'<span class="tier" style="background:{colors.get(tier, "#566573")}">{_esc(tier)}</span>'
    )


def _row(ev: AccountabilityEvent) -> str:
    held_cls = "held" if ev.held else "miss"
    held_txt = "✅ 站住" if ev.held else "✗ 沒站住"
    return (
        f'<tr class="{held_cls}">'
        f'<td class="claim">{_esc(ev.claim)}</td>'
        f'<td class="tiercell">{_tier_badge(ev.evidence_at_claim)}</td>'
        f'<td class="heldcell">{held_txt}</td>'
        f"<td>{_esc(ev.caught_by)}</td>"
        f'<td class="corr">{_esc(ev.correction) or "—"}</td>'
        f"</tr>"
    )


def _lane_section(title: str, subtitle: str, events: Sequence[AccountabilityEvent]) -> str:
    # misses first (they are the point), held claims after
    ordered = [e for e in events if not e.held] + [e for e in events if e.held]
    rows = "\n".join(_row(e) for e in ordered) or (
        '<tr><td colspan="5" class="empty">（尚無事件）</td></tr>'
    )
    return (
        f'<section class="lane">'
        f'<h2>{_esc(title)}</h2><p class="sub">{_esc(subtitle)}</p>'
        f"<table><thead><tr>"
        f"<th>我宣稱的</th><th>宣稱時證據</th><th>站住?</th><th>誰接住</th><th>修正</th>"
        f"</tr></thead><tbody>\n{rows}\n</tbody></table></section>"
    )


def render_panel(events: Sequence[AccountabilityEvent], *, generated_at: str) -> str:
    """Render the full self-contained HTML panel. `generated_at` is passed in (no clock here)."""
    total = len(events)
    misses = sum(1 for e in events if not e.held)
    self_events = [e for e in events if e.lane == "self-check"]
    co_events = [e for e in events if e.lane == "co-observer"]

    css = (
        "body{font-family:system-ui,'Noto Sans TC',sans-serif;max-width:1000px;margin:2rem auto;"
        "padding:0 1rem;color:#1c2833;background:#fbfcfc;line-height:1.5}"
        "h1{margin:.2rem 0}.disclaimer{color:#7b241c;font-weight:600;margin:.2rem 0 1rem}"
        ".counts{color:#566573;margin-bottom:1.5rem}.lane{margin:2rem 0}"
        "h2{border-bottom:2px solid #d5dbdb;padding-bottom:.3rem}.sub{color:#566573;margin-top:.2rem}"
        "table{border-collapse:collapse;width:100%;margin-top:.6rem;font-size:.93rem}"
        "th,td{border:1px solid #e5e8e8;padding:.5rem .6rem;text-align:left;vertical-align:top}"
        "th{background:#f4f6f6}tr.miss{background:#fdf2f0}tr.miss .heldcell{color:#c0392b;font-weight:600}"
        "tr.held .heldcell{color:#1e8449}.claim{font-weight:600;max-width:260px}.corr{color:#34495e}"
        ".tier{color:#fff;padding:.1rem .45rem;border-radius:.5rem;font-size:.8rem;font-weight:700}"
        ".empty{color:#909497;text-align:center}footer{margin-top:2.5rem;color:#7f8c8d;font-size:.85rem;"
        "border-top:1px solid #d5dbdb;padding-top:1rem}"
    )

    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>語魂 · 共同觀測 & 問責面板</title><style>{css}</style></head><body>"
        "<h1>語魂 · 共同觀測 &amp; 問責面板</h1>"
        '<p class="disclaimer">這不是成績單。它秀「我哪裡差點講錯、誰接住的」。</p>'
        f'<p class="counts">共 {total} 件事件 · 其中 <b>{misses}</b> 件沒站住(這些才是重點)· '
        "證據分級用專案自己的 E0–E4 尺(E0 最弱、E4 最強)。</p>"
        + _lane_section(
            "① 我查我自己",
            "自審 / 測試 / 不同模型(codex)接住的——同源 review 兩向都會偏,所以要外部眼。",
            self_events,
        )
        + _lane_section(
            "↔ ② 你查我(co-observer)",
            "人校準我。這一欄不是我看你——是你看我。兩欄打架的地方就是共創的價值。",
            co_events,
        )
        + f"<footer>generated_at {_esc(generated_at)} · 這頁由 <b>真實事件</b> 生成,不是 demo。"
        "claim ≤ evidence 也適用於這頁本身:每一列的『修正』都可回溯到當時的 session。</footer>"
        "</body></html>"
    )
