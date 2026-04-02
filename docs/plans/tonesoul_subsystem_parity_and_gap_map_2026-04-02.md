# ToneSoul Subsystem Parity And Gap Map (2026-04-02)

> Purpose: give successors one honest map of which subsystems are already usable, which are still partial, and which gaps matter most next.
> Source posture: ToneSoul-native gap map inspired by parity-style engineering maps such as `claw-code/PARITY.md`.
> Authority: planning and reality-alignment aid. Does not outrank runtime code, tests, or canonical contracts.

---

## Status Labels

- `baseline`
  - bounded, discoverable, and regression-backed enough for normal continuation
- `beta_usable`
  - usable in guided collaborator beta, but still not a public-maturity claim
- `partial`
  - real and useful, but still missing important readout, validation, or boundary closure
- `deferred`
  - real future value, not current priority

## Current Map

| Subsystem | Status | Strongest Current Truth | Main Gap | Next Bounded Move | Overclaim To Avoid |
|---|---|---|---|---|---|
| AI entry stack | `beta_usable` | `AI_ONBOARDING -> AI_QUICKSTART -> DESIGN -> session-start` exists | some entry docs still carry display-noise and uneven depth | keep entry surfaces aligned and successor-focused | "any AI can cold-start perfectly" |
| Session-start bundle | `baseline` | readiness, import posture, task/deliberation hints, working-style playbook are live | more successor-specific prioritization still possible | keep first-hop bundle tight and stable | "session-start alone captures the whole system" |
| Observer window | `baseline` | stable / contested / stale + delta summary exists and is tested | anchor selection can still get clearer | low-drift anchor phase 2 | "observer window is canonical truth" |
| Receiver posture | `baseline` | `ack / apply / promote` ladder is visible across packet/session-start/diagnose | still scattered in too many docs for cold readers | fold more of it into successor-facing program docs | "every agent will read the ladder the same way" |
| Packet / hot-state surfaces | `beta_usable` | freshness, import posture, evidence posture, realism note, launch claim posture exist | too many adjacent readouts for cold successors | strengthen anchor-center ordering | "packet equals complete memory" |
| Compaction / checkpoint handoff | `beta_usable` | bounded resumability and promotion hazards exist | closeout still too capable of looking smoother than reality | add stronger anti-fake-completion grammar | "compaction is a full task truth" |
| Subject snapshot / working style | `partial` | bounded working-style continuity and import limits exist | successors still confuse style with identity or authority | strengthen hot-memory ladder language | "shared style means shared selfhood" |
| Council realism / dossier | `partial` | descriptive-only, dissent, suppression, decomposition are visible | still no outcome calibration | keep realism explicit and resist overclaim | "council confidence predicts correctness" |
| Evidence posture | `beta_usable` | tested / runtime_present / descriptive_only / document_backed readout exists | needs wider adoption in operator storytelling | keep evidence readout visible in successor docs | "all current claims are equally proven" |
| Collaborator-beta launch posture | `beta_usable` | guided beta is explicit, public launch is blocked | external deployment and broader live validation still thin | continue bounded beta validation | "public maturity is ready" |
| Task-board governance | `partial` | `task.md` scope guard exists, short-board overwrite is blocked | new external ideas still need a clearer parking discipline | keep strategy in `docs/plans/` until ratified | "task.md is the place for all future ideas" |
| Hooks / mutation preflight | `partial` | some guards exist via tests, honesty gates, and scripts | no one current map of mutation hook chain | build write/preflight hook map | "guard rails are already fully explicit" |
| External transport / MCP / plugins | `deferred` | real future value identified | not needed for current collaborator-beta truth | keep parked under external roadmap | "ToneSoul already has a mature transport shell" |
| Public launch maturity | `deferred` | collaborator beta is honest current tier | proof base still insufficient | do not widen claims | "ToneSoul is launch-mature" |

## Most Important Gaps

### 1. Successor Coherence

The stack is richer than before, but still too dependent on the successor understanding ToneSoul's vocabulary and layering model.

### 2. Hot-Memory Ladder Legibility

Continuity surfaces exist, but the ladder from canonical anchors to residue is still too implicit.

### 3. Anti-Fake-Completion

Closeout and handoff are safer than before, but not yet strict enough about unresolved blockers and underdetermined states.

### 4. Hook And Mutation Map

The system has many write/read guards, but they are not yet packaged as one explicit mutation-preflight chain.

## What Is Already Good Enough To Stop Over-Optimizing

These lanes are no longer the shortest board:

- launch wording
- README entry wall cleanup
- basic working-style continuity readout
- observer window day-1 baseline
- council descriptive-vs-calibrated readout
- CI false-positive cleanup

## Recommended Reading Order For A Successor

1. `DESIGN.md`
2. `docs/status/codex_handoff_2026-04-02.md`
3. `docs/plans/tonesoul_successor_collaboration_and_hot_memory_program_2026-04-02.md`
4. this parity map
5. only then deeper continuity/council contracts as needed

## Compressed Thesis

ToneSoul is no longer missing core structure.
It is now in the phase where successor coherence, hot-memory layering, and honest subsystem maturity matter more than new theory.

## Runtime Distillation Note

This map now has a bounded successor-facing runtime distillation:

- `session-start bundle -> subsystem_parity`
- `observer window -> subsystem_parity`

That readout is intentionally smaller than this planning map.
It exists so later agents can see maturity posture without opening long plan files first.
