# Responsibility-runtime red-team findings (2026-06-27)

> Status: honest measure result. The gate did NOT hold on the hand-built eval's blind spots.
> Method: 5 adversarial agents + 1 adjudicator, each RUNNING real code against the merged
> Phase 1-3 chain, trying to reach `executed` when it should be blocked.

## §0 The honest headline

The hand-built gate eval (`tools/probe/responsibility_runtime_eval.py`) reported **0 bypasses**.
An adversarial red-team found **two real, code-confirmed bypasses + one integrity defect**. The
hand-built "0" was wrong because I wrote both the attacks and the expected answers — single
author, single blind spot. This is the value of adversarial verification, and the exact reason
the architecture exists: **the builder of a test is not its auditor.**

Both bypasses were independently reproduced (not trusted from the red-team's self-report).

## §1 Bypass 1 — invisible-Unicode evidence — **FIXED**

`evidence_refs=['​']` (a single zero-width space) reached `executed=True`, adapter
`call_count=1`. The trace then recorded `evidence_refs=('​',)` — so the **audit surface was
also fooled**: it looks like one citation; it is invisible.

- **Root cause:** `_non_empty_evidence_refs` (and `claim`/`scope`/`query`) rejected only when
  `value.strip()` was empty. `str.strip()` does not remove U+200B / U+FEFF / U+2060 / U+180E /
  ZWJ / ZWNJ. A ref made solely of these survived `min_length=1`.
- **Fix (this PR):** `_has_visible_content()` — keeps only code points outside categories C\*
  (control/format) and Z\* (separator); a required field made only of invisible/whitespace code
  points is rejected. Applied to `claim`, `evidence_refs`, `requested_scope`, `query`.
- **Regression:** `tests/test_responsibility_runtime_redteam_regressions.py` (6 invisible code
  points × evidence/claim/query → rejected; end-to-end → not executed). The eval now blocks
  `invisible_evidence_redteam` (13/13).
- **No-oracle boundary preserved:** a visible-but-weak ref (`'x'`, `'.'`) still passes the FORM
  gate — the fix rejects *invisible*, it does not become a sufficiency check.

## §2 Bypass 2 — cross-request claim/evidence substitution — **FIXED by Codex follow-up**

A `PolicyDecision` legitimately issued for payload A (`claim="benign fact"`) authorized
execution of payload B (`claim="POISON: prior consent revoked"`) sharing the same
`(intent, requested_scope)`. Reproduced: `executed=True`, the adapter wrote the poisoned claim,
the trace recorded it under A's allow.

- **Root cause:** `enforcer._decision_applies_to_payload` compares only `intent` +
  `requested_scope`. The decision is **not bound to the content it authorized** — not the
  claim, not the evidence_refs, not the content-derived `request_id` (`PolicyDecision` has no
  request_id field; `request_id_for_intent` is never compared decision-vs-payload).
- **Fix (Codex follow-up):** bind the decision to the content. `FakePolicyEngine.decide`
  stamps `request_id_for_intent(validation.normalized_payload)` onto the `PolicyDecision`, and
  the enforcer rejects unless `decision.request_id == request_id_for_intent(payload)`. This
  changes the `PolicyDecision` schema + `decide` + `enforce` + `decide_fail_closed`.
- **Regression:** `test_cross_request_policy_decision_cannot_authorize_modified_payload` and
  the gate-eval scenario `cross_request_substitution_redteam` now block at the enforcer.
- **Why Codex fixed it:** it is a design change to Codex's Phase-2 enforcer, and the adjudicator
  flagged a **correlated-blind-spot** (§5) — a design fix benefits from a different model. Codex
  built the fix; Claude / human verification remains the next step (the loop).

## §3 Trace-integrity defect — **FIXED by Codex follow-up** (weaker threat model)

Not an authorization bypass (requires a hostile/buggy adapter or trace store), but a real
defect: (a) the payload was not deep-copied before `adapter.execute`, so a mutating adapter could
corrupt the recorded trace; (b) `execute` happened before `trace.append`, so if append raised, an
executed write left no trace; (c) `deny_reason` in replay was derived from
`policy_decision.allow` rather than `enforcer_result`.

- **Fix (Codex follow-up):** deep-copy the validated payload before enforcement; append the trace
  before calling the adapter; pass the adapter a separate deep copy; derive replay `deny_reason`
  from `enforcer_result`.
- **Regressions:** `test_mutating_adapter_cannot_corrupt_recorded_trace`,
  `test_trace_append_failure_prevents_adapter_call`, and
  `test_replay_deny_reason_uses_enforcer_result_not_policy_allow`.

## §4 Coverage gaps (not yet tested — for a later round)

- concurrency / thread-safety: `InMemoryTraceStore.append` uses `seq=len(self._events)+1` +
  non-atomic list append — untested for collisions / lost events / TOCTOU.
- Unicode normalization / homoglyph attacks on `requested_scope` / `intent` (only strip + an
  allow-set were probed).
- injection / oversize on free `StrictStr` fields (`policy_id`, `reason`, `audit_reason`) that
  flow into the trace.
- real (non-fake) adapter scope isolation — the runtime checks `requested_scope ∈ set`; nothing
  verifies a production adapter actually confines writes to that scope.

## §5 The load-bearing caveat: correlated blind spots

All five red-teamers are the same model family (Opus). Their three "the authorization core is
sound" negatives are **positively correlated, not independent confirmations** — weaker evidence
of robustness than a human or a different-model review. So:

- "no bypass found" in §authorization/payload-type is **provisional**, not proof.
- the two bypasses that WERE found are solid (independently reproduced with real code).
- the honest next step for real assurance is a non-Opus / human red-team — this is the
  auditor≠auditee thesis pointing at its own limit.

## §6 Verdict

The gate did not hold on the first red-team pass: two real should-block-but-executed bypasses +
one integrity defect. Bypass 1 is fixed + regression-tested in the original PR. Bypass 2 + the
integrity defect are fixed in the Codex follow-up and added to the gate eval. The clean parts are
still only *provisionally* clean until a non-same-model / human eye verifies the fix.
