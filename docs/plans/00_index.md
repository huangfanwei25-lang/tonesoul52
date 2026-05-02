# docs/plans/ Index (2026-04-29)

> Purpose: navigation entry point for `docs/plans/`. Numbered-prefix taxonomy adopted 2026-04-29 (inspired by shadowMAS — see `feedback_catalog_naming_observation_pov.md` family for the broader pattern of borrowing structural ideas from external frameworks while keeping ToneSoul's own naming).
> Status: **partial migration**. Categories established; ~150 legacy files still at top level pending incremental classification.

---

## Convention

| Prefix | Meaning | When to put a file here |
|---|---|---|
| `01_active/` | Currently being executed | A live plan whose Day-by-Day or Phase-by-Phase steps are in flight right now |
| `02_proposals/` | Proposed but not started | Has been written + reviewed; no execution yet; awaiting trigger or decision |
| `03_followups/` | Deferred — waiting on external trigger | Has explicit re-evaluation gates (e.g. "after Phase X ships") and is parked until those gates fire |
| `99_archive/` | Overtaken / shipped / no longer steering work | Plan was executed and superseded, OR was never executed and is now historical |

Top-level (no prefix) = **legacy uncategorized**. Files older than this index were not migrated — see §"Migration status" below.

---

## Currently in `01_active/`

Files driving live work as of 2026-04-29:

- `tonesoul_beta_wave_14day_2026-04-28.md` — parent 14-day collaborator-beta wave plan (Codex-authored, 2026-04-28)
- `tonesoul_beta_wave_day1_2_execution_pack_2026-04-28.md` — Day 1-2 setup pack (3 task shapes + evidence schema)
- `tonesoul_beta_wave_participant_note_template_2026-04-28.md` — session note template for participants
- `tonesoul_beta_wave_operator_note_template_2026-04-28.md` — session note template for operators
- `tonesoul_beta_wave_day1_2_pack_gap_patch_list_2026-04-29.md` — 6 patches identified by Claude/Codex audit (now applied per Codex follow-up)
- `tonesoul_beta_wave_day1_decision_record_template_2026-04-29.md` — Day 1 decision record template

These all live together because they form one coherent operational set: the 14-day wave + Day 1-2 setup + per-session capture. When the wave runs, it consumes these.

---

## Currently in `02_proposals/`

Empty as of 2026-04-29 — to be populated as proposed-but-not-started plans get classified during incremental migration.

Candidates for future classification here (not yet moved):
- `release_readiness_staging.md`
- `concept_to_architecture_blueprint_2026-02-22.md`
- (others — pending audit)

---

## Currently in `03_followups/`

Empty as of 2026-04-29 — to be populated as deferred plans with explicit re-evaluation gates get classified.

Memory-side follow-ups (in agent memory store, not in this directory):
- `project_followup_nlnet_grant_2026-04-26.md` — NLnet defer with 3 re-eval gates
- `project_followup_strategy_mirror_shadow_flag_2026-04-28.md` — shadow flag PR design (now executing as PR #33)
- `project_followup_warm_memory_retrieval_2026-04-28.md` — Phase 5 candidate
- `project_followup_ai_daughter_sim_2026-04-26.md` — game-as-research follow-up

If/when any of these get a `docs/plans/` artifact, they land here.

---

## Currently in `99_archive/`

37 files as of 2026-04-29 first-pass migration. All are `memory_subjectivity_*_2026-03-*.md` — addenda to the implementation plan for Phase 864 (memory subjectivity / choice axis), which has been executing through PRs since 2026-04-18 and is no longer steering decisions at this level of granularity.

The parent spec `memory_subjectivity_choice_axis_2026-04-18.md` is **NOT archived** — it remains the active anchor for the Phase 864 three-layer design (864a EpistemicLabeler shipped, 864b Bucket B shipped, 864c deliberation_trace in current branch, GSE Phase 4 follow-on).

---

## Migration status

This is a **partial migration**. As of 2026-04-29:

- **6** files moved into `01_active/` (today's beta wave set)
- **37** files moved into `99_archive/` (Phase 864 implementation addenda from 2026-03)
- **~145** files remain at top level (uncategorized legacy)

The decision was deliberate: total file count (188) exceeded the budget for a single careful classification pass (~90+ minutes for 188 files at ~30 sec each). Partial migration establishes the pattern + handles obvious cases; remaining classification is incremental.

### Rules for incremental classification (future Claude / Codex / Fan-Wei)

1. **Never bulk-move** without reading each file's status block. Misclassification is worse than legacy clutter.
2. **Default = leave at top level**. If you're unsure whether a file is active or archive, do not move it. The top level is the "uncategorized but not lost" zone.
3. **Move only when the move is obviously correct**:
   - Dated 2026-02 or 2026-03 + the work it describes has shipped → `99_archive/`
   - Has explicit "Status: Active" or matches a current task.md program → `01_active/`
   - Has explicit "Status: Deferred" + re-eval gates → `03_followups/`
   - Has draft-style framing without execution → `02_proposals/`
4. **Update this index when you move files**. Don't let it drift.
5. **One file per move** until you have built confidence — don't `for f in` until 5-10 manual moves have validated your judgment.

---

## Provenance + acknowledgement

The numbered-prefix taxonomy is borrowed from **shadowMAS** (`https://github.com/scyprodigy/shadowMAS`), which uses `00_entry/ 01_truth/ 02_packets/ 03_memory/ 04_runtime/ 05_scripts/ 06_human_docs/ 07_working/`. Their taxonomy is more granular than ours (it includes runtime/memory categories that ToneSoul keeps elsewhere), but the **numbered-prefix-as-onboarding-aid** principle applies cleanly here.

This is the only ToneSoul subdirectory currently using the numbered prefix. Whether to extend it to other directories (`docs/architecture/`, `docs/status/`, `docs/runtime/`, etc.) is an open question — current bias is **don't extend without evidence the cold-reader problem also exists in those directories**.

See:
- `tonesoul_runtime_decomposition_2026-04-29.md` (in `docs/runtime/`) for the broader "explicit boundary contracts" theme this fits into
- The shadowMAS analysis (in conversation history, not yet a file) for the specific learning chain

---

## When to revisit this structure

- After 14-day beta wave Day 14: many `01_active/` files will become `99_archive/` candidates. Plan a single clean-up pass then.
- When `01_active/` exceeds ~10 files: that's the signal that "active" has lost meaning. Re-tighten what counts as active.
- When a category stays empty for >30 days: question whether it earns the slot. `02_proposals/` may not survive its first month if proposals don't accumulate.
