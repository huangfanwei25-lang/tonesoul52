# ToneSoul Launch Workstream Breakdown (2026-03-30)

> Purpose: break the launch maturity program into concrete workstreams with tasks, risks, and done conditions.
> Companion: `docs/plans/tonesoul_launch_maturity_program_2026-03-30.md`

## WS1: Live Validation

### Problem

Current continuity validation is real but still sparse.
We have bounded success, not enough repeated evidence.

### Tasks

1. Run fresh-agent entry validations under multiple states:
   - clean pass
   - claim conflict
   - stale compaction
   - contested council dossier
2. Record failure modes:
   - receiver posture misunderstanding
   - style continuity over-import
   - skipped `ack`
   - dossier over-trust
3. Turn repeated failures into bounded fixes, not new theory lanes.

### Deliverables

- validation notes or structured reports
- updated regression tests where the failure is machine-reproducible
- one summary of repeated failure patterns

### Exit Criteria

- at least one repeated validation wave exists
- later fixes are based on real misreads, not only expected misreads

### Anti-Patterns

- running one impressive demo and calling it solved
- treating style continuity as personality transfer
- expanding into swarm architecture redesign

---

## WS2: Coordination Backend Truth

### Problem

The repo can talk about file-backed and Redis-backed coordination, but launch maturity needs one honest default story.

### Tasks

1. Measure what currently works reliably in file-backed mode.
2. Measure what Redis mode actually supports today.
3. Classify Redis as:
   - launch-default
   - optional advanced mode
   - experimental/deferred
4. Tighten docs/readouts so later agents stop blurring the two.

### Deliverables

- backend decision note
- updated coordination wording in launch docs/readouts
- any small hardening patches needed for the chosen default

### Exit Criteria

- one coordination mode is clearly the launch-default
- the other mode is honestly labeled

### Anti-Patterns

- promising live shared-memory because the code path exists
- forcing Redis into the default story before repeated validation

---

## WS3: Launch Operations

### Problem

ToneSoul has many health/readiness surfaces, but not one current launch posture for this stack.

### Tasks

1. Consolidate:
   - health surfaces
   - readiness surfaces
   - rollback posture
   - freeze/unfreeze rules
2. Define the minimum launch check bundle.
3. Define what blocks collaborator beta.

### Deliverables

- a current launch operations/runbook document
- a current go/no-go checklist
- explicit rollback path

### Exit Criteria

- later operators know what to run before launch
- later operators know what to do if the launch posture goes red

### Anti-Patterns

- relying on old release notes as current truth
- scattering launch posture across multiple historical docs

---

## WS4: Evidence And Council Honesty

### Problem

The architecture can now describe itself richly, but launch claims can still outrun evidence if not bounded.

### Tasks

1. Bind public-facing claims to evidence levels.
2. Mark which claims are safe for:
   - internal alpha
   - collaborator beta
   - public launch
3. Keep council language descriptive unless calibration really exists.

### Deliverables

- launch-safe claim list
- blocked overclaim list
- explicit language for continuity/council/evidence posture

### Exit Criteria

- launch messaging can stay honest without rereading large evidence docs

### Anti-Patterns

- equating agreement with accuracy
- equating runtime presence with tested reliability
- equating documented intent with working mechanism

---

## WS5: Hygiene And Packaging

### Problem

Launch maturity also depends on not carrying ambiguous local residue.

### Tasks

1. Keep cleaning:
   - stale helper drafts
   - ghost scripts
   - local backup artifacts
2. Leave protected/private data alone.
3. Distinguish:
   - safe-to-commit utilities
   - local/operator residue
   - private memory data
   - OS-level leftovers

### Deliverables

- cleaner worktree
- fewer ambiguous untracked files
- explicit note of remaining ignored/private residues

### Exit Criteria

- remaining dirty paths are explainable and intentional

### Anti-Patterns

- deleting private or human-managed data
- hiding ambiguous residue by pretending it is canonical

## Compressed Rule

If a workstream cannot say:
- what problem it solves
- what artifact proves progress
- what counts as done

then it is not ready to be a launch workstream.
