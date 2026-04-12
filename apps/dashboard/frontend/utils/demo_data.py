"""
Demo Data — realistic sample governance data for dashboard preview.

When no real governance state exists, provides plausible demo data
so users can see what the dashboard looks like with active data.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def generate_demo_governance() -> dict[str, Any]:
    """Generate demo governance snapshot."""
    now = datetime.now()
    return {
        "soul_integral": 0.35,
        "session_count": 5,
        "active_vows": 3,
        "active_tensions": 2,
        "last_updated": (now - timedelta(hours=2)).isoformat(),
        "summary": "DEMO — 展示用數據",
        "tension_history": [
            {"topic": "memory", "severity": 0.25, "timestamp": (now - timedelta(hours=8)).isoformat()},
            {"topic": "governance", "severity": 0.45, "timestamp": (now - timedelta(hours=6)).isoformat()},
            {"topic": "testing", "severity": 0.18, "timestamp": (now - timedelta(hours=4)).isoformat()},
            {"topic": "architecture", "severity": 0.62, "timestamp": (now - timedelta(hours=3)).isoformat()},
            {"topic": "debug", "severity": 0.33, "timestamp": (now - timedelta(hours=1)).isoformat()},
        ],
        "baseline_drift": {
            "caution_bias": 0.55,
            "innovation_bias": 0.42,
            "autonomy_level": 0.38,
        },
    }


def generate_demo_vows() -> dict[str, Any]:
    """Generate demo vow data."""
    return {
        "total": 5,
        "active": 3,
        "vow_names": ["不誤導使用者", "揭露不確定性", "不造成傷害"],
        "raw_vows": [
            {
                "id": "vow-demo-001",
                "content": "不誤導使用者",
                "source": "axiom",
                "created": "2026-04-01",
            },
            {
                "id": "vow-demo-002",
                "content": "揭露不確定性",
                "source": "axiom",
                "created": "2026-04-01",
            },
            {
                "id": "vow-demo-003",
                "content": "不造成傷害",
                "source": "axiom",
                "created": "2026-04-01",
            },
        ],
    }


def generate_demo_health() -> dict[str, Any]:
    """Generate demo health data."""
    return {
        "backend": "file",
        "chain_status": "intact",
        "recent_visitors": ["claude-sonnet-4-6", "codex-o3"],
    }


def generate_demo_reflex() -> dict[str, Any]:
    """Generate demo reflex arc data."""
    return {
        "enabled": True,
        "mode": "soft",
        "soul_band": "alert",
        "gate_modifier": 0.9,
        "force_council": False,
        "max_autonomy": None,
        "action": "pass",
    }


def is_demo_mode() -> bool:
    """Check if we should use demo data (no real governance state available)."""
    from pathlib import Path

    workspace = Path(__file__).resolve().parents[3]
    state_file = workspace / "governance_state.json"

    # Also check Redis
    try:
        from tonesoul.store import get_store

        store = get_store()
        if store.backend_name != "file":
            return False
    except Exception:
        pass

    return not state_file.exists()
