"""
Memory/reference panel for the dashboard workspace.
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
    closeout_summary = str((closeout_attention or {}).get("summary_text", "")).strip()

    return {
        "title": "參考資料",
        "subtitle": (
            "這裡只做 reference selection，不是 operator truth、hot-memory truth、"
            "或新的治理控制台。"
        ),
        "operator_note": (
            "先看 Tier 0 / Tier 1 的 readiness、short board、closeout attention；"
            "只有目前 bounded move 真的需要時，才挑選最小參考集合。"
        ),
        "reference_boundary_class": "auxiliary_only",
        "reference_boundary": (
            "Selected references may support search, drafting, and review, but they must not override "
            "Tier 0 / Tier 1 / Tier 2 operator truth."
        ),
        "selection_focus": "只選對目前 bounded move 有幫助的最小集合。",
        "selection_caution": (
            "Closeout attention is active. Do not use reference material to smooth over partial or blocked work."
            if closeout_summary
            else ""
        ),
        "tier0_readiness": str(tier0_shell.get("readiness_status", "")).strip() or "unknown",
        "current_short_board": str((canonical_cards or {}).get("short_board", "")).strip(),
        "closeout_attention": closeout_summary,
        "selected_count": int(selected_count),
        "selected_count_summary": f"已選 {int(selected_count)} 份參考資料",
        "section_labels": {
            "skills": "技能",
            "seeds": "種子記憶",
            "user": "使用者記憶",
            "session": "本輪記憶",
            "conversation": "對話記錄",
            "agent": "代理記憶",
        },
    }


def _render_memory_group(
    title: str,
    entries: list[dict[str, Any]],
    key_prefix: str,
    *,
    show_gate: bool = False,
) -> None:
    st.markdown(f"**{title}**")
    for idx, entry in enumerate(entries[:6]):
        entry_title = entry["title"][:16] + ("..." if len(entry["title"]) > 16 else "")
        is_selected = entry["path"] in st.session_state.selected_memories
        if show_gate:
            gate = str(entry.get("gate") or "").strip().upper()
            badge = {"PASS": "[PASS]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(gate, "[?]")
            label = f"{badge} {entry_title}"
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
    """Render the dashboard reference-selection panel."""

    if "selected_memories" not in st.session_state:
        st.session_state.selected_memories = []

    view_model = build_memory_panel_view_model(
        tier0_shell=tier0_shell,
        tier1_shell=tier1_shell,
        selected_count=len(st.session_state.selected_memories),
    )
    section_labels = view_model["section_labels"]

    st.subheader(view_model["title"])
    st.caption(view_model["subtitle"])
    st.info(
        f"就緒狀態: `{view_model['tier0_readiness']}`"
        + (
            f" | 短板: {view_model['current_short_board']}"
            if view_model["current_short_board"]
            else ""
        )
    )
    if view_model["closeout_attention"]:
        st.warning(f"收尾注意: {view_model['closeout_attention']}")
    st.caption(view_model["operator_note"])
    st.caption(view_model["reference_boundary"])
    if view_model["selection_caution"]:
        st.warning(view_model["selection_caution"])
    st.caption(view_model["selection_focus"])

    search = st.text_input("搜尋參考資料", "", key="memory_panel_search")

    skills = list_skills()
    entries = list_memory_entries()

    if search:
        keyword = search.strip().lower()
        skills = [skill for skill in skills if keyword in skill["name"].lower()]
        entries = [entry for entry in entries if keyword in entry["title"].lower()]

    layered: dict[str, list[dict[str, Any]]] = {
        "seeds": [],
        "user": [],
        "session": [],
        "agent": [],
    }
    for entry in entries:
        layer = entry.get("layer") or "seeds"
        if layer in layered:
            layered[layer].append(entry)
        else:
            layered["seeds"].append(entry)

    st.markdown(f"**{section_labels['skills']}**")
    for idx, skill in enumerate(skills[:6]):
        label = skill["name"]
        is_selected = skill["path"] in st.session_state.selected_memories
        if st.checkbox(label, value=is_selected, key=f"mem_skill_{idx}"):
            if skill["path"] not in st.session_state.selected_memories:
                st.session_state.selected_memories.append(skill["path"])
        else:
            if skill["path"] in st.session_state.selected_memories:
                st.session_state.selected_memories.remove(skill["path"])

    _render_memory_group(section_labels["seeds"], layered["seeds"], "seed", show_gate=True)

    with st.expander(section_labels["user"], expanded=False):
        _render_memory_group(section_labels["user"], layered["user"], "user")

    with st.expander(section_labels["session"], expanded=False):
        _render_memory_group(section_labels["session"], layered["session"], "session")

    conversations = list_conversations(limit=12)
    with st.expander(section_labels["conversation"], expanded=False):
        if conversations:
            _render_memory_group(section_labels["conversation"], conversations, "conversation")
        else:
            st.caption("尚無對話記錄。")

    with st.expander(section_labels["agent"], expanded=False):
        _render_memory_group(section_labels["agent"], layered["agent"], "agent")

    st.markdown("---")
    st.caption(view_model["selected_count_summary"])

    if st.button("清空已選參考"):
        st.session_state.selected_memories = []
        st.info("已清空目前選取的參考資料。")


def load_memory_content(path: str) -> str:
    """Load selected reference content for the workspace chat context."""

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
        return f"[讀取失敗: {exc}]"

    if len(content) > 2000:
        content = content[:2000] + "\n...(內容過長，已截斷)"

    return content
