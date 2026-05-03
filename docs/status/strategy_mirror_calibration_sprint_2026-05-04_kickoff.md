# strategy_mirror Calibration Sprint — Kickoff (2026-05-04)

> Purpose: record the start of a creator-team-internal calibration sprint for the Phase 2 `strategy_mirror` system. This is **not** the start of the 14-day collaborator beta wave proper.
> Status: live record. Frozen at end of Day 1; subsequent decisions go in follow-up records, not in-place mutation.
> Scope: Day 1 decisions for the calibration sprint only. Does not outrank `task.md`, code, tests, or `AXIOMS.json`.
> Source: closes the gap between `docs/plans/01_active/tonesoul_beta_wave_day1_2_execution_pack_2026-04-28.md` (designed for non-creator validation) and the actual repo state on 2026-05-04 (no non-creator participants recruited yet, but `strategy_mirror` ready for first-hand data).

---

## 0. Why this is a calibration sprint, not "Day 1 of the 14-day wave"

The 14-day collaborator beta wave plan (`docs/plans/01_active/tonesoul_beta_wave_14day_2026-04-28.md`) is built around **non-creator legibility validation** — it asks "can a cold reader use ToneSoul without becoming the creator's apprentice first?" Its participant eligibility (§3.6 of the execution pack) explicitly excludes anyone who has read `DESIGN.md` deeply or co-worked with the creator > 3 hours.

Today (2026-05-04), no non-creator participants are recruited or onboarded. Starting the wave proper would require synthesising data from people who do not exist yet.

But Phase 2 `strategy_mirror` ships in master with three load-bearing surfaces (catalog, detector, council integration) that have **never been exercised against real conversational pressure** — only against synthetic tests and a happy-path fixture. Whatever Day 7-9 calibration the wave needs, the catalog/detector parameters are still effectively unobserved.

So the cleanest split:

- **Pre-wave calibration sprint (this record)** — creator team structured exercises that produce first-hand `StrategySignature` data + structural pattern coverage estimates + a false-positive list. Creator-team participation is the entire point, not a fallback.
- **14-day wave proper** — opens when non-creator participants are recruited AND the calibration sprint has a baseline signature distribution to compare against. Separate Day 1 record at that point.

This split avoids two failure modes:

1. **Indefinite wait** — refusing to start anything until participants appear, and `strategy_mirror` accumulating zero real-traffic evidence in the meantime.
2. **Pseudo-wave** — pretending creator-team sessions count as wave evidence and then having the legibility findings polluted by people who already know where current truth lives.

---

## 1. `strategy_mirror` posture

> Decision: **Option A** (`scan=True / enforce=False`, shadow mode)

- Mechanism: `TONESOUL_GSE_STRATEGY_MIRROR_SCAN_ENABLED=1` (per-session env var)
- Mechanism shipped: PR #37 (`fix(gse): make strategy mirror shadow mode operational`), merged on master
- Default in `tonesoul/soul_config.py` remains `False / False` — opt-in does not change repo-wide behaviour for non-sprint consumers
- Catalog + detector commit baseline (record so post-hoc replay is reproducible if needed):
  - `tonesoul/gse/strategy_mirror/catalog/period_1_foundation.json` @ `origin/master` head
  - `tonesoul/gse/strategy_mirror/structural_patterns.py` @ `origin/master` head
  - `tonesoul/gse/strategy_mirror/detector.py` @ `origin/master` head
- Soft freeze on those three files for sprint duration: changes allowed but **must be flagged in the synthesis** so calibration data is interpretable

---

## 2. Participant set + eligibility variation

> Variation from execution pack §3.6 — explicitly recorded per §3.6's last sentence: "If the wave uses anyone outside these defaults, record it as an evidence-integrity caveat."

### Participants

| Label | Type | Eligibility status | Caveat |
|---|---|---|---|
| Fan-Wei | creator | excluded as too warm (creator) | all sessions tagged `creator` |
| Claude (Opus 4.7) | creator-aligned | excluded as too warm (read DESIGN.md, co-worked >> 3 hr) | all sessions tagged `creator-aligned` |
| Codex (GPT-5) | creator-aligned | excluded as too warm (read DESIGN.md, co-worked >> 3 hr) | all sessions tagged `creator-aligned` |

### Caveat applied to evidence

Every session record produced in this sprint carries the field `evidence_integrity_caveat: creator_team_internal` and explicitly **does not count** toward the 14-day wave's "non-creator validation" success metric.

What the sprint evidence **does** count toward:

- `strategy_mirror` signature distribution baseline
- structural pattern coverage estimate
- false-positive list for the catalog
- detector confidence threshold calibration

These are calibration-class outputs, independent of participant cold-ness.

---

## 3. Task shape allocation

| Shape | Lead | Why this lead | Why others not |
|---|---|---|---|
| A — Cold Truth Recovery | **PARKED** | Designed to test entry-surface routing for cold readers. Creator team is too warm — would produce "I went to the file I already knew about" outcomes. Useless signal. | Park until a non-creator participant exists. |
| B — Claim Honesty Rewrite | **Codex** | Already routinely produces evidence-bounded PR descriptions and commit messages with explicit Why / Verification / Boundary discipline; has demonstrated calibrated evidence-ladder discipline (e.g. PR #37 body). | Claude can cross-shoot for variance. Fan-Wei runs additional rounds with claim seeds chosen for harder ambiguity. |
| C — Governance Friction Review | **Claude** | Council verdict logic (perspective evaluation, coherence scoring, refine/block reasoning) is the working surface across PRs #32-#33 + audit responsibilities for #37/#38/#39. | Codex can cross-shoot for variance. Fan-Wei runs additional rounds with risky-draft seeds. |

Verbatim prompts: **use the execution pack §3 strings unchanged**. No diff.

Cross-shoot policy: each lead runs ≥2 sessions; the other agent runs ≥1 cross-shoot for variance; Fan-Wei runs ≥1 round of his own with seeds he picks. Total ≈ 6-8 sessions across Day 2-5.

---

## 4. Operator + schedule

- **Sprint operator**: Fan-Wei (this is the only role he plays in the sprint mechanics; he can also participate as a leaf participant in cross-shoot rounds)
- **Per-session captured fields** (subset of execution pack §4 evidence schema, plus the caveat field above):
  - `session_id`
  - `agent_id`
  - `task_shape` (B / C only)
  - `started_at` / `ended_at` (UTC)
  - `strategy_mirror_signature` (raw payload from runtime)
  - `verdict` (when applicable)
  - `friction_tags`
  - `evidence_integrity_caveat: creator_team_internal`
  - `notes` (free text — surprises, false positives, friction friction)
- **Schedule (target, can slip)**:
  - Day 1 (today, 2026-05-04): this kickoff record + env var verified
  - Day 2-5 (2026-05-05 to 2026-05-08): structured sessions, ≥6 total
  - Day 6 (2026-05-09): first synthesis
  - Day 7-9 (2026-05-10 to 2026-05-12): calibration analysis (signature distribution, false positive review, threshold sensitivity)
  - Day 10 (2026-05-13): graduate decision

---

## 5. Artifact storage paths

- Per-session record: `docs/status/calibration_sprint_2026-05-04_session_<label>.md`
- First synthesis: `docs/status/calibration_sprint_2026-05-04_synthesis_day6.md`
- Calibration analysis: `docs/status/calibration_sprint_2026-05-04_strategy_mirror_calibration.md`
- Graduate decision: `docs/status/calibration_sprint_2026-05-04_graduate_decision.md`

---

## 6. Day 10 graduate decision options

At Day 10, the sprint synthesis lands one of three outcomes:

- **Promote to enforce** — `scan=True / enforce=True` becomes the default in `tonesoul/soul_config.py` after a confidence threshold + catalog adjustment. Trigger: shadow data shows the detector is well-calibrated and false positives are tractable.
- **Stay in shadow** — keep `scan=True / enforce=False` as the recommended posture; defer enforcement. Trigger: signatures are useful but the catalog needs more work before downgrade rules can be trusted.
- **Default-off** — keep both flags at `False` and require explicit env var to enable. Trigger: shadow data shows the detector produces too much noise to be operationally useful in its current form.

The 14-day wave proper opens **after** the graduate decision lands, regardless of which option is chosen — non-creator validation tests legibility, which is independent of strategy_mirror posture.

---

## 7. Open follow-ups going into Day 2

- Recruit ≥1 non-creator participant for the eventual 14-day wave proper (does not block this sprint, blocks wave Day 1 only)
- First sprint session: Codex runs Task B with a self-chosen claim seed, env var on, captures session record at the path in §5
- Confirm that the `tmp/` rule from PR #35 (rehearsal artifacts go to `tmp/`, not tracked status surfaces) is followed — sprint records ARE meant to be tracked, but rehearsal scratch is not

---

## 8. Honest read

This sprint is creator-team-only on purpose. It does not satisfy the 14-day wave's non-creator legibility goal and does not pretend to. It produces calibration data that the wave will need either way, in a window where waiting for participants would burn `strategy_mirror`'s ship-then-test risk.

If the synthesis at Day 6 shows the sprint is not producing useful calibration signal (e.g. signatures cluster trivially, no false positives surface, structural pattern coverage stays at the existing 3.33%), that is itself useful evidence — it tells us the catalog needs more work before the wave's Day 7-9 calibration step is meaningful, and the wave timeline should adjust accordingly.

This record is itself authored under the same conditions it documents. Strategy_mirror is not running on its draft (this conversation does not pass through ToneSoul's PreOutputCouncil). The first session that DOES run with the env var on will be the first true sprint data point.
