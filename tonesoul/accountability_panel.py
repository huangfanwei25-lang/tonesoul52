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
    (or '—' when not applicable); `held` is whether the claim survived scrutiny.

    CounterEvidence extension (RFC responsibility_exoskeleton 2026-07-02, owner-ratified,
    shadow-first): the optional fields turn an event into one link of a counterevidence
    chain — how the claim was challenged (`method`), what happened (`outcome`:
    refuted/survived/narrowed), and where the receipts live (`evidence_ref`: PR/commit/
    doc). Old records without these fields stay valid; nothing consumes them for gating."""

    claim: str
    evidence_at_claim: str
    held: bool
    caught_by: str
    correction: str
    lane: str
    method: str = ""
    outcome: str = ""
    evidence_ref: str = ""

    def __post_init__(self) -> None:
        if self.lane not in _LANES:
            raise ValueError(f"lane must be one of {_LANES}, got {self.lane!r}")
        if self.evidence_at_claim not in _TIERS:
            raise ValueError(
                f"evidence_at_claim must be one of {_TIERS}, got {self.evidence_at_claim!r}"
            )
        if self.outcome not in ("", "refuted", "survived", "narrowed"):
            raise ValueError(f"outcome must be refuted/survived/narrowed/'', got {self.outcome!r}")
        for name in ("method", "evidence_ref"):
            if not isinstance(getattr(self, name), str):
                raise ValueError(f"{name} must be a string")
        # coherence (codex finding): a refuted claim cannot be held; a survived one must be
        if self.outcome == "refuted" and self.held:
            raise ValueError("outcome=refuted contradicts held=True")
        if self.outcome == "survived" and not self.held:
            raise ValueError("outcome=survived contradicts held=False")


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
        f'<tr class="{held_cls}" data-lane="{_esc(ev.lane)}" '
        f'data-held="{1 if ev.held else 0}" data-tier="{_esc(ev.evidence_at_claim)}">'
        f'<td class="claim">{_esc(ev.claim)}</td>'
        f'<td class="tiercell">{_tier_badge(ev.evidence_at_claim)}</td>'
        f'<td class="heldcell">{held_txt}</td>'
        f"<td>{_esc(ev.caught_by)}</td>"
        f'<td class="corr">{_esc(ev.correction) or "—"}'
        + (
            f' <span class="ceref">〔{_esc(ev.method)}→{_esc(ev.outcome)};{_esc(ev.evidence_ref)}〕</span>'
            if ev.outcome
            else ""
        )
        + "</td></tr>"
    )


def _lane_section(
    title: str, subtitle: str, events: Sequence[AccountabilityEvent], tbody_id: str
) -> str:
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
        f'</tr></thead><tbody id="{tbody_id}">\n{rows}\n</tbody></table></section>'
    )


# Vanilla JS (no framework, no deps). Progressive enhancement: the table works without it.
# Filters toggle row visibility; the "mark me" form live-adds a row AND emits the add.py CLI command
# to persist it (a static page can't write to disk — the persistence is explicit, not faked).
_JS = """
(function(){
  var missOnly=document.getElementById('f-miss'), laneSel=document.getElementById('f-lane');
  function apply(){
    var mo=missOnly.checked, ln=laneSel.value;
    document.querySelectorAll('tr[data-lane]').forEach(function(tr){
      var show=(!mo||tr.dataset.held==='0')&&(ln==='all'||tr.dataset.lane===ln);
      tr.style.display=show?'':'none';
    });
  }
  missOnly.addEventListener('change',apply); laneSel.addEventListener('change',apply);
  document.getElementById('mark-form').addEventListener('submit',function(e){
    e.preventDefault();
    var lane=document.getElementById('m-lane').value;
    var claim=document.getElementById('m-claim').value.trim(); if(!claim)return;
    var held=document.getElementById('m-held').checked;
    var caught=document.getElementById('m-caught').value.trim()||(lane==='co-observer'?'\\u4eba\\uff08\\u6893\\u5a01\\uff09':'\\u81ea\\u5df1');
    var corr=document.getElementById('m-corr').value.trim();
    var tier=lane==='co-observer'?'\\u2014':'E1';
    var tb=document.getElementById(lane==='co-observer'?'tbody-co':'tbody-self');
    var tr=document.createElement('tr');
    tr.className=held?'held':'miss';
    tr.dataset.lane=lane; tr.dataset.held=held?'1':'0'; tr.dataset.tier=tier;
    function td(t,c){var d=document.createElement('td'); if(c)d.className=c; d.textContent=t; return d;}
    tr.appendChild(td(claim,'claim'));
    var c1=document.createElement('td');
    c1.innerHTML='<span class="tier" style="background:'+(tier==='E1'?'#d35400':'#566573')+'"></span>';
    c1.firstChild.textContent=tier; tr.appendChild(c1);
    tr.appendChild(td(held?'\\u2705 \\u7ad9\\u4f4f':'\\u2717 \\u6c92\\u7ad9\\u4f4f','heldcell'));
    tr.appendChild(td(caught,''));
    tr.appendChild(td(corr||'\\u2014','corr'));
    tb.insertBefore(tr, tb.firstChild);
    function qq(s){return '"'+s.replace(/"/g,'\\\\"')+'"';}
    var cmd='python tools/accountability_panel/add.py --lane '+lane+' --claim '+qq(claim);
    if(held)cmd+=' --held';
    cmd+=' --caught-by '+qq(caught);
    if(corr)cmd+=' --correction '+qq(corr);
    document.getElementById('cli-out').textContent=cmd;
    document.getElementById('cli-box').style.display='block';
    apply();
  });
})();
"""


def render_panel(events: Sequence[AccountabilityEvent], *, generated_at: str) -> str:
    """Render the full self-contained interactive HTML panel. Progressive enhancement: the table
    works without JS; JS adds filters + a live "mark me" form. `generated_at` is passed in (no clock).
    """
    total = len(events)
    misses = sum(1 for e in events if not e.held)
    self_events = [e for e in events if e.lane == "self-check"]
    co_events = [e for e in events if e.lane == "co-observer"]

    css = (
        "body{font-family:system-ui,'Noto Sans TC',sans-serif;max-width:1000px;margin:2rem auto;"
        "padding:0 1rem;color:#1c2833;background:#fbfcfc;line-height:1.5}"
        "h1{margin:.2rem 0}.disclaimer{color:#7b241c;font-weight:600;margin:.2rem 0 1rem}"
        ".counts{color:#566573;margin-bottom:1rem}.lane{margin:2rem 0}"
        "h2{border-bottom:2px solid #d5dbdb;padding-bottom:.3rem}.sub{color:#566573;margin-top:.2rem}"
        "table{border-collapse:collapse;width:100%;margin-top:.6rem;font-size:.93rem}"
        "th,td{border:1px solid #e5e8e8;padding:.5rem .6rem;text-align:left;vertical-align:top}"
        "th{background:#f4f6f6}tr.miss{background:#fdf2f0}tr.miss .heldcell{color:#c0392b;font-weight:600}"
        ".ceref{color:#7f8c8d;font-size:.85em}"
        "tr.held .heldcell{color:#1e8449}.claim{font-weight:600;max-width:260px}.corr{color:#34495e}"
        ".tier{color:#fff;padding:.1rem .45rem;border-radius:.5rem;font-size:.8rem;font-weight:700}"
        ".empty{color:#909497;text-align:center}"
        ".controls{margin:1rem 0;display:flex;gap:1.2rem;align-items:center;flex-wrap:wrap;"
        "background:#f4f6f6;padding:.5rem .8rem;border-radius:.4rem}"
        ".markbox{margin:1.5rem 0;border:1px solid #d5dbdb;border-radius:.4rem;padding:.4rem .9rem;"
        "background:#fff}.markbox summary{cursor:pointer;font-weight:600;color:#1a5276}"
        "#mark-form{display:flex;flex-direction:column;gap:.5rem;margin:.8rem 0;max-width:560px}"
        "#mark-form input,#mark-form select{width:100%;padding:.35rem}"
        "#mark-form button{align-self:start;padding:.4rem 1.1rem;background:#1a5276;color:#fff;"
        "border:none;border-radius:.3rem;cursor:pointer}"
        "pre{background:#1c2833;color:#eafaf1;padding:.7rem;border-radius:.3rem;overflow-x:auto;"
        "font-size:.85rem;white-space:pre-wrap;word-break:break-all}"
        "footer{margin-top:2.5rem;color:#7f8c8d;font-size:.85rem;border-top:1px solid #d5dbdb;"
        "padding-top:1rem}"
    )

    controls = (
        '<div class="controls">'
        '<label><input type="checkbox" id="f-miss"> 只看沒站住</label>'
        '<label>欄位:<select id="f-lane"><option value="all">全部</option>'
        '<option value="self-check">我查我自己</option>'
        '<option value="co-observer">你查我</option></select></label></div>'
    )
    mark_form = (
        '<details class="markbox"><summary>➕ 你標我一筆(即時)</summary>'
        '<form id="mark-form">'
        '<label>欄位 <select id="m-lane"><option value="co-observer">你查我(co-observer)</option>'
        '<option value="self-check">我查我自己</option></select></label>'
        '<label>被校準的事 <input id="m-claim" type="text" placeholder="例:我對 X 過度警告" required></label>'
        '<label>誰接住 <input id="m-caught" type="text" placeholder="人(梵威)"></label>'
        '<label>修正 <input id="m-corr" type="text" placeholder="其實…"></label>'
        '<label><input type="checkbox" id="m-held"> 這條其實站住了(不是 miss)</label>'
        '<button type="submit">加到面板</button></form>'
        '<div id="cli-box" style="display:none"><p class="sub">已即時加到上面。要 <b>永久</b> 存進倉庫,'
        '跑這行(用剛建的 CLI):</p><pre id="cli-out"></pre></div></details>'
    )

    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>語魂 · 共同觀測 & 問責面板</title><style>{css}</style></head><body>"
        "<h1>語魂 · 共同觀測 &amp; 問責面板</h1>"
        '<p class="disclaimer">這不是成績單。它秀「我哪裡差點講錯、誰接住的」。</p>'
        f'<p class="counts">共 {total} 件事件 · 其中 <b>{misses}</b> 件沒站住(這些才是重點)· '
        "證據分級用專案自己的 E0–E4 尺(E0 最弱、E4 最強)。</p>"
        + controls
        + mark_form
        + _lane_section(
            "① 我查我自己",
            "自審 / 測試 / 不同模型(codex)接住的——同源 review 兩向都會偏,所以要外部眼。",
            self_events,
            "tbody-self",
        )
        + _lane_section(
            "↔ ② 你查我(co-observer)",
            "人校準我。這一欄不是我看你——是你看我。兩欄打架的地方就是共創的價值。",
            co_events,
            "tbody-co",
        )
        + f"<footer>generated_at {_esc(generated_at)} · 這頁由 <b>真實事件</b> 生成,不是 demo。"
        "claim ≤ evidence 也適用於這頁本身:每一列的『修正』都可回溯到當時的 session。</footer>"
        f"<script>{_JS}</script>"
        "</body></html>"
    )


def render_story(story: dict, *, generated_at: str, theme: str = "paper") -> str:
    """Render the bilingual NARRATIVE page (zh/en toggle, default zh) — the outward face. This is the
    accountability story told as prose (claim -> who caught it -> correction), NOT a feelings diary.
    Pure: content in -> HTML out. `story` = {"title":{zh,en}, "lede":{zh,en},
    "sections":[{"heading":{zh,en}, "paras":[{zh,en}, ...]}]}.
    `theme`: "paper" (docs/status serif page) or "site" (matches site/ blueprint tokens:
    #f4f7fb grid bg, Inter/Noto Sans TC, accent #2b6cb0, glass cards, back-to-home link)."""
    if theme not in ("paper", "site"):
        raise ValueError(f"theme must be 'paper' or 'site', got {theme!r}")

    def bi(node: dict, tag: str, cls: str = "") -> str:
        prefix = (cls + " ") if cls else ""
        return (
            f'<{tag} class="{prefix}zh">{_esc(node["zh"])}</{tag}>'
            f'<{tag} class="{prefix}en">{_esc(node["en"])}</{tag}>'
        )

    sections = ""
    for sec in story["sections"]:
        paras = "".join(bi(p, "p") for p in sec["paras"])
        sections += f"<section>{bi(sec['heading'], 'h2')}{paras}</section>"

    if theme == "paper":
        css = (
            "body{font-family:Georgia,'Noto Serif TC',serif;max-width:720px;margin:2.5rem auto;"
            "padding:0 1.2rem;color:#1c2833;background:#fbfcfc;line-height:1.75;font-size:1.05rem}"
            "h1{font-size:1.7rem;line-height:1.3;margin:.4rem 0 1rem}"
            "h2{font-size:1.15rem;margin:2rem 0 .5rem;color:#34495e}.lede{color:#566573;font-style:italic}"
            ".langbar{margin-bottom:1rem}.langbar button{border:1px solid #d5dbdb;background:#fff;"
            "padding:.25rem .8rem;cursor:pointer;border-radius:.3rem;margin-right:.4rem;font:inherit;font-size:.85rem}"
            ".langbar button.active{background:#1a5276;color:#fff;border-color:#1a5276}"
            "body.lang-zh .en{display:none}body.lang-en .zh{display:none}"
            "footer{margin-top:2.5rem;color:#7f8c8d;font-size:.85rem;border-top:1px solid #d5dbdb;"
            "padding-top:1rem;font-family:system-ui,sans-serif}"
        )
        fonts_link = ""
        topbar_back = ""
    else:
        # tokens mirror site/index.html :root (--bg #f4f7fb, --text #1a202c, --accent #2b6cb0)
        css = (
            "body{font-family:'Inter','Noto Sans TC',sans-serif;max-width:760px;margin:0 auto;"
            "padding:4.5rem 1.2rem 2rem;color:#1a202c;background:#f4f7fb;line-height:1.8;"
            "background-image:linear-gradient(rgba(43,108,176,.05) 1px,transparent 1px),"
            "linear-gradient(90deg,rgba(43,108,176,.05) 1px,transparent 1px);background-size:40px 40px}"
            "h1{font-size:1.9rem;line-height:1.3;margin:.4rem 0 1rem;font-weight:900;letter-spacing:-.01em}"
            "h2{font-size:1.1rem;margin:0 0 .6rem;color:#2b6cb0;font-weight:700}"
            ".lede{color:#4a5568;font-style:italic}"
            "section{background:rgba(255,255,255,.7);border:1px solid rgba(0,0,0,.05);"
            "border-radius:12px;padding:1.4rem 1.7rem;margin:1.4rem 0}"
            ".topbar{position:fixed;top:0;left:0;width:100%;display:flex;justify-content:space-between;"
            "align-items:center;padding:.6rem 1.2rem;background:rgba(244,247,251,.85);"
            "backdrop-filter:blur(12px);border-bottom:1px solid rgba(0,0,0,.05);"
            "font-family:'JetBrains Mono',monospace;font-size:.85rem;font-weight:700;letter-spacing:.05em}"
            ".topbar .back{color:#4a5568;text-decoration:none;padding:.4rem .8rem;border-radius:6px}"
            ".topbar .back:hover{color:#2b6cb0;background:rgba(135,206,250,.15)}"
            ".langbar button{border:1px solid rgba(0,0,0,.08);background:rgba(255,255,255,.7);"
            "padding:.25rem .8rem;cursor:pointer;border-radius:6px;margin-left:.4rem;"
            "font-family:'JetBrains Mono',monospace;font-size:.8rem;font-weight:700}"
            ".langbar button.active{background:#2b6cb0;color:#fff;border-color:#2b6cb0}"
            "body.lang-zh .en{display:none}body.lang-en .zh{display:none}"
            "footer{margin-top:2.5rem;color:#6b7c8d;font-size:.85rem;"
            "border-top:1px solid rgba(0,0,0,.08);padding-top:1rem}"
        )
        fonts_link = (
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700;900'
            "&family=JetBrains+Mono:wght@400;700&family=Noto+Sans+TC:wght@300;400;700;900"
            '&display=swap" rel="stylesheet">'
        )
        topbar_back = '<a class="back" href="index.html">&larr; ToneSoul</a>'
    js = (
        "document.querySelectorAll('.langbar button').forEach(function(b){"
        "b.addEventListener('click',function(){document.body.className='lang-'+b.dataset.l;"
        "document.querySelectorAll('.langbar button').forEach(function(x){"
        "x.classList.toggle('active',x===b);});});});"
    )
    foot_zh = "這份紀錄由真實協作事件寫成,不是宣傳。claim ≤ evidence 也適用於這頁本身。"
    foot_en = (
        "Written from real collaboration events, not marketing. claim ≤ evidence applies here too."
    )
    langbar = (
        '<div class="langbar"><button data-l="zh" class="active">中文</button>'
        '<button data-l="en">English</button></div>'
    )
    header_bar = f'<div class="topbar">{topbar_back}{langbar}</div>' if theme == "site" else langbar
    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{_esc(story['title']['zh'])}</title>{fonts_link}<style>{css}</style></head>"
        '<body class="lang-zh">'
        + header_bar
        + bi(story["title"], "h1")
        + bi(story["lede"], "p", "lede")
        + sections
        + f'<footer>generated_at {_esc(generated_at)} · <span class="zh">{foot_zh}</span>'
        f'<span class="en">{foot_en}</span></footer>' + f"<script>{js}</script></body></html>"
    )
