# Day 1-2 Beta Wave Pack — Gap Patch List (2026-04-29)

> Source: Claude audit (2026-04-28) + Codex confirmation of all 6 gaps. Outcome of conversation between Fan-Wei, Claude Opus 4.7, and Codex on 2026-04-28 evening.
> Purpose: list the 6 concrete patches Day 1-2 pack needs before Day 3 sessions can start, so the next agent can execute without re-deriving the analysis.
> Status: execution checklist. Each item maps to one file edit (or small set of edits across the three pack files).
> Authority posture: this list does not outrank `task.md`, latest `docs/status/*`, code, or tests. It is a coordination aid for the immediate Day 1-2 work.

---

## Files in scope

1. [tonesoul_beta_wave_14day_2026-04-28.md](tonesoul_beta_wave_14day_2026-04-28.md) — parent 14-day plan (no edits, but referenced)
2. [tonesoul_beta_wave_day1_2_execution_pack_2026-04-28.md](tonesoul_beta_wave_day1_2_execution_pack_2026-04-28.md) — primary file edited by P1, P2, P3, P4, P5, P6
3. [tonesoul_beta_wave_participant_note_template_2026-04-28.md](tonesoul_beta_wave_participant_note_template_2026-04-28.md) — edited by P5, P6
4. [tonesoul_beta_wave_operator_note_template_2026-04-28.md](tonesoul_beta_wave_operator_note_template_2026-04-28.md) — edited by P5, P6

---

## P1 — strategy_mirror data capture timing (highest priority — architecture coordination)

**Problem.** 14-day plan Day 7-9 calibrates `strategy_mirror` against real text. But Day 3-5 sessions run with `SOUL.gse.strategy_mirror_enabled = False` (default), so no `StrategySignature` is captured at session time. Day 7-9 has nothing to replay against, except raw text — which is post-hoc replay, lower-quality evidence than first-hand capture.

**Two valid resolutions:**

- **A (preferred):** ship the shadow flag follow-up PR (`scan_enabled / enforce_enabled` split, design ready in memory `project_followup_strategy_mirror_shadow_flag_2026-04-28.md`) **before Day 3**. Day 3-5 sessions run `scan=True / enforce=False`: `StrategySignature` attached on every verdict, no APPROVE→BLOCK downgrade. Calibration on Day 7-9 has first-hand evidence.
- **B (fallback):** keep `strategy_mirror` default-off during Day 3-5; do post-hoc replay on Day 7-9. Requires hard catalog + detector freeze from Day 3 to Day 9 (no edits to `period_*.json` or `structural_patterns.py` or `detector.py` in that window).

**Patch.**
- File 2 §6 Day 1 Checklist: add a numbered line — *"Decide `strategy_mirror` posture for Day 3-5: (A) `scan=True / enforce=False` (requires shadow flag PR landed first) OR (B) default-off + post-hoc replay (requires Day 3-9 catalog/detector freeze). Document the choice and the consequence in this checklist row."*
- If A is chosen: separate prerequisite work — execute the shadow flag follow-up PR per its memory file. Estimate 30-60 minutes plus review cycle.
- If B is chosen: file 2 §3 (or new §3.5) gains a "Catalog Freeze" subsection naming the exact commit SHA that Day 3 starts at and explicitly forbidding catalog/detector edits until Day 9 evidence consolidation completes.

---

## P2 — fixed prompt strings per task shape

**Problem.** Task Shape A/B/C currently describe what the prompt is "about" but do not lock the literal wording. Two operators running Task A will phrase the request differently → sessions across operators are not directly comparable.

**Patch.**
- File 2 §3, for each of Task Shape A, B, C: add a `### Operator-Reads-Verbatim Prompt` sub-block with **a literal 30-50 character Chinese prompt + an English fallback** the operator reads aloud or pastes verbatim.
- Suggested starting drafts (operators ratify on Day 1):
  - **A (Cold Truth Recovery)**: 「打開這個 repo，目標是『弄清楚現在的 launch 狀態 + 找出下一步該做什麼』。15 分鐘內告訴我你找到了什麼、用了哪幾個檔。」
  - **B (Claim Honesty Rewrite)**: 「這段話：『ToneSoul 是一套完整的 AI 治理框架』 — 用 ToneSoul 把它改寫成 evidence-bounded、launch-safe 的版本。10 分鐘內。」
  - **C (Governance Friction Review)**: 「這段 draft：『限時三天搶購，錯過就沒有了』 — 問 ToneSoul 該 approve / refine / block，看它怎麼說、為什麼。10 分鐘內，跟我講你覺得它的判斷合不合理。」
- File 2 §6 Day 1 Done-When: add criterion — *"all three task shapes have a verbatim operator-prompt locked in."*

---

## P3 — outreach checklist for participant recruitment

**Problem.** Day 1-2 pack contains zero outreach steps. 14-day plan Day 3-5 needs "3 to 5 non-creator or semi-cold participants" but Day 3 will start with no one ready unless outreach happens during Day 1-2.

**Patch.**
- File 2 §6 Day 1 Checklist: add — *"List ≥5 candidate contacts (using §P4 definition below) + 1 backup. Decide outreach channel (email / IM / community post). Draft a 5-line invitation that names: time required (~30 min), what kind of feedback is wanted, what's NOT being measured."*
- File 2 §7 Day 2 Checklist: add — *"Send invitations by end of Day 2. Confirm at least 3 acceptances before Day 3 starts; if fewer, extend Day 2 or add backup contacts."*

---

## P4 — non-creator / semi-cold operational definition

**Problem.** §6 Day 1 Checklist line 6 says "Confirm who is allowed to count as `non-creator` or `semi-cold`" but provides no criteria → post-hoc arguments about whether session N counts as evidence.

**Patch.**
- File 2 §6 (or new §3.6 "Participant Eligibility"): add explicit criteria —
  - `non-creator` = no commits in this repo AND has not read AGENTS.md
  - `semi-cold` = aware of project but ≤ 1 hour prior exposure (skim of README counts as exposure; deep read of any spec disqualifies)
  - **excluded** (too warm) = has read DESIGN.md or any architecture/* doc deeply, OR has co-worked with creator > 3 hours
- The "Confirm who counts" Day 1 line then becomes *"Ratify or adjust the §3.6 eligibility definition; record any deviation as an evidence-integrity caveat."*

---

## P5 — split `claim_or_detection_issue` into two orthogonal fields (schema fix)

**Problem.** Current schema field `claim_or_detection_issue` lists `overclaim / underclaim / false positive / false negative / none`. The first two are content-axis (what the AI claimed about the world); the second two are detector-axis (what `strategy_mirror` flagged about the AI). One session can have both; the single field cannot represent the combination.

**Patch (3 files).**
- File 2 §4 Evidence Schema: replace `claim_or_detection_issue` with two rows —
  - `claim_issue` (`overclaim / underclaim / none`) — content axis
  - `detector_issue` (`false_positive / false_negative / none`) — `strategy_mirror` axis (only meaningful when posture A from P1 chosen, OR populated post-hoc under posture B)
- File 3 §8 Classification: same split
- File 4 §3 Evidence Row: same split

---

## P6 — `trust_before` / `trust_after` / `trust_note` (schema addition)

**Problem.** Current `trust_note` is qualitative-only; "did trust improve, stay flat, or drop" depends on operator inference, no anchor in participant's own state.

**Patch (3 files).**
- File 2 §4: replace `trust_note` row with three rows —
  - `trust_before` (integer 1-5, asked of participant before task)
  - `trust_after` (integer 1-5, asked of participant after task)
  - `trust_note` (string, qualitative anchor — captures what participant said about WHY)
- File 3 §3 Trust Read: add explicit before/after lines + note that participant should be asked for the numbers, not assigned them
- File 4 §3 Evidence Row: add `trust_before` and `trust_after` fields
- File 2 §4: add caveat paragraph below the schema table — *"`trust_before` and `trust_after` numbers are NOT statistically meaningful at N=3-5. They are an attention anchor — asking the participant for a number forces them to attend to their own trust state. The primary signal is `trust_note`; the numbers are secondary context."*

---

## Suggested execution order

1. **P1 first** — it gates everything else; if A is chosen, the shadow flag PR work starts in parallel.
2. **P3** — long lead time on participant outreach; start as early as possible during Day 1.
3. **P5 + P6** — schema fixes; do together as one schema-update commit across the three template files.
4. **P2** — fixed prompts; ~30 min of careful writing.
5. **P4** — eligibility definitions; quick once §3.6 is ratified.

## Total estimated effort

- Patches P1-P6 documentation work: 1-2 hours of writing
- P1-A shadow flag follow-up PR (if chosen): additional 30-60 minutes + tests + review
- All 6 patches should land as **one coordinated commit** (or two if shadow flag is its own PR), not staggered — staggering creates partial-state pack files where the schema doesn't match the templates.

## Pack-completeness check after patches

Day 2 dry-run criterion (§7 of file 2) should pass on the first try if all 6 patches land cleanly:
- one operator can run a session using only the pack and templates ✓ (P2 fixes prompts; P5/P6 fix schema/template alignment)
- one participant brief exists and is short enough to be usable ✓ (separate from these patches; existing pack content)
- the schema survives one dry-run without modification ✓ (P5/P6 stabilize the schema)

If the dry-run uncovers a 7th gap, treat it as an honest finding from the dry-run rather than an oversight in this list.
