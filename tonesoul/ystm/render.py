import json
import math
from typing import TYPE_CHECKING, Dict, List, Optional, Sequence, Tuple

from .schema import Node

if TYPE_CHECKING:
    from PIL import Image as PILImage


def xml_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def render_svg(
    nodes: Sequence[Node],
    points: Sequence[Tuple[float, float]],
    field_to_x: Optional[Dict[str, int]],
    segments_by_level: Dict[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]],
    bounds: Tuple[float, float, float, float],
    axis_labels: Optional[Tuple[str, str]] = None,
    drift_segments: Optional[Sequence[Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
    width: int = 900,
    height: int = 560,
    margin: int = 60,
) -> str:
    x_min, x_max, y_min, y_max = bounds
    x_span = x_max - x_min if x_max != x_min else 1.0
    y_span = y_max - y_min if y_max != y_min else 1.0

    def project(x: float, y: float) -> Tuple[float, float]:
        px = margin + (x - x_min) / x_span * (width - 2 * margin)
        py = margin + (y_max - y) / y_span * (height - 2 * margin)
        return px, py

    colors = ["#cfe8cf", "#a6d6a6", "#79c179", "#4da65b", "#2f8444"]
    levels = sorted(segments_by_level.keys())
    svg_lines = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        'xmlns="http://www.w3.org/2000/svg" role="img">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="8" refX="8" refY="4" '
        'orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L8,4 L0,8 Z" fill="#ef6c00" />',
        "</marker>",
        "</defs>",
    ]

    svg_lines.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="none" />')

    field_to_x = field_to_x or {}
    if field_to_x:
        svg_lines.append('<g class="grid-lines">')
        for mode, x_idx in field_to_x.items():
            px, _ = project(float(x_idx), y_min)
            svg_lines.append(
                f'<line x1="{px:.2f}" y1="{margin}" x2="{px:.2f}" y2="{height - margin}" '
                'stroke="#d7e4d3" stroke-width="1" class="grid-line" />'
            )
            label_x, _ = project(float(x_idx), y_min)
            svg_lines.append(
                f'<text x="{label_x:.2f}" y="{height - margin + 20}" '
                'text-anchor="middle" font-size="12" fill="#4c5c4c" class="axis-label">'
                f"{xml_escape(mode)}</text>"
            )
        svg_lines.append("</g>")

    svg_lines.append('<g class="contours">')
    for level_index, level in enumerate(levels):
        color = colors[level_index % len(colors)]
        for seg in segments_by_level[level]:
            (x1, y1), (x2, y2) = seg
            px1, py1 = project(x1, y1)
            px2, py2 = project(x2, y2)
            svg_lines.append(
                f'<line x1="{px1:.2f}" y1="{py1:.2f}" x2="{px2:.2f}" y2="{py2:.2f}" '
                f'stroke="{color}" stroke-width="1.2" class="contour level-{level_index}" />'
            )
    svg_lines.append("</g>")

    svg_lines.append('<g class="nodes">')
    for index, node in enumerate(nodes):
        x, y = points[index]
        px, py = project(x, y)
        label = xml_escape(node.id)
        tooltip = xml_escape(node.text)
        svg_lines.append(
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="6" fill="#1f2937" '
            'stroke="#f8fafc" stroke-width="1.5" class="node-dot" '
            f'data-node-id="{label}">'
            f"<title>{tooltip}</title></circle>"
        )
        svg_lines.append(
            f'<text x="{px + 8:.2f}" y="{py - 8:.2f}" font-size="11" '
            f'fill="#1f2937" class="node-label">{label}</text>'
        )
    svg_lines.append("</g>")

    if drift_segments is None:
        drift_segments = [(points[index - 1], points[index]) for index in range(1, len(points))]

    svg_lines.append('<g class="drift-lines">')
    for (x0, y0), (x1, y1) in drift_segments:
        px0, py0 = project(x0, y0)
        px1, py1 = project(x1, y1)
        svg_lines.append(
            f'<line x1="{px0:.2f}" y1="{py0:.2f}" x2="{px1:.2f}" y2="{py1:.2f}" '
            'stroke="#ef6c00" stroke-width="2" marker-end="url(#arrow)" class="drift" />'
        )
    svg_lines.append("</g>")

    svg_lines.append(
        f'<rect x="{margin}" y="{margin}" width="{width - 2 * margin}" '
        f'height="{height - 2 * margin}" fill="none" stroke="#94a88f" '
        'stroke-width="1" />'
    )
    if axis_labels:
        x_label, y_label = axis_labels
        svg_lines.append(
            f'<text x="{width / 2:.2f}" y="{height - 18:.2f}" '
            'text-anchor="middle" font-size="12" fill="#4c5c4c" class="axis-label">'
            f"{xml_escape(x_label)}</text>"
        )
        svg_lines.append(
            f'<text x="{18:.2f}" y="{height / 2:.2f}" '
            f'text-anchor="middle" font-size="12" fill="#4c5c4c" '
            f'transform="rotate(-90 18 {height / 2:.2f})" class="axis-label">'
            f"{xml_escape(y_label)}</text>"
        )
    svg_lines.append("</svg>")
    return "\n".join(svg_lines)


def render_png(
    nodes: Sequence[Node],
    points: Sequence[Tuple[float, float]],
    field_to_x: Optional[Dict[str, int]],
    segments_by_level: Dict[float, List[Tuple[Tuple[float, float], Tuple[float, float]]]],
    bounds: Tuple[float, float, float, float],
    axis_labels: Optional[Tuple[str, str]] = None,
    drift_segments: Optional[Sequence[Tuple[Tuple[float, float], Tuple[float, float]]]] = None,
    width: int = 900,
    height: int = 560,
    margin: int = 60,
    scale: float = 1.0,
) -> Optional["PILImage.Image"]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return None

    if scale <= 0:
        scale = 1.0
    width_px = max(1, int(width * scale))
    height_px = max(1, int(height * scale))
    margin_px = max(1, int(margin * scale))

    x_min, x_max, y_min, y_max = bounds
    x_span = x_max - x_min if x_max != x_min else 1.0
    y_span = y_max - y_min if y_max != y_min else 1.0

    def project(x: float, y: float) -> Tuple[float, float]:
        px = margin_px + (x - x_min) / x_span * (width_px - 2 * margin_px)
        py = margin_px + (y_max - y) / y_span * (height_px - 2 * margin_px)
        return px, py

    def color(hex_value: str) -> Tuple[int, int, int]:
        return tuple(int(hex_value[i : i + 2], 16) for i in (1, 3, 5))

    img = Image.new("RGB", (width_px, height_px), color("#f5f7f2"))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    field_to_x = field_to_x or {}
    grid_color = color("#d7e4d3")
    if field_to_x:
        for mode, x_idx in field_to_x.items():
            px, _ = project(float(x_idx), y_min)
            draw.line(
                [(px, margin_px), (px, height_px - margin_px)],
                fill=grid_color,
                width=max(1, int(1 * scale)),
            )
            draw.text(
                (px - 10, height_px - margin_px + 4),
                str(mode),
                fill=color("#4c5c4c"),
                font=font,
            )

    contour_colors = ["#cfe8cf", "#a6d6a6", "#79c179", "#4da65b", "#2f8444"]
    levels = sorted(segments_by_level.keys())
    for level_index, level in enumerate(levels):
        stroke = color(contour_colors[level_index % len(contour_colors)])
        for seg in segments_by_level[level]:
            (x1, y1), (x2, y2) = seg
            px1, py1 = project(x1, y1)
            px2, py2 = project(x2, y2)
            draw.line(
                [(px1, py1), (px2, py2)],
                fill=stroke,
                width=max(1, int(1.2 * scale)),
            )

    if drift_segments is None:
        drift_segments = [(points[index - 1], points[index]) for index in range(1, len(points))]
    drift_color = color("#ef6c00")
    for (x0, y0), (x1, y1) in drift_segments:
        px0, py0 = project(x0, y0)
        px1, py1 = project(x1, y1)
        draw.line(
            [(px0, py0), (px1, py1)],
            fill=drift_color,
            width=max(1, int(2 * scale)),
        )
        dx = px1 - px0
        dy = py1 - py0
        length = math.hypot(dx, dy)
        if length > 0:
            ux, uy = dx / length, dy / length
            size = max(6.0 * scale, 6.0)
            left = (px1 - ux * size - uy * size * 0.35, py1 - uy * size + ux * size * 0.35)
            right = (px1 - ux * size + uy * size * 0.35, py1 - uy * size - ux * size * 0.35)
            draw.line([(px1, py1), left], fill=drift_color, width=max(1, int(2 * scale)))
            draw.line([(px1, py1), right], fill=drift_color, width=max(1, int(2 * scale)))

    node_fill = color("#1f2937")
    node_outline = color("#f8fafc")
    node_radius = max(4.0 * scale, 4.0)
    for index, node in enumerate(nodes):
        x, y = points[index]
        px, py = project(x, y)
        draw.ellipse(
            [(px - node_radius, py - node_radius), (px + node_radius, py + node_radius)],
            fill=node_fill,
            outline=node_outline,
            width=max(1, int(1.5 * scale)),
        )
        draw.text(
            (px + node_radius + 2, py - node_radius - 2),
            str(node.id),
            fill=node_fill,
            font=font,
        )

    draw.rectangle(
        [margin_px, margin_px, width_px - margin_px, height_px - margin_px],
        outline=color("#94a88f"),
        width=max(1, int(1 * scale)),
    )

    if axis_labels:
        x_label, y_label = axis_labels
        draw.text(
            (width_px / 2 - 20, height_px - margin_px + 16),
            x_label,
            fill=color("#4c5c4c"),
            font=font,
        )
        draw.text(
            (12, height_px / 2),
            y_label,
            fill=color("#4c5c4c"),
            font=font,
        )

    return img


def render_html(svg: str, visual_params: Dict[str, object], nodes: Sequence[Node]) -> str:
    params_json = json.dumps(visual_params, indent=2)
    plane_label = visual_params.get("plane", "P1")
    plane_note = visual_params.get(
        "note",
        "Contours show E_total, arrows show drift between adjacent nodes.",
    )
    energy_note = visual_params.get("energy_note", "E_total = normalize(||v_sem||)")
    drift_note = visual_params.get("drift_note", "arrows = drift_ref")
    legend_note = xml_escape(f"{energy_note} | {drift_note}")
    node_payload = []
    for node in nodes:
        node_payload.append(
            {
                "id": node.id,
                "text": node.text,
                "where": {
                    "where_time": node.where.where_time.__dict__,
                    "where_field": node.where.where_field.__dict__,
                    "where_task": node.where.where_task.__dict__,
                },
                "scalar": node.scalar.__dict__,
                "drift": node.drift.__dict__,
            }
        )
    nodes_json = json.dumps(node_payload, indent=2)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>YSTM v0.1 Demo</title>
  <style>
    :root {{
      --ink: #1f2937;
      --muted: #4c5c4c;
      --accent: #ef6c00;
      --line: #dfe6d9;
      --bg1: #f5f7f2;
      --bg2: #e7efe0;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "Trebuchet MS", "DejaVu Sans", sans-serif;
      color: var(--ink);
      background: radial-gradient(1200px 600px at 10% 10%, var(--bg1), var(--bg2));
    }}
    .wrap {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 24px 48px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 260px;
      gap: 20px;
      align-items: start;
    }}
    h1 {{
      font-size: 28px;
      margin-bottom: 6px;
    }}
    p {{
      margin: 6px 0 18px;
      color: var(--muted);
      max-width: 720px;
    }}
    .panel {{
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 20px;
      background: rgba(255, 255, 255, 0.65);
      backdrop-filter: blur(6px);
      animation: rise 700ms ease-out;
    }}
    .controls {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 13px;
      color: var(--muted);
      margin-bottom: 12px;
    }}
    .controls label {{
      display: inline-flex;
      gap: 6px;
      align-items: center;
      cursor: pointer;
    }}
    .node-dot {{
      cursor: pointer;
      transition: transform 120ms ease;
    }}
    .node-dot:hover {{
      transform: scale(1.06);
    }}
    .node-dot.active {{
      stroke: var(--accent);
      stroke-width: 3;
    }}
    pre {{
      background: #f1f5f1;
      border-radius: 12px;
      padding: 12px 16px;
      font-size: 13px;
      color: #2f3b2f;
      overflow: auto;
    }}
    .legend {{
      margin-top: 16px;
      font-size: 13px;
      color: var(--muted);
    }}
    .side {{
      position: sticky;
      top: 20px;
    }}
    .detail-box {{
      white-space: pre-wrap;
      font-size: 12px;
      line-height: 1.5;
    }}
    @media (max-width: 960px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .side {{
        position: static;
      }}
    }}
    @keyframes rise {{
      from {{
        opacity: 0;
        transform: translateY(12px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>YSTM v0.1 Minimal Demo</h1>
    <p>
      Plane: {plane_label}. {plane_note} Visualization does not rewrite representation.
    </p>
    <div class="controls">
      <label><input type="checkbox" id="toggle-contours" checked />Contours</label>
      <label><input type="checkbox" id="toggle-drift" checked />Drift</label>
      <label><input type="checkbox" id="toggle-labels" checked />Labels</label>
    </div>
    <div class="layout">
      <div class="panel">
        {svg}
        <div class="legend">{legend_note}</div>
      </div>
      <div class="panel side">
        <strong>Node Details</strong>
        <div id="node-details" class="detail-box">Select a node.</div>
      </div>
    </div>
    <h2 style="margin-top: 24px;">Audit Parameters</h2>
    <pre>{params_json}</pre>
  </div>
  <script id="ystm-nodes" type="application/json">{nodes_json}</script>
  <script>
    const nodeData = JSON.parse(document.getElementById("ystm-nodes").textContent);
    const details = document.getElementById("node-details");
    const nodeEls = Array.from(document.querySelectorAll(".node-dot"));

    function formatNode(node) {{
      const drift = node.drift || {{}};
      const driftFrom = drift.drift_ref ? drift.drift_ref.from_node_id : "n/a";
      return [
        "id: " + node.id,
        "text: " + node.text,
        "mode: " + node.where.where_field.mode,
        "domain: " + node.where.where_task.domain,
        "turn: " + node.where.where_time.turn_id,
        "event_index: " + node.where.where_time.event_index,
        "E_total: " + node.scalar.E_total,
        "drift_from: " + driftFrom,
      ].join("\\n");
    }}

    function selectNode(id) {{
      nodeEls.forEach((el) => el.classList.remove("active"));
      const active = nodeEls.find((el) => el.dataset.nodeId === id);
      if (active) {{
        active.classList.add("active");
      }}
      const node = nodeData.find((item) => item.id === id);
      if (node) {{
        details.textContent = formatNode(node);
      }}
    }}

    nodeEls.forEach((el) => {{
      el.addEventListener("click", () => selectNode(el.dataset.nodeId));
    }});

    function toggle(selector, enabled) {{
      document.querySelectorAll(selector).forEach((el) => {{
        el.style.display = enabled ? "" : "none";
      }});
    }}

    document.getElementById("toggle-contours").addEventListener("change", (e) => {{
      toggle(".contour", e.target.checked);
    }});
    document.getElementById("toggle-drift").addEventListener("change", (e) => {{
      toggle(".drift", e.target.checked);
    }});
    document.getElementById("toggle-labels").addEventListener("change", (e) => {{
      toggle(".node-label", e.target.checked);
    }});

    if (nodeData.length) {{
      selectNode(nodeData[0].id);
    }}
  </script>
</body>
</html>
"""
