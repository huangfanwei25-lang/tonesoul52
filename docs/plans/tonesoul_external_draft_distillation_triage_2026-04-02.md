# ToneSoul External Draft Distillation Triage (2026-04-02)

> Purpose: record which currently parked external design drafts are worth distilling into ToneSoul-native next steps, and which must remain parked to avoid creating a second roadmap.
> Authority: planning aid only. Does not outrank runtime code, tests, accepted contracts, or the active short board in `task.md`.

---

## Scope

This triage covers the currently parked design drafts in `docs/plans/`:

1. `tonesoul_three_order_isolation_design_2026-04-02.md`
2. `tonesoul_dual_layer_numeric_design_2026-04-02.md`
3. `tonesoul_anti_fake_completion_design_2026-04-02.md`
4. `tonesoul_architecture_thinning_and_tiered_flow_design_2026-04-02.md`

The goal is not to absorb these documents wholesale.
The goal is to extract only the bounded patterns that reduce current friction in the active ToneSoul stack.

---

## Review Outcome

| Draft | Verdict | Why |
|---|---|---|
| `three_order_isolation` | `distill_selectively` | strong boundary language, but drifts from live ToneSoul naming and references retired sidecar files |
| `dual_layer_numeric` | `park_for_later` | valuable long-range design, but depends on outcome-feedback infrastructure that does not exist yet |
| `anti_fake_completion` | `distill_selectively` | real problem statement, but should not be pushed directly into `task.md` phase formatting |
| `architecture_thinning_and_tiered_flow` | `distill_selectively` | best source of next-step latency ideas, but mixes stale metrics, external comparisons, and too much roadmap in one file |

---

## What To Keep

### 1. Three-Order Isolation

Keep the core warning:

- shell readout is not execution permission
- resolver checks authorize
- execution cannot rewrite authority after the fact

Do not keep:

- `governance_kernel` as the dominant live resolver label
- references to retired sidecar docs
- any framing that creates a second control-plane vocabulary beside current ToneSoul contracts

ToneSoul-native extraction:

- use the language already present in `readiness`, `mutation_preflight`, `shared_edit_preflight`, and `publish_push_preflight`
- keep the rule as successor-facing interpretation discipline, not a new foundational model

### 2. Dual-Layer Numeric

Keep only the warning:

- descriptive confidence and calibrated confidence are different things
- do not read current council agreement as probability of correctness

Do not keep right now:

- `CalibrationRecord`
- new storage lanes
- `record_verdict_outcome.py`
- observer/runtime integration of posterior values

Reason:

- ToneSoul still lacks a real outcome-feedback loop
- adding fake-calibration scaffolding now would create more narrative than truth

### 3. Anti-Fake-Completion

Keep the core problem statement:

- completed phase != solved subsystem
- smooth compaction / closeout wording can still overstate what is actually proven

Do not keep:

- mandatory `Cannot Support` lines in every `task.md` phase
- large-scale backfill of older phases
- task-board inflation for the sake of anti-overclaim semantics

ToneSoul-native extraction:

- prefer successor-facing readouts, closeout grammar, observer emphasis, and subsystem parity notes
- keep `task.md` short-board discipline boring and explicit

### 4. Architecture Thinning And Tiered Flow

Keep the strongest bounded ideas:

- default to a fast path
- pull deeper governance only when needed
- keep multi-agent deliberation as escalation, not as the default shape of every turn

Do not keep as-is:

- stale point-in-time metrics
- raw external comparison tables as execution truth
- the whole mixed roadmap as one master spec

ToneSoul-native extraction:

- use `tiered pull` as the next latency program
- keep it framed around current ToneSoul surfaces, not around becoming `claw-code`

---

## Recommended ToneSoul Direction

ToneSoul should keep its multi-agent architecture, but stop paying the full governance cost on every turn.

The right move is:

1. `single-agent fast path` by default
2. `bounded orientation shell` for most normal continuations
3. `deep governance / council / full observer detail` only on triggered escalation

This preserves:

- successor coherence
- bounded safety discipline
- dissent visibility
- multi-agent value where it actually matters

And it reduces:

- cold-start delay
- unnecessary council overhead
- over-reading of large continuity surfaces

---

## What Should Happen Next

### Immediate Next Program

Start a ToneSoul-native latency program centered on:

- `Tier 0`: instant gate
- `Tier 1`: orientation shell
- `Tier 2`: deep governance on demand

### What Not To Do

- do not import WFGY naming directly
- do not start outcome-calibration implementation yet
- do not expand `task.md` into a phase-boundary encyclopedia
- do not rewrite ToneSoul into a generic agent harness

---

## Parking Decision

These four drafts should remain parked in `docs/plans/` as source material.

They are not:

- active authority
- current runtime truth
- accepted implementation spec

If later work absorbs one bounded idea from them, that idea should be rewritten into a new ToneSoul-native plan or contract rather than promoted by reference to the original draft.
