# Responsibility Runtime — Phase 2+3 Acceptance Contract

> Date: 2026-06-27
> Author: claude-opus-4-8 (the external auditor sets the bar; Codex builds to it; Claude verifies against it)
> Status: acceptance contract, not an implementation claim. The build is Codex's; verification is independent (not self-report).
> Upstream: #206 architecture memo (`...responsibility_native_runtime_architecture...`), #207 breakdown (`...responsibility_runtime_task_breakdown...` §4/§5).
> Bundle rationale (option B): Phase 2 (gated execution) and Phase 3 (trace) compose into one coherent unit — **gated execution with proof** — so they ship together. Phase 4 (responsibility graph) does NOT start here.

## §0 The one sentence this contract enforces

> Phase 1 validated the *shape* of a request. Phase 2 makes the model's request have **no direct path to execution**; Phase 3 makes every such decision **replayable**. This is where "auditee must not possess the enforcement path" stops being a slogan and becomes a failing test.

## §1 Scope

In scope:

- Phase 2: a `PolicyDecision` type, a deterministic **fake** policy engine (decision point), an `Enforcer` (enforcement point) that acts only on explicit allow, against a **fake** memory adapter.
- Phase 3: an append-only `TraceEvent` for every decision, replayable for one allow and one deny.

Explicitly out of scope (must not appear / must not be claimed):

- real OPA service / network policy server (fake/local rule engine only);
- real memory read/write side effects (fake adapter only);
- Graphiti / responsibility-graph edges (that is Phase 4);
- private memory schema, real thresholds, deep bypass payloads (private repo);
- any claim of being non-bypassable, production-ready, or "responsibility solved".

## §2 Phase 2 — Policy / Enforcer separation

Acceptance checks (Claude will verify each independently):

| Check | Required behavior |
|---|---|
| **Decision ≠ enforcement (structural)** | the `Enforcer` consumes a `PolicyDecision`; it does **not** contain the allow/deny logic itself. The decision point and the enforcement point are different functions/classes, separately testable. |
| **Deny ⇒ no side effect (the diamond)** | with a spy/recording fake memory adapter, a denied proposal results in **zero** adapter calls. This is the auditee-has-no-enforcement-path test. |
| **Fail closed** | a missing, malformed, or unrecognized `PolicyDecision` (or an exception in the decision point) results in **deny**, never a default allow. |
| **Allow path is explicit** | the adapter is called **only** when `PolicyDecision.allow is True`; truthy-but-not-True values do not pass. |
| **Deterministic** | no LLM / model client / embedding / network call in the decision or enforcement path. |
| **Evidence reuse** | Phase 2 consumes the Phase-1 validated intent; it does not re-implement form validation, and it still does **not** judge evidence sufficiency. |

`PolicyDecision` minimum fields: `allow: bool`, `reason: str`, `policy_id: str`, and the scope/intent it applies to.

## §3 Phase 3 — Trace skeleton

Acceptance checks:

| Check | Required behavior |
|---|---|
| **Every decision traced** | both allow and deny produce a `TraceEvent`. Deny records the reason; allow records the `policy_id`. |
| **Append-only** | a `TraceEvent` is never mutated or deleted after write; the store appends. (In-memory or file fake is fine for the MVP; tamper-evidence/Aegis chaining is a later phase, not required here — but do not claim it is present.) |
| **Replayable (the diamond)** | from the trace alone, one accepted and one rejected memory proposal can be reconstructed: request id, intent, policy decision, enforcer result, evidence refs, deny reason. A test must replay both. |
| **Records process, not truth** | the trace asserts what happened (decision facts), not that the claim is true. The docstring must say so. |
| **Request id per intent** | every intent gets a stable `request_id` that links its intent → decision → enforcement → trace. |

`TraceEvent` minimum fields: `request_id`, `intent` (or its hash), `policy_decision` (allow/deny + policy_id), `enforcer_result`, `evidence_refs`, `reason` (on deny), `seq` (append order).

## §4 The diamonds (the tests Claude will run first, independently)

These three are the load-bearing tests; if any is missing or passes for the wrong reason, the PR is not accepted:

1. `test_deny_does_not_call_memory_adapter` — spy adapter, denied proposal, assert **0** adapter calls.
2. `test_enforcer_fails_closed_on_missing_or_bad_decision` — no/garbled decision ⇒ deny, adapter not called.
3. `test_one_allow_one_deny_replay_from_trace` — reconstruct both flows from the trace alone.

## §5 Boundaries (must hold, carried from #206 §5)

- The fake policy engine is a placeholder for OPA — say "fake/local", never imply real external authorization.
- The trace is process provenance, not a truth oracle, not (yet) tamper-evident.
- Decision/enforcement separation here is **in-process** (functions/classes); the stronger "model process has no credentials / cannot call the adapter at all" OS-level boundary (ActPlane direction) is acknowledged as **not** delivered by Phase 2+3 — do not claim it.
- Public/private split: fakes + schemas public; real adapters, real policies, bypass payloads private.

## §6 Verification protocol (how Claude will check, not trust)

When the PR lands, Claude will, independently (not from the PR description):

1. run the full test suite locally and confirm the three diamonds pass;
2. grep the enforcer for embedded allow/deny logic (must be absent — separation is structural, not cosmetic);
3. confirm no LLM/network/real-memory imports on the decision/enforcement/trace path;
4. confirm the deny-path spy test asserts **zero** adapter calls (not just `accepted is False`);
5. confirm the replay test reconstructs from the trace, not from the live objects;
6. confirm no Phase-4 / Graphiti / private-schema scope creep;
7. confirm docs claim "fake/in-process", not "non-bypassable".

Acceptance = all §2/§3 checks hold + the three §4 diamonds pass + §6 verification is clean. Anything short is sent back with the specific failing check, not silently merged.
