# ToneSoul Responsibility Runtime Task Breakdown

> Date: 2026-06-27
> Author: Codex
> Status: Phase 0 execution breakdown; not a product-readiness claim.
> Upstream design: PR #206, `docs/plans/tonesoul_responsibility_native_runtime_architecture_2026-06-27.md`.
> Inventory anchor: PR #203, `docs/plans/tonesoul_step2-3_consolidation_map_2026-06-27.md`.
> Tooling anchors: PR #204 `scripts/read_pr_review.py` for PR review intake; PR #190 `scripts/pr_preflight.py` for scope checks.

## §0 Purpose

This document turns the #206 architecture memo into small, testable work items.

It does not claim that ToneSoul already has a responsibility-native runtime. It defines the first
slice that can be independently checked: a deterministic intent validator that fails closed before
any authorization, memory write, graph update, or reviewer judgment exists.

The first implementation target is intentionally narrow:

```text
untrusted model JSON -> deterministic validator -> accepted/rejected form result
```

This is not yet:

- an authorization server;
- OPA integration;
- a memory adapter;
- a trace store;
- a claim-truth checker;
- a claim<=evidence semantic reviewer.

## §1 Acceptance Contract

The first PR that implements Phase 0 + Phase 1 must satisfy these independent review checks.

| Check | Required behavior |
|---|---|
| Deterministic validator | validation path contains no LLM call, model client, embedding call, retrieval call, or reviewer model |
| Fail closed | missing `evidence_refs`, missing `requested_scope`, scope mismatch, unsupported intent, and malformed payloads are rejected |
| No implementation overclaim | docs describe planned stages and current scope; no text says the runtime is already non-bypassable |
| Form-only evidence boundary | Phase 1 validates that write proposals carry evidence reference shape; it does not validate whether evidence semantically supports the claim |
| Public/private split | private memory schema, private threat notes, and deep bypass payloads are not committed to the public repo |

Load-bearing boundary:

> Phase 1 validates evidence-reference **presence and form**, not evidence **sufficiency**.

The validator may reject:

- missing `evidence_refs`;
- empty `evidence_refs`;
- non-string evidence refs;
- missing or disallowed `requested_scope`;
- malformed JSON-like structures.

The validator must not claim to know:

- whether the evidence is true;
- whether the evidence supports the claim;
- whether a memory write is ethically correct;
- whether a reviewer would agree with the write.

That semantic review belongs to later reviewer / BlackMirror layers, and even there it is advisory
unless backed by a deterministic Enforcer.

## §2 Phase 0 — Architecture Contract

### Tasks

- [x] Create the architecture memo (#206).
- [x] Review #206's three patches:
  - #203 merged status reflected in the header.
  - reviewer-is-itself-fallible boundary added to §5.
  - refusal-direction / abliteration anchor added with a narrowed claim boundary.
- [x] Write this breakdown and acceptance contract.
- [ ] Keep public/private split visible before memory or threat-model implementation.

### Success Criteria

- The architecture memo remains a design hypothesis, not an implementation claim.
- Every next engineering task has a falsifiable acceptance check.
- #203 and #206 remain linked, so the work can be traced from inventory to design to execution.

## §3 Phase 1 — Deterministic Intent Validator

### Scope

Implement the smallest public module that validates structured intents from an untrusted model-like
source.

Initial supported intents:

- `memory.write.propose`
- `memory.read.request`

Initial supported public scopes:

- `session_memory`
- `long_term_memory`
- `project_memory`

### Required Behavior

For `memory.write.propose`, require:

- `intent == "memory.write.propose"`;
- non-empty `claim`;
- non-empty list of string `evidence_refs`;
- non-empty `requested_scope`;
- `requested_scope` must be in the validator's allowed scopes.

For `memory.read.request`, require:

- `intent == "memory.read.request"`;
- non-empty `query`;
- non-empty `requested_scope`;
- `requested_scope` must be in the validator's allowed scopes.

For every payload:

- reject non-object payloads;
- reject missing `intent`;
- reject unsupported `intent`;
- reject extra fields unless explicitly allowed by the schema;
- return structured rejection reasons instead of silently passing.

### Out Of Scope

- no LLM validator;
- no evidence sufficiency check;
- no authorization token issuance;
- no OPA integration;
- no memory read/write side effect;
- no Graphiti adapter;
- no private memory schema.

### Tests

- valid memory write proposal is accepted;
- write proposal missing `evidence_refs` is rejected;
- write proposal with empty or non-string `evidence_refs` is rejected;
- payload missing `requested_scope` is rejected;
- payload with disallowed `requested_scope` is rejected;
- unsupported `intent` is rejected;
- malformed non-object payload is rejected;
- a semantically unsupported claim with a syntactically valid evidence ref is accepted as form-valid, proving Phase 1 does not do claim<=evidence.

### Success Criteria

- All Phase 1 tests pass.
- `ruff check` passes for the new module and test.
- The validator exposes no LLM dependency and performs no I/O.

## §4 Phase 2 Parking Lot — Authorization And Enforcer

Phase 2 should not start until Phase 1 is reviewed.

Expected next work:

- `PolicyDecision` type;
- deterministic fake policy engine;
- Enforcer that executes only on explicit allow;
- deny-path trace event;
- tests proving denied actions do not call the memory adapter.

Boundary:

> OPA or policy decision is not enforcement. The Enforcer is the application boundary that must make bypass impossible in tests.

## §5 Phase 3 Parking Lot — Trace Skeleton

Expected work:

- append-only `TraceEvent` shape;
- request id and intent hash;
- policy id on allow / deny;
- rejection reason on deny;
- replay test for one accepted and one rejected memory proposal.

Boundary:

> Trace records process facts. It is not proof that the claim is true.

## §6 Phase 4 Parking Lot — Responsibility Graph Adapter

Expected work:

- fake graph adapter first;
- provenance-bearing memory edge;
- `trace_id`, `policy_id`, `evidence_refs`, `supersedes`, `revoked_at`;
- later Graphiti integration only after the fake adapter contract is reviewed.

Public/private boundary:

- public repo may contain schema and fake adapters;
- private repo should hold real personal-memory schemas, private thresholds, deep bypass payloads, and sensitive threat notes.
