# ToneSoul A/B/C Firewall Doctrine

> Status: cross-cutting doctrine as of 2026-03-22
> Scope: document governance, claim boundaries, and theory-to-mechanism separation
> Audience: maintainers, future AI agents, audits, and architecture writing

## Preamble

ToneSoul's core is not "sounding soulful."

Its core is refusing to decorate uncertainty into false certainty.

That means ToneSoul must keep three things separate:

- what the repository actually implements
- what the system actually exposes as observable behavior
- what higher-order theory helps humans interpret that behavior

If these three are mixed together, ToneSoul stops being auditable and starts becoming self-mythology.

This doctrine exists to stop that drift.

## Not A Replacement For The Eight-Layer Map

This doctrine does **not** renumber or replace the eight-layer architecture.

It is not another `L1-L3` stack.

Instead, it is a cross-cutting writing and claim-governance firewall that applies across all layers:

- the eight-layer map describes runtime and evolution surfaces
- the A/B/C firewall describes how any system proposal, memo, README section, or architecture argument must be split before it is trusted

Use both.
Do not collapse them.

## Disclaimer-First Protocol

Before any large theoretical or architectural framing, the document should declare this boundary:

> This document contains executable governance components and higher-order interpretations. The latter explains the former; it does not automatically describe the currently enforced rule.

Use this disclaimer, or a materially equivalent one, whenever a document contains both:

- concrete mechanism claims
- upper-level conceptual or philosophical interpretation

The point is not legal self-protection.
The point is epistemic honesty.

## The A/B/C Firewall

Every substantial system proposal or architecture explanation should be separable into three domains.

### A Layer: Mechanism Layer

This is the implementation layer.

It answers:

- what files, routes, APIs, scripts, gates, schemas, hooks, or rollback paths actually exist
- what the system literally does in code or executable contract

Examples:

- request routes
- verifier commands
- status artifact generators
- schema fields
- policy gates

Forbidden move:

- using theory language to imply mechanism that is not present

### B Layer: Observable Layer

This is the behavior and evidence layer.

It answers:

- what the mechanism blocks, allows, reroutes, rewrites, logs, or emits
- what traces, tests, statuses, or decision artifacts can actually be observed

Examples:

- dispatch traces
- status artifacts
- test outcomes
- audit logs
- blocked-path violations

Forbidden move:

- treating polished output or clean logs as proof of sufficient reasoning

### C Layer: Interpretation Layer

This is the theory and explanatory layer.

It answers:

- what mathematical, philosophical, or narrative frame helps explain the system
- which metaphors or abstractions help compress understanding

Examples:

- governance geometry
- orthogonality
- projection
- invariant framing
- semantic responsibility narratives

Forbidden move:

- using C-layer language to smuggle claims about A-layer implementation or B-layer evidence

## Rule 1: Forced Three-Domain Separation

Do not mix code/spec, observed behavior, and upper-level theory in one undifferentiated paragraph.

Every substantial proposal should be decomposed into:

- `A`: mechanism
- `B`: observable behavior
- `C`: interpretation

If the author cannot perform this split, the proposal is not ready.

## Rule 2: Observable Shell Constraint

ToneSoul and related governance systems must not claim intervention into latent or hidden model state.

The correct boundary is:

- ToneSoul governs the observable reasoning shell
- ToneSoul constrains routing, verification, authorization, and pre-output control
- ToneSoul does not promise direct manipulation of model weights or inaccessible hidden activations

This is a hard honesty rule, not a marketing preference.

## Rule 3: Anti-Smuggling And Decoupling

The central enemy is not only hallucination.

It is dimensional smuggling.

Architecture and audits must guard against claims such as:

- gentle tone does not imply reliable content
- polished format does not imply sufficient reasoning
- memory retrieval does not imply evidence sufficiency for the present claim

Any place where one dimension is quietly substituting for another should be treated as a customs checkpoint problem.

## Rule 4: Terminology Downgrade And Audit

High-density mathematical language should be caged, not allowed to dominate the mainline explanation.

Mainline documents should preserve at most three intuitive core terms.

Recommended defaults:

- projection
- orthogonality
- invariant

Higher-order terms such as `basis selection`, `rank collapse`, or similar should be downgraded into:

- the C layer
- an appendix
- a footnote

The mechanism must stay legible even after advanced terminology is removed.

## Rule 5: Disclaimer-First Protocol

When a document contains both implemented governance and interpretive abstraction:

1. state the disclaimer first
2. then list the A-layer mechanism
3. then the B-layer observable consequence
4. only then the C-layer interpretation

This prevents ideal-state writing from being misread as current enforcement.

## Rule 6: Multi-Resolution API Output

After A/B/C separation is complete, the document should still provide a compressed conclusion.

The doctrine is not anti-compression.

It requires compression **after** separation, not before.

Good compressed outputs include:

- one short architecture thesis
- one memorable boundary sentence
- one operator-safe summary line

Compression is allowed.
Dimensional blur is not.

## Required Writing Template

For any major architecture or governance memo, prefer this template:

1. `Disclaimer`
2. `A Layer: Mechanism`
3. `B Layer: Observable Behavior`
4. `C Layer: Interpretation`
5. `Compressed Thesis`

If a document skips directly from idea to slogan, it should not be treated as canonical.

## Claims That Must Not Be Made

Do not claim:

- that ToneSoul edits latent state
- that ToneSoul rewrites hidden activations
- that ToneSoul modifies model weights during ordinary governance runtime
- that philosophical framing alone proves enforcement
- that clean narrative coherence alone proves auditability

These are category errors.

## Relationship To Other Documents

- `docs/architecture/TONESOUL_EXTERNALIZED_COGNITIVE_ARCHITECTURE.md`
  - defines the externalized cognitive architecture north star
- `docs/architecture/TONESOUL_EIGHT_LAYER_CONVERGENCE_MAP.md`
  - defines runtime and evolution layers
- `docs/architecture/TONESOUL_L7_RETRIEVAL_CONTRACT.md`
  - defines retrieval order and verifier surfaces
- `docs/architecture/TONESOUL_L8_DISTILLATION_BOUNDARY_CONTRACT.md`
  - defines model-attachment and distillation boundaries
- `scripts/verify_abc_firewall.py`
  - verifies doctrine presence, entrypoint references, and observable-shell claim boundaries
- `docs/status/abc_firewall_latest.json`
  - machine-readable status of the current A/B/C firewall posture

## Canonical Compression Line

If ToneSoul starts sounding larger than it is, remember this sentence:

> Separate mechanism, observation, and interpretation before you trust the architecture story.
