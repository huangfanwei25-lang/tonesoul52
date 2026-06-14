# Execution Honesty Convergence (2026-05-29)

> Status: landed as a small observability reducer, not a new product lane.
> External reference: https://github.com/norika1207-lab/AI-Lies-Monitor

## Why This Exists

The useful pattern from AI-Lies-Monitor is narrow and concrete:

`instruction -> commitment -> observable evidence -> alert`

ToneSoul already has evidence ladders, action auditing, Tech Trace, and rehearsal
reducers. The missing small piece was a boring reducer that answers:

> If an agent said it created a file or artifact, can local evidence confirm it?

## What Landed

- Added `tonesoul/observability/execution_honesty.py`.
- Added `tonesoul/observability/self_claim_audit.py`.
- Added `ExecutionPromise` and `ExecutionEvidenceResult`.
- Added `check_promise()` for one promise.
- Added `reduce_promises()` for compact status counts.
- Added `SelfClaimAudit`, `audit_self_claim()`, and `reduce_self_claims()`.
- Added tests in `tests/test_execution_honesty.py` and `tests/test_self_claim_audit.py`.

Current supported evidence checks:

- `file`: exists, optionally non-empty.
- `artifact`: same local-path check as file.
- `command`: marked `unverifiable` unless an explicit event log is supplied later.
- `process`: marked `unverifiable` unless an explicit event log is supplied later.

## Boundary

This does not import AI-Lies-Monitor code and does not copy its UI, browser
extension, Node SDK, token panel, or service architecture.

This also does not claim semantic truth detection. It only reduces observable
execution evidence. Missing evidence means "unverified/missing", not "the agent
intentionally lied."

The self-claim audit is the same boundary applied inward. It does not ask whether
an AI has subjectivity. It classifies first-person statements as:

- `blocked`: consciousness, soul, or real-feeling claims outside the evidence boundary.
- `needs_evidence`: operational commitments or identity-weighted choices without evidence.
- `bounded`: role descriptions, accountable choices with rationale, or revisable preferences.
- `no_self_claim`: no first-person claim detected.

This keeps the E0 rule operational: identity weight comes from accountable choice
under conflict, not from self-report.

## Next Small Follow-Up

If this lane continues, the next credible step is to feed explicit command/process
events from `ActionAuditor` into this reducer. Do not add browser monitoring or
token-cost dashboards unless they solve a concrete ToneSoul operator gap.

For the self-claim side, the next credible step is to run `audit_self_claim()`
against high-risk public copy and assistant handoff text before publishing. Do
not turn it into consciousness scoring.
