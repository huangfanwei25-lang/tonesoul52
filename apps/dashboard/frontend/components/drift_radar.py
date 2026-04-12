"""
Drift Radar — three-axis indicator for baseline drift.

Friendly labels:
  caution_bias → 謹慎度
  innovation_bias → 創意度
  autonomy_level → 自主度
"""

import math
from typing import Dict

import streamlit as st


_AXES = [
    {"key": "caution_bias", "label": "謹慎度", "angle": 90},
    {"key": "innovation_bias", "label": "創意度", "angle": 210},
    {"key": "autonomy_level", "label": "自主度", "angle": 330},
]


def render_drift_radar(drift: Dict[str, float]) -> None:
    """Render a triangular radar chart for baseline drift values."""
    if not drift:
        st.caption("沒有性格偏移資料")
        return

    cx, cy = 100, 95
    r_max = 70

    # Background triangle (neutral = 0.5)
    neutral_pts = []
    for axis in _AXES:
        angle_rad = math.radians(axis["angle"] - 90)  # -90 to start from top
        nr = r_max * 0.5
        nx = cx + nr * math.cos(angle_rad)
        ny = cy + nr * math.sin(angle_rad)
        neutral_pts.append(f"{nx:.1f},{ny:.1f}")
    neutral_polygon = f'<polygon points="{" ".join(neutral_pts)}" fill="none" stroke="#b8d4e8" stroke-width="1" stroke-dasharray="4,4"/>'

    # Grid circles
    grid_circles = ""
    for pct in [0.25, 0.5, 0.75, 1.0]:
        gr = r_max * pct
        grid_circles += f'<circle cx="{cx}" cy="{cy}" r="{gr:.0f}" fill="none" stroke="rgba(90,142,192,0.12)" stroke-width="0.5"/>'

    # Axis lines and labels
    axis_lines = ""
    for axis in _AXES:
        angle_rad = math.radians(axis["angle"] - 90)
        ex = cx + r_max * math.cos(angle_rad)
        ey = cy + r_max * math.sin(angle_rad)
        axis_lines += f'<line x1="{cx}" y1="{cy}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="rgba(90,142,192,0.15)" stroke-width="0.5"/>'

        # Label
        lx = cx + (r_max + 16) * math.cos(angle_rad)
        ly = cy + (r_max + 16) * math.sin(angle_rad)
        val = drift.get(axis["key"], 0.5)
        axis_lines += (
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" dominant-baseline="middle" '
            f'font-size="11" fill="#6b7c8d">{axis["label"]} {val:.2f}</text>'
        )

    # Data polygon
    data_pts = []
    for axis in _AXES:
        val = max(0, min(1, drift.get(axis["key"], 0.5)))
        angle_rad = math.radians(axis["angle"] - 90)
        dr = r_max * val
        dx = cx + dr * math.cos(angle_rad)
        dy = cy + dr * math.sin(angle_rad)
        data_pts.append(f"{dx:.1f},{dy:.1f}")

    data_polygon = (
        f'<polygon points="{" ".join(data_pts)}" '
        f'fill="rgba(58,107,159,0.15)" stroke="#3a6b9f" stroke-width="1.5"/>'
    )

    # Data dots
    dots = ""
    for axis in _AXES:
        val = max(0, min(1, drift.get(axis["key"], 0.5)))
        angle_rad = math.radians(axis["angle"] - 90)
        dr = r_max * val
        dx = cx + dr * math.cos(angle_rad)
        dy = cy + dr * math.sin(angle_rad)
        dots += f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="3.5" fill="#3a6b9f"/>'

    svg = f"""
    <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"
         style="max-width:200px;margin:0 auto;display:block">
      {grid_circles}
      {axis_lines}
      {neutral_polygon}
      {data_polygon}
      {dots}
    </svg>
    """

    st.markdown(
        f'<div class="ts-card" style="text-align:center">'
        f'<div class="ts-section-title">性格偏移</div>'
        f"{svg}</div>",
        unsafe_allow_html=True,
    )
