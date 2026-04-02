# ToneSoul Task-Board Parking Preflight (2026-04-02)

> Purpose: keep outside ideas, speculative follow-ups, and ecosystem borrowings from competing with the ratified short board in `task.md`.
> Authority: implementation planning aid. Does not outrank `task.md`, runtime code, tests, or human ratification.

---

## Problem

ToneSoul already has a `task.md` scope guard, but later agents can still make one common mistake:

- discover a useful idea
- treat it as obviously important
- land it directly in `task.md`

That creates short-board drift and makes active execution look broader than it really is.

---

## Bounded Goal

Add one successor-facing preflight that answers:

- `task_md_allowed`
- `docs_plans_first`
- `parking_clear`
- `human_review`

without inventing a new planning authority system.

---

## Input Signals

The preflight should only rely on already-visible surfaces:

- `readiness.status`
- `canonical_center.current_short_board`
- `task_track_hint.suggested_track`
- explicit `proposal_kind`
- explicit `target_path`

---

## Proposal Kinds

### Allowed Into `task.md`

- `ratified_followthrough`
- `execution_status`
- `accepted_short_board_rotation`

### Default To `docs/plans/`

- `external_idea`
- `speculative_roadmap`
- `theory_import`
- `ecosystem_borrowing`
- `unratified_program`
- `unspecified`

---

## Runtime Shape

1. session-start should expose a default `task_board_preflight`
   - default assumption: a newly discovered idea still belongs in `docs/plans/`
2. a dedicated script should let successors check a specific candidate:
   - `python scripts/run_task_board_preflight.py --agent <id> --proposal-kind <kind> --target-path <path>`
3. mutation preflight should point its next bounded follow-up at this hook once publish/push posture is already real

---

## Non-Goals

- no new sovereign planning system
- no automatic rewrite of `task.md`
- no promotion of `docs/plans/` material into the short board
- no reopening design-center or hot-memory theory

---

## Success Criteria

- later agents stop treating `task.md` as the default landing zone for every useful idea
- `docs/plans/` becomes the boring default parking lane for unratified follow-ups
- the ratified short board remains visibly narrower than the idea backlog
