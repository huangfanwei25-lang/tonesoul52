#!/usr/bin/env python3
"""Update governance_state.json from a session trace record.

Usage:
    python scripts/update_governance_state.py \
        --state ~/path/to/governance_state.json \
        --trace session_trace.json

    # Or pipe trace from stdin:
    echo '{"session_id":"..."}' | python scripts/update_governance_state.py \
        --state ~/path/to/governance_state.json --stdin

Core operations:
  1. Decay old tension_history entries based on elapsed time
  2. Append new tension events from the trace
  3. Update soul_integral with decay + new max tension
  4. Reconcile vow list (create / retire)
  5. Apply baseline drift
  6. Increment session_count
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# --- Constants (aligned with RFC-015) ---
TENSION_DECAY_ALPHA = 0.05  # per hour
TENSION_PRUNE_THRESHOLD = 0.01
DRIFT_RATE = 0.001
MAX_TENSION_HISTORY = 50  # cap to prevent unbounded growth


def parse_iso(ts: str) -> datetime:
    """Parse ISO 8601 timestamp, handling various formats."""
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        # Fallback: strip trailing Z and try again
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def decay_tensions(tensions: list[dict], now: datetime) -> list[dict]:
    """Apply exponential decay to tension history and prune."""
    kept = []
    for t in tensions:
        ts = parse_iso(t["timestamp"])
        hours = (now - ts).total_seconds() / 3600.0
        new_severity = t["severity"] * math.exp(-TENSION_DECAY_ALPHA * hours)
        if new_severity >= TENSION_PRUNE_THRESHOLD:
            t["severity"] = round(new_severity, 6)
            kept.append(t)
    return kept


def update_soul_integral(current: float, hours_since_last: float, max_tension: float) -> float:
    """S_new = S_old * e^(-alpha * hours) + max_tension_this_session."""
    decayed = current * math.exp(-TENSION_DECAY_ALPHA * hours_since_last)
    return round(decayed + max_tension, 6)


def apply_drift(baseline: dict[str, float], session_signals: dict[str, float]) -> dict[str, float]:
    """Apply 0.1% baseline drift toward session signals."""
    result = {}
    for key, old_val in baseline.items():
        signal = session_signals.get(key, old_val)
        new_val = old_val + DRIFT_RATE * (signal - old_val)
        result[key] = round(max(0.0, min(1.0, new_val)), 6)
    return result


def infer_session_signals(trace: dict) -> dict[str, float]:
    """Infer drift signals from trace content.

    Simple heuristics:
    - aegis_vetoes present -> caution_bias up
    - stance_shift present -> innovation_bias up
    - many key_decisions -> autonomy_level up
    """
    signals: dict[str, float] = {}

    if trace.get("aegis_vetoes"):
        signals["caution_bias"] = 0.70
    if trace.get("stance_shift"):
        signals["innovation_bias"] = 0.70
    if len(trace.get("key_decisions", [])) >= 3:
        signals["autonomy_level"] = 0.50

    return signals


def main() -> None:
    parser = argparse.ArgumentParser(description="Update governance state from trace")
    parser.add_argument("--state", type=Path, required=True, help="Path to governance_state.json")
    parser.add_argument("--trace", type=Path, default=None, help="Path to session trace JSON")
    parser.add_argument("--stdin", action="store_true", help="Read trace from stdin")
    parser.add_argument(
        "--trace-log", type=Path, default=None, help="Append trace to this JSONL log file"
    )
    args = parser.parse_args()

    # Load state
    if not args.state.exists():
        print(f"ERROR: State file not found: {args.state}")
        print("Run init_governance_state.py first.")
        sys.exit(1)

    state = json.loads(args.state.read_text(encoding="utf-8"))

    # Load trace
    if args.stdin:
        trace = json.loads(sys.stdin.read())
    elif args.trace:
        trace = json.loads(args.trace.read_text(encoding="utf-8"))
    else:
        print("ERROR: Provide --trace or --stdin")
        sys.exit(1)

    now = datetime.now(timezone.utc)
    last_updated = parse_iso(state["last_updated"])
    hours_since_last = (now - last_updated).total_seconds() / 3600.0

    # 1. Decay old tensions
    state["tension_history"] = decay_tensions(state["tension_history"], now)

    # 2. Append new tension events (with dedup)
    existing_keys = {
        (t.get("topic", ""), t.get("resolution", "")) for t in state["tension_history"]
    }
    for event in trace.get("tension_events", []):
        event.setdefault("timestamp", now.isoformat())
        key = (event.get("topic", ""), event.get("resolution", ""))
        if key not in existing_keys:
            state["tension_history"].append(event)
            existing_keys.add(key)

    # Cap history size
    if len(state["tension_history"]) > MAX_TENSION_HISTORY:
        state["tension_history"] = sorted(
            state["tension_history"],
            key=lambda t: t["severity"],
            reverse=True,
        )[:MAX_TENSION_HISTORY]

    # 3. Update soul_integral
    max_tension = max(
        (e["severity"] for e in trace.get("tension_events", [])),
        default=0.0,
    )
    state["soul_integral"] = update_soul_integral(
        state["soul_integral"], hours_since_last, max_tension
    )

    # 4. Reconcile vows
    for vow_event in trace.get("vow_events", []):
        if vow_event["action"] == "created":
            state["active_vows"].append(
                {
                    "id": vow_event["vow_id"],
                    "content": vow_event.get("detail", ""),
                    "created": now.isoformat(),
                    "source": "session",
                }
            )
        elif vow_event["action"] == "retired":
            state["active_vows"] = [
                v for v in state["active_vows"] if v["id"] != vow_event["vow_id"]
            ]

    # 5. Append aegis vetoes from trace
    for veto in trace.get("aegis_vetoes", []):
        veto.setdefault("timestamp", now.isoformat())
        state["aegis_vetoes"].append(veto)

    # 6. Apply baseline drift
    session_signals = infer_session_signals(trace)
    state["baseline_drift"] = apply_drift(state["baseline_drift"], session_signals)

    # 7. Increment session count
    state["session_count"] += 1
    state["last_updated"] = now.isoformat()

    # Write back
    args.state.write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    # Optionally append trace to log
    if args.trace_log:
        args.trace_log.parent.mkdir(parents=True, exist_ok=True)
        with args.trace_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(trace, ensure_ascii=False) + "\n")
        print(f"Trace appended to: {args.trace_log}")

    print(
        f"State updated: session_count={state['session_count']}, "
        f"soul_integral={state['soul_integral']:.4f}, "
        f"active_tensions={len(state['tension_history'])}"
    )


if __name__ == "__main__":
    main()
