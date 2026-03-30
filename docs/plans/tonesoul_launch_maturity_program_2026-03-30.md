# ToneSoul Launch Maturity Program (2026-03-30)

> Purpose: turn the current "almost mature but not yet launch-safe" judgment into a bounded execution program.
> Scope: internal alpha -> collaborator beta -> public-facing launch readiness.
> Status: active planning baseline

## 1. Current Judgment

ToneSoul is no longer at the "conceptual prototype" stage.

It already has:
- bounded session-start / session-end rituals
- file-backed R-memory continuity with receiver guards
- subject snapshot and working-style continuity
- council dossier / dissent / descriptive confidence readouts
- authority/evidence/historical-surface honesty contracts
- a much cleaner public entry stack

But it is not yet honest to call it "maturely launch-ready" for broad public claims.

### Current Maturity Estimate

| Launch tier | Current estimate | Meaning |
|---|---:|---|
| Internal alpha | 80% | a small trusted group can use it and learn from it |
| Collaborator beta | 65% | careful external collaborators could test it with guidance |
| Public launch maturity | 60% | too many surfaces are still honest-but-thin rather than hardened |

### Current Launch-State Update

After Phase 726, the current operating decision is:
- `GO` for a bounded `collaborator beta`
- `NO-GO` for public-launch maturity claims

## 2. What "Mature Enough To Launch" Means

This program does not define "launch" as "the repo looks impressive."

It defines launch as:

1. Later agents can enter through the normal entry stack and safely continue work without hidden chat history.
2. The system can state what is tested, runtime-present, descriptive-only, and document-backed without overclaim.
3. Real coordination still works under repeated agent handoffs, not only in one bounded validation.
4. The operator story is clear:
   - what to run before using it
   - how to see current health
   - how to stop, rollback, or pause
5. Public-facing claims do not outrun evidence.

## 3. The Remaining Short Boards

The shortest boards are no longer "more contracts" or "more prompt theory."

They are:

### A. Live multi-agent validation is still thin

We have several bounded validations, but not yet a sustained wave that proves:
- repeated handoff still stays aligned
- later agents really obey `ack / apply / promote`
- style continuity survives more than one neat demo

### B. Redis/live coordination is not mature enough to promise

File-backed discipline is strong enough for current internal use.
Redis-backed real-time coordination exists conceptually and partially in code, but it is not yet hardened enough to advertise as a mature default.

### C. Council quality is still descriptive, not calibrated

ToneSoul can now say:
- how much agreement existed
- whether minority report existed
- whether suppression risk is visible

It still cannot honestly say:
- the council is X% accurate
- confidence means historical correctness

### D. Launch operations are not yet consolidated into one clean go/no-go surface

There are existing runbooks and historical release docs, but the current stack does not yet have one modern ToneSoul-native launch posture for:
- current health
- current blocked surfaces
- rollback path
- what is safe to promise publicly

### E. Workspace and data hygiene are improved, but not fully settled

The repo is much cleaner than before, but launch maturity also requires:
- fewer stale local residues
- no ambiguous script ghosts
- cleaner distinction between public artifacts and personal/runtime residue

## 4. Program Structure

This program is split into 5 workstreams.

| Workstream | Goal | Why it matters |
|---|---|---|
| WS1 Live Validation | prove continuity under repeated real handoffs | launch without this becomes a one-demo illusion |
| WS2 Coordination Backend | decide and harden the real shared-memory story | otherwise Redis/file-backed claims stay blurry |
| WS3 Launch Operations | unify readiness, health, rollback, and release posture | operators need one current story |
| WS4 Evidence And Council Honesty | keep public claims bounded by evidence | prevents "looks mature" from becoming false maturity |
| WS5 Hygiene And Packaging | remove ambiguous residue and ghost tooling | launch should not ride on messy local leftovers |

## 5. Phase Plan

### Phase 721: Launch Baseline Consolidation

**Goal**: capture the current maturity state, short boards, and launch tiers in one place.

Tasks:
- freeze the current maturity estimate and launch-tier vocabulary
- align it with existing evidence, continuity, and control-plane contracts
- define what counts as `internal alpha`, `collaborator beta`, and `public launch`

Success criteria:
- later agents stop speaking about launch maturity in vague prose
- a bounded maturity baseline exists and is discoverable

### Phase 722: Repeated Live Continuity Validation

**Goal**: prove that the current entry stack survives multiple real handoffs, not one bounded demo.

Tasks:
- run repeated fresh-agent validation waves
- vary claim state, compaction state, and council dossier state
- record where agents still misread receiver posture or working-style guidance

Success criteria:
- at least one repeated validation set exists with reproducible findings
- the next fixes come from live failure patterns, not theory

### Phase 723: Shared-Coordination Backend Decision

**Goal**: stop blurring "file-backed discipline" and "live Redis coordination."

Tasks:
- explicitly decide what is launch-default
- harden the chosen default
- classify the other backend as either experimental, optional, or deferred

Success criteria:
- later agents can answer "what coordination mode is ToneSoul actually using?" without ambiguity
- public claims about Redis/live surfaces become honest

Current note:
- `docs/plans/tonesoul_coordination_backend_decision_2026-03-30.md`

### Phase 724: Launch Operations Surface

**Goal**: expose one modern launch/readiness posture for current ToneSoul.

Tasks:
- define current go/no-go signals
- define rollback / freeze / operator-response path
- define minimum pre-launch checks and health surfaces

Success criteria:
- one current launch-operations document exists for this stack
- launch posture no longer depends on reading several historical runbooks

### Phase 725: Public-Claim Honesty Gate

**Goal**: prevent public launch language from outrunning evidence.

Current note:
- `docs/plans/tonesoul_public_claim_honesty_gate_2026-03-30.md`

Tasks:
- bind current launch claims to the evidence ladder
- identify which statements are safe at alpha/beta/public levels
- keep council quality and continuity effectiveness wording bounded

Success criteria:
- launch messaging can distinguish tested/runtime-present/descriptive/document-backed
- the most likely overclaims are pre-blocked

### Phase 726: Beta Go/No-Go Review

**Goal**: decide whether ToneSoul is ready for collaborator beta.

Current note:
- `docs/plans/tonesoul_collaborator_beta_go_nogo_review_2026-03-30.md`

Tasks:
- review outputs of WS1-WS5
- classify unresolved blockers as blocking/non-blocking
- decide:
  - continue internal alpha
  - open collaborator beta
  - hold public launch

Success criteria:
- the decision is evidence-based, not mood-based
- unresolved blockers remain explicit instead of being silently waived

## 6. Non-Goals

This program does not attempt to:
- calibrate council accuracy with historical outcomes
- turn Redis into a mandatory default if file-backed discipline is sufficient
- reopen every prompt family
- solve all philosophy/runtime gaps before launch
- pretend "beta-ready" means "fully mature"

## 7. Recommended Execution Order

Do not start with cosmetics.

Recommended order:
1. Phase 721
2. Phase 722
3. Phase 723
4. Phase 724
5. Phase 725
6. Phase 726

## 8. Compressed Thesis

ToneSoul is already beyond "interesting prototype."
It is not yet honest to call it mature public infrastructure.

The path forward is not more abstraction.
It is:
- repeated live validation
- bounded backend truth
- current launch operations
- evidence-bounded claims
- cleaner residue boundaries
