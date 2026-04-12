#!/usr/bin/env python3
"""Launch the ToneSoul governance dashboard.

Primary mode: Streamlit dashboard (apps/dashboard/frontend/app.py)
Legacy mode:  Static HTML dashboard (apps/dashboard/index.html) with --legacy flag

Usage:
    python scripts/launch_dashboard.py
    python scripts/launch_dashboard.py --port 8502
    python scripts/launch_dashboard.py --no-browser
    python scripts/launch_dashboard.py --legacy --state path/to/governance_state.json
"""

from __future__ import annotations

import argparse
import http.server
import json
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STREAMLIT_APP = REPO_ROOT / "apps" / "dashboard" / "frontend" / "app.py"
DASHBOARD_HTML = REPO_ROOT / "apps" / "dashboard" / "index.html"

SEARCH_PATHS = [
    Path.home() / ".gemini" / "tonesoul" / "governance_state.json",
    Path.home() / ".codex" / "memories" / "governance_state.json",
    Path.cwd() / "governance_state.json",
]

JOURNAL_SEARCH_PATHS = [
    Path(__file__).resolve().parent.parent / "memory" / "self_journal.jsonl",
    Path.home() / ".tonesoul" / "self_journal.jsonl",
]

INJECT_SCRIPT = """
<script>
// Auto-injected by launch_dashboard.py
(function() {{
  const STATE = {state_json};
  const JOURNAL = {journal_json};
  window.addEventListener('DOMContentLoaded', function() {{
    // Hide drop zone, show dashboard
    var dz = document.getElementById('dropZone');
    if (dz) dz.style.display = 'none';
    var db = document.getElementById('dashboard');
    if (db) db.classList.add('active');
    // Render
    if (typeof renderDashboard === 'function') {{
      renderDashboard(STATE, '{filename}', JOURNAL);
    }}
  }});
}})();
</script>
"""


def _relative_date_label(date_str: str, today: str) -> str:
    """Return '今天', '昨天', 'N 天前' relative to today."""
    try:
        from datetime import date as date_cls

        d = date_cls.fromisoformat(date_str)
        t = date_cls.fromisoformat(today)
        delta = (t - d).days
        if delta == 0:
            return "今天"
        if delta == 1:
            return "昨天"
        return f"{delta} 天前"
    except Exception:
        return date_str


def load_journal_entries(journal_path: Path | None, limit: int = 50) -> dict:
    """Read the most recent N entries, group by date, and compute verdict summary.

    Returns:
        {
            "groups": [{"date", "label", "count", "verdicts", "entries"}, ...],
            "verdict_summary": {"approve", "block", "concern", "dominant", "stress_level"}
        }
    """
    from datetime import date as date_cls

    path = journal_path
    if path is None:
        for p in JOURNAL_SEARCH_PATHS:
            if p.exists():
                path = p
                break

    empty: dict = {
        "groups": [],
        "verdict_summary": {
            "approve": 0,
            "block": 0,
            "concern": 0,
            "dominant": "",
            "stress_level": 0.0,
        },
    }
    if path is None or not path.exists():
        return empty

    raw_lines: list[str] = []
    try:
        with path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    raw_lines.append(line)
    except OSError:
        return empty

    today = date_cls.today().isoformat()
    recent = raw_lines[-limit:]

    # Parse entries newest-first
    entries: list[dict] = []
    for line in reversed(recent):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue

        payload = record.get("payload", {})
        timestamp = record.get("timestamp", payload.get("timestamp", ""))
        date_str = timestamp[:10] if timestamp else "—"

        verdict = payload.get("verdict", "")
        entry_type = payload.get("type", "self_reflection")
        title = f"{entry_type} · {verdict}" if verdict else entry_type

        reflection = payload.get("reflection") or payload.get("self_statement") or ""
        if len(reflection) > 300:
            reflection = reflection[:297] + "..."

        coherence = payload.get("coherence")
        core_divergence = payload.get("core_divergence", "")
        key_decision = payload.get("key_decision", "")

        entries.append(
            {
                "date": date_str,
                "label": _relative_date_label(date_str, today),
                "title": title,
                "body": reflection or "（無反思文字）",
                "verdict": verdict,
                "coherence": round(coherence, 3) if isinstance(coherence, float) else None,
                "core_divergence": core_divergence[:120] if core_divergence else "",
                "key_decision": key_decision[:120] if key_decision else "",
            }
        )

    # Group by date (preserve newest-first order)
    groups_map: dict[str, dict] = {}
    for e in entries:
        d = e["date"]
        if d not in groups_map:
            groups_map[d] = {
                "date": d,
                "label": e["label"],
                "count": 0,
                "verdicts": {"approve": 0, "block": 0, "concern": 0, "other": 0},
                "entries": [],
            }
        g = groups_map[d]
        g["count"] += 1
        v = e["verdict"]
        if v in ("approve", "block", "concern"):
            g["verdicts"][v] += 1
        elif v:
            g["verdicts"]["other"] += 1
        g["entries"].append(e)

    groups = list(groups_map.values())  # already newest-first from reversed iteration

    # Verdict summary across all entries (use up to 20 most recent)
    recent_20 = entries[:20]
    summary: dict[str, int] = {"approve": 0, "block": 0, "concern": 0}
    for e in recent_20:
        v = e["verdict"]
        if v in summary:
            summary[v] += 1

    total = sum(summary.values()) or 1
    dominant = max(summary, key=lambda k: summary[k])
    stress_level = round(summary["block"] / total, 3)

    print(f"Loaded {len(entries)} journal entries ({len(groups)} days) from {path}")
    return {
        "groups": groups,
        "verdict_summary": {**summary, "dominant": dominant, "stress_level": stress_level},
    }


def find_state(explicit: Path | None) -> Path | None:
    """Find governance_state.json from explicit path or known locations."""
    if explicit and explicit.exists():
        return explicit
    for p in SEARCH_PATHS:
        if p.exists():
            return p
    return None


def build_html(state_path: Path, journal_entries: list[dict]) -> str:
    """Read dashboard HTML and inject governance state + journal entries."""
    html = DASHBOARD_HTML.read_text(encoding="utf-8")
    state_data = json.loads(state_path.read_text(encoding="utf-8"))
    state_json = json.dumps(state_data, ensure_ascii=False)
    journal_json = json.dumps(journal_entries, ensure_ascii=False)

    # We need renderDashboard to be globally accessible
    # Modify the HTML to expose it
    html = html.replace("function renderDashboard(", "window.renderDashboard = function(")

    inject = INJECT_SCRIPT.format(
        state_json=state_json,
        journal_json=journal_json,
        filename=state_path.name,
    )
    html = html.replace("</body>", inject + "\n</body>")
    return html


def launch_streamlit(port: int, no_browser: bool) -> None:
    """Launch the Streamlit-based dashboard (primary mode)."""
    if not STREAMLIT_APP.exists():
        print(f"ERROR: Streamlit app not found at {STREAMLIT_APP}")
        sys.exit(1)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(STREAMLIT_APP),
        f"--server.port={port}",
        "--server.headless=true",
    ]

    print(f"Starting ToneSoul dashboard on port {port}...")
    proc = subprocess.Popen(cmd)

    if not no_browser:
        time.sleep(2)
        url = f"http://localhost:{port}"
        print(f"Opening {url}")
        webbrowser.open(url)

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        print("\nDashboard stopped.")


def launch_legacy(state_path_arg: Path | None, journal_path: Path | None,
                  journal_limit: int, port: int, no_browser: bool) -> None:
    """Launch the static HTML dashboard (legacy mode)."""
    if not DASHBOARD_HTML.exists():
        print(f"ERROR: Dashboard not found at {DASHBOARD_HTML}")
        sys.exit(1)

    state_path = find_state(state_path_arg)
    if state_path is None:
        print("No governance_state.json found. Searched:")
        for p in SEARCH_PATHS:
            print(f"  {'✓' if p.exists() else '✗'} {p}")
        print("\nRun: python scripts/init_governance_state.py --output ./governance_state.json")
        sys.exit(1)

    print(f"Loading state from: {state_path}")
    journal_entries = load_journal_entries(journal_path, limit=journal_limit)
    html_content = build_html(state_path, journal_entries)

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html_content.encode("utf-8"))

        def log_message(self, format: str, *log_args: object) -> None:
            pass

    server = http.server.HTTPServer(("127.0.0.1", port), Handler)
    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}"

    print(f"Dashboard running at: {url}")
    print("Press Ctrl+C to stop.\n")

    if not no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped.")
        server.shutdown()


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch ToneSoul governance dashboard")
    parser.add_argument("--port", type=int, default=8501, help="Port (default: 8501)")
    parser.add_argument("--no-browser", action="store_true", help="Don't auto-open browser")
    parser.add_argument("--legacy", action="store_true", help="Use static HTML dashboard instead of Streamlit")
    parser.add_argument("--state", type=Path, default=None, help="Path to governance_state.json (legacy mode)")
    parser.add_argument("--journal", type=Path, default=None, help="Path to self_journal.jsonl (legacy mode)")
    parser.add_argument(
        "--journal-limit", type=int, default=50, help="Max journal entries (legacy mode, default: 50)"
    )
    args = parser.parse_args()

    if args.legacy:
        legacy_port = args.port if args.port != 8501 else 0
        launch_legacy(args.state, args.journal, args.journal_limit, legacy_port, args.no_browser)
    else:
        launch_streamlit(args.port, args.no_browser)


if __name__ == "__main__":
    main()
