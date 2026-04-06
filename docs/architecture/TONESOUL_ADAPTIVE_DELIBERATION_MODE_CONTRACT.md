# ToneSoul Adaptive Deliberation Mode Contract

> Status: architectural discipline contract
> Purpose: define when ToneSoul deliberation should stay lightweight, use standard council, or elevate to full multi-round council — mapped against task track, readiness, risk, and claim state
> Last Updated: 2026-04-07
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md (dossier shape)
>   - docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md (task tracks + readiness)
>   - docs/architecture/TONESOUL_PLAN_DELTA_CONTRACT.md (plan change discipline)
>   - docs/architecture/TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md (opacity classification)
>   - tonesoul/council/runtime.py (CouncilRuntime + threshold adjustment)
>   - tonesoul/council/types.py (VerdictType, CoherenceScore)
>   - tonesoul/deliberation/adaptive_rounds.py (multi-round debate)
>   - tonesoul/unified_pipeline.py (_resolve_council_decision, council convening logic)
> Scope: 3 deliberation modes, 1 mode selection matrix, 5 escalation triggers, 3 de-escalation conditions

## How To Use This Document

If you are an AI agent about to trigger council deliberation, or you are reviewing whether a council verdict used appropriate depth:

1. Check the **Mode Definitions** to understand what each mode does and does not include
2. Check the **Mode Selection Matrix** to find the recommended mode for your task + risk combination
3. Check the **Escalation Triggers** for conditions that force upward mode shift
4. Check the **De-escalation Conditions** for when a lighter mode is justified even if the matrix suggests heavier

## Why This Document Exists

ToneSoul currently has two deliberation systems that always run at the same depth:

1. **Pre-Output Council** (`tonesoul/council/`): 4 perspectives (Guardian/Analyst/Critic/Advocate) vote on draft output. Always convened when `_resolve_council_decision()` says yes, always at the same coherence/block thresholds (modulo role council adjustments).

2. **Internal Deliberation** (`tonesoul/deliberation/`): 3 voices (Muse/Logos/Aegis) with adaptive multi-round debate. Always runs when available, with `calculate_debate_rounds()` determining round count.

Neither system adjusts its deliberation depth based on what kind of task is being performed. This creates mode mismatch:

- **Over-deliberation**: a typo fix triggers full multi-round council with 4 perspectives, evolution weight tracking, benevolence audit, genesis inference, and VTP evaluation. The overhead dwarfs the task.
- **Under-deliberation**: an architecture contract that redefines system boundaries gets the same single-round council as the typo fix. No elevated scrutiny, no mandatory multi-round debate, no explicit dissent requirement.

The cost is not just computational. Over-deliberation creates noise in evolution weights (trivial approvals inflate alignment rates). Under-deliberation creates false confidence in high-stakes verdicts.

## Compressed Thesis

Match deliberation depth to task stakes. A typo fix needs a gate check, not a symposium. An architecture contract needs adversarial scrutiny, not a rubber stamp. The system already has the mechanisms — it just does not select between them based on what matters.

---

## Mode Definitions

### lightweight_review

**What it does**: single-pass gate check. Runs contract observer and basic safety filter. Does not convene the full perspective council. Does not run multi-round deliberation.

**What it produces**: a pass/flag/block signal with a one-line reason. No minority report (no perspectives were convened). Dossier shape is minimal: `final_verdict`, `confidence_posture: "high"` (if pass) or `"low"` (if block), `deliberation_mode: "lightweight_review"`.

**Runtime equivalent**: the current fast-route bypass in `unified_pipeline.py` (lines ~1765-1830) when local POAV + contract observer are sufficient.

**Appropriate for**:
- Tasks where the output is narrowly bounded and low-risk
- Corrections, typo fixes, documentation edits within existing scope
- Tasks where the gate check is sufficient and full deliberation would produce no additional signal

### standard_council

**What it does**: convenes the 4-perspective Pre-Output Council (Guardian/Analyst/Critic/Advocate). Single round. Produces a `CouncilVerdict` with votes, coherence score, and divergence analysis. May include role council weight adjustments.

**What it produces**: full dossier per the Council Dossier And Dissent Contract. Minority report if dissent exists. Confidence posture derived from coherence + dissent ratio.

**Runtime equivalent**: the current default council path in `unified_pipeline.py` (lines ~2727-2771) when `_resolve_council_decision()` returns true.

**Appropriate for**:
- Feature implementation when clarification pressure, claim collision, or elevated risk makes multi-perspective review worth the cost
- Schema additions with identified consumers
- Contract observer or gate wiring
- Any task where perspectives are valuable but adversarial multi-round debate is not needed

### elevated_council

**What it does**: convenes the 4-perspective Pre-Output Council AND triggers multi-round adaptive deliberation. Requires at least 2 rounds. Explicitly tracks change-of-position across rounds. Requires minority report even if no dissent exists (in that case, the report states "no dissent detected after N rounds"). May lower coherence threshold to surface hidden disagreement.

**What it produces**: extended dossier with `change_of_position` entries, per-round tension tracking, and explicit `opacity_declaration`. If internal deliberation (Muse/Logos/Aegis) is available, its tension zone classification is included.

**Runtime equivalent**: the current adaptive debate path in `tonesoul/deliberation/adaptive_rounds.py` combined with the full council path. Currently these run independently; elevated mode would explicitly coordinate them.

**Appropriate for**:
- Architecture contracts that define new boundaries
- Schema version migrations
- Changes to governance posture, axioms, or canonical surfaces
- Any task where a wrong decision cascades to multiple later agents or sessions
- Tasks where `risk_posture.level` is "elevated" or "critical"

---

## Mode Selection Matrix

| Task Track | Risk Posture | Claim Collision | Readiness State | Recommended Mode | Rationale |
|---|---|---|---|---|---|
| quick_change | normal | none | pass | lightweight_review | Low stakes, bounded scope, gate check sufficient |
| quick_change | normal | none | needs_clarification | lightweight_review | Clarification needed but deliberation depth is not the issue |
| quick_change | elevated | none | pass | standard_council | Elevated risk on a quick change is unusual — council should verify |
| quick_change | any | active collision | any | standard_council | Claim collision means coordination complexity; council should arbitrate |
| feature_track | normal | none | pass | lightweight_review | Bounded feature work should stay on the fast path unless ambiguity, collision, or elevated risk earns deeper review |
| feature_track | normal | active collision | pass | standard_council | Collision adds coordination complexity |
| feature_track | elevated | any | pass | elevated_council | Elevated risk on feature work warrants adversarial scrutiny |
| feature_track | any | any | needs_clarification | standard_council | Clarification needed; council can help identify what is unclear |
| system_track | normal | none | pass | elevated_council | Cross-cutting changes always warrant multi-round scrutiny |
| system_track | normal | active collision | any | elevated_council | System track + collision is high coordination risk |
| system_track | elevated | any | any | elevated_council | Maximum scrutiny warranted |
| system_track | critical | any | any | elevated_council + human | Critical risk on system track requires human in the loop |
| any | critical | any | blocked | **do not deliberate** | Blocked state means the task should not proceed; council is premature |

### Reading The Matrix

- The matrix recommends a default mode. An agent may override upward (choosing elevated when standard is recommended) without justification.
- An agent may override downward (choosing lightweight when standard is recommended) only if it records the override reason in the dossier's `deliberation_mode` field.
- Downward override from elevated is a governance signal and should appear in compaction `carry_forward`.

---

## Escalation Triggers

These conditions force upward mode shift regardless of the matrix recommendation:

### Trigger 1: High-Confidence Dissent In Standard Mode

If a standard_council deliberation produces a dissenting vote with `confidence >= 0.7`, the mode should escalate to elevated_council for a second round to test whether the dissent survives adversarial examination.

### Trigger 2: Coherence Score Below Block Threshold

If the coherence score falls below the `block_threshold` (default 0.3), the mode should escalate to elevated_council. A coherence score this low suggests the perspectives fundamentally disagree — more rounds may reveal whether the disagreement is resolvable.

### Trigger 3: Protected Surface Modification

If the task involves modifying any surface classified as `Durable Identity` lane in the Subject Snapshot Field Lanes contract, or modifying AXIOMS.json, or modifying canonical governance posture, the mode should be at least elevated_council regardless of task track.

### Trigger 4: Plan Thrash Detection

If the Plan Delta Contract's thrash detection criteria are met (two forks from the same origin, or consecutive STOP compactions), deliberation should escalate to elevated_council to determine whether the plan itself is viable.

### Trigger 5: Evolution Weight Suppression

If `CouncilEvolution` has reduced any perspective's weight below 0.6 (40% reduction from baseline), elevated_council should be used to ensure that suppressed perspectives still have meaningful influence on high-stakes decisions.

---

## De-escalation Conditions

These conditions justify lighter deliberation even when the matrix suggests heavier:

### Condition 1: Identical Repeat Task

If the current task is structurally identical to a recently completed task that received elevated_council with high confidence, and no new risk signals have appeared, standard_council is sufficient. The previous elevated verdict serves as precedent.

### Condition 2: Human Pre-Approval

If the human has explicitly pre-approved the task approach (e.g., in a work order with specific acceptance criteria), lightweight_review is sufficient for execution steps that match the pre-approved spec exactly. The human's pre-approval is a stronger signal than council deliberation.

### Condition 3: Post-Fact Audit

If the deliberation is happening as a post-fact audit (reviewing already-committed work) rather than pre-commit review, standard_council is sufficient regardless of task track. The decision is already made; elevated scrutiny would be retroactive and cannot change the outcome.

---

## Current Runtime State vs. Contract

| Contract Concept | Current Runtime | Gap |
|---|---|---|
| Mode selection | `TONESOUL_COUNCIL_MODE` env var (rules/hybrid/full_llm) | Different axis: env var controls perspective *implementation* (rule-based vs LLM), not deliberation *depth* |
| Lightweight bypass | Fast-route in `unified_pipeline.py` when POAV + contracts suffice | Exists but not named as a deliberation mode |
| Standard council | Default council path in `unified_pipeline.py` | Exists; the default path |
| Elevated council | Adaptive rounds in `deliberation/adaptive_rounds.py` | Exists but runs independently of council path; not coordinated as "elevated mode" |
| Mode selection based on task track | Does not exist | Full gap: no task-track-aware mode selection |
| Escalation triggers | `_resolve_council_decision()` decides whether to convene at all, but not at what depth | Partial gap: convene/skip exists, depth does not |
| De-escalation | Does not exist | Full gap |
| Mode recorded in verdict | `council_mode_observability` in transcript records which perspective config was used | Partial gap: records perspective mode, not deliberation depth |

### Implementation Path

The contract does not require new subsystems. The mechanisms exist:

1. `unified_pipeline.py` already has a fast-route bypass (lightweight) and a full council path (standard)
2. `deliberation/adaptive_rounds.py` already has multi-round debate (elevated)
3. `_resolve_council_decision()` already decides whether to convene

What is missing is the wiring: a function that reads task track + risk posture + claim state and returns the recommended mode. This is a bounded `feature_track` implementation for Codex.

---

## Mode Interaction With Existing Council Mode Env Var

`TONESOUL_COUNCIL_MODE` (rules/hybrid/full_llm) controls how perspectives generate their votes — rule-based evaluation, LLM-based evaluation, or hybrid. This is orthogonal to deliberation depth:

| | lightweight_review | standard_council | elevated_council |
|---|---|---|---|
| rules | Gate check only (no perspectives) | Rule-based perspectives, single round | Rule-based perspectives, multi-round |
| hybrid | Gate check only (no perspectives) | Hybrid perspectives, single round | Hybrid perspectives, multi-round |
| full_llm | Gate check only (no perspectives) | LLM perspectives, single round | LLM perspectives, multi-round |

The env var stays as-is. Deliberation mode is a separate axis added by this contract.

---

## Deliberation Mode Names

The contract proposes three mode names. These may be renamed if better ToneSoul-native vocabulary emerges, but the semantic boundaries must be preserved:

| Proposed Name | Alternative Names Considered | Why This Name |
|---|---|---|
| `lightweight_review` | `gate_check`, `fast_pass`, `quick_scan` | "Review" signals governance intent; "lightweight" signals bounded depth |
| `standard_council` | `normal_council`, `default_council`, `single_round` | "Standard" is the unmarked default; "council" signals multi-perspective involvement |
| `elevated_council` | `deep_council`, `adversarial_council`, `multi_round` | "Elevated" signals higher scrutiny; avoids "deep" which is overloaded in ToneSoul |

---

## Relationship To Other Documents

Implementation note (2026-04-07): `scripts/start_agent_session.py` now surfaces a bounded machine-readable `deliberation_mode_hint` derived from `task_track_hint`, readiness, risk, and claim collision. For `feature_track + normal risk + no collision + pass`, the default successor-facing hint is `lightweight_review`; deeper council is treated as earned escalation rather than default overhead. The hint now separates:

- `active_escalation_signals`: pressure already visible now
- `escalation_triggers`: conditional reasons to pull deeper if they appear
- `review_cues`: signals explaining why a bounded shell can stay lightweight

This readout remains advisory only and still does not select runtime council depth automatically.

| Document | Relationship |
|----------|-------------|
| `TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md` | Defines the dossier shape that each mode must produce; lightweight produces minimal dossier, elevated produces extended dossier |
| `TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md` | Provides the task track classification that drives mode selection |
| `TONESOUL_PLAN_DELTA_CONTRACT.md` | Plan thrash detection is an escalation trigger for elevated mode |
| `TONESOUL_OBSERVABLE_SHELL_OPACITY_CONTRACT.md` | Elevated council should include explicit `opacity_declaration` in its dossier |
| `TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Deliberation mode should be recorded in compaction or checkpoint for later-agent visibility |
| `TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md` | Durable Identity lane modifications trigger mandatory elevated mode |
| `spec/council_spec.md` | Original perspective definitions; this contract does not change roles, only depth |
| `docs/COUNCIL_RUNTIME.md` | Facade design; mode selection would be a new responsibility of the facade |

---

## Canonical Handoff Line

Not every decision needs a tribunal. Not every decision can afford a rubber stamp. Match the deliberation depth to what is at stake: lightweight for bounded corrections and clear feature work, standard when ambiguity or coordination pressure appears, elevated for boundary-defining work. The system already has the mechanisms — this contract tells it when to use which one.
