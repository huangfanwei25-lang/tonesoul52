# ToneSoul Working-Style Wave-2 Selection (2026-04-02)

> Purpose: choose one explicit post-successor working-style consumer so bucket rotation resumes without reopening voice-heavy or tightly coupled families.
> Authority: implementation planning aid. Does not outrank runtime code, tests, or current task short-board decisions.

---

## Why This Selection Exists

The successor/hot-memory bucket reached baseline through:

- `session-start` playbook and validation
- `operator_guidance` integration
- `diagnose` readout
- `shared_edit_preflight` hook

At that point, ToneSoul needed one explicit next bucket instead of drifting back into:

- more hot-memory theory
- already-finished prompt-adoption work
- high-risk persona/navigation prompts

This selection therefore answers one narrow question:

`what is the next low-risk surface that should consume working-style continuity?`

---

## Selection Rules

The chosen wave must be:

1. generic or coordination-facing
2. already close to an existing runtime/readout path
3. low enough risk that bounded adoption is more likely to help than to distort behavior
4. not part of a voice-heavy or tightly chained family

The deferred wave should be:

1. plausible later
2. obviously riskier right now
3. named explicitly so later agents do not reopen it by accident

---

## Candidate Scan

### Candidate A: `shared_edit_preflight`

Files:

- `tonesoul/shared_edit_preflight.py`
- `scripts/run_shared_edit_preflight.py`

Why it fits:

- already sits between `readiness`, `claims`, and mutation decisions
- coordination-facing, not voice-facing
- used before shared edits where style drift is costly
- can consume only the first one or two working-style habits without becoming identity mythology

Main risk:

- turning a bounded overlap hook into a second policy engine

Decision:

- `implementation_wave`

---

### Candidate B: `tonesoul/scribe/narrative_builder.py`

Why it was considered:

- low risk
- prompt-adjacent
- reflective output could benefit from bounded style reminders

Why it was not chosen now:

- it is a template/formatter, not a high-leverage coordination consumer
- it would not reduce current successor or collaboration friction as much as `shared_edit_preflight`

Decision:

- `not_now`

---

### Candidate C: `tonesoul/tonebridge/personas.py::build_hardened_prompt()`

Why it was considered:

- high-frequency surface
- could eventually benefit from bounded priority reminders

Why it must wait:

- persona/voice coupling is still high
- file still carries display/encoding noise from older text
- a rushed change here would risk flattening value-bearing voice instead of improving coordination

Decision:

- `deferred_wave`

---

## Chosen Implementation Wave

### Wave 2A: Shared-Edit Working-Style Consumer

Bounded scope:

- let `shared_edit_preflight` reuse the visible `working_style_playbook`
- expose only the first one or two actionable habits
- keep the playbook advisory
- keep the non-promotion rule visible

What this wave must not do:

- invent new permissions
- rewrite claim/readiness logic
- promote working-style into vows, durable identity, or canonical planning truth

Expected gain:

- a collaborator about to touch shared paths sees not only overlap status, but also the local working habits that reduce avoidable drift

---

## Deferred Wave

### Wave 2B: Persona Hardening Boundary Review

Deferred target:

- `tonesoul/tonebridge/personas.py::build_hardened_prompt()`

Why deferred:

- belongs to `persona_and_voice`
- needs a separate boundary review before adoption
- should not be reopened under the label of "low-risk working-style continuity"
- reality-checked on 2026-04-02: still deferred because no explicit working-style playbook input path exists yet, and the ripple radius reaches `build_navigation_prompt()`

---

## Operational Line

The selected implementation wave is:

`Phase 750: Working-Style Wave-2 Shared-Edit Consumer`

The explicit deferred wave is:

`persona hardening / navigation family review`

This keeps bucket rotation clean:

- do one coordination-facing consumer now
- leave persona/voice work parked until a dedicated review says otherwise
