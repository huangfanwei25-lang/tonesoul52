#!/usr/bin/env python3
"""Launch the ToneSoul world map with live zone data.

Rebuilds zone_registry from session traces, injects data into world.html,
and opens your browser.

Usage:
    python scripts/launch_world.py
    python scripts/launch_world.py --port 8766
"""
from __future__ import annotations

import argparse
import http.server
import json
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORLD_HTML = ROOT / "apps" / "dashboard" / "world.html"
GOV_STATE = ROOT / "governance_state.json"
TRACES = ROOT / "memory" / "autonomous" / "session_traces.jsonl"
REGISTRY = ROOT / "memory" / "autonomous" / "zone_registry.json"

sys.path.insert(0, str(ROOT))


def build_html() -> str:
    """Rebuild zones from traces, inject into world.html."""
    from tonesoul.zone_registry import rebuild_and_save

    world = rebuild_and_save(
        traces_path=TRACES,
        governance_path=GOV_STATE,
        registry_path=REGISTRY,
    )
    world_json = json.dumps(world.to_dict(), ensure_ascii=False)

    gov_json = "{}"
    if GOV_STATE.exists():
        gov_json = GOV_STATE.read_text(encoding="utf-8")

    html = WORLD_HTML.read_text(encoding="utf-8")

    inject = f"""
<script>
// Auto-injected by launch_world.py
var __WORLD_DATA__ = {world_json};
var __GOV_DATA__ = {gov_json};
</script>
"""
    html = html.replace("</head>", inject + "\n</head>")
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch ToneSoul world map")
    parser.add_argument("--port", type=int, default=0, help="HTTP port (0 = auto)")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if not WORLD_HTML.exists():
        print(f"ERROR: world.html not found at {WORLD_HTML}")
        sys.exit(1)

    html_content = build_html()
    print(f"World rebuilt: zones from {TRACES}")

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))

        def log_message(self, fmt: str, *log_args: object) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", args.port), Handler)
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}"

    print(f"World map at: {url}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWorld map stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
