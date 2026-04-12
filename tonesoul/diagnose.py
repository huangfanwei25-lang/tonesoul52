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

from tonesoul.receiver_posture import build_receiver_parity_readout
from tonesoul.working_style import build_working_style_playbook


def _utc_now_trimmed() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _emit_text(text: str) -> None:
    """Write terminal output safely on Windows code pages.

    Always emit UTF-8 to stdout.buffer so that CJK characters (zone names,
    vow content, etc.) survive even when the console code page is cp950/cp936.
    Falls back to replacement encoding only when no binary buffer is available.
    """
    payload = text if text.endswith("\n") else f"{text}\n"
    data = payload.encode("utf-8", errors="replace")
    buffer = getattr(sys.stdout, "buffer", None)
    if buffer is not None:
        buffer.write(data)
        buffer.flush()
        return
    # No binary buffer — fall back to console encoding with replacement
    encoding = getattr(sys.stdout, "encoding", None) or "utf-8"
    sys.stdout.write(data.decode(encoding, errors="replace"))
    sys.stdout.flush()


def _clip(text: str, limit: int = 72) -> str:
    stripped = " ".join(str(text or "").split())
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 3]}..."


def _latest_council_dossier_summary(packet: dict[str, Any]) -> dict[str, Any]:
    for trace in list(packet.get("recent_traces") or []):
        summary = trace.get("council_dossier_summary")
        if isinstance(summary, dict) and summary:
            return summary
    for compaction in list(packet.get("recent_compactions") or []):
        dossier = compaction.get("council_dossier")
        if isinstance(dossier, dict) and dossier:
            return dossier
    return {}


def _packet(
    store,
    posture,
    *,
    observer_id: str = "",
    trace_limit: int = 5,
    visitor_limit: int = 5,
) -> dict[str, Any]:
    from tonesoul.runtime_adapter import r_memory_packet

    try:
        return r_memory_packet(
            posture=posture,
            store=store,
            observer_id=observer_id,
            trace_limit=trace_limit,
            visitor_limit=visitor_limit,
        )
    except Exception:
        return {
            "recent_traces": [],
            "recent_visitors": [],
            "active_claims": [],
            "recent_checkpoints": [],
            "recent_compactions": [],
            "recent_subject_snapshots": [],
            "recent_routing_events": [],
            "parallel_lanes": {},
            "posture": {"risk_posture": {}},
            "project_memory_summary": {},
            "coordination_mode": {},
            "operator_guidance": {},
        }


def compact_diagnostic(agent_id: str = "unknown") -> str:
    """One-line diagnostic for low-context session start."""
    try:
        from tonesoul.runtime_adapter import load
        from tonesoul.store import get_store

        store = get_store()
        posture = load(agent_id=agent_id, source="diagnose")
        packet = _packet(
            store,
            posture,
            observer_id=agent_id,
            trace_limit=3,
            visitor_limit=3,
        )

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
            f"R={float(((packet.get('posture') or {}).get('risk_posture') or {}).get('score', 0.0)):.2f}"
            f"/{((packet.get('posture') or {}).get('risk_posture') or {}).get('level', 'unknown')} | "
            f"coord={((packet.get('coordination_mode') or {}).get('mode', store.backend_name))} | "
            f"traces={traces_n} claims={len(packet.get('active_claims', []))} "
            f"compactions={len(packet.get('recent_compactions', []))} "
            f"subjects={len(packet.get('recent_subject_snapshots', []))} zones={zones_n} | "
            f"git={((packet.get('project_memory_summary') or {}).get('repo_progress') or {}).get('head', 'unknown')}"
            f"/dirty={int((((packet.get('project_memory_summary') or {}).get('repo_progress') or {}).get('dirty_count', 0) or 0))} | "
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
        "recent_checkpoints": [],
        "recent_compactions": [],
        "recent_subject_snapshots": [],
        "recent_routing_events": [],
        "parallel_lanes": {},
        "posture": {"risk_posture": {}},
        "project_memory_summary": {},
        "coordination_mode": {},
        "operator_guidance": {},
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
        packet = _packet(store, posture, observer_id=agent_id) if store is not None else packet
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
        risk_posture = (packet.get("posture") or {}).get("risk_posture") or {}
        if risk_posture:
            lines.extend(
                [
                    "  Risk Posture:",
                    f"    score={float(risk_posture.get('score', 0.0)):.2f}",
                    f"    level={risk_posture.get('level', 'unknown')}",
                    f"    action={risk_posture.get('recommended_action', 'unknown')}",
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
    checkpoints = packet.get("recent_checkpoints", [])
    compactions = packet.get("recent_compactions", [])
    subject_snapshots = packet.get("recent_subject_snapshots", [])
    visitors = packet.get("recent_visitors", [])
    lines.append(
        "[Shared Runtime] "
        f"claims={len(claims)} visitors={len(visitors)} checkpoints={len(checkpoints)} "
        f"compactions={len(compactions)} "
        f"subject_snapshots={len(subject_snapshots)}"
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
    if checkpoints:
        for entry in checkpoints[:3]:
            lines.append(
                "  "
                f"checkpoint {entry.get('updated_at', '')[:16]} | "
                f"{entry.get('agent', '?')} | "
                f"next={_clip(entry.get('next_action', ''))}"
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

    project_memory_summary = packet.get("project_memory_summary") or {}
    if project_memory_summary:
        lines.append("")
        lines.append("[Project Memory Summary]")
        lines.append(f"  {_clip(project_memory_summary.get('summary_text', ''))}")
        focus_topics = list(project_memory_summary.get("focus_topics") or [])
        if focus_topics:
            lines.append(f"  focus_topics={', '.join(focus_topics)}")
        pending_paths = list(project_memory_summary.get("pending_paths") or [])
        if pending_paths:
            lines.append(f"  pending_paths={', '.join(pending_paths[:3])}")
        repo_progress = project_memory_summary.get("repo_progress") or {}
        if repo_progress.get("available"):
            lines.append(
                "  repo="
                f"{repo_progress.get('branch', 'unknown')}@{repo_progress.get('head', 'unknown')}"
                f" dirty={int(repo_progress.get('dirty_count', 0) or 0)}"
                f" staged={int(repo_progress.get('staged_count', 0) or 0)}"
                f" modified={int(repo_progress.get('modified_count', 0) or 0)}"
                f" untracked={int(repo_progress.get('untracked_count', 0) or 0)}"
            )
            path_preview = list(repo_progress.get("path_preview") or [])
            if path_preview:
                lines.append(f"  repo_paths={', '.join(path_preview[:3])}")

        subject_anchor = project_memory_summary.get("subject_anchor") or {}
        if subject_anchor:
            lines.append("  subject_anchor:")
            summary = str(subject_anchor.get("summary", "")).strip()
            if summary:
                lines.append(f"    summary={_clip(summary)}")
            for key in (
                "stable_vows",
                "durable_boundaries",
                "decision_preferences",
                "verified_routines",
                "active_threads",
            ):
                values = list(subject_anchor.get(key) or [])
                if values:
                    lines.append(f"    {key}={', '.join(values[:3])}")
        working_style_anchor = project_memory_summary.get("working_style_anchor") or {}
        if working_style_anchor:
            lines.append("  working_style_anchor:")
            summary = str(working_style_anchor.get("summary", "")).strip()
            if summary:
                lines.append(f"    summary={_clip(summary)}")
            for key in ("decision_preferences", "verified_routines", "guardrail_boundaries"):
                values = list(working_style_anchor.get(key) or [])
                if values:
                    lines.append(f"    {key}={', '.join(values[:3])}")
            receiver_posture = str(working_style_anchor.get("receiver_posture", "")).strip()
            if receiver_posture:
                lines.append(f"    receiver_posture={receiver_posture}")
            playbook = build_working_style_playbook(working_style_anchor)
            if playbook.get("present"):
                lines.append("  working_style_playbook:")
                playbook_summary = str(playbook.get("summary_text", "")).strip()
                if playbook_summary:
                    lines.append(f"    summary={_clip(playbook_summary)}")
                for item in list(playbook.get("checklist") or [])[:4]:
                    lines.append(f"    - {_clip(item)}")
                application_rule = str(playbook.get("application_rule", "")).strip()
                if application_rule:
                    lines.append(f"    apply={_clip(application_rule)}")
                non_promotion_rule = str(playbook.get("non_promotion_rule", "")).strip()
                if non_promotion_rule:
                    lines.append(f"    guard={_clip(non_promotion_rule)}")
        working_style_observability = (
            project_memory_summary.get("working_style_observability") or {}
        )
        if working_style_observability:
            lines.append("  working_style_observability:")
            lines.append(
                "    "
                f"status={working_style_observability.get('status', 'unknown')} "
                f"drift={working_style_observability.get('drift_risk', 'unknown')} "
                f"reinforced={int(working_style_observability.get('reinforced_item_count', 0) or 0)}"
                f"/{int(working_style_observability.get('trackable_item_count', 0) or 0)} "
                f"signals={int(working_style_observability.get('signal_count', 0) or 0)}"
            )
            for item in list(working_style_observability.get("unreinforced_items") or [])[:2]:
                lines.append(f"    unreinforced={_clip(item)}")
            receiver_note = str(working_style_observability.get("receiver_note", "")).strip()
            if receiver_note:
                lines.append(f"    note={_clip(receiver_note)}")
        working_style_import_limits = (
            project_memory_summary.get("working_style_import_limits") or {}
        )
        if working_style_import_limits:
            lines.append("  working_style_import_limits:")
            lines.append(
                "    "
                f"apply_posture={working_style_import_limits.get('apply_posture', 'unknown')} "
                f"safe={len(working_style_import_limits.get('safe_apply') or [])} "
                f"blocked={len(working_style_import_limits.get('must_not_import') or [])}"
            )
            for item in list(working_style_import_limits.get("safe_apply") or [])[:2]:
                lines.append(f"    safe_apply={_clip(item)}")
            for item in list(working_style_import_limits.get("must_not_import") or [])[:2]:
                lines.append(f"    must_not_import={_clip(item)}")
            receiver_guidance = str(
                working_style_import_limits.get("receiver_guidance", "")
            ).strip()
            if receiver_guidance:
                lines.append(f"    guidance={_clip(receiver_guidance)}")
        evidence_readout_posture = project_memory_summary.get("evidence_readout_posture") or {}
        if evidence_readout_posture:
            lines.append("  evidence_readout_posture:")
            summary_text = str(evidence_readout_posture.get("summary_text", "")).strip()
            if summary_text:
                lines.append(f"    summary={_clip(summary_text, limit=110)}")
            classification_counts = evidence_readout_posture.get("classification_counts") or {}
            if classification_counts:
                lines.append(
                    "    "
                    f"tested={int(classification_counts.get('tested', 0) or 0)} "
                    f"runtime_present={int(classification_counts.get('runtime_present', 0) or 0)} "
                    f"descriptive_only={int(classification_counts.get('descriptive_only', 0) or 0)} "
                    f"document_backed={int(classification_counts.get('document_backed', 0) or 0)}"
                )
            for lane in list(evidence_readout_posture.get("lanes") or [])[:3]:
                lane_name = str(lane.get("lane", "")).strip()
                classification = str(lane.get("classification", "")).strip()
                if lane_name and classification:
                    lines.append(f"    {lane_name}={classification}")
            receiver_rule = str(evidence_readout_posture.get("receiver_rule", "")).strip()
            if receiver_rule:
                lines.append(f"    receiver_rule={_clip(receiver_rule, limit=120)}")
        launch_claim_posture = project_memory_summary.get("launch_claim_posture") or {}
        if launch_claim_posture:
            lines.append("  launch_claim_posture:")
            summary_text = str(launch_claim_posture.get("summary_text", "")).strip()
            if summary_text:
                lines.append(f"    summary={_clip(summary_text, limit=110)}")
            lines.append(
                "    "
                f"current={launch_claim_posture.get('current_tier', 'unknown')} "
                f"next={launch_claim_posture.get('next_target_tier', 'unknown')} "
                f"public_ready={bool(launch_claim_posture.get('public_launch_ready', False))}"
            )
            for tier in list(launch_claim_posture.get("tier_guidance") or [])[:3]:
                tier_name = str(tier.get("tier", "")).strip()
                posture = str(tier.get("posture", "")).strip()
                if tier_name and posture:
                    lines.append(f"    tier={tier_name}:{posture}")
            for item in list(launch_claim_posture.get("blocked_overclaims") or [])[:3]:
                claim = str(item.get("claim", "")).strip()
                classification = str(item.get("current_classification", "")).strip()
                if claim and classification:
                    lines.append(f"    blocked={claim}:{classification}")
            receiver_rule = str(launch_claim_posture.get("receiver_rule", "")).strip()
            if receiver_rule:
                lines.append(f"    receiver_rule={_clip(receiver_rule, limit=120)}")
        launch_health_trend_posture = (
            project_memory_summary.get("launch_health_trend_posture") or {}
        )
        if launch_health_trend_posture:
            lines.append("  launch_health_trend_posture:")
            summary_text = str(launch_health_trend_posture.get("summary_text", "")).strip()
            if summary_text:
                lines.append(f"    summary={_clip(summary_text, limit=110)}")
            current_state = launch_health_trend_posture.get("current_state") or {}
            if current_state:
                lines.append(
                    "    "
                    f"current={current_state.get('current_tier', 'unknown')} "
                    f"public_ready={bool(current_state.get('public_launch_ready', False))} "
                    f"backend={current_state.get('launch_default_mode', 'unknown')} "
                    f"alignment={current_state.get('launch_alignment', 'unknown')}"
                )
            for item in list(launch_health_trend_posture.get("metric_classes") or [])[:4]:
                metric = str(item.get("metric", "")).strip()
                classification = str(item.get("classification", "")).strip()
                if metric and classification:
                    lines.append(f"    metric={metric}:{classification}")
            for item in list(launch_health_trend_posture.get("trend_watch_cues") or [])[:2]:
                metric = str(item.get("metric", "")).strip()
                watch_for = str(item.get("watch_for", "")).strip()
                if metric and watch_for:
                    lines.append(f"    watch={metric}:{watch_for}")
            for item in list(launch_health_trend_posture.get("forecast_blockers") or [])[:2]:
                metric = str(item.get("metric", "")).strip()
                classification = str(item.get("classification", "")).strip()
                if metric and classification:
                    lines.append(f"    blocker={metric}:{classification}")
            for action in list(launch_health_trend_posture.get("operator_actions") or [])[:2]:
                action_text = str(action).strip()
                if action_text:
                    lines.append(f"    action={_clip(action_text, limit=120)}")
            forecast_boundary = str(
                launch_health_trend_posture.get("forecast_boundary", "")
            ).strip()
            if forecast_boundary:
                lines.append(f"    boundary={_clip(forecast_boundary, limit=120)}")
            receiver_rule = str(launch_health_trend_posture.get("receiver_rule", "")).strip()
            if receiver_rule:
                lines.append(f"    receiver_rule={_clip(receiver_rule, limit=120)}")
        internal_state_observability = (
            project_memory_summary.get("internal_state_observability") or {}
        )
        if internal_state_observability:
            lines.append("  internal_state_observability:")
            summary_text = str(internal_state_observability.get("summary_text", "")).strip()
            if summary_text:
                lines.append(f"    summary={_clip(summary_text, limit=110)}")
            current_state = internal_state_observability.get("current_state") or {}
            if current_state:
                lines.append(
                    "    "
                    f"coordination={current_state.get('coordination_strain', 'unknown')} "
                    f"drift={current_state.get('continuity_drift', 'unknown')} "
                    f"stop={current_state.get('stop_reason_pressure', 'unknown')} "
                    f"deliberation={current_state.get('deliberation_conflict', 'unknown')}"
                )
            for item in list(internal_state_observability.get("evidence_sources") or [])[:4]:
                lines.append(f"    evidence={_clip(str(item))}")
            for item in list(internal_state_observability.get("pressure_watch_cues") or [])[:2]:
                signal = str(item.get("signal", "")).strip()
                current_value = str(item.get("current_value", "")).strip()
                if signal and current_value:
                    lines.append(f"    watch={signal}:{current_value}")
            for action in list(internal_state_observability.get("operator_actions") or [])[:2]:
                action_text = str(action).strip()
                if action_text:
                    lines.append(f"    action={_clip(action_text, limit=120)}")
            selfhood_boundary = str(
                internal_state_observability.get("selfhood_boundary", "")
            ).strip()
            if selfhood_boundary:
                lines.append(f"    boundary={_clip(selfhood_boundary, limit=120)}")
            receiver_rule = str(internal_state_observability.get("receiver_rule", "")).strip()
            if receiver_rule:
                lines.append(f"    receiver_rule={_clip(receiver_rule, limit=120)}")
        routing_summary = project_memory_summary.get("routing_summary") or {}
        if routing_summary:
            lines.append("  routing_summary:")
            lines.append(
                "    "
                f"events={int(routing_summary.get('total_events', 0) or 0)} "
                f"writes={int(routing_summary.get('write_count', 0) or 0)} "
                f"previews={int(routing_summary.get('preview_count', 0) or 0)} "
                f"misroute_signals={int(routing_summary.get('misroute_signal_count', 0) or 0)}"
            )
            dominant_surface = str(routing_summary.get("dominant_surface", "")).strip()
            if dominant_surface:
                lines.append(f"    dominant_surface={dominant_surface}")
        subject_refresh = project_memory_summary.get("subject_refresh") or {}
        if subject_refresh:
            lines.append("  subject_refresh:")
            lines.append(
                "    "
                f"status={subject_refresh.get('status', 'unknown')} "
                f"recommended={bool(subject_refresh.get('refresh_recommended', False))} "
                f"newer_compactions={int(subject_refresh.get('newer_compaction_count', 0) or 0)} "
                f"newer_checkpoints={int(subject_refresh.get('newer_checkpoint_count', 0) or 0)} "
                f"hazards={len(subject_refresh.get('promotion_hazards') or [])}"
            )
            recommended_command = str(subject_refresh.get("recommended_command", "")).strip()
            if recommended_command:
                lines.append(f"    recommended_command={_clip(recommended_command)}")
            field_guidance = list(subject_refresh.get("field_guidance") or [])
            for item in field_guidance[:3]:
                field_name = str(item.get("field", "")).strip()
                action = str(item.get("action", "")).strip()
                evidence_level = str(item.get("evidence_level", "")).strip()
                if field_name and action:
                    lines.append(
                        f"    {field_name}={action}"
                        + (f" ({evidence_level})" if evidence_level else "")
                    )

    subject_snapshots = packet.get("recent_subject_snapshots", [])
    if subject_snapshots:
        lines.append("")
        lines.append(f"[Subject Snapshot] count={len(subject_snapshots)}")
        latest = subject_snapshots[0]
        lines.append(
            "  "
            f"{latest.get('updated_at', '')[:16]} | "
            f"{latest.get('agent', '?')} | "
            f"summary={_clip(latest.get('summary', ''))}"
        )
        for key in (
            "durable_boundaries",
            "decision_preferences",
            "verified_routines",
            "active_threads",
        ):
            values = list(latest.get(key) or [])
            if values:
                lines.append(f"  {key}={', '.join(values[:3])}")

    routing_events = packet.get("recent_routing_events", [])
    if routing_events:
        lines.append("")
        lines.append(f"[Routing Telemetry] count={len(routing_events)}")
        for event in routing_events[:3]:
            lines.append(
                "  "
                f"{event.get('updated_at', '')[:16]} | "
                f"{event.get('agent', '?')} | "
                f"{event.get('action', '?')} -> {event.get('surface', '?')} | "
                f"forced={bool(event.get('forced', False))} "
                f"overlap={bool(event.get('overlap', False))}"
            )

    coordination_mode = packet.get("coordination_mode") or {}
    if coordination_mode:
        lines.append("")
        lines.append("[Coordination Mode]")
        lines.append(
            "  "
            f"mode={coordination_mode.get('mode', 'unknown')} "
            f"live={bool(coordination_mode.get('live_surfaces_available', False))} "
            f"delta={bool(coordination_mode.get('delta_feed_enabled', False))}"
        )
        summary_text = str(coordination_mode.get("summary_text", "")).strip()
        if summary_text:
            lines.append(f"  summary={_clip(summary_text)}")
        refresh_hint = str(coordination_mode.get("refresh_hint", "")).strip()
        if refresh_hint:
            lines.append(f"  refresh_hint={_clip(refresh_hint)}")
        launch_default = str(coordination_mode.get("launch_default_mode", "")).strip()
        launch_alignment = str(coordination_mode.get("launch_alignment", "")).strip()
        if launch_default:
            lines.append(
                "  "
                f"launch_default={launch_default} "
                f"alignment={launch_alignment or 'unknown'}"
            )
        launch_posture_note = str(coordination_mode.get("launch_posture_note", "")).strip()
        if launch_posture_note:
            lines.append(f"  launch_note={_clip(launch_posture_note)}")
        recheck_command = str(coordination_mode.get("recheck_command", "")).strip()
        if recheck_command:
            lines.append(f"  recheck_command={recheck_command}")
        ack_command = str(coordination_mode.get("ack_command", "")).strip()
        if ack_command:
            lines.append(f"  ack_command={ack_command}")
        surface_modes = coordination_mode.get("surface_modes") or {}
        if surface_modes:
            lines.append(
                "  surfaces="
                f"claims:{surface_modes.get('claims', '?')} "
                f"checkpoints:{surface_modes.get('checkpoints', '?')} "
                f"subjects:{surface_modes.get('subject_snapshots', '?')} "
                f"visitors:{surface_modes.get('visitors', '?')}"
            )

    delta_feed = packet.get("delta_feed") or {}
    if delta_feed:
        lines.append("")
        lines.append("[Since Last Seen]")
        lines.append(
            "  "
            f"observer={delta_feed.get('observer_id', '?')} "
            f"updates={int(delta_feed.get('update_count', 0) or 0)} "
            f"has_updates={bool(delta_feed.get('has_updates', False))}"
        )
        previous_seen_at = str(delta_feed.get("previous_seen_at", "")).strip()
        if previous_seen_at:
            lines.append(f"  previous_seen_at={previous_seen_at}")
        summary_text = str(delta_feed.get("summary_text", "")).strip()
        if summary_text:
            lines.append(f"  summary={_clip(summary_text)}")
        if delta_feed.get("first_observation"):
            lines.append("  first_observation=true")
        for key in (
            "new_compactions",
            "new_subject_snapshots",
            "new_checkpoints",
            "new_traces",
            "new_claims",
        ):
            values = list(delta_feed.get(key) or [])
            if values:
                lines.append(f"  {key}={len(values)}")
        released_claim_ids = list(delta_feed.get("released_claim_ids") or [])
        if released_claim_ids:
            lines.append(f"  released_claim_ids={', '.join(released_claim_ids[:3])}")
        repo_change = delta_feed.get("repo_change") or {}
        if repo_change.get("changed"):
            lines.append(
                "  repo_change="
                f"{repo_change.get('previous_head', 'unknown')} -> "
                f"{repo_change.get('current_head', 'unknown')} "
                f"dirty={int(repo_change.get('previous_dirty_count', 0) or 0)}"
                f"->{int(repo_change.get('current_dirty_count', 0) or 0)}"
            )
        ack_command = str(delta_feed.get("ack_command", "")).strip()
        if ack_command:
            lines.append(f"  ack_command={ack_command}")

    operator_guidance = packet.get("operator_guidance") or {}
    if operator_guidance:
        lines.append("")
        lines.append("[Operator Guidance]")
        session_start = list(operator_guidance.get("session_start") or [])
        if session_start:
            lines.append("  session_start:")
            for command in session_start[:3]:
                lines.append(f"    {command}")
        session_end = list(operator_guidance.get("session_end") or [])
        if session_end:
            lines.append("  session_end:")
            for command in session_end[:3]:
                lines.append(f"    {command}")
        commands = operator_guidance.get("coordination_commands") or {}
        if commands:
            lines.append("  coordination_commands:")
            for key in (
                "claim",
                "perspective",
                "checkpoint",
                "compaction",
                "signal_router",
                "subject_snapshot",
                "apply_subject_refresh",
                "release",
            ):
                command = str(commands.get(key, "")).strip()
                if command:
                    lines.append(f"    {key}={command}")
        preflight_chain = operator_guidance.get("preflight_chain") or {}
        if preflight_chain.get("present"):
            lines.append("  preflight_chain:")
            summary_text = str(preflight_chain.get("summary_text", "")).strip()
            if summary_text:
                lines.append(f"    summary={summary_text}")
            for stage in list(preflight_chain.get("stages") or [])[:3]:
                lines.append(
                    "    "
                    f"{stage.get('name', 'unknown')}="
                    f"{str(stage.get('command', '')).strip()}"
                )
        completion_rule = str(operator_guidance.get("completion_rule", "")).strip()
        if completion_rule:
            lines.append(f"  completion_rule={_clip(completion_rule)}")
        reminders = list(operator_guidance.get("current_reminders") or [])
        if reminders:
            lines.append("  current_reminders:")
            for reminder in reminders[:4]:
                lines.append(f"    - {_clip(reminder)}")

    council_dossier = _latest_council_dossier_summary(packet)
    if council_dossier:
        realism_lines: list[str] = []
        confidence_posture = str(council_dossier.get("confidence_posture", "")).strip()
        if confidence_posture:
            realism_lines.append(f"  confidence_posture={confidence_posture}")
        decomposition = council_dossier.get("confidence_decomposition") or {}
        calibration_status = str(decomposition.get("calibration_status", "")).strip()
        if calibration_status:
            realism_lines.append(f"  calibration_status={calibration_status}")
        coverage_posture = str(decomposition.get("coverage_posture", "")).strip()
        if coverage_posture:
            realism_lines.append(f"  coverage_posture={coverage_posture}")
        adversarial_posture = str(decomposition.get("adversarial_posture", "")).strip()
        if adversarial_posture:
            realism_lines.append(f"  adversarial_posture={adversarial_posture}")
        if "has_minority_report" in council_dossier:
            realism_lines.append(
                f"  has_minority_report={bool(council_dossier.get('has_minority_report'))}"
            )
        if "evolution_suppression_flag" in council_dossier:
            realism_lines.append(
                "  evolution_suppression_flag="
                f"{bool(council_dossier.get('evolution_suppression_flag'))}"
            )
        realism_note = str(council_dossier.get("realism_note", "")).strip()
        if realism_note:
            realism_lines.append(f"  note={_clip(realism_note, limit=110)}")
        if realism_lines:
            lines.append("")
            lines.append("[Council Realism]")
            lines.extend(realism_lines)
    receiver_parity = build_receiver_parity_readout(
        council_snapshot=council_dossier,
        project_memory_summary=project_memory_summary,
    )
    if receiver_parity.get("present"):
        lines.append("")
        lines.append("[Receiver Posture]")
        summary_text = str(receiver_parity.get("summary_text", "")).strip()
        if summary_text:
            lines.append(f"  summary={_clip(summary_text, limit=110)}")
        receiver_rule = str(receiver_parity.get("rule", "")).strip()
        if receiver_rule:
            lines.append(f"  rule={_clip(receiver_rule, limit=120)}")
        for alert in list(receiver_parity.get("alerts") or [])[:5]:
            lines.append(f"  - {_clip(str(alert), limit=120)}")

    lanes = packet.get("parallel_lanes", {})
    if lanes:
        lines.extend(
            [
                "  Surfaces:",
                "    packet=GET /packet or python scripts/run_r_memory_packet.py",
                "    claims=POST /claim,/release or python scripts/run_task_claim.py",
                f"    perspectives={lanes.get('perspectives_surface', 'ts:perspectives:{agent_id}')}",
                f"    checkpoints={lanes.get('checkpoints_surface', 'ts:checkpoints:*')}",
                "    compaction=POST /compact or python scripts/save_compaction.py",
                f"    subject_snapshots={lanes.get('subject_snapshot_surface', 'ts:subject_snapshots')}",
                f"    canonical_commit_serialized={lanes.get('canonical_commit_serialized', True)}",
            ]
        )

    lines.append("")
    lines.extend(
        [
            "[Visibility Model]",
            "  Visible after explicit write: claims, perspectives, checkpoints, compactions, subject snapshots, accepted traces.",
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
    parser.add_argument(
        "--compact", action="store_true", help="One-line output, minimal context cost"
    )
    args = parser.parse_args()

    os.environ.setdefault("TONESOUL_REDIS_URL", "redis://localhost:6379/0")

    if args.compact:
        _emit_text(compact_diagnostic(agent_id=args.agent))
    else:
        _emit_text(full_diagnostic(agent_id=args.agent))


if __name__ == "__main__":
    main()
