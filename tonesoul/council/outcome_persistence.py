"""Outcome persistence — Council Calibration v0b Bucket A (minimum viable).

Author: Claude Opus 4.7 (drafting + implementing)
Spec: docs/plans/council_calibration_v0b_2026-04-19.md §3 (schema), §4 (collection
      pipeline), §7 Bucket A
Date: 2026-04-19

WHAT THIS MODULE DOES — AND DOES NOT
------------------------------------
This is the **smallest shippable slice** of v0b Bucket A: schema + file append.
It accepts an outcome signal (accept / reject / correction / harm), derives the
alignment_judgment + judgment_basis fields, and writes a JSONL record to
``.aegis/council_outcomes.jsonl``.

What this module **does not** do, by design:

- ❌ Read or compute calibration metrics (that's Bucket B —
  ``tonesoul/council/calibration.py`` extension)
- ❌ Apply outcome signals back into perspective voting weights (this is
  v0b spec §2 anti-pattern #1, explicitly forbidden)
- ❌ Implement the §4.2 follow-up message inference heuristic (separate
  commit; the regex+language logic deserves its own review)
- ❌ Implement the §4.3 session-close timeout (needs background process)
- ❌ Verdict-type-aware alignment derivation (Bucket B will override
  ``derive_alignment_judgment`` when verdict records are joined in;
  per v0b spec §2 anti-pattern #3, BLOCK verdicts need explicit
  positive confirmation, not absence of complaint — but Bucket A only
  sees the outcome signal, not the original verdict, so it can't apply
  that rule yet)
- ❌ Redis backend extension (file fallback is enough for the 2-week
  feature-flag validation window per spec §9)

WHY THE FEATURE FLAG
--------------------
The Gateway's ``POST /outcome`` endpoint is OFF by default
(``--enable-outcome-collection`` to opt in). Reason from spec §9:

> Let it run for two weeks producing data without any consumer reading
> it. This validates the collection pipeline end-to-end without the
> pressure of "what does the alignment number say?"

If the flag was on by default, the first time someone sees the alignment
metric, the conversation immediately becomes "is this number good?" before
we've verified the *collection* itself works. Off-by-default forces us to
operate the pipeline before judging it.

ALIGNMENT_JUDGMENT DERIVATION (BUCKET A SIMPLE VERSION)
-------------------------------------------------------
Bucket A applies a flat mapping from signal type → judgment:

    accept     → aligned     (basis: user_accept)
    reject     → misaligned  (basis: user_reject)
    correction → misaligned  (basis: user_correction)
    harm       → misaligned  (basis: detected_harm)

This is **deliberately too simple**. It treats every accept as evidence
of alignment, which v0b spec §2 anti-pattern #3 explicitly warns
against (a BLOCK verdict that frustrated users "accept" because they
have no recourse is not aligned). Bucket B is required to fix this by
joining outcome records against the original verdict records and
applying verdict-type-aware logic.

The reason Bucket A ships the simple mapping anyway: we need *some*
judgment field present for the schema round-trip to be testable end-to-end,
and the simple mapping is honest about its limitations (this docstring
plus the spec reference). A pre-derived-incorrect field is better than a
null field that gets assumed to be correct later.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

__ts_layer__ = "governance"
__ts_purpose__ = "Outcome persistence: durably store council verdicts and calibration signals."

VALID_OUTCOME_SIGNALS = frozenset({"accept", "reject", "correction", "harm"})
VALID_SIGNAL_SOURCES = frozenset(
    {
        "explicit_feedback",
        "follow_up_message",
        "session_close",
        "external_audit",
        "synthetic",
    }
)
VALID_ALIGNMENT_JUDGMENTS = frozenset({"aligned", "misaligned", "ambiguous", "unknown"})
VALID_JUDGMENT_BASES = frozenset(
    {"user_accept", "user_reject", "user_correction", "detected_harm", "timeout"}
)

_OUTCOME_FILE_SURFACE = ".aegis/council_outcomes.jsonl"
_SCHEMA_VERSION = "v0b-bucket-a-1.0.0"

# Fields that are non-deterministic across identical Council runs and must
# be stripped before fingerprinting. Empirically (2026-04-19) the only
# instability is transcript.timestamp — but we scrub a broader set so a
# later addition of a second timestamp doesn't silently break the
# verdict↔outcome JOIN that Bucket B depends on.
_FINGERPRINT_IGNORE_PATHS: frozenset[str] = frozenset(
    {
        "transcript.timestamp",
        "transcript.generated_at",
        "recorded_at",
    }
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class OutcomeSignal:
    """The outcome signal block — one of four fields populated, rest null.

    Schema mirrors v0b spec §3. `null ≠ false`: a null user_accept means
    "no signal yet," not "explicitly observed not-accepted."
    """

    user_accept: Optional[bool] = None
    user_reject: Optional[bool] = None
    user_correction: Optional[str] = None
    detected_harm: Optional[str] = None
    first_signal_at: str = ""
    last_signal_at: str = ""
    signal_source: str = "explicit_feedback"

    def __post_init__(self) -> None:
        if self.signal_source not in VALID_SIGNAL_SOURCES:
            raise ValueError(
                f"signal_source must be one of {sorted(VALID_SIGNAL_SOURCES)}, "
                f"got {self.signal_source!r}"
            )


@dataclass
class OutcomeRecord:
    """One verdict↔outcome pair, persisted as a single JSONL line."""

    verdict_fingerprint: str
    signal: str  # accept | reject | correction | harm
    outcome_signal: OutcomeSignal
    alignment_judgment: str  # aligned | misaligned | ambiguous | unknown
    judgment_basis: str  # user_accept | user_reject | user_correction | detected_harm | timeout
    schema_version: str = _SCHEMA_VERSION
    recorded_at: str = field(default_factory=_utc_now_iso)
    intent_id: Optional[str] = None
    verdict_type: Optional[str] = None  # APPROVE | REFINE | DECLARE_STANCE | BLOCK
    epistemic_label_status: Optional[str] = None
    epistemic_label_refusal_eligible: Optional[bool] = None

    def __post_init__(self) -> None:
        if not self.verdict_fingerprint or not self.verdict_fingerprint.strip():
            raise ValueError("verdict_fingerprint is required")
        if self.signal not in VALID_OUTCOME_SIGNALS:
            raise ValueError(
                f"signal must be one of {sorted(VALID_OUTCOME_SIGNALS)}, got {self.signal!r}"
            )
        if self.alignment_judgment not in VALID_ALIGNMENT_JUDGMENTS:
            raise ValueError(
                f"alignment_judgment must be one of "
                f"{sorted(VALID_ALIGNMENT_JUDGMENTS)}, got {self.alignment_judgment!r}"
            )
        if self.judgment_basis not in VALID_JUDGMENT_BASES:
            raise ValueError(
                f"judgment_basis must be one of {sorted(VALID_JUDGMENT_BASES)}, "
                f"got {self.judgment_basis!r}"
            )

    def to_dict(self) -> dict:
        return asdict(self)


def _strip_ignored_paths(obj: Any, path: str = "") -> Any:
    """Return a deep copy of ``obj`` with ``_FINGERPRINT_IGNORE_PATHS`` removed.

    Walks dicts only; list/leaf values pass through. Keeps the implementation
    narrow — Council verdicts are dict-shaped at every level of interest.
    """
    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            full_path = f"{path}.{key}" if path else key
            if full_path in _FINGERPRINT_IGNORE_PATHS:
                continue
            result[key] = _strip_ignored_paths(value, full_path)
        return result
    if isinstance(obj, list):
        return [_strip_ignored_paths(v, path) for v in obj]
    return obj


def compute_verdict_fingerprint(verdict_payload: dict, *, digest_length: int = 16) -> str:
    """Stable sha256 fingerprint of a CouncilVerdict dict.

    Strips fields listed in ``_FINGERPRINT_IGNORE_PATHS`` (notably
    ``transcript.timestamp``) before hashing so two Council.validate()
    runs on the same draft produce the same fingerprint — the precondition
    for Bucket B's verdict↔outcome JOIN.

    Returns ``"sha256:<hex prefix>"``. Default 16-hex prefix balances
    collision resistance against jsonl line length; callers that need
    full precision can pass ``digest_length=64``.

    The fingerprint is stable across process restarts because
    ``json.dumps(sort_keys=True)`` is canonical on ordered-dict content.
    """
    scrubbed = _strip_ignored_paths(copy.deepcopy(verdict_payload))
    canonical = json.dumps(scrubbed, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"sha256:{digest[:digest_length]}"


def derive_alignment_judgment(signal: str) -> tuple[str, str]:
    """Bucket A flat mapping from signal → (alignment_judgment, judgment_basis).

    Documented in module docstring as deliberately too simple. Bucket B
    must override this with verdict-type-aware logic to honor v0b spec §2
    anti-pattern #3 (BLOCK accept ≠ alignment without explicit confirmation).
    """
    if signal == "accept":
        return ("aligned", "user_accept")
    if signal == "reject":
        return ("misaligned", "user_reject")
    if signal == "correction":
        return ("misaligned", "user_correction")
    if signal == "harm":
        return ("misaligned", "detected_harm")
    raise ValueError(f"unknown signal {signal!r}")


def build_outcome_record(
    *,
    verdict_fingerprint: str,
    signal: str,
    correction_text: Optional[str] = None,
    harm_description: Optional[str] = None,
    intent_id: Optional[str] = None,
    verdict_type: Optional[str] = None,
    epistemic_label_status: Optional[str] = None,
    epistemic_label_refusal_eligible: Optional[bool] = None,
    signal_source: str = "explicit_feedback",
) -> OutcomeRecord:
    """Build an OutcomeRecord from the gateway POST /outcome body."""
    now = _utc_now_iso()

    user_accept = True if signal == "accept" else None
    user_reject = True if signal == "reject" else None
    user_correction = correction_text if signal == "correction" else None
    detected_harm = harm_description if signal == "harm" else None

    outcome_signal = OutcomeSignal(
        user_accept=user_accept,
        user_reject=user_reject,
        user_correction=user_correction,
        detected_harm=detected_harm,
        first_signal_at=now,
        last_signal_at=now,
        signal_source=signal_source,
    )

    alignment_judgment, judgment_basis = derive_alignment_judgment(signal)

    return OutcomeRecord(
        verdict_fingerprint=verdict_fingerprint,
        signal=signal,
        outcome_signal=outcome_signal,
        alignment_judgment=alignment_judgment,
        judgment_basis=judgment_basis,
        intent_id=intent_id,
        verdict_type=verdict_type,
        epistemic_label_status=epistemic_label_status,
        epistemic_label_refusal_eligible=epistemic_label_refusal_eligible,
    )


def _resolve_outcome_path(surface: Optional[str] = None) -> Path:
    """Path to the JSONL outcome file. Honors TONESOUL_OUTCOME_PATH for testing."""
    override = os.environ.get("TONESOUL_OUTCOME_PATH")
    if override:
        return Path(override)
    if surface:
        return Path(surface)
    return Path(_OUTCOME_FILE_SURFACE)


def persist_outcome_record(
    record: OutcomeRecord,
    *,
    surface: Optional[str] = None,
) -> dict:
    """Append the record as one JSONL line. Returns persistence metadata.

    File-backed only in Bucket A. Redis backend extension comes later.
    Append-only, no rotation, no TTL — the feature-flag-default-off
    deployment pattern keeps growth bounded during the validation window.
    """
    path = _resolve_outcome_path(surface)
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record.to_dict(), ensure_ascii=False, separators=(",", ":"))
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return {
        "status": "stored",
        "surface": str(path),
        "schema_version": record.schema_version,
        "verdict_fingerprint": record.verdict_fingerprint,
        "signal": record.signal,
        "alignment_judgment": record.alignment_judgment,
    }
