# Codex Subjectivity Handoff (2026-03-10)

## Branch / Head

- branch: `feat/env-perception`
- head: `143f984` (`feat: add subjectivity shadow pressure report`)

## Read Order After Restart

1. `docs/plans/memory_subjectivity_implementation_plan_2026-03-10.md`
2. `docs/plans/memory_subjectivity_context_roadmap_2026-03-10.md`
3. `task.md`
4. `docs/plans/google_always_on_vs_tonesoul.md`

## Stable Context

- `MemoryLayer` and `subjectivity_layer` are already split.
- `MemoryWriteGateway` is the admissibility boundary for public memory writes.
- `DreamEngine`, `sleep_consolidate()`, and `ToneSoulMirror` can emit `tension` candidates.
- reviewed `tension -> vow` has a canonical workflow and replay seam.
- operator-side subjectivity reporting already exists.
- live recall is still unchanged.

## Recently Completed Phases

### Phase 208: Google Always-On Overlap Settlement

- Google `always-on-memory-agent` is now treated as a structural reference, not a competing roadmap.
- immediate borrowing lane: query/report seam shape for retrieval shadow mode
- deferred: multimodal ingest, inbox watcher, dashboard/UI parity
- non-transferable: ungated writes, value-neutral memory, UI-first detour

### Phase 209: Retrieval Shadow Query Foundation

- added `tonesoul/memory/subjectivity_shadow.py`
- added `scripts/run_subjectivity_shadow_query.py`
- shadow profiles:
  - `classified_first`
  - `tension_first`
  - `reviewed_vow_first`
- output compares:
  - baseline candidates
  - shadow candidates
  - overlap / promoted / demoted ids

### Phase 210: Retrieval Shadow Pressure Metrics

- added `build_subjectivity_shadow_pressure_report(...)`
- added `scripts/run_subjectivity_shadow_pressure_report.py`
- pressure metrics now include:
  - `changed_query_rate`
  - `top1_changed_rate`
  - `pressure_query_rate`
  - `avg_classified_lift`
  - tension / reviewed-vow top1 gain rates
- registered `docs/status/subjectivity_shadow_pressure_latest.{json,md}` in `scripts/run_refreshable_artifact_report.py`

## Validation Baseline

- latest successful full validation:
  - `python -m pytest tests/ -x --tb=short -q` -> `1499 passed, 3 warnings`
  - `ruff check tonesoul tests scripts` -> passed
- note: one earlier full `pytest` run hit a transient `pytest INTERNALERROR ... MemoryError`; rerunning the same command passed cleanly

## Files Added Or Changed Most Recently

- `tonesoul/memory/subjectivity_shadow.py`
- `scripts/run_subjectivity_shadow_query.py`
- `scripts/run_subjectivity_shadow_pressure_report.py`
- `scripts/run_refreshable_artifact_report.py`
- `tests/test_subjectivity_shadow.py`
- `tests/test_run_subjectivity_shadow_query.py`
- `tests/test_run_subjectivity_shadow_pressure_report.py`
- `tests/test_run_refreshable_artifact_report.py`

## Current Next Step

- do **not** widen `SoulDB` yet
- use the new shadow pressure artifacts to define a minimal `Step 4` decision gate:
  - what pressure thresholds justify persistence/index widening
  - what pressure is still low enough to stay payload-first

## Dirty Files To Leave Alone

- `CODEX_TASK.md`
- `memory/crystals.jsonl`
- `docs/plans/phase140_codex_coordination_briefing.md`
- `docs/plans/rmm_vs_tonesoul.md`
