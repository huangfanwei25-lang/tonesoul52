"""ToneSoul self-diagnostic entrypoint.

This command gives later agents one place to inspect:
1. storage backend and posture source
2. current governance posture
3. Aegis integrity posture
4. recent accepted traces
5. shared-runtime coordination surfaces such as claims and compactions
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import Any


def _utc_now_trimmed() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit_text(text: str) -> None:
    """Write terminal output safely on Windows code pages.

    Some ToneSoul data contains Unicode that a local console encoding may not
    support. Emit bytes with replacement instead of crashing the diagnostic.
    """
    payload = text if text.endswith("\n") else f"{text}\n"
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    data = payload.encode(encoding, errors="replace")
    buffer = getattr(sys.stdout, "buffer", None)
    if buffer is not None:
        buffer.write(data)
        buffer.flush()
        return
    sys.stdout.write(data.decode(encoding, errors="replace"))
    sys.stdout.flush()


def _clip(text: str, limit: int = 72) -> str:
    stripped = " ".join(str(text or "").split())
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 3]}..."


def _packet(store, posture, *, trace_limit: int = 5, visitor_limit: int = 5) -> dict[str, Any]:
    from tonesoul.runtime_adapter import r_memory_packet

    try:
        return r_memory_packet(
            posture=posture,
            store=store,
            trace_limit=trace_limit,
            visitor_limit=visitor_limit,
        )
    except Exception:
        return {
            "recent_traces": [],
            "recent_visitors": [],
            "active_claims": [],
            "recent_compactions": [],
            "parallel_lanes": {},
        }


def compact_diagnostic(agent_id: str = "unknown") -> str:
    """One-line diagnostic for low-context session start."""
    try:
        from tonesoul.store import get_store
        from tonesoul.runtime_adapter import load

        store = get_store()
        posture = load(agent_id=agent_id, source="diagnose")
        packet = _packet(store, posture, trace_limit=3, visitor_limit=3)

        traces_n = len(store.get_traces(n=999))
        zones_n = 0
        try:
            zones_n = len((store.get_zones() or {}).get("zones", []))
        except Exception:
            zones_n = 0

        aegis = "unknown"
        try:
            from tonesoul.aegis_shield import AegisShield

            shield = AegisShield.load(store)
            audit = shield.audit(store)
            aegis = str(audit.get("integrity", "unknown"))
        except Exception:
            pass

        return (
            f"[ToneSoul] {store.backend_name} | SI={posture.soul_integral:.2f} | "
            f"vows={len(posture.active_vows)} tensions={len(posture.tension_history)} | "
            f"traces={traces_n} claims={len(packet.get('active_claims', []))} "
            f"compactions={len(packet.get('recent_compactions', []))} zones={zones_n} | "
            f"aegis={aegis} | agent={agent_id}"
        )
    except Exception as exc:
        return f"[ToneSoul] Diagnostic error: {exc}"


def full_diagnostic(agent_id: str = "unknown") -> str:
    """Run a full human-readable diagnostic report."""
    lines: list[str] = []
    lines.extend(
        [
            "============================================",
            "ToneSoul System Diagnostic",
            "============================================",
            f"Time: { _utc_now_trimmed() }",
            f"Agent: {agent_id}",
            "",
        ]
    )

    store = None
    posture = None
    packet: dict[str, Any] = {
        "recent_traces": [],
        "recent_visitors": [],
        "active_claims": [],
        "recent_compactions": [],
        "parallel_lanes": {},
    }

    try:
        from tonesoul.store import get_store

        store = get_store()
        lines.append(f"[Storage] Backend: {store.backend_name}")
        if getattr(store, "is_redis", False):
            info = store._r.info("memory")
            used_mb = info.get("used_memory", 0) / (1024 * 1024)
            lines.append(f"  Redis memory: {used_mb:.1f} MB")
            lines.append(f"  Keys: {store._r.dbsize()}")
    except Exception as exc:
        lines.append(f"[Storage] ERROR: {exc}")

    lines.append("")

    try:
        from tonesoul.runtime_adapter import load

        posture = load(agent_id=agent_id, source="diagnose")
        packet = _packet(store, posture) if store is not None else packet
        lines.extend(
            [
                "[Governance Posture]",
                f"  Soul Integral (Psi): {posture.soul_integral:.4f}",
                f"  Sessions: {posture.session_count}",
                f"  Last Updated: {posture.last_updated or 'unknown'}",
                "  Baseline Drift:",
                f"    caution={posture.baseline_drift.get('caution_bias', '?')}",
                f"    innovation={posture.baseline_drift.get('innovation_bias', '?')}",
                f"    autonomy={posture.baseline_drift.get('autonomy_level', '?')}",
                f"  Active Vows: {len(posture.active_vows)}",
                f"  Recent Tensions: {len(posture.tension_history)}",
            ]
        )
        for vow in posture.active_vows[:3]:
            lines.append(f"    vow[{vow.get('id', '?')}]: {_clip(vow.get('content', ''))}")
        for tension in posture.tension_history[-3:]:
            lines.append(
                "    tension:"
                f" severity={float(tension.get('severity', 0.0)):.2f}"
                f" topic={_clip(tension.get('topic', ''))}"
            )
    except Exception as exc:
        lines.append(f"[Governance Posture] ERROR: {exc}")

    lines.append("")

    if store is not None:
        try:
            from tonesoul.aegis_shield import AegisShield

            shield = AegisShield.load(store)
            audit = shield.audit(store)
            lines.extend(
                [
                    f"[Aegis Shield] Integrity: {audit.get('integrity', 'unknown')}",
                    f"  Chain valid: {audit.get('chain_valid')}",
                    f"  Total traces: {audit.get('total_traces')}",
                    f"  Signature failures: {len(audit.get('signature_failures', []))}",
                    f"  Chain errors: {len(audit.get('chain_errors', []))}",
                ]
            )
        except ImportError:
            lines.append("[Aegis Shield] Not available (PyNaCl not installed)")
        except Exception as exc:
            lines.append(f"[Aegis Shield] ERROR: {exc}")
    else:
        lines.append("[Aegis Shield] Skipped (no store)")

    lines.append("")

    traces = packet.get("recent_traces", [])
    lines.append(f"[Recent Sessions] count={len(traces)}")
    if traces:
        for trace in traces[-5:]:
            topics = ", ".join(trace.get("topics", [])[:3]) or "-"
            lines.append(
                "  "
                f"{trace.get('timestamp', '')[:16]} | "
                f"{trace.get('agent', 'unknown')} | "
                f"topics={topics} | "
                f"decisions={trace.get('key_decision_count', 0)}"
            )
    else:
        lines.append("  No recent accepted traces exposed in the current packet.")

    lines.append("")

    if store is not None:
        try:
            zones_data = store.get_zones() or {}
            zones = zones_data.get("zones", [])
            lines.append(
                f"[World Map] zones={len(zones)} total_sessions={zones_data.get('total_sessions', '?')}"
            )
            if zones:
                lines.append(
                    "  "
                    f"mood={zones_data.get('world_mood', '?')} "
                    f"weather={zones_data.get('weather', '?')}"
                )
                for zone in sorted(zones, key=lambda item: -item.get("visit_count", 0))[:5]:
                    lines.append(
                        "  "
                        f"Lv{zone.get('level', '?')} "
                        f"{zone.get('name', '?')} "
                        f"visits={zone.get('visit_count', 0)}"
                    )
        except Exception as exc:
            lines.append(f"[World Map] ERROR: {exc}")

    lines.append("")

    claims = packet.get("active_claims", [])
    compactions = packet.get("recent_compactions", [])
    visitors = packet.get("recent_visitors", [])
    lines.append(
        f"[Shared Runtime] claims={len(claims)} visitors={len(visitors)} compactions={len(compactions)}"
    )
    if claims:
        for claim in claims[:5]:
            first_path = (claim.get("paths") or ["-"])[0]
            lines.append(
                "  "
                f"claim {claim.get('task_id', '?')} | "
                f"agent={claim.get('agent', '?')} | "
                f"path={first_path} | "
                f"summary={_clip(claim.get('summary', ''))}"
            )
    else:
        lines.append("  No active task claims are visible right now.")
    if visitors:
        for visitor in visitors[:5]:
            lines.append(
                "  "
                f"visitor {visitor.get('timestamp', '')[:19]} | "
                f"{visitor.get('agent', '?')} | "
                f"source={visitor.get('source', '?')}"
            )
    if compactions:
        for entry in compactions[:3]:
            lines.append(
                "  "
                f"compaction {entry.get('updated_at', '')[:16]} | "
                f"{entry.get('agent', '?')} | "
                f"summary={_clip(entry.get('summary', ''))}"
            )
    else:
        lines.append("  No recent compactions are visible right now.")

    lanes = packet.get("parallel_lanes", {})
    if lanes:
        lines.extend(
            [
                "  Surfaces:",
                f"    packet=GET /packet or python scripts/run_r_memory_packet.py",
                f"    claims=POST /claim,/release or python scripts/run_task_claim.py",
                f"    perspectives={lanes.get('perspectives_surface', 'ts:perspectives:{agent_id}')}",
                f"    checkpoints={lanes.get('checkpoints_surface', 'ts:checkpoints:*')}",
                f"    compaction=POST /compact or python scripts/save_compaction.py",
                f"    canonical_commit_serialized={lanes.get('canonical_commit_serialized', True)}",
            ]
        )

    lines.append("")
    lines.extend(
        [
            "[Visibility Model]",
            "  Visible after explicit write: claims, perspectives, checkpoints, compactions, accepted traces.",
            "  Never assume visible: private reasoning, local context window, unstaged edits, or unwritten task state.",
            "",
            "[Recommended Order]",
            "  diagnose/load -> packet -> claim -> work -> perspective/checkpoint/compaction -> commit -> release",
            "============================================",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse
    import os

    parser = argparse.ArgumentParser(description="ToneSoul System Diagnostic")
    parser.add_argument("--agent", default="unknown")
    parser.add_argument("--compact", action="store_true", help="One-line output, minimal context cost")
    args = parser.parse_args()

    os.environ.setdefault("TONESOUL_REDIS_URL", "redis://:tonesoul-2026@localhost:6379/0")

    if args.compact:
        _emit_text(compact_diagnostic(agent_id=args.agent))
    else:
        _emit_text(full_diagnostic(agent_id=args.agent))


if __name__ == "__main__":
    main()
