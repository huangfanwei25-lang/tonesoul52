"""
Live Data — file-mtime polling for auto-refresh.

Watches governance state files and triggers st.rerun() when they change.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import streamlit as st

# Files to watch for changes
_WATCH_FILES = [
    "governance_state.json",
    "memory/autonomous/session_traces.jsonl",
    "memory/autonomous/zone_registry.json",
    "memory/conversation_ledger.jsonl",
]


def _get_workspace() -> Path:
    return Path(__file__).resolve().parents[3]


def _collect_mtimes() -> Dict[str, float]:
    """Collect modification times for watched files."""
    workspace = _get_workspace()
    mtimes: Dict[str, float] = {}
    for rel in _WATCH_FILES:
        p = workspace / rel
        if p.exists():
            mtimes[rel] = p.stat().st_mtime
        else:
            mtimes[rel] = 0.0
    return mtimes


def check_for_changes() -> bool:
    """Check if any watched file changed since last check.

    Returns True if changes detected (caller should rerun).
    """
    current = _collect_mtimes()
    previous: Optional[Dict[str, float]] = st.session_state.get("_live_data_mtimes")

    if previous is None:
        st.session_state["_live_data_mtimes"] = current
        return False

    changed = current != previous
    if changed:
        st.session_state["_live_data_mtimes"] = current
        # Clear world HTML cache so it rebuilds with fresh data
        st.session_state.pop("world_html_cache", None)
    return changed


def render_auto_refresh_toggle() -> None:
    """Render auto-refresh toggle in sidebar. Call from overview page."""
    auto = st.sidebar.checkbox("自動更新", value=False, key="live_auto_refresh")
    if auto:
        if check_for_changes():
            st.rerun()
        st.sidebar.caption("監控中 — 治理狀態變更時自動重新載入")
    else:
        st.sidebar.caption("手動模式 — 按 R 重新載入")
