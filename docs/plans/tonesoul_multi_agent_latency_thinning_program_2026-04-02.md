# ToneSoul Multi-Agent Latency Thinning Program (2026-04-02)

> Purpose: reduce reaction time without abandoning ToneSoul's multi-agent and governance architecture.
> Authority: accepted planning program candidate. Runtime truth remains in code, tests, and accepted contracts.

---

## Problem Statement

ToneSoul's core structure is now strong enough that the main bottleneck is not missing theory.

The bottleneck is:

- too much cold-start work on normal turns
- too many successor-facing surfaces pulled at once
- multi-agent deliberation still feeling closer to default overhead than to explicit escalation

ToneSoul should keep multi-agent architecture.
It should not keep paying full multi-agent cost when the task does not justify it.

---

## Design Thesis

The right target is not "less governance".
The right target is:

`governance by tiered pull instead of monolithic push`

That means:

1. `Tier 0` answers: can I safely start, and what is the first bounded move?
2. `Tier 1` answers: what stable orientation do I need before I act?
3. `Tier 2` answers: what deeper governance, continuity, and council surfaces do I need only if the task is risky, contested, or blocked?

---

## Tier Model

### Tier 0: Instant Gate

Use for:

- typo fixes
- narrow code edits
- quick read/write continuation
- bounded follow-up on an already clear short board

Should expose only:

- `readiness`
- `task_track_hint`
- `deliberation_mode_hint`
- `hook_chain`
- `mutation_preflight` summary
- one-line `canonical_center` summary

Must not require:

- full observer-window prose
- full packet reread
- council dossier interpretation
- full hot-memory ladder detail

### Tier 1: Orientation Shell

Use for:

- feature-track continuation
- successor handoff where local context is not enough
- moderate ambiguity without full blockage

Should expose:

- `canonical_center`
- `subsystem_parity`
- `closeout_attention`
- bounded `observer_window`
- low-drift anchor summary

Must still avoid:

- full deep-governance dump by default

### Tier 2: Deep Governance

Use only when:

- `readiness` is not pass
- shared-path mutation is involved
- claims overlap
- closeout is partial / blocked / underdetermined
- council realism matters
- system-track work is active

Can expose:

- full packet
- full observer window
- hot-memory ladder and decay map
- council realism / dossier detail
- deeper continuity and subject surfaces

---

## Multi-Agent Policy

ToneSoul should remain multi-agent, but with a stricter default:

- one agent owns the fast path
- council and extra perspectives are escalation tools
- multi-agent overhead must be earned by risk, ambiguity, or conflict

Practical rule:

- `quick_change` should usually stay single-agent
- `feature_track` may open bounded review
- `system_track` and contested states may escalate to richer council use

This preserves the value of dissent without turning every action into a committee.

---

## What To Build First

### Phase 763: Tier-0 Session-Start Fast Path

Bounded scope:

- add a `--tier 0` path to `start_agent_session.py`
- keep current default behavior unchanged
- return only the minimum safe orientation surfaces for a quick start
- add regression coverage for tiered output shape

Why first:

- lowest risk
- highest latency payoff
- does not require deleting existing governance surfaces

### Phase 764: Tier-1 Orientation Shell

Bounded scope:

- add a `--tier 1` path that returns orientation shell surfaces without the full deep-governance bundle
- keep the current no-flag path backward compatible

### Phase 765: Deliberation Escalation Tightening

Bounded scope:

- make it clearer that deeper council use is tied to task/risk state
- keep this as readout and routing discipline first, not a full runtime rewrite

---

## What To Leave Deferred

- outcome-calibrated council confidence
- transport / MCP shell expansion
- persona/voice layer refactors
- large compaction storage redesign
- external theory naming import

Those are not the shortest board right now.

---

## Success Metric

This program succeeds when:

1. quick-change continuations can start with a much smaller entry bundle
2. feature-track work can pull orientation without paying full Tier-2 cost
3. deep-governance surfaces are still available, but no longer the first thing every successor must load
4. multi-agent deliberation is preserved as an escalation path, not as universal overhead

---

## Non-Goals

- not replacing ToneSoul with a simpler harness
- not deleting the observer window
- not deleting council
- not flattening continuity into one giant state object
- not claiming latency victory before measurements exist

---

## Current Recommendation

Accept this as the current live short-board direction.

Completed:

- `Phase 763: Tier-0 Session-Start Fast Path`
- `Phase 764: Tier-1 Orientation Shell`
- `Phase 765: Deliberation Escalation Tightening`
- `Phase 766: Tiered Agent Workspace Spec`
- `Phase 767: Workspace Frontend Readiness Map`

The next bounded translation move should be:

`Phase 768: Workspace View-Model Adapter Contract`
