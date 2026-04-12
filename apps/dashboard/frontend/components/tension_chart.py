"""
Tension Chart — area chart showing tension severity history.
"""

from typing import Any, Dict, List

import streamlit as st


def render_tension_chart(tensions: List[Dict[str, Any]]) -> None:
    """Render tension history as a visual chart.

    Parameters
    ----------
    tensions : list of dicts with keys ``topic``, ``severity``, ``timestamp``
    """
    if not tensions:
        st.markdown(
            '<div class="ts-card" style="text-align:center;padding:24px">'
            '<span style="color:#6b7c8d">目前沒有壓力記錄</span></div>',
            unsafe_allow_html=True,
        )
        return

    # Build bar chart HTML for each tension
    bars_html = ""
    for t in tensions[:10]:  # Show last 10
        sev = float(t.get("severity", 0))
        topic = str(t.get("topic", "unknown"))
        pct = max(5, int(sev * 100))

        if sev >= 0.7:
            bar_color = "#ef4444"
        elif sev >= 0.4:
            bar_color = "#f97316"
        else:
            bar_color = "#3a6b9f"

        bars_html += (
            f'<div style="margin-bottom:6px">'
            f'<div style="display:flex;justify-content:space-between;font-size:12px;color:#6b7c8d">'
            f"<span>{topic}</span><span>{sev:.2f}</span></div>"
            f'<div style="background:rgba(90,142,192,0.1);border-radius:4px;height:8px;overflow:hidden">'
            f'<div style="width:{pct}%;height:100%;background:{bar_color};border-radius:4px;'
            f'transition:width 0.3s"></div>'
            f"</div></div>"
        )

    st.markdown(
        f'<div class="ts-card">'
        f'<div class="ts-section-title">壓力歷程</div>'
        f"{bars_html}</div>",
        unsafe_allow_html=True,
    )
