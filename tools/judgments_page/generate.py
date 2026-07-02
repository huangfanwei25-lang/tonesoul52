"""Render docs/plans/judgment_*.md into a public judgments page (site/judgments/).

Same pattern as the accountability pages: static, dependency-free, site design tokens,
published by the Pages workflow (site/**). One page, all judgments, newest first.
The markdown subset handled is exactly what the judgment records use (##, **bold**,
lists, paragraphs); anything unrecognized passes through escaped — honest degradation.
"""

from __future__ import annotations

import html
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PLANS = REPO_ROOT / "docs" / "plans"
OUT = REPO_ROOT / "site" / "judgments" / "index.html"

_BOLD = re.compile(r"\*\*([^*]+)\*\*")


def _inline(text: str) -> str:
    escaped = html.escape(text, quote=False)
    return _BOLD.sub(r"<strong>\1</strong>", escaped)


def md_to_html(md: str) -> str:
    out: list[str] = []
    in_list = False
    for raw in md.splitlines():
        line = raw.rstrip()
        if line.startswith("> "):
            continue  # provenance quotes stay repo-side; the page is the plain face
        if not line.strip():
            if in_list:
                out.append("</ul>")
                in_list = False
            continue
        if line.startswith("- ") or line.startswith("* "):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(line[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if line.startswith("### "):
            out.append(f"<h4>{_inline(line[4:])}</h4>")
        elif line.startswith("## "):
            out.append(f"<h3>{_inline(line[3:])}</h3>")
        elif line.startswith("# "):
            out.append(f"<h2>{_inline(line[2:])}</h2>")
        elif line.startswith("---"):
            out.append("<hr>")
        else:
            out.append(f"<p>{_inline(line)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


CSS = (
    "body{font-family:'Inter','Noto Sans TC',sans-serif;max-width:780px;margin:0 auto;"
    "padding:4.5rem 1.2rem 2rem;color:#1a202c;background:#f4f7fb;line-height:1.8;"
    "background-image:linear-gradient(rgba(43,108,176,.05) 1px,transparent 1px),"
    "linear-gradient(90deg,rgba(43,108,176,.05) 1px,transparent 1px);background-size:40px 40px}"
    "h1{font-weight:900;font-size:1.8rem}h2{color:#2b6cb0;font-size:1.3rem;margin-top:2rem}"
    "h3{font-size:1.05rem;margin:1.2rem 0 .4rem}h4{font-size:1rem;color:#4a5568}"
    "article{background:rgba(255,255,255,.7);border:1px solid rgba(0,0,0,.05);"
    "border-radius:12px;padding:1.4rem 1.7rem;margin:1.4rem 0}"
    ".topbar{position:fixed;top:0;left:0;width:100%;padding:.6rem 1.2rem;"
    "background:rgba(244,247,251,.85);backdrop-filter:blur(12px);"
    "border-bottom:1px solid rgba(0,0,0,.05);font-family:'JetBrains Mono',monospace;"
    "font-size:.85rem;font-weight:700}"
    ".topbar a{color:#4a5568;text-decoration:none}.topbar a:hover{color:#2b6cb0}"
    ".lede{color:#4a5568;font-style:italic}"
    "footer{margin-top:2.5rem;color:#6b7c8d;font-size:.85rem;"
    "border-top:1px solid rgba(0,0,0,.08);padding-top:1rem}"
)


def build_page(records: list[tuple[str, str]], generated_at: str) -> str:
    articles = "\n".join(f"<article>{md_to_html(md)}</article>" for _, md in records)
    return (
        '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>判斷書 Judgments — 語魂 ToneSoul</title>"
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900'
        '&family=JetBrains+Mono:wght@700&family=Noto+Sans+TC:wght@400;700;900&display=swap"'
        ' rel="stylesheet">'
        f"<style>{CSS}</style></head><body>"
        '<div class="topbar"><a href="../index.html">&larr; ToneSoul</a></div>'
        "<h1>判斷書 Judgments</h1>"
        '<p class="lede">結構化的誠實判斷:五個視角真實分工、對抗裁決、白話論點在上、'
        "證據在下。判決帶信心上限與翻案條件——判斷不落痕,等於沒發生。</p>"
        + articles
        + f"<footer>generated_at {html.escape(generated_at)} · "
        "來源:docs/plans/judgment_*.md(公開可稽核)· 判決不構成投資或法律建議。</footer>"
        "</body></html>"
    )


def main() -> int:
    records = sorted(
        ((p.name, p.read_text(encoding="utf-8")) for p in PLANS.glob("judgment_*.md")),
        reverse=True,
    )
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(build_page(records, generated_at), encoding="utf-8", newline="\n")
    print(f"[wrote site/judgments/index.html — {len(records)} judgment(s)]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
