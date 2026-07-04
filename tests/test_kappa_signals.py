"""κ Phase 1 signal collection tests — shadow-only discipline.

Covers: posture classification, evidence grading, the mismatch rule
(assertive posture on weak evidence, and ONLY that), ledger encoding
discipline (UTF-8 / LF / no BOM), runtime wiring (transcript always carries
kappa_signals; ledger writes only when the SOUL flag is on), and the
never-a-gate invariant (the signal does not change the verdict).
"""

import json
from types import SimpleNamespace

import tonesoul.council.kappa_signals as kappa_signals
from tonesoul.council.epistemic_labeler import EpistemicLabel
from tonesoul.council.kappa_signals import (
    SCHEMA_VERSION,
    KappaSignalSensor,
    append_kappa_ledger,
    attach_kappa_signals,
    build_ledger_record,
)
from tonesoul.council.runtime import CouncilRequest, CouncilRuntime

# Lexicon-guaranteed drafts (tsr_metrics DEFAULT_LEXICON): "must/shall/enforce/
# required" are strong modals; "may/risk/uncertain" are caution markers.
ASSERTIVE_DRAFT = "You must proceed. We shall enforce the required path."
HEDGED_DRAFT = "This may fail; the risk is uncertain and needs review."
NEUTRAL_DRAFT = "The sky over the harbor is blue today."


def _label(status="generated", source_weight="none", confidence_band="unknown"):
    return EpistemicLabel(
        status=status,
        source_weight=source_weight,
        confidence_band=confidence_band,
        refusal_eligible=False,
        framing_required=False,
        framing_present=None,
    )


def _strong_label():
    return _label(status="retrieved", source_weight="primary", confidence_band="high")


def test_posture_classification():
    sensor = KappaSignalSensor()
    assert sensor.assess(ASSERTIVE_DRAFT).posture == "assertive"
    assert sensor.assess(HEDGED_DRAFT).posture == "hedged"
    assert sensor.assess(NEUTRAL_DRAFT).posture == "neutral"


def test_hedging_wins_over_strong_modals():
    # A draft with both "must" and "may": hedged, because the dangerous shape
    # is certainty WITHOUT hedges.
    signal = KappaSignalSensor().assess("You must act, though it may fail.")
    assert signal.posture == "hedged"
    assert signal.posture_evidence_mismatch is False


def test_mismatch_fires_only_on_assertive_plus_weak():
    sensor = KappaSignalSensor()

    hit = sensor.assess(ASSERTIVE_DRAFT, epistemic_label=_label())
    assert hit.evidence_grade == "weak"
    assert hit.posture_evidence_mismatch is True
    assert "status=generated" in hit.mismatch_reasons

    assert sensor.assess(HEDGED_DRAFT, epistemic_label=_label()).posture_evidence_mismatch is False
    strong = sensor.assess(ASSERTIVE_DRAFT, epistemic_label=_strong_label())
    assert strong.evidence_grade == "strong"
    assert strong.posture_evidence_mismatch is False


def test_no_label_is_not_counted_as_mismatch():
    # claim <= evidence: absence of a label is not evidence of weakness.
    signal = KappaSignalSensor().assess(ASSERTIVE_DRAFT, epistemic_label=None)
    assert signal.evidence_grade == "unlabeled"
    assert signal.posture_evidence_mismatch is False
    assert signal.mismatch_reasons == []


def test_grade_evidence_accepts_serialized_dict():
    signal = KappaSignalSensor().assess(
        ASSERTIVE_DRAFT,
        epistemic_label=_label().to_dict(),
    )
    assert signal.evidence_grade == "weak"
    assert signal.posture_evidence_mismatch is True


def test_ledger_append_encoding_discipline(tmp_path):
    path = tmp_path / "kappa_ledger.jsonl"
    signal = KappaSignalSensor().assess(ASSERTIVE_DRAFT, epistemic_label=_label())
    record = build_ledger_record(signal, verdict_type="BLOCK", intent_id="intent-1")
    resolved = append_kappa_ledger(record, path=str(path))
    assert resolved == str(path)

    raw = path.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")  # no BOM
    assert b"\r\n" not in raw  # LF only
    parsed = json.loads(raw.decode("utf-8").splitlines()[0])
    assert parsed["schema_version"] == SCHEMA_VERSION
    assert parsed["verdict"] == "BLOCK"
    assert parsed["intent_id"] == "intent-1"
    assert parsed["posture_evidence_mismatch"] is True
    assert parsed["recorded_at"].endswith("Z")


def _deliberate(draft=NEUTRAL_DRAFT):
    runtime = CouncilRuntime()
    request = CouncilRequest(
        draft_output=draft,
        context={"tsr_baseline": {"T": 0.0, "S_norm": 0.0, "R": 0.0}},
        user_intent="ask",
    )
    return runtime.deliberate(request)


def test_runtime_transcript_always_carries_kappa_signals(tmp_path, monkeypatch):
    ledger_path = tmp_path / "kappa_ledger.jsonl"
    monkeypatch.setenv("TONESOUL_KAPPA_LEDGER_PATH", str(ledger_path))

    verdict = _deliberate()

    payload = (verdict.transcript or {}).get("kappa_signals")
    assert isinstance(payload, dict)
    assert payload["schema_version"] == SCHEMA_VERSION
    assert payload["posture"] in {"assertive", "hedged", "neutral"}
    # One record carries the whole κ fuel row: delta mirrors the verdict field.
    assert payload["tsr_delta_norm"] == verdict.tsr_delta_norm
    # Ledger flag defaults OFF: transcript observability must not write files.
    assert not ledger_path.exists()


def test_ledger_writes_only_when_flag_enabled(tmp_path, monkeypatch):
    ledger_path = tmp_path / "kappa_ledger.jsonl"
    monkeypatch.setenv("TONESOUL_KAPPA_LEDGER_PATH", str(ledger_path))

    verdict = _deliberate(draft=ASSERTIVE_DRAFT)
    assert not ledger_path.exists()

    # SOUL config is frozen; swap the module reference (the seam the runtime
    # reads) rather than mutating shared global config.
    monkeypatch.setattr(
        kappa_signals,
        "SOUL",
        SimpleNamespace(council=SimpleNamespace(kappa_signal_ledger_enabled=True)),
    )
    attach_kappa_signals(verdict, draft_output=ASSERTIVE_DRAFT)

    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["intent_id"] == verdict.intent_id
    assert parsed["verdict"] == verdict.verdict.value


def test_signal_never_changes_the_verdict():
    # Never-a-gate invariant: attaching the signal must not move the decision.
    verdict = _deliberate(draft=ASSERTIVE_DRAFT)
    before = verdict.verdict
    attach_kappa_signals(verdict, draft_output=ASSERTIVE_DRAFT)
    assert verdict.verdict == before
