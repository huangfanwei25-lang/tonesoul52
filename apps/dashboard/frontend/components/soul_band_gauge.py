"""
Soul Band Gauge — SVG radial gauge showing current soul band state.

Labels use friendly Chinese terms:
  serene=平靜, alert=警覺, strained=緊繃, critical=危機
"""

import math

import streamlit as st


_BAND_DEFS = [
    {"key": "serene", "label": "平靜", "color": "#4ade80", "start": 0.0, "end": 0.30},
    {"key": "alert", "label": "警覺", "color": "#facc15", "start": 0.30, "end": 0.55},
    {"key": "strained", "label": "緊繃", "color": "#f97316", "start": 0.55, "end": 0.80},
    {"key": "critical", "label": "危機", "color": "#ef4444", "start": 0.80, "end": 1.00},
]


def render_soul_band_gauge(
    soul_integral: float,
    band_name: str,
    gate_modifier: float,
    force_council: bool = False,
) -> None:
    """Render a radial gauge showing the current soul band."""
    si = max(0.0, min(1.0, soul_integral))

    # SVG dimensions
    cx, cy = 120, 100
    r = 75
    stroke_w = 14
    start_angle = 180  # left
    end_angle = 360    # right (semicircle)

    arcs = []
    for band in _BAND_DEFS:
        a0 = start_angle + band["start"] * (end_angle - start_angle)
        a1 = start_angle + band["end"] * (end_angle - start_angle)
        arcs.append(_arc_path(cx, cy, r, a0, a1, band["color"], stroke_w, opacity=0.3))

    # Active highlight
    active_band = next((b for b in _BAND_DEFS if b["key"] == band_name), _BAND_DEFS[0])
    a0 = start_angle + active_band["start"] * (end_angle - start_angle)
    a1 = start_angle + active_band["end"] * (end_angle - start_angle)
    arcs.append(_arc_path(cx, cy, r, a0, a1, active_band["color"], stroke_w, opacity=0.9))

    # Needle
    needle_angle = start_angle + si * (end_angle - start_angle)
    nx = cx + (r - 5) * math.cos(math.radians(needle_angle))
    ny = cy + (r - 5) * math.sin(math.radians(needle_angle))
    needle_svg = (
        f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" '
        f'stroke="#2c3e50" stroke-width="2.5" stroke-linecap="round"/>'
    )
    # Center dot
    center_dot = f'<circle cx="{cx}" cy="{cy}" r="5" fill="#2c3e50"/>'

    # Labels
    label = active_band["label"]
    color = active_band["color"]
    council_indicator = ""
    if force_council:
        council_indicator = (
            f'<circle cx="{cx + 55}" cy="{cy + 30}" r="6" fill="{color}" opacity="0.8">'
            f'<animate attributeName="opacity" values="0.8;0.3;0.8" dur="1.5s" repeatCount="indefinite"/>'
            f"</circle>"
            f'<text x="{cx + 70}" y="{cy + 35}" fill="{color}" font-size="11">審議中</text>'
        )

    svg = f"""
    <svg viewBox="0 0 240 150" xmlns="http://www.w3.org/2000/svg"
         style="max-width:240px;margin:0 auto;display:block">
      {''.join(arcs)}
      {needle_svg}
      {center_dot}
      <text x="{cx}" y="{cy + 28}" text-anchor="middle"
            font-size="22" font-weight="bold" fill="{color}">{label}</text>
      <text x="{cx}" y="{cy + 45}" text-anchor="middle"
            font-size="12" fill="#6b7c8d">壓力 {si:.2f} | 閘門 {gate_modifier:.0%}</text>
      {council_indicator}
    </svg>
    """

    st.markdown(f'<div class="ts-gauge">{svg}</div>', unsafe_allow_html=True)


def _arc_path(
    cx: float,
    cy: float,
    r: float,
    start_deg: float,
    end_deg: float,
    color: str,
    stroke_width: float,
    opacity: float = 1.0,
) -> str:
    """Generate an SVG arc path element."""
    x1 = cx + r * math.cos(math.radians(start_deg))
    y1 = cy + r * math.sin(math.radians(start_deg))
    x2 = cx + r * math.cos(math.radians(end_deg))
    y2 = cy + r * math.sin(math.radians(end_deg))
    large_arc = 1 if (end_deg - start_deg) > 180 else 0
    return (
        f'<path d="M {x1:.1f} {y1:.1f} A {r} {r} 0 {large_arc} 1 {x2:.1f} {y2:.1f}" '
        f'fill="none" stroke="{color}" stroke-width="{stroke_width}" '
        f'stroke-linecap="round" opacity="{opacity}"/>'
    )
