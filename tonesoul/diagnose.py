"""ToneSoul Self-Diagnostic — one command to see everything.

Any AI agent runs this at session start to understand:
  1. Am I connected to Redis or falling back to files?
  2. Is memory integrity intact? (Aegis audit)
  3. Who has been here since I was last here?
  4. What's the current governance posture?
  5. What happened in recent sessions?

Usage:
    python -m tonesoul.diagnose
    python -m tonesoul.diagnose --agent claude-opus-4-6

Or from code:
    from tonesoul.diagnose import full_diagnostic
    report = full_diagnostic(agent_id="claude-opus-4-6")
    print(report)
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def compact_diagnostic(agent_id: str = "unknown") -> str:
    """One-line diagnostic — minimal context cost."""
    try:
        from tonesoul.store import get_store
        from tonesoul.runtime_adapter import load
        store = get_store()
        posture = load(agent_id=agent_id, source="diagnose")
        si = posture.soul_integral
        vows = len(posture.active_vows)
        tensions = len(posture.tension_history)
        backend = store.backend_name

        traces_n = len(store.get_traces(n=999))
        zones_data = store.get_zones() if store.is_redis else {}
        zones_n = len(zones_data.get("zones", []))

        aegis = "?"
        if store.is_redis:
            try:
                from tonesoul.aegis_shield import AegisShield
                shield = AegisShield.load(store)
                audit = shield.audit(store)
                aegis = audit["integrity"]
            except Exception:
                pass

        return (
            f"[ToneSoul] {backend} | SI={si:.2f} | "
            f"vows={vows} tensions={tensions} | "
            f"traces={traces_n} zones={zones_n} | "
            f"aegis={aegis} | agent={agent_id}"
        )
    except Exception as e:
        return f"[ToneSoul] Diagnostic error: {e}"


def full_diagnostic(agent_id: str = "unknown") -> str:
    """Run all diagnostics, return human-readable report."""
    lines: list[str] = []
    lines.append("╔══════════════════════════════════════════╗")
    lines.append("║     ToneSoul System Diagnostic           ║")
    lines.append("╚══════════════════════════════════════════╝")
    lines.append(f"  Time: {datetime.now(timezone.utc).isoformat()[:19]}Z")
    lines.append(f"  Agent: {agent_id}")
    lines.append("")

    # ── 1. Storage backend ──
    try:
        from tonesoul.store import get_store
        store = get_store()
        lines.append(f"[Storage] Backend: {store.backend_name}")
        if store.is_redis:
            info = store._r.info("memory")
            used_mb = info.get("used_memory", 0) / (1024 * 1024)
            lines.append(f"  Redis memory: {used_mb:.1f} MB")
            lines.append(f"  Keys: {store._r.dbsize()}")
    except Exception as e:
        lines.append(f"[Storage] ERROR: {e}")
        store = None

    lines.append("")

    # ── 2. Governance posture ──
    try:
        from tonesoul.runtime_adapter import load, summary
        posture = load(agent_id=agent_id, source="diagnose")
        lines.append(summary(posture))
    except Exception as e:
        lines.append(f"[Governance] ERROR: {e}")

    lines.append("")

    # ── 3. Aegis integrity ──
    if store is not None:
        try:
            from tonesoul.aegis_shield import AegisShield
            shield = AegisShield.load(store)
            audit = shield.audit(store)
            status = audit["integrity"]
            icon = "✓" if status == "intact" else "✗"
            lines.append(f"[Aegis Shield] Integrity: {icon} {status}")
            lines.append(f"  Chain valid: {audit['chain_valid']}")
            lines.append(f"  Total traces: {audit['total_traces']}")
            if audit["chain_errors"]:
                for err in audit["chain_errors"][:3]:
                    lines.append(f"  CHAIN ERROR: {err}")
            sig_fail = audit["signature_failures"]
            signed = audit["total_traces"] - len(sig_fail)
            lines.append(f"  Signed: {signed}/{audit['total_traces']}")
            if sig_fail:
                unsigned = [f for f in sig_fail if f["reason"] == "no signature"]
                tampered = [f for f in sig_fail if f["reason"] != "no signature"]
                if unsigned:
                    lines.append(f"  Unsigned (legacy): {len(unsigned)}")
                if tampered:
                    lines.append(f"  ⚠ TAMPERED: {len(tampered)}")
                    for t in tampered[:3]:
                        lines.append(f"    entry {t['entry']}: {t['reason']}")
        except ImportError:
            lines.append("[Aegis Shield] Not available (PyNaCl not installed)")
        except Exception as e:
            lines.append(f"[Aegis Shield] ERROR: {e}")
    else:
        lines.append("[Aegis Shield] Skipped (no store)")

    lines.append("")

    # ── 4. Recent sessions ──
    if store is not None:
        try:
            traces = store.get_traces(n=5)
            lines.append(f"[Recent Sessions] (last {len(traces)})")
            for t in reversed(traces[-5:]):
                agent = t.get("agent", "?")
                ts = t.get("timestamp", "")[:16]
                topics = ", ".join(t.get("topics", [])[:3])
                decisions = len(t.get("key_decisions", []))
                lines.append(f"  {ts} | {agent:20s} | {topics}")
                if decisions:
                    lines.append(f"    → {decisions} key decisions")
        except Exception as e:
            lines.append(f"[Recent Sessions] ERROR: {e}")

    lines.append("")

    # ── 5. World map zones ──
    if store is not None:
        try:
            zones_data = store.get_zones()
            zones = zones_data.get("zones", [])
            if zones:
                lines.append(f"[World Map] {len(zones)} zones, {zones_data.get('total_sessions', '?')} sessions")
                lines.append(f"  Mood: {zones_data.get('world_mood', '?')} | Weather: {zones_data.get('weather', '?')}")
                for z in sorted(zones, key=lambda x: -x.get("visit_count", 0))[:5]:
                    lines.append(f"  Lv{z.get('level', '?')} {z.get('name', '?'):16s} visits={z.get('visit_count', 0)}")
        except Exception as e:
            lines.append(f"[World Map] ERROR: {e}")

    lines.append("")
    lines.append("─" * 44)
    return "\n".join(lines)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="ToneSoul System Diagnostic")
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--compact", action="store_true", help="One-line output, minimal context cost")
    args = parser.parse_args()

    import os
    os.environ.setdefault("TONESOUL_REDIS_URL", "redis://:tonesoul-2026@localhost:6379/0")

    if args.compact:
        print(compact_diagnostic(agent_id=args.agent))
    else:
        print(full_diagnostic(agent_id=args.agent))


if __name__ == "__main__":
    main()
