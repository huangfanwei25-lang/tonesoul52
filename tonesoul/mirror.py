from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from tonesoul.schemas import (
    DualTrackResponse,
    GovernanceDecision,
    MirrorDelta,
    SubjectivityLayer,
    TensionSnapshot,
)


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: object, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _get_field(obj: object, key: str, default: object = None) -> object:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class ToneSoulMirror:
    """
    Runtime companion that compares raw output against a deterministic
    governance projection without introducing new LLM calls.
    """

    def __init__(self, tension_engine: object = None, governance_kernel: object = None) -> None:
        self.tension_engine = tension_engine
        self.governance_kernel = governance_kernel

    def reflect(
        self, raw_output: str, context: Optional[Dict[str, Any]] = None
    ) -> DualTrackResponse:
        raw = str(raw_output or "")
        ctx = dict(context or {})

        if self.tension_engine is None or self.governance_kernel is None:
            empty = self._empty_snapshot()
            return DualTrackResponse(
                raw_response=raw,
                governed_response=raw,
                mirror_delta=MirrorDelta(
                    tension_before=empty,
                    tension_after=empty,
                    governance_decision=None,
                    subjectivity_flags=[],
                    delta_summary="Mirror unavailable; passed through raw response.",
                    mirror_triggered=False,
                ),
                final_choice="raw",
                reflection_note="Mirror unavailable.",
            )

        before_result = self._compute_tension(raw, ctx, override_tension=None)
        decision = self._build_governance_decision(before_result, raw, ctx)
        governed = self._apply_governance(raw, decision)
        after_result = self._compute_tension(
            governed,
            ctx,
            override_tension=self._project_after_tension(before_result, decision),
        )
        delta = self._compute_delta(before_result, after_result, decision)
        return DualTrackResponse(
            raw_response=raw,
            governed_response=governed,
            mirror_delta=delta,
            final_choice="governed" if delta.mirror_triggered else "raw",
            reflection_note=delta.delta_summary,
        )

    def record_delta(
        self,
        dual: DualTrackResponse,
        write_gateway: object,
        *,
        source: object = None,
    ) -> Optional[str]:
        """Persist triggered mirror deltas through the canonical memory write gateway."""
        if not isinstance(dual, DualTrackResponse):
            raise TypeError("record_delta expects a DualTrackResponse")
        if not hasattr(write_gateway, "write_payload"):
            raise TypeError("record_delta expects a write gateway with write_payload")
        if not dual.mirror_delta.mirror_triggered:
            return None

        from tonesoul.memory.soul_db import MemorySource

        resolved_source = source or MemorySource.CUSTOM
        payload = self._build_memory_payload(dual)
        return write_gateway.write_payload(resolved_source, payload)

    def _compute_tension(
        self,
        text: str,
        context: Dict[str, Any],
        *,
        override_tension: Optional[float],
    ) -> Any:
        resolved_tension = (
            self._resolve_text_tension(text, context)
            if override_tension is None
            else max(0.0, min(1.0, float(override_tension)))
        )
        confidence = self._resolve_confidence(context)
        try:
            return self.tension_engine.compute(text_tension=resolved_tension, confidence=confidence)
        except TypeError:
            return self.tension_engine.compute(text_tension=resolved_tension)

    def _build_governance_decision(
        self,
        tension_result: Any,
        raw_output: str,
        context: Dict[str, Any],
    ) -> GovernanceDecision:
        total = self._extract_total(tension_result)
        friction_score = self._extract_cognitive_friction(tension_result)
        should_convene = False
        council_reason = ""
        if hasattr(self.governance_kernel, "should_convene_council"):
            try:
                should_convene, council_reason = self.governance_kernel.should_convene_council(
                    tension=total,
                    friction_score=friction_score,
                    user_tier=str(context.get("user_tier") or "free"),
                    message_length=len(raw_output),
                )
            except Exception:
                should_convene = False
                council_reason = ""

        provenance = {
            "source": "tonesoul_mirror",
            "text_tension": round(self._resolve_text_tension(raw_output, context), 4),
            "confidence": round(self._resolve_confidence(context), 4),
        }

        return GovernanceDecision.model_validate(
            {
                "should_convene_council": should_convene,
                "council_reason": council_reason,
                "friction_score": friction_score,
                "circuit_breaker_status": "ok",
                "provenance": provenance,
            }
        )

    def _apply_governance(self, raw: str, decision: Optional[GovernanceDecision]) -> str:
        if decision is None:
            return raw
        if decision.circuit_breaker_status == "frozen":
            reason = decision.circuit_breaker_reason or "circuit breaker triggered"
            return f"[Governance projection] Pause delivery pending review: {reason}."
        if decision.should_convene_council:
            reason = decision.council_reason or "council review recommended"
            return f"{raw}\n\n[Governance projection: {reason}]"
        return raw

    def _compute_delta(
        self,
        before: Any,
        after: Any,
        decision: Optional[GovernanceDecision],
    ) -> MirrorDelta:
        before_snapshot = self._snapshot_from_tension(before)
        after_snapshot = self._snapshot_from_tension(after)

        friction_delta = round(
            before_snapshot.cognitive_friction - after_snapshot.cognitive_friction,
            4,
        )
        mirror_triggered = bool(
            decision
            and (
                decision.should_convene_council
                or decision.circuit_breaker_status != "ok"
                or friction_delta > 0.05
            )
        )

        if mirror_triggered:
            summary = (
                "Mirror detected governance-relevant tension shift "
                f"({before_snapshot.cognitive_friction:.2f} -> "
                f"{after_snapshot.cognitive_friction:.2f})."
            )
        else:
            summary = "Mirror pass-through; governance delta below trigger threshold."

        return MirrorDelta(
            tension_before=before_snapshot,
            tension_after=after_snapshot,
            governance_decision=decision,
            subjectivity_flags=[SubjectivityLayer.TENSION] if mirror_triggered else [],
            delta_summary=summary,
            mirror_triggered=mirror_triggered,
        )

    def _project_after_tension(
        self,
        before_result: Any,
        decision: Optional[GovernanceDecision],
    ) -> float:
        baseline = self._extract_total(before_result)
        if decision is None:
            return baseline
        if decision.circuit_breaker_status == "frozen":
            return 0.0
        if decision.should_convene_council:
            return max(0.0, baseline - 0.35)
        return baseline

    def _build_memory_payload(self, dual: DualTrackResponse) -> Dict[str, Any]:
        from tonesoul.memory.soul_db import MemoryLayer

        delta = dual.mirror_delta
        decision = delta.governance_decision
        timestamp = (
            str(delta.tension_after.timestamp or "").strip()
            or str(delta.tension_before.timestamp or "").strip()
            or _utcnow_iso()
        )
        evidence = self._build_evidence(
            delta.delta_summary,
            dual.raw_response,
            dual.governed_response,
        )
        provenance = {
            "kind": "mirror_delta",
            "source": "tonesoul_mirror",
            "timestamp": timestamp,
            "final_choice": dual.final_choice,
            "mirror_triggered": True,
            "subjectivity_flags": list(delta.subjectivity_flags),
        }
        if decision is not None:
            provenance.update(
                {
                    "council_reason": decision.council_reason,
                    "circuit_breaker_status": decision.circuit_breaker_status,
                    "friction_score": decision.friction_score,
                }
            )
        provenance = {
            key: value for key, value in provenance.items() if value not in (None, "", [], {})
        }

        return {
            "type": "mirror_delta",
            "timestamp": timestamp,
            "layer": MemoryLayer.WORKING.value,
            "title": "ToneSoul mirror delta",
            "summary": delta.delta_summary,
            "raw_response": dual.raw_response,
            "governed_response": dual.governed_response,
            "final_choice": dual.final_choice,
            "reflection_note": dual.reflection_note,
            "mirror_delta": delta.model_dump(mode="json"),
            "subjectivity_layer": SubjectivityLayer.TENSION.value,
            "promotion_gate": {
                "status": "candidate",
                "source": "tonesoul_mirror",
                "review_basis": delta.delta_summary,
            },
            "decay_policy": {"policy": "adaptive"},
            "tags": ["mirror", "runtime", "dual_track"],
            "evidence": evidence,
            "provenance": provenance,
        }

    def _resolve_text_tension(self, text: str, context: Dict[str, Any]) -> float:
        for key in ("text_tension", "tension_score", "tone_strength"):
            value = context.get(key)
            if isinstance(value, (int, float)):
                return max(0.0, min(1.0, float(value)))
        exclamation_boost = min(text.count("!"), 3) * 0.1
        uppercase_boost = 0.15 if text.isupper() and text.strip() else 0.0
        return max(0.0, min(1.0, exclamation_boost + uppercase_boost))

    @staticmethod
    def _resolve_confidence(context: Dict[str, Any]) -> float:
        value = context.get("confidence", 0.8)
        return max(0.0, min(1.0, _safe_float(value, 0.8)))

    @staticmethod
    def _build_evidence(*items: object) -> list[str]:
        evidence: list[str] = []
        seen: set[str] = set()
        for item in items:
            text = str(item or "").strip()
            if not text:
                continue
            normalized = text.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            evidence.append(text[:500])
        return evidence

    @staticmethod
    def _extract_total(result: Any) -> float:
        return max(0.0, min(1.0, _safe_float(_get_field(result, "total", 0.0), 0.0)))

    @staticmethod
    def _extract_cognitive_friction(result: Any) -> float:
        signals = _get_field(result, "signals", {})
        return max(
            0.0,
            min(1.0, _safe_float(_get_field(signals, "cognitive_friction", 0.0), 0.0)),
        )

    @staticmethod
    def _snapshot_from_tension(result: Any) -> TensionSnapshot:
        if result is None:
            return ToneSoulMirror._empty_snapshot()

        signals = _get_field(result, "signals", {})
        if hasattr(signals, "to_dict"):
            signals_payload = signals.to_dict()
        elif isinstance(signals, dict):
            signals_payload = dict(signals)
        else:
            signals_payload = {}

        prediction = _get_field(result, "prediction")
        zone = _get_field(result, "zone")
        phase_state = _get_field(zone, "value")
        if not isinstance(phase_state, str) or not phase_state.strip():
            phase_state = str(_get_field(result, "phase_state", "stable") or "stable")

        return TensionSnapshot.model_validate(
            {
                "cognitive_friction": ToneSoulMirror._extract_cognitive_friction(result),
                "lyapunov_exponent": _safe_float(
                    _get_field(prediction, "lyapunov_exponent", 0.0),
                    0.0,
                ),
                "phase_state": phase_state,
                "timestamp": str(_get_field(result, "timestamp", _utcnow_iso()) or _utcnow_iso()),
                "signals": signals_payload,
            }
        )

    @staticmethod
    def _empty_snapshot() -> TensionSnapshot:
        return TensionSnapshot(
            cognitive_friction=0.0,
            lyapunov_exponent=0.0,
            phase_state="stable",
            timestamp=_utcnow_iso(),
            signals={},
        )


__all__ = ["ToneSoulMirror"]
