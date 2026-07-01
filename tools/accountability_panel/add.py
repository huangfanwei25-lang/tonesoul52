"""Append an accountability event (a co-observer calibration or a self-check) and regenerate the panel.

The bidirectional "you check me" input: record a calibration from the command line without hand-editing
events.json. Examples:

    # Fan-Wei catches me (co-observer lane) — the common case:
    python tools/accountability_panel/add.py --claim "我對 X 過度悲觀" --correction "其實有證據支持"

    # a self-check catch (a different model / test / self caught a claim):
    python tools/accountability_panel/add.py --lane self-check --claim "..." \
        --evidence E2 --caught-by "不同模型(codex)" --correction "..."

Defaults are tuned for the common case (Fan-Wei catching me): lane=co-observer, held=false (an event
is usually a *catch*), evidence='—', caught-by='人(梵威)'. Pass --held for a claim that survived.
After appending it re-validates the whole file and regenerates docs/status/accountability_panel_latest.html.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tonesoul.accountability_panel import AccountabilityEvent  # noqa: E402

EVENTS_PATH = Path(__file__).resolve().parent / "events.json"


def append_event(events_path: Path, event: AccountabilityEvent) -> int:
    """Append one validated event to the JSON ledger; return the new total count.

    Re-validates EVERY existing entry too (a malformed ledger is caught here, not silently), and
    writes back deterministically (indent=2, trailing newline, UTF-8, no BOM).
    """
    raw = json.loads(events_path.read_text(encoding="utf-8")) if events_path.exists() else []
    existing = [AccountabilityEvent(**e) for e in raw]  # revalidate the whole file
    updated = existing + [event]
    payload = [
        {
            "lane": e.lane,
            "claim": e.claim,
            "evidence_at_claim": e.evidence_at_claim,
            "held": e.held,
            "caught_by": e.caught_by,
            "correction": e.correction,
        }
        for e in updated
    ]
    events_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return len(updated)


def main() -> int:
    parser = argparse.ArgumentParser(description="Append an accountability / co-observation event.")
    parser.add_argument("--lane", choices=["co-observer", "self-check"], default="co-observer")
    parser.add_argument(
        "--claim", required=True, help="what was claimed (the thing being calibrated)"
    )
    parser.add_argument(
        "--evidence", default=None, help="E0..E4 or '—' (default: '—' co-observer / E1 self)"
    )
    parser.add_argument(
        "--held", action="store_true", help="set if the claim SURVIVED (default: a catch)"
    )
    parser.add_argument("--caught-by", dest="caught_by", default=None)
    parser.add_argument("--correction", default="")
    parser.add_argument("--no-regen", action="store_true", help="skip regenerating the HTML")
    args = parser.parse_args()

    evidence = args.evidence or ("—" if args.lane == "co-observer" else "E1")
    caught_by = args.caught_by or ("人(梵威)" if args.lane == "co-observer" else "自己")

    try:
        event = AccountabilityEvent(
            claim=args.claim,
            evidence_at_claim=evidence,
            held=args.held,
            caught_by=caught_by,
            correction=args.correction,
            lane=args.lane,
        )
    except ValueError as exc:
        sys.stderr.write(f"[add] rejected: {exc}\n")
        return 2

    total = append_event(EVENTS_PATH, event)
    sys.stdout.buffer.write(
        f"[add] appended to {args.lane}; ledger now has {total} events\n".encode("utf-8")
    )

    if not args.no_regen:
        from tools.accountability_panel.generate import main as regen  # noqa: E402

        regen()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
