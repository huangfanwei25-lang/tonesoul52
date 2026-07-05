"""κ Phase 1 signal collection — shadow-only, per-deliberation (2026-07-05).

Provenance: docs/plans/kappa_vow_collapse_experiment_2026-07-05.md. The κ
predictor (LINEAGE parked asset #1) died in G4 because there was no real
signal to calibrate against. Phase 1 does NOT predict anything: it lands the
discrete signals the TSR adjudication kept (堆三) into every council trace,
so that Phase 2 modeling (owner-gated, behind the >=20 committed-events
threshold) has a time series to stand on.

Signals per deliberation:
- ``tsr_delta_norm`` — already computed by ``intent_reconstructor``; carried
  into this record so one schema holds the whole κ fuel row.
- posture-evidence mismatch — the discretized 「語氣錯位」: the draft's tone
  posture (strong modals vs caution markers, from ``tsr_metrics``) checked
  against the EpistemicLabel evidence grade. ``assertive`` posture on
  ``weak`` evidence = one mismatch event.

Honest limits (v0): the tsr_metrics lexicon is English-only (its tokenizer
drops CJK), so pure-Chinese drafts classify as ``neutral`` posture and
mismatches there are UNDER-detected. Treat counts as a floor, not the true
rate. No label -> ``unlabeled`` evidence, never counted as mismatch
(claim <= evidence: absence of a label is not evidence of weakness).

A RECORDED signal, never a gate (DESIGN Inv3): nothing here reads the
verdict decision to change it. The transcript attachment is side-effect-free
and always on (same posture as epistemic_label); the JSONL ledger append is
a file side effect and therefore flag-gated default OFF
(``SOUL.council.kappa_signal_ledger_enabled``, #219 shadow-seam discipline).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import tonesoul.tsr_metrics as tsr_metrics
from tonesoul.soul_config import SOUL

__ts_layer__ = "governance"
__ts_purpose__ = (
    "Kappa Phase 1 shadow signals: posture-evidence mismatch + tsr_delta_norm per deliberation."
)

SCHEMA_VERSION = "kappa_signal_v0"

DEFAULT_LEDGER_PATH = os.path.join("memory", "kappa_signal_ledger.jsonl")
_LEDGER_PATH_ENV = "TONESOUL_KAPPA_LEDGER_PATH"

_WEAK_STATUS = {"generated", "speculative_metaphysical"}
_WEAK_SOURCE_WEIGHT = {"inferred", "none"}
_WEAK_CONFIDENCE_BAND = {"low", "unknown"}


@dataclass
class KappaSignal:
    posture: str  # assertive | hedged | neutral
    evidence_grade: str  # strong | medium | weak | unlabeled
    posture_evidence_mismatch: bool
    mismatch_reasons: List[str] = field(default_factory=list)
    tsr_delta_norm: Optional[float] = None
    schema_version: str = SCHEMA_VERSION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "posture": self.posture,
            "evidence_grade": self.evidence_grade,
            "posture_evidence_mismatch": self.posture_evidence_mismatch,
            "mismatch_reasons": list(self.mismatch_reasons),
            "tsr_delta_norm": self.tsr_delta_norm,
        }


class KappaSignalSensor:
    """Deterministic — no LLM, no network, no I/O (same contract as EpistemicLabeler)."""

    def assess(
        self,
        draft_output: str,
        epistemic_label: Optional[object] = None,
        tsr_delta_norm: Optional[float] = None,
    ) -> KappaSignal:
        posture = self._classify_posture(draft_output or "")
        evidence_grade, weak_dims = self._grade_evidence(epistemic_label)
        mismatch = posture == "assertive" and evidence_grade == "weak"
        return KappaSignal(
            posture=posture,
            evidence_grade=evidence_grade,
            posture_evidence_mismatch=mismatch,
            mismatch_reasons=list(weak_dims) if mismatch else [],
            tsr_delta_norm=tsr_delta_norm,
        )

    @staticmethod
    def _classify_posture(text: str) -> str:
        metrics = tsr_metrics.score(text)
        signals = metrics.get("signals") if isinstance(metrics, dict) else None
        if not isinstance(signals, dict):
            return "neutral"
        caution = int(signals.get("caution_hits", 0) or 0)
        strong = int(signals.get("strong_modal_hits", 0) or 0)
        # Any hedging marker wins over strong modals: the dangerous shape is
        # certainty WITHOUT hedges, so a hedged-but-firm draft is not flagged.
        if caution > 0:
            return "hedged"
        if strong > 0:
            return "assertive"
        return "neutral"

    @staticmethod
    def _grade_evidence(label: Optional[object]) -> Tuple[str, List[str]]:
        if label is None:
            return "unlabeled", []
        if isinstance(label, dict):
            status = label.get("status")
            source_weight = label.get("source_weight")
            confidence_band = label.get("confidence_band")
        else:
            status = getattr(label, "status", None)
            source_weight = getattr(label, "source_weight", None)
            confidence_band = getattr(label, "confidence_band", None)

        weak_dims: List[str] = []
        if status in _WEAK_STATUS:
            weak_dims.append(f"status={status}")
        if source_weight in _WEAK_SOURCE_WEIGHT:
            weak_dims.append(f"source_weight={source_weight}")
        if confidence_band in _WEAK_CONFIDENCE_BAND:
            weak_dims.append(f"confidence_band={confidence_band}")
        if weak_dims:
            return "weak", weak_dims
        if status == "retrieved" and confidence_band == "high":
            return "strong", []
        return "medium", []


def build_ledger_record(
    signal: KappaSignal,
    *,
    verdict_type: Optional[str] = None,
    intent_id: Optional[str] = None,
) -> Dict[str, Any]:
    record = signal.to_dict()
    record["recorded_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record["verdict"] = verdict_type
    record["intent_id"] = intent_id
    return record


def append_kappa_ledger(record: Dict[str, Any], path: Optional[str] = None) -> str:
    resolved = path or os.environ.get(_LEDGER_PATH_ENV) or DEFAULT_LEDGER_PATH
    directory = os.path.dirname(resolved)
    if directory:
        os.makedirs(directory, exist_ok=True)
    # UTF-8, LF, no BOM on every platform (encoding discipline).
    with open(resolved, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return resolved


def attach_kappa_signals(verdict: object, draft_output: str) -> KappaSignal:
    """Attach the shadow signal to ``verdict.transcript``; ledger only when flagged.

    Called by ``CouncilRuntime.deliberate()`` AFTER the genesis step so that
    ``verdict.tsr_delta_norm`` and ``verdict.epistemic_label`` are populated.
    Never touches ``verdict.verdict``.
    """
    signal = KappaSignalSensor().assess(
        draft_output=draft_output,
        epistemic_label=getattr(verdict, "epistemic_label", None),
        tsr_delta_norm=getattr(verdict, "tsr_delta_norm", None),
    )
    transcript = verdict.transcript if isinstance(verdict.transcript, dict) else {}
    transcript["kappa_signals"] = signal.to_dict()
    verdict.transcript = transcript

    if SOUL.council.kappa_signal_ledger_enabled:
        raw_verdict = getattr(verdict, "verdict", None)
        verdict_type = getattr(raw_verdict, "value", None) or (
            str(raw_verdict) if raw_verdict is not None else None
        )
        append_kappa_ledger(
            build_ledger_record(
                signal,
                verdict_type=verdict_type,
                intent_id=getattr(verdict, "intent_id", None),
            )
        )
    return signal
