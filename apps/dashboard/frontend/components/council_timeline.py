"""
Council Timeline — vertical timeline showing council deliberation history.
"""

from typing import Any, Dict, List

import streamlit as st


_ROLE_COLORS = {
    "guardian": "#2a9d8f",
    "analyst": "#e9c46a",
    "critic": "#e76f51",
    "advocate": "#264653",
    "axiomatic": "#7c5cfc",
}


def render_council_timeline(traces: List[Dict[str, Any]]) -> None:
    """Render council deliberation history as a vertical timeline.

    Parameters
    ----------
    traces : session trace dicts (from session_traces.jsonl)
    """
    council_traces = [t for t in traces if t.get("council_dossier")]
    if not council_traces:
        st.info("目前沒有審議記錄")
        return

    st.markdown('<div class="ts-timeline">', unsafe_allow_html=True)

    for trace in reversed(council_traces[-10:]):
        ts = trace.get("timestamp", "")[:16]
        agent = trace.get("agent", "unknown")
        dossier = trace.get("council_dossier", {})

        # Extract verdict if present
        verdict = dossier.get("verdict", "")
        coherence = dossier.get("coherence", "")
        votes = dossier.get("votes", [])

        # Build role indicators
        role_dots = ""
        for v in votes[:5]:
            perspective = v.get("perspective", "")
            color = _ROLE_COLORS.get(perspective, "#6b7c8d")
            decision = v.get("decision", "")
            role_dots += (
                f'<span style="display:inline-block;width:8px;height:8px;'
                f'border-radius:50%;background:{color};margin-right:4px" '
                f'title="{perspective}: {decision}"></span>'
            )

        verdict_label = {
            "approve": "通過",
            "refine": "修正",
            "declare_stance": "宣告立場",
            "block": "阻擋",
        }.get(str(verdict), str(verdict))

        verdict_color = {
            "approve": "#4ade80",
            "refine": "#facc15",
            "declare_stance": "#5a8ec0",
            "block": "#ef4444",
        }.get(str(verdict), "#6b7c8d")

        entry_html = (
            f'<div class="ts-timeline-entry">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-size:12px;color:#6b7c8d">{ts} · {agent}</span>'
            f'<span style="font-size:12px;font-weight:bold;color:{verdict_color}">{verdict_label}</span>'
            f"</div>"
            f'<div style="margin-top:6px">{role_dots}</div>'
            f"</div>"
        )
        st.markdown(entry_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
