# ToneSoul Tool-Permission / Hook Gap Scan (2026-04-02)

> Purpose: identify the next bounded outer-shell hook gap after `mutation_preflight` and `shared_edit_preflight`.
> Authority: implementation planning aid. Does not outrank runtime code, tests, or current launch posture.

---

## Current Covered Chain

ToneSoul already has bounded successor-facing hooks or guards for:

- shared code path overlap
- claim-before-shared-edit discipline
- honest checkpoint / compaction closeout
- bounded subject refresh
- human-gated `task.md` updates
- Aegis-locked canonical commit
- launch claim language posture

This means the next hook should not reopen those lanes.

---

## Gap Criteria

The next gap should be:

1. outside the hot-memory bucket
2. more outer-shell than inner-theory
3. concrete enough to become one bounded helper or preflight
4. useful for collaborator-beta reliability

---

## Candidate Gaps

### Candidate A: `publish_push.posture_preflight`

What it would cover:

- whether the repo is in a safe enough state to publish or push
- whether launch-claim posture and evidence posture are aligned with the intended action
- whether a dirty worktree / missing preflight / unresolved closeout should stop the action

Why it is attractive:

- clearly outer-shell
- directly relevant to collaborator-beta safety
- aligns with the Agent-OS lesson of explicit permission chains before side effects

Current state:

- pieces exist, but are scattered:
  - CI checks
  - launch claim posture
  - repo-state awareness
  - collaborator-beta preflight

Why it is still a gap:

- there is no one bounded successor-facing `publish/push` preflight surface today

### Candidate B: `task_board_update.scope_preflight`

What it would cover:

- whether a proposed `task.md` mutation belongs in short board vs `docs/plans/`
- whether the current edit is ratified-board maintenance or speculative drift

Why it is useful:

- directly protects the main board from agent drift

Why it is not first:

- `task.md` already has a strong scope guard and human-gated posture
- the immediate risk is lower than accidental publish / push / overclaim

### Candidate C: `external_tool_execution.permission_map`

What it would cover:

- MCP / plugin / external-tool action classes

Why it is deferred:

- too broad for one bounded next move
- would reopen transport / packaging architecture too early

---

## Selected Next Gap

`publish_push.posture_preflight`

---

## Why This One Wins

It is the cleanest next outer-shell reliability move because it ties together:

- repo-state awareness
- launch honesty posture
- collaborator-beta guardrails
- side-effect discipline before publishing

without reopening:

- hot-memory theory
- persona voice prompts
- plugin / MCP transport breadth

---

## Expected Shape

The next bounded runtime/helper should answer:

- `clear`
- `review_before_push`
- `blocked`

based on visible signals such as:

- dirty worktree
- current launch tier / blocked overclaims
- unresolved closeout state
- missing preflight or failed readiness checks

It should remain descriptive + guard-oriented, not a new sovereign permission system.
