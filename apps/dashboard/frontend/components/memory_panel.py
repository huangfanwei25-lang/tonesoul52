"""
記憶面板元件 - 參考資料選取面板
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
from utils.memory import (
    list_conversations,
    list_memory_entries,
    list_skills,
    load_conversation_entry,
)


def build_memory_panel_view_model(
    *,
    tier0_shell: dict[str, Any] | None,
    tier1_shell: dict[str, Any] | None,
    selected_count: int,
) -> dict[str, Any]:
    tier0_shell = tier0_shell or {}
    tier1_shell = tier1_shell or {}
    canonical_cards = tier1_shell.get("canonical_cards") or {}
    closeout_attention = tier1_shell.get("closeout_attention") or {}

    return {
        "title": "參考資料",
        "subtitle": "這裡只做 reference selection，不是 operator truth。",
        "operator_note": (
            "先看 Tier 0 / Tier 1 的 readiness、short board、closeout，再決定是否拉入額外參考。"
            " 被選取的資料只輔助理解，不等於目前的治理真相或完成狀態。"
        ),
        "tier0_readiness": str(tier0_shell.get("readiness_status", "")).strip() or "unknown",
        "current_short_board": str((canonical_cards or {}).get("short_board", "")).strip(),
        "closeout_attention": str((closeout_attention or {}).get("summary_text", "")).strip(),
        "selected_count": int(selected_count),
    }


def _render_memory_group(
    title: str,
    entries: list,
    key_prefix: str,
    show_gate: bool = False,
) -> None:
    st.markdown(f"**{title}**")
    for idx, entry in enumerate(entries[:6]):
        entry_title = entry["title"][:16] + ("..." if len(entry["title"]) > 16 else "")
        is_selected = entry["path"] in st.session_state.selected_memories
        if show_gate:
            gate = entry.get("gate")
            badge = {"PASS": "通過", "WARN": "注意", "FAIL": "阻擋"}.get(gate, "未知")
            label = f"{badge} · {entry_title}"
        else:
            label = entry_title
        if st.checkbox(label, value=is_selected, key=f"mem_{key_prefix}_{idx}"):
            if entry["path"] not in st.session_state.selected_memories:
                st.session_state.selected_memories.append(entry["path"])
        else:
            if entry["path"] in st.session_state.selected_memories:
                st.session_state.selected_memories.remove(entry["path"])


def render_memory_panel(
    *,
    tier0_shell: dict[str, Any] | None = None,
    tier1_shell: dict[str, Any] | None = None,
) -> None:
    """渲染記憶面板（側邊欄）"""

    if "selected_memories" not in st.session_state:
        st.session_state.selected_memories = []

    view_model = build_memory_panel_view_model(
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        selected_count=len(st.session_state.selected_memories),
    )

    st.subheader(view_model["title"])
    st.caption(view_model["subtitle"])
    st.info(
        f"Tier 0 readiness: `{view_model['tier0_readiness']}`"
        + (
            f" | short board: {view_model['current_short_board']}"
            if view_model["current_short_board"]
            else ""
        )
    )
    if view_model["closeout_attention"]:
        st.warning(f"Closeout attention: {view_model['closeout_attention']}")
    st.caption(view_model["operator_note"])

    search = st.text_input("搜尋", "", key="memory_panel_search")

    skills = list_skills()
    entries = list_memory_entries()

    if search:
        keyword = search.strip().lower()
        skills = [s for s in skills if keyword in s["name"].lower()]
        entries = [e for e in entries if keyword in e["title"].lower()]

    layered = {"seeds": [], "user": [], "session": [], "agent": []}
    for entry in entries:
        layer = entry.get("layer") or "seeds"
        if layer in layered:
            layered[layer].append(entry)
        else:
            layered.setdefault("seeds", []).append(entry)

    st.markdown("**技能庫**")
    for idx, skill in enumerate(skills[:6]):
        label = skill["name"]
        is_selected = skill["path"] in st.session_state.selected_memories
        if st.checkbox(label, value=is_selected, key=f"mem_skill_{idx}"):
            if skill["path"] not in st.session_state.selected_memories:
                st.session_state.selected_memories.append(skill["path"])
        else:
            if skill["path"] in st.session_state.selected_memories:
                st.session_state.selected_memories.remove(skill["path"])

    _render_memory_group("專案筆記", layered["seeds"], "seed", show_gate=True)

    with st.expander("使用者記憶", expanded=False):
        _render_memory_group("使用者記憶", layered["user"], "user")

    with st.expander("會話記憶", expanded=False):
        _render_memory_group("會話記憶", layered["session"], "session")

    conversations = list_conversations(limit=12)
    with st.expander("對話記錄", expanded=False):
        if conversations:
            _render_memory_group("對話記錄", conversations, "conversation")
        else:
            st.caption("尚無對話記錄。")

    with st.expander("代理記憶", expanded=False):
        _render_memory_group("代理記憶", layered["agent"], "agent")

    st.markdown("---")
    st.caption(f"已選擇 {view_model['selected_count']} 個參考")

    if st.button("新增參考"):
        st.info("新增參考功能開發中")


def load_memory_content(path: str) -> str:
    """載入記憶內容"""

    path_str = str(path)
    if path_str.startswith("ledger:"):
        record_id = path_str.split(":", 1)[-1]
        entry = load_conversation_entry(record_id)
        if not entry:
            return ""
        timestamp = entry.get("timestamp") or ""
        status = entry.get("status") or ""
        context = entry.get("context") if isinstance(entry.get("context"), dict) else {}
        user_message = context.get("user_message") or ""
        response = entry.get("response") or ""
        return (
            f"[對話記錄 {record_id}]\n"
            f"時間: {timestamp}\n"
            f"狀態: {status}\n"
            f"使用者: {user_message}\n"
            f"回覆: {response}\n"
        )

    path_obj = Path(path_str)
    if not path_obj.exists():
        return ""

    try:
        content = path_obj.read_text(encoding="utf-8")
    except Exception as exc:
        return f"[載入失敗: {exc}]"

    if len(content) > 2000:
        content = content[:2000] + "\n...(內容過長已截斷)"

    return content
