"""
Vow Cards — styled cards for active vows (commitments).
"""

from typing import Any, Dict, List

import streamlit as st


def render_vow_cards(vows: List[Dict[str, Any]]) -> None:
    """Render active vows as styled cards.

    Parameters
    ----------
    vows : list of dicts with keys ``id``, ``content``, ``created``, ``source``
    """
    if not vows:
        st.markdown(
            '<div class="ts-card" style="text-align:center;padding:16px">'
            '<span style="color:#6b7c8d">使用預設承諾：不誤導、揭露不確定性、不造成傷害</span></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown('<div class="ts-section-title">我的承諾</div>', unsafe_allow_html=True)

    for vow in vows:
        vow_id = vow.get("id", "")
        content = vow.get("content", str(vow))
        source = vow.get("source", "")
        created = vow.get("created", "")

        # Short display of creation time
        created_short = created[:10] if created else ""

        meta_parts = []
        if vow_id:
            meta_parts.append(vow_id)
        if source:
            meta_parts.append(source)
        if created_short:
            meta_parts.append(created_short)
        meta_text = " · ".join(meta_parts)

        st.markdown(
            f'<div class="ts-vow-card">'
            f'<div style="font-size:14px;font-weight:500;color:#2c3e50">{content}</div>'
            f'<div style="font-size:11px;color:#6b7c8d;margin-top:4px">{meta_text}</div>'
            f"</div>",
            unsafe_allow_html=True,
        )
