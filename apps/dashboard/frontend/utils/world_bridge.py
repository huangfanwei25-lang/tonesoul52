"""
World Bridge — bridges Python governance data into the world.html RPG map.

Loads governance state, zone registry, visitor list, and Aegis integrity,
serialises everything as JSON, and injects it into world.html <script> globals
so Streamlit can render the world map via st.components.v1.html().
"""

import json
from pathlib import Path
from typing import Any, Dict, List


def _load_world_data() -> Dict[str, Any]:
    """Load zone registry (WorldState)."""
    try:
        from tonesoul.zone_registry import load as load_zones

        ws = load_zones()
        return ws if isinstance(ws, dict) else ws.to_dict() if hasattr(ws, "to_dict") else {}
    except Exception:
        # Fallback: read JSON directly
        path = Path(__file__).resolve().parents[4] / "memory" / "autonomous" / "zone_registry.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"zones": [], "total_sessions": 0, "world_mood": "serene", "weather": "clear"}


def _load_gov_data() -> Dict[str, Any]:
    """Load governance posture."""
    try:
        from tonesoul.runtime_adapter import load

        p = load()
        return p.to_dict() if hasattr(p, "to_dict") else {}
    except Exception:
        path = Path(__file__).resolve().parents[4] / "governance_state.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {"soul_integral": 0.0, "session_count": 0, "active_vows": [], "baseline_drift": {}}


def _load_visitors() -> List[Dict[str, Any]]:
    """Load recent visitor list."""
    try:
        from tonesoul.runtime_adapter import get_recent_visitors

        return get_recent_visitors() or []
    except Exception:
        return []


def _load_aegis() -> Dict[str, Any]:
    """Load Aegis Shield integrity status."""
    try:
        from tonesoul.aegis_shield import AegisShield

        shield = AegisShield.load()
        report = shield.audit()
        return {
            "integrity": report.get("integrity", "unknown"),
            "chain_valid": report.get("chain_valid", False),
            "total_traces": report.get("total_traces", 0),
            "signature_failures": report.get("signature_failures", 0),
        }
    except Exception:
        return {
            "integrity": "unknown",
            "chain_valid": False,
            "total_traces": 0,
            "signature_failures": 0,
        }


def build_world_html() -> str:
    """Build world.html with live governance data injected.

    Returns the complete HTML string ready for st.components.v1.html().
    """
    # Load data
    world_data = _load_world_data()
    gov_data = _load_gov_data()
    visitors = _load_visitors()
    aegis = _load_aegis()

    # Read world.html template
    world_html_path = Path(__file__).resolve().parents[2] / "world.html"
    if not world_html_path.exists():
        return "<p>world.html not found</p>"

    html = world_html_path.read_text(encoding="utf-8")

    # Inject data as JS globals before the first <script> tag
    injection = "<script>\n"
    injection += f"var __WORLD_DATA__ = {json.dumps(world_data, ensure_ascii=True)};\n"
    injection += f"var __GOV_DATA__ = {json.dumps(gov_data, ensure_ascii=True)};\n"
    injection += f"var __VISITORS__ = {json.dumps(visitors, ensure_ascii=True)};\n"
    injection += f"var __AEGIS__ = {json.dumps(aegis, ensure_ascii=True)};\n"
    injection += "</script>\n"

    # Insert before the first <script> tag in the HTML
    html = html.replace("<script>", injection + "<script>", 1)

    return html
