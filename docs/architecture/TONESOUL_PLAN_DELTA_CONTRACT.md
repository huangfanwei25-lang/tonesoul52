# ToneSoul Plan Delta Contract

> Status: operational discipline contract
> Purpose: define when later agents should keep a plan, append a bounded delta, fork a new phase, or stop and ask a human — instead of silently rewriting task.md or thrashing between plan revisions
> Last Updated: 2026-03-28
> Produced By: Claude Opus
> Depends On:
>   - docs/architecture/TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md (track classification)
>   - docs/architecture/TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md (shared surface semantics)
>   - task.md (the canonical progress record this contract governs)
> Scope: 4 plan operations, 5 silent override protection rules, task.md boundary definition

## How To Use This Document

If you are an AI agent and your task's scope has changed, or you need to decide what belongs in `task.md` versus a compaction:

1. Check the **Plan Delta Decision Matrix** to determine whether to keep, append, fork, or stop
2. Check the **Content Boundary Table** to know where each type of content belongs
3. Follow the **Silent Override Protection Rules** before modifying any existing Phase
4. If in doubt, choose the less destructive option: append rather than rewrite, fork rather than overwrite, stop rather than silently change success criteria

## Why This Document Exists

ToneSoul's `task.md` is the canonical progress record that all agents share. Without rules for how to modify it, three failure modes emerge:

1. **Plan thrash**: every scope change rewrites the entire plan. Success criteria shift mid-flight. Later agents cannot tell what the original goal was.

2. **Silent override**: an agent modifies another agent's Phase success criteria without recording the change. The original contract between the human and the first agent is lost.

3. **Content leakage**: temporary session state (hypotheses, intermediate progress, carry-forward items) gets written into `task.md` where it persists indefinitely, or canonical progress gets written only into compactions where it decays in 7 days.

## Compressed Thesis

`task.md` is append-only progress, not a whiteboard. If the scope fits the existing Phase, mark checkboxes. If it extends the Phase, append objectives. If it changes direction, fork a new Phase. If the success criteria themselves need to change, stop and ask the human. Never silently rewrite what another agent committed to deliver.

---

## Plan Delta Decision Matrix

### keep plan

Do not modify `task.md`. The current Phase covers the work.

**When to use**:
- Scope is within the natural extension of the original Phase's success criteria
- Progress can be recorded by marking existing `- [ ]` objectives as `- [x]`
- A bug was found but the bug is within the original Phase's stated scope
- Work is progressing normally and no new objectives are needed

**Example**: Phase 657 says "add bounded subject-refresh summary". You implement the summary exactly as described. Mark objectives `[x]`. Done.

### append delta

Add new `- [ ]` objectives to the existing Phase without changing the success criteria.

**When to use**:
- Scope extends but direction stays the same
- The new objectives can be covered by the existing success criteria
- The number of added objectives does not exceed the number of original objectives

**Constraints**:
- Do not modify the `**Success Criteria**` line
- Add new objectives below the existing ones, clearly separated
- If appending more objectives than the Phase originally had, consider fork instead

**Example**: Phase 654 says "session start bundle". You discover it also needs a `--dry-run` flag for testing. Append `- [ ] add --dry-run preview mode` below the existing objectives.

### fork new phase

Create a new Phase with a new number, title, and success criteria.

**When to use**:
- Work direction has changed enough that the original Phase's success criteria cannot cover it
- The original Phase's scope would need to double or triple to include the new work
- You discover a prerequisite that the original Phase did not account for
- The scope has already been delta-appended once and needs to expand again (two deltas = time to fork)

**Constraints**:
- The original Phase stays unchanged — do not modify its objectives or success criteria
- The new Phase goes above the original (newest-first convention in `task.md`)
- The new Phase header should reference its origin: `(forked from Phase NNN)` or `(extends Phase NNN)`
- The new Phase gets its own success criteria independent of the original

**Example**: Phase 654 says "session start bundle". You discover the store module needs reorganization first. Fork to Phase 660: "Store module cleanup (prerequisite for Phase 654)".

### stop and ask human

Do not modify `task.md`. Leave the question in a compaction and wait.

**When to use**:
- Success criteria themselves need to be redefined (the human changed their mind, or the original criteria are impossible)
- A previous Phase's success criteria contain an error that would cascade
- The task requires modifying protected files without explicit authorization
- The task requires modifying AXIOMS.json or canonical governance posture
- The scope has forked twice or more already (plan thrash signal — two forks from the same origin suggest the original direction was wrong)
- Risk posture is `"critical"` and the task is not directly fixing the critical condition

**How to stop**:
- Write a compaction with `next_action: "STOP: <specific question for human>"`
- Include the specific decision you need from the human
- Do not leave a vague "needs discussion" — name the exact fork in the road

---

## Content Boundary Table

| Content Type | Where It Belongs | Why |
|---|---|---|
| Phase objectives `- [ ]` / `- [x]` | `task.md` | Canonical progress record visible to all agents |
| Phase success criteria | `task.md` | Defines the completion contract between human and agent |
| Long Program goals and guardrails | `task.md` | Defines strategic direction; only modified on human request |
| Validation commands and results | `task.md` | Proves the Phase was completed correctly |
| Mid-session progress and next steps | compaction `next_action` | Non-canonical handoff; decays in 7 days |
| Unfinished pending paths | compaction `pending_paths` or checkpoint `pending_paths` | Resumability context, not canonical progress |
| Cross-session carry-forward items | compaction `carry_forward` | Non-canonical; decays after TTL |
| Temporary hypotheses and stances | perspective | Non-canonical; TTL 2 hours |
| Stable work habits and preferences | subject_snapshot | Non-canonical but durable (30 days) |
| Actual governance state changes | `commit()` to canonical traces | Canonical, append-only, Aegis-protected |
| Plan operation record (keep/append/fork/stop) | compaction `carry_forward` | Advisory metadata for later agents to detect plan thrash |

### What Must Not Go In task.md

- Intermediate exploration notes ("I looked at these files and found...")
- Session-level debugging context ("the error was caused by...")
- Temporary hypotheses ("I think the issue might be...")
- Personal preferences or working style notes
- Raw tool output or long code snippets

These belong in compaction, checkpoint, or perspective — surfaces that decay naturally.

### What Must Not Go Only In Compaction

- Whether a Phase is complete or not (this must be in `task.md` via `[x]`)
- New strategic direction (this must be a new Phase in `task.md` or a human conversation)
- Changes to success criteria (this must go through the "stop and ask human" path)

---

## Silent Override Protection Rules

These five rules protect `task.md` from unintentional drift.

### Rule 1: Do not modify another agent's success criteria

If a Phase was not started by you (different `agent` in the originating compaction or commit), you may not modify its `**Success Criteria**` line. You may append delta objectives below the existing ones, but the success criteria are a contract between the original agent and the human.

If you believe the success criteria are wrong, use the "stop and ask human" path.

### Rule 2: Do not mark objectives complete prematurely

A `- [ ]` objective may only be marked `- [x]` when:
- The objective's actual deliverable exists (file created, code written, test passing)
- The deliverable satisfies the Phase's success criteria
- Any validation commands listed in the Phase pass

Marking `[x]` before the deliverable exists is falsification, not optimism.

### Rule 3: Do not uncheck or delete completed objectives

Any `- [x]` objective must not be reverted to `- [ ]` or deleted unless the human explicitly requests it. If you discover a regression in a completed objective:
- Create a new Phase to fix the regression
- Reference the original Phase: "Fix regression in Phase NNN objective M"
- Do not uncheck the original — it was completed at the time; the regression is a new event

### Rule 4: Do not rewrite Long Program direction

The Long Program section at the top of `task.md` (`Program Goal`, `Execution Guardrails`, Phase roadmap) may only be modified when the human explicitly requests a direction change. An agent may not unilaterally redefine the program's strategic direction based on scope discovery.

If you believe the Long Program direction is wrong, use the "stop and ask human" path.

### Rule 5: Do not delete historical Phases

`task.md` is an append-only progress record. Completed Phases are historical evidence, not clutter. If `task.md` becomes too long:
- The human may run `scripts/split_task_archive.py` to archive old Phases to `docs/chronicles/`
- Agents may suggest archiving but must not execute it unilaterally
- Archived Phases remain available in the chronicles; they are not deleted from the repo

---

## Phase Lifecycle

A Phase in `task.md` progresses through these observable states:

| State | How To Recognize | What Agents May Do |
|---|---|---|
| **planned** | `## Phase NNN:` header exists, all objectives are `- [ ]` | Begin work if readiness = `pass` per the Track & Readiness Contract |
| **in_progress** | Some objectives are `- [x]`, some are `- [ ]` | Continue work, append delta objectives if needed |
| **completed** | All objectives are `- [x]` | Do not modify; create a new Phase if follow-up work is needed |
| **forked** | Header contains `(forked from Phase NNN)` | Treat as a new independent Phase with its own lifecycle |

There is no "cancelled" or "abandoned" state. If a Phase is no longer relevant:
- Leave it as-is with unchecked objectives
- Note in a compaction why work was stopped
- The human may archive it later

---

## Plan Thrash Detection

Plan thrash is when scope changes faster than work progresses. Signs:

- Two or more forks from the same origin Phase within one session
- Success criteria change requests in consecutive compactions
- `next_action: "STOP"` appears in two consecutive compactions from the same agent
- More delta-appended objectives than original objectives across multiple Phases

When plan thrash is detected:
1. Stop adding more Phases or deltas
2. Write a compaction with `carry_forward: ["plan thrash detected: <description>"]`
3. Ask the human to confirm the current direction before continuing
4. Do not attempt to "fix" the thrash by writing a meta-plan — that is more thrash

---

## Relationship To Other Documents

| Document | Relationship |
|----------|-------------|
| `TONESOUL_TASK_TRACK_AND_READINESS_CONTRACT.md` | Prerequisite — track classification determines which plan operations are appropriate (quick_change rarely needs fork; system_track often does) |
| `TONESOUL_SHARED_R_MEMORY_OPERATIONS_CONTRACT.md` | Defines the shared surfaces (compaction, checkpoint, perspective) that this contract routes non-task.md content to |
| `TONESOUL_SUBJECT_REFRESH_BOUNDARY_CONTRACT.md` | Subject snapshot changes follow this contract's delta rules: schema field additions require fork, not delta |
| `task.md` | The canonical object this contract governs |
| `scripts/split_task_archive.py` | The archiving tool referenced in Rule 5 |

---

## Canonical Handoff Line

When scope changes, do not reach for the delete key. Append if it fits, fork if it does not, and stop if the destination itself is uncertain. `task.md` remembers what was promised; your compaction remembers what happened along the way.
