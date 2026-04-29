# ToneSoul Beta Wave Day 1 Decision Record Template (2026-04-29)

> Use this template for `docs/status/beta_wave_<wave-date>_day1_decision_record.md` when the 14-day beta wave actually starts.
> Status: planning aid — empty template until Day 1 happens. After Day 1 fills it in, that filled-in copy becomes immutable record under `docs/status/`.
> Scope: Day 1 decisions only. Day 2 work tracked separately. Does not outrank `task.md`, latest `docs/status/*`, code, or tests.
> Source: closes the loop on `tonesoul_beta_wave_day1_2_execution_pack_2026-04-28.md` §6 Day 1 Checklist — every checklist item lands as a row in this record.

---

# ToneSoul Beta Wave Day 1 Decisions (`<wave-date>`)

> Filled by: `<operator name / agent id>`
> Filled at: `<YYYY-MM-DD HH:MM TZ>`
> Frozen at end of Day 1 — subsequent edits go in a follow-up record, not in-place mutation.

## 1. `strategy_mirror` posture for Day 3-5

> Resolves [Day 1-2 Pack Patch List](tonesoul_beta_wave_day1_2_pack_gap_patch_list_2026-04-29.md) §P1.

- **Choice**: `A` (scan_enabled / enforce_disabled — first-hand signature capture) **or** `B` (default-off + post-hoc replay)
- **Rationale**:
- **Prerequisite**:
  - if `A`: shadow flag follow-up PR landed at commit `<sha>` — verified by `<who>`
  - if `B`: catalog + detector frozen at commit `<sha>` from now until Day 9 evidence consolidation completes — freeze witnessed by `<who>`

If neither prerequisite is verified, do not start Day 3.

---

## 2. Participant candidates

> Resolves Patch List §P3 outreach + §P4 eligibility.

### Eligibility ratification

- non-creator definition (from execution pack §3.6): no commits in this repo AND has not read AGENTS.md → **ratified / adjusted to: `<change>`**
- semi-cold definition: aware of project but ≤ 1 hour prior exposure → **ratified / adjusted to: `<change>`**
- exclusion threshold: read DESIGN.md or any `architecture/*` deeply, OR co-worked with creator > 3 hours → **ratified / adjusted to: `<change>`**

### Candidate list

| Label | Type (`non-creator` / `semi-cold`) | Contact channel | Invited at | Status (`pending` / `accepted` / `declined`) | Notes |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

### Backup contacts (≥1 required)

| Label | Type | Contact channel | Notes |
|---|---|---|---|
| | | | |

### Acceptance count gate

- Confirmed acceptances by end of Day 2: **`<n>`**
- Required for Day 3 start: **≥3**
- If `<n>` < 3 by end of Day 2: extend Day 2 OR activate backup OR delay Day 3 (record decision in §7 below).

---

## 3. Prompt ratification

> Resolves Patch List §P2.

For each of Task Shape A/B/C, lock the verbatim string operators read aloud or paste during Day 3-5 sessions.

### Task A — Cold Truth Recovery

- **Final verbatim prompt (Chinese)**:
  > `<paste here>`
- **Final verbatim prompt (English fallback)**:
  > `<paste here>`
- **Diff from execution pack §3 draft**: `none` / `<describe>`

### Task B — Claim Honesty Rewrite

- **Final verbatim prompt (Chinese)**:
  > `<paste here>`
- **Final verbatim prompt (English fallback)**:
  > `<paste here>`
- **Diff from execution pack §3 draft**: `none` / `<describe>`

### Task C — Governance Friction Review

- **Final verbatim prompt (Chinese)**:
  > `<paste here>`
- **Final verbatim prompt (English fallback)**:
  > `<paste here>`
- **Diff from execution pack §3 draft**: `none` / `<describe>`

---

## 4. Eligibility deviation log

For any participant accepted who does not strictly match the §2 ratified criteria, record the deviation here. Each session run by such a participant carries this caveat in its session record.

| Participant label | Strict criterion failed | Why accepted anyway | Caveat applied to that session's evidence |
|---|---|---|---|
| | | | |

If this table is non-empty at end of Day 1, the affected session records (Day 3-5) must reference this row in their `task_outcome` justification.

---

## 5. Operator + schedule

- **Day 3-5 operator(s)**: `<name>`
- **Session schedule**:
  | Slot | Date / time | Participant label | Task shape | Operator |
  |---|---|---|---|---|
  | 1 | | | | |
  | 2 | | | | |
  | 3 | | | | |
  | 4 (optional) | | | | |
  | 5 (optional) | | | | |
- **Manual rescue policy** (per execution pack §7): `<repeat or modify>`

---

## 6. Artifact storage paths confirmed

- Day 3-5 session records will live at: `docs/status/beta_wave_<wave-date>_session_<label>.md` (per participant template)
- Day 3-5 operator notes will live at: `docs/status/beta_wave_<wave-date>_operator_<label>.md` (per operator template)
- Day 6 evidence summary will live at: `docs/status/beta_wave_<wave-date>_evidence_summary.md`
- Day 7-9 calibration note will live at: `docs/status/beta_wave_<wave-date>_strategy_mirror_calibration.md`
- Day 14 go/no-go note will live at: `docs/status/beta_wave_<wave-date>_go_nogo.md`

---

## 7. Open issues going into Day 2

> Anything Day 1 surfaced that needs Day 2 attention before Day 3 starts. Leave blank if none.

- 
- 
- 

---

## 8. Day 1 done-when checklist

Per execution pack §6, Day 1 is done when ALL of these check:

- [ ] §1 `strategy_mirror` posture decision documented with verified prerequisite
- [ ] §2 eligibility criteria ratified (or explicitly adjusted)
- [ ] §2 candidate list has at least 5 contacted + 1 backup
- [ ] §3 all three task shapes have verbatim prompts locked
- [ ] §6 artifact storage paths confirmed
- [ ] §7 open issues either resolved by end-of-Day-1 OR explicitly handed to Day 2

---

## 9. Honest Read

If Day 1 ends with any decision in §1-§3 still at "we'll figure it out later", treat that as a Day 2 work item, not a Day 3 deferral.

**Do not start Day 3 sessions with any §1-§3 decision still open.**

The cost of delaying Day 3 by one day to firm up Day 1 decisions is much smaller than the cost of running Day 3-5 sessions on undocumented assumptions and discovering on Day 6 that the evidence is not comparable.
