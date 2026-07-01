"""Generate the accountability / co-observation panel HTML from real events.

Reads tools/accountability_panel/events.json and writes a self-contained static page to
docs/status/accountability_panel_latest.html (matching the *_latest.html convention). No server, no
deps. The panel shows MISSES (claims that did not hold + who caught them), graded E0-E4, bidirectional
(self-check / co-observer).

Usage:
    python tools/accountability_panel/generate.py            # write the page
    python tools/accountability_panel/generate.py --stdout   # print HTML to stdout
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.accountability_panel import AccountabilityEvent, render_panel  # noqa: E402

EVENTS_PATH = Path(__file__).resolve().parent / "events.json"
OUT_PATH = REPO_ROOT / "docs" / "status" / "accountability_panel_latest.html"


def load_events() -> list[AccountabilityEvent]:
    raw = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    return [AccountabilityEvent(**e) for e in raw]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    events = load_events()
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")
    html_doc = render_panel(events, generated_at=generated_at)

    if args.stdout:
        sys.stdout.buffer.write(html_doc.encode("utf-8"))
        return 0
    OUT_PATH.write_text(html_doc, encoding="utf-8", newline="\n")
    sys.stdout.buffer.write(
        f"[wrote {OUT_PATH.relative_to(REPO_ROOT)} — {len(events)} events]\n".encode("utf-8")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
