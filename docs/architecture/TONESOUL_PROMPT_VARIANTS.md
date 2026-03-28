# ToneSoul Prompt Variants

> Purpose: provide ToneSoul-native prompt variants built on top of the Prompt Discipline Skeleton so later agents can choose a task-shaped prompt pattern instead of improvising from scratch.
> Status: active prompt-variant catalog and implementation companion.
> Last Updated: 2026-03-29

---

## Why This Exists

The skeleton answers:

`how should a good extraction or transfer prompt be structured?`

This document answers:

`which variant should I use for this specific job?`

The goal is not to create one universal prompt.
The goal is to choose a bounded variant that matches the task's memory lane, evidence posture, and compression target.

## Selection Rule

Choose a variant based on three questions:

1. What must survive: project state, meeting decisions, operator identity, or council dissent?
2. What surface will receive the result: report, checkpoint, compaction, dossier, or subject snapshot?
3. What compression level is acceptable: full, standard, bounded handoff, or emergency?

## Variant 1: Project Continuity Transfer

Use when a later agent needs to inherit:

- architecture understanding
- current progress
- known problems
- working norms
- active threads

Best receiving surfaces:

- full report
- compaction
- plan delta

### Recommended shape

- Goal function: make the receiver operable on first contact
- Priority:
  - `P0`: do not invent status, debt, or solved-ness
  - `P1`: preserve dates, reasons, and known blockers
  - `P2`: preserve cross-links and background narrative
- Stability bands:
  - durable: project purpose, canonical architecture
  - slow: conventions, stack choices, recurring debt
  - fast: active tasks, blockers, current branch posture
- Compression:
  - `Level 0/1` for long project brief
  - `Level 2` for compaction handoff

### ToneSoul alignment

- context continuity adoption
- plan-delta discipline
- compaction / packet-first handoff

## Variant 2: Conversation Or Meeting Distillation

Use when the reader needs:

- decisions
- action items
- unresolved questions
- deadlines
- bounded quotations

Best receiving surfaces:

- report
- checkpoint
- compaction

### Recommended shape

- Goal function: preserve what was decided and what still requires action
- Priority:
  - `P0`: do not invent decisions or assignees
  - `P1`: preserve direct quotes for key turning points
  - `P2`: preserve optional background context
- Hard constraints:
  - keep speaker attribution explicit
  - mark ambiguity as `[資料不足]` or `[需確認]`
  - filter chatter unless it changes future action
- Compression:
  - `Level 1` for normal summary
  - `Level 2` for action-oriented handoff

### ToneSoul alignment

- checkpoint / compaction
- plan-delta continuity
- receiver instructions for follow-up timing

## Variant 3: Operator Or User Snapshot

Use when a later session needs stable non-canonical continuity about:

- durable boundaries
- verified routines
- stable preferences
- working identity

Best receiving surfaces:

- subject snapshot
- subject refresh review

### Recommended shape

- Goal function: preserve durable working identity without inflating temporary state
- Priority:
  - `P0`: do not invent preferences or vows
  - `P1`: preserve evidence, dates, and change markers
  - `P2`: preserve optional cross-links and decay hints
- Stability bands:
  - durable identity
  - refreshable working identity
  - temporary carry-forward
- Hard rule:
  - temporary frustration, one-off tone, or short-lived tactical preference must not be promoted into durable identity

### ToneSoul alignment

- subject snapshot lanes
- subject refresh boundary contracts
- context continuity adoption map

## Variant 4: Council Dossier Replay

Use when a later agent must inherit:

- final verdict
- confidence posture
- coherence score
- dissent ratio
- minority report
- replay-safe evidence summary

Best receiving surfaces:

- dossier report
- compaction
- recent trace summary

### Recommended shape

- Goal function: preserve what the council concluded without flattening dissent
- Priority:
  - `P0`: do not lose minority positions
  - `P1`: preserve confidence posture and coherence
  - `P2`: preserve deeper background reasoning summaries
- Hard constraints:
  - if dissent exists, keep `minority_report`
  - never compress verdict to one flat approval word when replay safety matters
- Compression:
  - `Level 1` = full dossier
  - `Level 2` = bounded dossier summary in compaction
  - `Level 3` = minimal status line only in urgent cases

### ToneSoul alignment

- council dossier contract
- adaptive deliberation contract
- dossier carry surfaces in traces and compactions

## Variant 5: Session-End Resumability Handoff

Use when the current agent is finishing work and another agent may resume later.

Best receiving surfaces:

- compaction
- release-ready handoff

### Recommended shape

- Goal function: let the next agent resume without reopening the full session
- Priority:
  - `P0`: preserve next action, blockers, and unresolved risk honestly
  - `P1`: preserve path, affected surfaces, and bounded evidence
  - `P2`: preserve optional narrative context
- Required fields:
  - what changed
  - what remains
  - what must be checked next
  - whether human clarification is required
- Compression:
  - almost always `Level 2`

### ToneSoul alignment

- end-agent session bundle
- compaction `next_action`
- delta feed / observer cursor

## Compression Guidance

| Variant | Typical level | Why |
|---|---|---|
| Project continuity transfer | `Level 1` or `Level 2` | Usually too large for packet-only carry |
| Conversation distillation | `Level 1` | Reader still needs decisions + actions + open questions |
| Operator snapshot | `Level 1` | Identity should not be over-compressed casually |
| Council dossier replay | `Level 1/2` | Depends on whether dissent must survive fully |
| Session-end resumability handoff | `Level 2` | Fast later-agent recovery is the point |

## Anti-Patterns

Do not:

- use the operator-snapshot variant to carry temporary hot state
- use the meeting variant to canonize architecture truth
- use the project-transfer variant when only one next action matters
- use the council-dossier variant to smuggle hidden reasoning
- use any variant without explicit receiver instructions when the output is meant for another agent

## Selection Shortcut

| If the task is... | Start with... |
|---|---|
| bring a new agent up to project speed | Project Continuity Transfer |
| compress a long discussion into action | Conversation Or Meeting Distillation |
| preserve stable operator continuity | Operator Or User Snapshot |
| preserve verdict + dissent | Council Dossier Replay |
| hand work to the next session | Session-End Resumability Handoff |

## Current Rule

Pick the variant first.

Then tune:

- goal function
- evidence hardness
- compression level
- receiver instructions

That is safer than starting from a blank prompt every time.
