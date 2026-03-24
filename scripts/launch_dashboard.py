#!/usr/bin/env python3
"""Launch the ToneSoul governance dashboard with state auto-loaded.

Reads governance_state.json, injects it into the dashboard HTML,
and opens your browser — one command, zero friction.

Usage:
    python scripts/launch_dashboard.py
    python scripts/launch_dashboard.py --state path/to/governance_state.json
    python scripts/launch_dashboard.py --port 8765
"""
from __future__ import annotations

import argparse
import http.server
import json
import sys
import threading
import webbrowser
from pathlib import Path

DASHBOARD_HTML = Path(__file__).resolve().parent.parent / "apps" / "dashboard" / "index.html"

SEARCH_PATHS = [
    Path.home() / ".gemini" / "tonesoul" / "governance_state.json",
    Path.home() / ".codex" / "memories" / "governance_state.json",
    Path.cwd() / "governance_state.json",
]

INJECT_SCRIPT = """
<script>
// Auto-injected by launch_dashboard.py
(function() {{
  const STATE = {state_json};
  window.addEventListener('DOMContentLoaded', function() {{
    // Hide drop zone, show dashboard
    var dz = document.getElementById('dropZone');
    if (dz) dz.style.display = 'none';
    var db = document.getElementById('dashboard');
    if (db) db.classList.add('active');
    // Render
    if (typeof renderDashboard === 'function') {{
      renderDashboard(STATE, '{filename}');
    }}
  }});
}})();
</script>
"""


def find_state(explicit: Path | None) -> Path | None:
    """Find governance_state.json from explicit path or known locations."""
    if explicit and explicit.exists():
        return explicit
    for p in SEARCH_PATHS:
        if p.exists():
            return p
    return None


def build_html(state_path: Path) -> str:
    """Read dashboard HTML and inject governance state."""
    html = DASHBOARD_HTML.read_text(encoding="utf-8")
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    state_json = json.dumps(state_data, ensure_ascii=False)

    # We need renderDashboard to be globally accessible
    # Modify the HTML to expose it
    html = html.replace("function renderDashboard(", "window.renderDashboard = function(")

    inject = INJECT_SCRIPT.format(
        state_json=state_json,
        filename=state_path.name,
    )
    html = html.replace("</body>", inject + "\n</body>")
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch ToneSoul governance dashboard")
    parser.add_argument("--state", type=Path, default=None, help="Path to governance_state.json")
    parser.add_argument("--port", type=int, default=0, help="HTTP port (0 = auto)")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    if not DASHBOARD_HTML.exists():
        print(f"ERROR: Dashboard not found at {DASHBOARD_HTML}")
        sys.exit(1)

    state_path = find_state(args.state)
    if state_path is None:
        print("No governance_state.json found. Searched:")
        for p in SEARCH_PATHS:
            print(f"  {'✓' if p.exists() else '✗'} {p}")
        print("\nRun: python scripts/init_governance_state.py --output ./governance_state.json")
        sys.exit(1)

    print(f"Loading state from: {state_path}")
    html_content = build_html(state_path)

    # Serve via simple HTTP server
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))

        def log_message(self, format: str, *log_args: object) -> None:
            pass  # Quiet

    server = http.server.HTTPServer(("127.0.0.1", args.port), Handler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"

    print(f"Dashboard running at: {url}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
