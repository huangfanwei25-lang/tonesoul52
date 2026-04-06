# ToneSoul Agent Workspace And IDE Translation Program (2026-04-06)

> Purpose: translate ToneSoul's tiered runtime surfaces into a future operator workspace / IDE without collapsing canonical, advisory, descriptive, and preflight boundaries into one dashboard.
> Authority: accepted planning program. Runtime truth remains in code, tests, and accepted contracts.

---

## Program Goal

Build a ToneSoul-native agent workspace path that:

- preserves the current `Tier 0 / 1 / 2` pull model
- shortens successor reaction time
- makes preflight and escalation legible
- stays CLI/runtime-aligned instead of becoming a second competing control plane

This is not a general frontend beautification pass.
It is a translation program from:

`runtime surfaces -> panel-ready read models -> bounded UI implementation`

---

## Design Pressure

ToneSoul now has enough machine-readable surfaces that a future IDE can help a lot.

It can also fail in a very predictable way:

- pull too much too early
- turn observer prose into permission
- turn summaries into completion claims
- make every surface look equally authoritative
- add UI latency on top of runtime latency

So the workspace must preserve:

- `Tier 0` for instant gate
- `Tier 1` for orientation shell
- `Tier 2` for deep governance

while keeping multi-agent architecture as escalation, not default tax.

---

## Execution Guardrails

- Prefer view-model adapters and render budgets over raw packet or observer dumps.
- Keep CLI parity visible; the UI must never become the only way to act.
- Do not merge `canonical`, `operational`, `advisory`, `descriptive`, and `preflight` into one generic status badge.
- Treat `apps/dashboard` as the first likely operator-workspace target.
- Treat `apps/web` as public/demo-facing until a concrete operator panel need proves otherwise.
- Treat `apps/council-playground` as a specialized deep-governance auxiliary, not the main workspace shell.

---

## Phase Plan

### Phase 767: Workspace Frontend Readiness Map

- inventory current runtime surfaces against `Tier 0 / 1 / 2`
- classify each one as `render_direct`, `adapter_needed`, `deep_pull_only`, or `defer`
- map the current repo frontend surfaces against those tiers

### Phase 768: Workspace View-Model Adapter Contract

- define one ToneSoul-native adapter shape for `Tier 0` and `Tier 1` panel rendering
- keep `Tier 2` mostly as bounded drawer pulls
- preserve command parity and label discipline

### Phase 769: Dashboard Operator Shell Adoption

- adapt `apps/dashboard/frontend/pages/workspace.py` to the tier model first
- keep it operator-facing
- do not attempt a whole-repo UI rewrite

### Phase 770: Deep-Governance Drawer Budget

- define what `Tier 2` may open by default, what must stay collapsed, and what needs explicit user pull
- cap initial drawer scope so deep governance does not flood the main workspace

### Phase 771: Public / Demo Surface Alignment

- decide what part of the tier model should appear in `apps/web`
- keep public/demo surfaces subordinate to operator-truth surfaces
- do not let the public site invent a competing control center

---

## Existing Frontend Reality

Current repo UI surfaces already split naturally:

- `apps/dashboard/frontend/pages/workspace.py`
  - closest to an operator workspace
  - best candidate for Tier 0 / Tier 1 shell adoption
- `apps/dashboard/frontend/components/status_panel.py`
  - useful as a future bounded status card region
  - currently mixes many runtime concepts into one generic status story
- `apps/dashboard/frontend/components/memory_panel.py`
  - closer to reference selection than hot-memory truth
  - should stay subordinate to tiered orientation panels
- `apps/web/src/app/page.tsx`
  - public/demo conversation surface
  - not yet the right place for operator governance panels
- `apps/council-playground`
  - deep-governance auxiliary
  - suitable for controlled Tier-2 drilldown, not first-hop orientation

---

## Success Condition

This program succeeds when:

1. a future agent workspace can open in `Tier 0` without loading the whole governance stack
2. `Tier 1` gives stable orientation without becoming a packet dump
3. `Tier 2` is available for risky/contested work without becoming universal overhead
4. the UI helps successors keep boundaries instead of flattening them

---

## Non-Goals

- rewriting the whole frontend stack now
- replacing CLI entry with a browser-only workflow
- making `apps/web` the canonical operator workspace before proof
- reintroducing monolithic dashboard design through prettier cards

---

## Current Recommendation

Accept this as the live long program for the frontend / IDE translation lane.

The current short board remains:

`Phase 768: Workspace View-Model Adapter Contract`
