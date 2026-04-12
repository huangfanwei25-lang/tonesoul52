"""
Session Journal — narrative-style session history cards.
"""

from typing import Any, Dict, List

import streamlit as st


def render_session_journal(traces: List[Dict[str, Any]]) -> None:
    """Render session history as readable journal entries.

    Parameters
    ----------
    traces : session trace dicts (from session_traces.jsonl)
    """
    if not traces:
        st.info("目前沒有對話記錄")
        return

    for trace in reversed(traces[-10:]):
        ts = trace.get("timestamp", "")[:16]
        agent = trace.get("agent", "unknown")
        duration = trace.get("duration_minutes", 0)
        topics = trace.get("topics", [])
        decisions = trace.get("key_decisions", [])
        tensions = trace.get("tension_events", [])
        stance = trace.get("stance_shift", {})

        # Topic badges
        topic_badges = ""
        topic_colors = {
            "governance": "#3a6b9f",
            "memory": "#2a9d8f",
            "testing": "#e9c46a",
            "architecture": "#7c5cfc",
            "debug": "#ef4444",
            "gamification": "#f97316",
            "dashboard": "#5a8ec0",
        }
        for topic in topics[:5]:
            color = topic_colors.get(topic, "#6b7c8d")
            topic_badges += (
                f'<span style="display:inline-block;padding:2px 8px;border-radius:10px;'
                f'font-size:11px;background:{color}18;color:{color};border:1px solid {color}33;'
                f'margin-right:4px">{topic}</span>'
            )

        # Decisions list
        decisions_html = ""
        if decisions:
            for d in decisions[:4]:
                short = str(d)[:80]
                decisions_html += f'<div style="font-size:12px;color:#2c3e50;margin:2px 0">· {short}</div>'

        # Tension indicators
        tension_html = ""
        if tensions:
            for t in tensions[:3]:
                sev = float(t.get("severity", 0))
                topic_t = str(t.get("topic", ""))
                sev_color = "#ef4444" if sev >= 0.7 else "#f97316" if sev >= 0.4 else "#3a6b9f"
                tension_html += (
                    f'<span style="font-size:11px;color:{sev_color}">'
                    f'{topic_t} ({sev:.2f})</span> '
                )

        # Stance shift
        stance_html = ""
        if stance and stance.get("from") and stance.get("to"):
            stance_html = (
                f'<div style="font-size:11px;color:#6b7c8d;margin-top:4px">'
                f'立場轉變: {stance["from"]} → {stance["to"]}</div>'
            )

        duration_str = f"{int(duration)}m" if duration else ""

        entry_html = (
            f'<div class="ts-journal-entry">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-weight:500;color:#2c3e50">{agent}</span>'
            f'<span style="font-size:12px;color:#6b7c8d">{ts} · {duration_str}</span>'
            f"</div>"
            f'<div style="margin:6px 0">{topic_badges}</div>'
            f"{decisions_html}"
            f"{tension_html}"
            f"{stance_html}"
            f"</div>"
        )
        st.markdown(entry_html, unsafe_allow_html=True)
