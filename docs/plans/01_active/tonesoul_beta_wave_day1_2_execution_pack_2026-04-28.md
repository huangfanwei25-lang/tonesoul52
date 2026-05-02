# ToneSoul Beta Wave Day 1-2 Execution Pack (2026-04-28)

> Purpose: turn the 14-day beta wave into an immediately runnable Day 1-2 setup pack: fixed task shapes, evidence schema, artifact list, and operator steps.
> Status: execution aid only. This file does not outrank [task.md](../../task.md), latest `docs/status/*`, code, or tests.
> Scope: Day 1-2 only. This pack does not cover later calibration, enforcement, or public-claim decisions.

---

## 1. Current Truth Anchors

Read these before starting the Day 1-2 setup:

1. [task.md](../../task.md)
2. [README.md](../../README.md)
3. [tonesoul_beta_wave_14day_2026-04-28.md](tonesoul_beta_wave_14day_2026-04-28.md)
4. latest collaborator-beta preflight under `docs/status/collaborator_beta_preflight_latest.{md,json}`
5. latest go/no-go review under `docs/status/phase726_go_nogo_*.md`
6. latest current-truth handoff under `docs/status/codex_handoff_*.md`

Do not let side experiments or old launch packs silently replace these.

---

## 2. Day 1-2 Goal

By the end of Day 2, the repo should have:

- 3 fixed beta task shapes
- 1 shared evidence schema
- 1 participant note template
- 1 operator note template
- 1 clear artifact map for the coming usage wave

This pack is successful if the next agent can start Day 3 usage collection without inventing new task definitions.

---

## 3. Fixed Task Shapes

Use these as the default Day 3-5 collaborator-beta tasks.

## Task Shape A: Cold Truth Recovery

### Prompt Shape

Ask the participant to use ToneSoul to recover current project state and the next safe move from first-hop surfaces.

### Operator-Reads-Verbatim Prompt

Chinese:

> 請只用這個 repo 的一級入口，找出它目前的 launch 狀態與下一步可做的事。15 分鐘後告訴我你看了哪些檔、得出什麼結論。

English fallback:

> Using only the repo's first-hop entry surfaces, figure out the current launch status and the next safe move. After 15 minutes, tell me which files you used and what conclusion you reached.

### What It Exercises

- entry-surface routing
- current-truth recovery
- bounded status reasoning
- whether ToneSoul feels like a collaborator instead of a theory maze

### Success Markers

- participant can identify current posture correctly
- participant can name one next move without broad repo archaeology
- participant reports low confusion about where authority lives

### Failure Markers

- participant gets lost across docs or stale surfaces
- system gives too much theory and too little actionable routing
- participant cannot tell what is current truth

## Task Shape B: Claim Honesty Rewrite

### Prompt Shape

Give ToneSoul a short product or repo claim and ask it to make the wording evidence-bounded and launch-safe.

### Operator-Reads-Verbatim Prompt

Chinese:

> 我會給你一句關於 ToneSoul 的說法。請把它改寫成 evidence-bounded、launch-safe 的版本，並告訴我你刪掉或保留了什麼。

English fallback:

> I will give you one claim about ToneSoul. Rewrite it into an evidence-bounded, launch-safe version, and tell me what you removed or kept.

### What It Exercises

- evidence-ladder discipline
- governance friction that should feel protective
- distinction between test-backed, runtime-present, doc-backed, and philosophical claims

### Success Markers

- output becomes more precise without becoming unusably defensive
- participant can tell what the system is willing to claim and why
- rewrite improves trust rather than sounding evasive

### Failure Markers

- output stays overclaiming
- output overcorrects into vague emptiness
- participant feels the system is obstructive rather than clarifying

## Task Shape C: Governance Friction Review

### Prompt Shape

Give ToneSoul a short risky draft and ask it whether it should pass, refine, or block, and why.

### Operator-Reads-Verbatim Prompt

Chinese:

> 我會給你一段可能有風險的草稿。請用 ToneSoul 判斷它應該 approve、refine、還是 block，並用可執行的理由解釋。

English fallback:

> I will give you a potentially risky draft. Use ToneSoul to decide whether it should approve, refine, or block it, and explain the reason in an actionable way.

### What It Exercises

- council posture
- boundary honesty
- whether safety/governance is legible to a real user
- whether blocking or refining feels justified

### Success Markers

- verdict feels explainable
- participant can distinguish justified friction from random obstruction
- requested rewrite/refine path is concrete

### Failure Markers

- participant cannot tell why friction happened
- refusal/block feels arbitrary
- explanation is too abstract to act on

## 3.5 `strategy_mirror` Capture Posture Decision

This is the one Day 1 architecture coordination decision that must be made before Day 3.

### Option A: `scan=True / enforce=False` (preferred)

- prerequisite: land the shadow-flag follow-up (`strategy_mirror_scan_enabled`, `strategy_mirror_enforce_enabled`, with `enforce => scan`)
- operator env for runtime sessions:
  - `TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED=1`
  - `TONESOUL_GSE_STRATEGY_MIRROR_ENFORCE_ENABLED=0`
- session-time result:
  - signatures are attached
  - no APPROVE-to-BLOCK downgrade happens
  - Day 7-9 calibration uses first-hand captured `StrategySignature`

### Option B: default-off + post-hoc replay

- no follow-up PR required before Day 3
- session-time result:
  - no `StrategySignature` is attached during Day 3-5
  - Day 7-9 must replay the raw texts through the detector afterward
- if this option is chosen, the following files must freeze from Day 3 start until Day 9 evidence consolidation finishes:
  - `tonesoul/gse/strategy_mirror/catalog/period_1_foundation.json`
  - `tonesoul/gse/strategy_mirror/structural_patterns.py`
  - `tonesoul/gse/strategy_mirror/detector.py`
- record the exact starting commit SHA in the Day 1 notes so the replay basis is explicit

This pack does not choose A or B on its own. Day 1 must choose and record one.

## 3.6 Participant Eligibility

Use these as the default evidence-integrity definitions unless Day 1 explicitly ratifies a variation:

- `non-creator`
  - no commits in this repo
  - has not read `AGENTS.md`
- `semi-cold`
  - aware the project exists, but no more than 1 hour of prior exposure
  - a skim of `README.md` counts as exposure
  - a deep read of `DESIGN.md` or any `docs/architecture/*` file disqualifies
- excluded as too warm
  - has read `DESIGN.md` or any architecture document deeply
  - has co-worked with the creator on this project for more than 3 hours
  - already knows where current truth and launch posture live without needing first-hop routing

If the wave uses anyone outside these defaults, record it as an evidence-integrity caveat.

---

## 4. Evidence Schema

Every beta session should capture the same fields.

| Field | Meaning | Required |
|---|---|---|
| `session_id` | stable local identifier | yes |
| `task_shape` | `A / B / C` | yes |
| `participant_type` | non-creator / semi-cold / other bounded label | yes |
| `surface_used` | `apps/web`, CLI, docs, mixed | yes |
| `system_verdict_path` | `approve / refine / block / n/a` | yes |
| `task_outcome` | completed / partial / failed / no-count | yes |
| `trust_before` | participant-reported trust before task, `1-5` | yes |
| `trust_after` | participant-reported trust after task, `1-5` | yes |
| `trust_note` | participant's explanation of why trust changed or stayed flat | yes |
| `confusion_points` | short bullets only | yes |
| `manual_rescue_required` | yes / no | yes |
| `governance_friction` | justified / unclear / over-strict / under-strict | yes |
| `claim_issue` | `overclaim / underclaim / none` | yes |
| `detector_issue` | `false_positive / false_negative / none` | yes |
| `next_fix_candidate` | one smallest meaningful next step | yes |

Do not invent extra fields during the first wave unless a repeated issue proves the schema is missing something load-bearing.

`trust_before` and `trust_after` are not statistically meaningful at `N=3-5`.
They are an attention anchor: asking the participant for a number forces them to attend to their own trust state.
The primary signal is still `trust_note`; the numbers are secondary context.

---

## 5. Artifact Map

Day 1-2 should prepare these files or file paths:

### Planning Files

- this pack
- [docs/plans/tonesoul_beta_wave_participant_note_template_2026-04-28.md](tonesoul_beta_wave_participant_note_template_2026-04-28.md)
- [docs/plans/tonesoul_beta_wave_operator_note_template_2026-04-28.md](tonesoul_beta_wave_operator_note_template_2026-04-28.md)

### Day 3-5 Runtime Outputs

Create these under `docs/status/` when the real sessions begin:

- `beta_wave_2026-04-28_session_<label>.md`
- `beta_wave_2026-04-28_operator_<label>.md`
- `beta_wave_2026-04-28_evidence_summary.md`

Keep labels public-safe. Do not publish raw personal identifiers.

---

## 6. Day 1 Checklist

1. Confirm the 14-day wave still aligns with current `task.md`.
2. Confirm the latest preflight / go-no-go / handoff are the active truth anchors.
3. Ratify or adjust the 3 default task shapes above.
4. Lock the verbatim operator prompt for each task shape.
5. Decide `strategy_mirror` posture for Day 3-5:
   - `A`: `scan=True / enforce=False` after the shadow-flag follow-up lands
   - `B`: default-off + post-hoc replay, with Day 3-9 catalog/detector freeze
   - record the choice and consequence in the Day 1 notes
6. Ratify the evidence schema without adding vanity metrics.
7. Confirm where Day 3 session notes will be stored.
8. Ratify or adjust the `non-creator` / `semi-cold` eligibility definition in §3.6; record any deviation as an evidence-integrity caveat.
9. List at least 5 candidate contacts plus 1 backup.
10. Decide outreach channel (`email / IM / community post`) and draft a 5-line invitation naming:
    - expected time (~30 min)
    - what feedback is wanted
    - what is not being measured

### Day 1 Done When

- no task shape is still ambiguous
- all three task shapes have a verbatim operator prompt locked in
- `strategy_mirror` posture for Day 3-5 is explicitly chosen
- no evidence field is still hand-wavey
- no one needs to improvise where notes will live

---

## 7. Day 2 Checklist

1. Prepare one short beta operator brief:
   - what to test
   - what not to test
   - what counts as manual rescue
2. Prepare one participant-facing brief:
   - task goal
   - expected time
   - what kind of feedback is useful
3. Dry-run one synthetic session internally using the templates only.
4. Verify that the dry-run can be summarized using the schema without adding fields.
5. Lock the artifact naming convention for Day 3-5.
6. Send invitations by end of Day 2.
7. Confirm at least 3 acceptances before Day 3 starts; if fewer, extend Day 2 or activate backup contacts.

### Day 2 Done When

- one operator can run a session using only the pack and templates
- one participant brief exists and is short enough to be usable
- outreach has been sent
- at least 3 likely participants are actually lined up for Day 3-5
- the schema survives one dry-run without modification

---

## 8. Stop Conditions

Pause the Day 1-2 setup if any of these start happening:

- task shape discussions drift into new product-definition work
- someone starts expanding `strategy_mirror` catalog before real session data exists
- `Under The Island` or other side experiments start competing for time
- the schema grows because it feels elegant, not because it captures a real observation
- Day 1-2 turns into launch wording debate instead of beta setup

---

## 9. Honest Read

This pack does not prove that ToneSoul is ready for a broader beta.

It only tries to ensure that the next 3 to 5 real sessions generate evidence that is:

- bounded
- comparable
- operator-legible
- and useful for a later governance decision

If Day 1-2 ends with "we now know exactly how to run the next 3 sessions without improvising," that is a valid success state.
