#!/usr/bin/env python3
"""Re-anchor the Aegis chain head to the trace-log tail — with provenance.

Why this exists (2026-07-03): the session-start diagnostic had been showing
``aegis=compromised`` for days. diagnose narrowed it to the benign branch
(chain valid, 0 signature failures, stored head != log tail — a local /
historical re-anchor gap, NOT tamper), but there was no tool to repair it,
so every session start cried wolf. Alarm fatigue in the integrity layer is
itself a risk: a real compromise would look exactly like the noise everyone
has learned to ignore.

Repair discipline (the ToneSoul way): the repair itself must leave a trace.
This tool never edits or deletes anything in the log. It appends a signed,
chained ``aegis_reanchor`` event that records the old stored head and the
tail it re-anchored to, then points the stored head at that new entry. The
gap stays visible in history; only the anchor moves.

Fail-closed: it refuses to touch anything unless the audit shows EXACTLY the
benign shape — chain_valid AND zero signature failures AND head!=tail. A
broken chain or bad signature is possible real tamper; that needs a human,
not an auto-repair. Default is dry-run; pass --apply to write.

Usage:
    python scripts/aegis_reanchor.py --agent <you>            # dry-run
    python scripts/aegis_reanchor.py --agent <you> --apply
    python scripts/aegis_reanchor.py --agent <you> --apply --reason "..."

Exit codes: 0 = intact already / dry-run ok / re-anchored+verified,
2 = refused (audit shape is not the benign re-anchor gap), 1 = error.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from tonesoul.aegis_shield import AegisShield  # noqa: E402

__ts_layer__ = "surface"
__ts_purpose__ = "Operator tool: repair the benign Aegis head/tail re-anchor gap, with provenance."


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def diagnose_gap(audit: dict) -> str:
    """Classify the audit result. Only 'reanchor_gap' is auto-repairable."""
    if audit.get("integrity") == "intact":
        return "intact"
    if (
        audit.get("chain_valid")
        and not audit.get("signature_failures")
        and not audit.get("head_matches_tail")
    ):
        return "reanchor_gap"
    return "unsafe"


def reanchor(store, shield: AegisShield, agent: str, reason: str, apply: bool) -> dict:
    """Audit; if the gap is the benign re-anchor shape, append a provenance
    event chained onto the log tail and move the stored head to it.

    Returns a result dict; raises nothing on the refusal path (see 'status').
    """
    before = shield.audit(store)
    shape = diagnose_gap(before)
    result = {
        "status": shape,
        "before": {
            "integrity": before["integrity"],
            "chain_head": before["chain_head"],
            "chain_tail": before["chain_tail"],
            "total_traces": before["total_traces"],
            "chain_errors": before["chain_errors"],
        },
        "applied": False,
    }
    if shape != "reanchor_gap" or not apply:
        return result

    event = {
        "type": "aegis_reanchor",
        "agent": agent,
        "timestamp": _utc_now(),
        "reason": reason,
        "old_stored_head": before["chain_head"],
        "reanchored_to_tail": before["chain_tail"],
        "audit_before": {
            "total_traces": before["total_traces"],
            "chain_valid": before["chain_valid"],
            "signature_failures": len(before["signature_failures"]),
        },
    }
    # Chain the event onto the ACTUAL log tail (the truth), not the stale
    # stored head. The stale head is preserved inside the event payload.
    shield.chain_head = before["chain_tail"]
    protected, check = shield.protect_trace(event, agent)
    if check.severity == "blocked":
        result["status"] = "blocked_by_content_filter"
        result["violations"] = check.violations
        return result
    store.append_trace(protected)
    shield.save(store)

    after = AegisShield.load(store).audit(store)
    result["applied"] = True
    result["after"] = {
        "integrity": after["integrity"],
        "chain_head": after["chain_head"],
        "total_traces": after["total_traces"],
    }
    result["status"] = "reanchored" if after["integrity"] == "intact" else "reanchor_failed"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", required=True, help="agent id signing the re-anchor event")
    parser.add_argument(
        "--reason",
        default="historical head/tail re-anchor gap (local trace store)",
        help="why the re-anchor is justified; recorded on the chained event",
    )
    parser.add_argument("--apply", action="store_true", help="write; default is dry-run")
    args = parser.parse_args()

    from tonesoul.store import get_store

    store = get_store()
    shield = AegisShield.load(store)
    result = reanchor(store, shield, args.agent, args.reason, args.apply)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result["status"] in ("intact", "reanchored"):
        return 0
    if result["status"] == "reanchor_gap":  # dry-run, repairable
        print("dry-run: gap is the benign re-anchor shape; re-run with --apply", file=sys.stderr)
        return 0
    print(
        "REFUSED: audit is not the benign re-anchor shape — possible real tamper "
        "or repair failure. Human review required.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
