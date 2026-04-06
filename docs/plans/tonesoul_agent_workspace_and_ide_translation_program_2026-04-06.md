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

### Phase 772: Dashboard Deep-Governance Drawer Implementation

- translate the bounded Tier-2 drawer budget into a real dashboard pull path
- keep default workspace load on Tier 0 / Tier 1 and require explicit operator action for deeper governance
- surface mutation, closeout, and contested continuity first; keep packet/detail payloads behind deeper pull

### Phase 773: Workspace Role-Parity Validation

- validate that `apps/dashboard` and `apps/web` now present distinct roles without role drift
- check that dashboard still follows CLI/runtime truth while `apps/web` stays educational/demo-first
- keep the lane parity-focused; do not reopen monolithic UI redesign

### Phase 774: Dashboard Status Panel Tier Alignment

- realign the dashboard status panel to the new tier model instead of legacy generic status storytelling
- keep the panel subordinate to the operator shell and deep-governance drawer
- reduce mixed authority language before any broader workspace polish

### Phase 780: Operator Walkthrough Pack

- add one bounded operator walkthrough pack for `Tier 0 / Tier 1 / Tier 2`
- teach first-hop usage with scenario-first examples instead of raw surface dumps
- keep the pack operator-facing and route public/demo readers back to educational surfaces instead of creating a second console

### Phase 781: Memory Panel Tier Subordination

- realign the dashboard memory panel so it stays a reference selector, not a competing operator-truth region
- keep selected memories subordinate to `Tier 0 / Tier 1` orientation and `Tier 2` deep pulls
- avoid turning reference selection into a pseudo hot-memory or operator-governance console

### Phase 782: Dashboard Command Shelf Parity

- add one compact command shelf that points back to core CLI/runtime commands
- keep the shelf tier-aware instead of turning it into a browser-side workflow engine
- reinforce that dashboard is an operator shell layered on top of CLI/runtime truth, not a separate control plane

### Phase 783: Search Context Boundary Cue

- add one bounded cue around local/web search toggles so retrieval stays visibly auxiliary
- keep search context beneath tiered operator truth instead of letting it impersonate the current runtime state
- avoid reopening retrieval architecture or a new search control plane inside the workspace

### Phase 784: Retrieval Preview Strip

- add one bounded retrieval-preview strip for search-assisted chat turns in the dashboard workspace
- surface local/web provenance so operators can inspect auxiliary context without mistaking it for current runtime truth
- keep the preview beneath Tier 0 / Tier 1 / Tier 2 instead of turning it into a fourth workspace tier

### Phase 784: Retrieval Preview Strip

- add one bounded retrieval-preview strip for local/web-assisted chat turns
- show what auxiliary context is feeding the workspace chat loop without treating that preview as operator truth
- keep provenance and authority labels visible so the preview stays below Tier 0 / Tier 1 / Tier 2

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

Once `Phase 784` lands, freeze this bucket unless a concrete workspace misread or role-parity regression reopens it.
