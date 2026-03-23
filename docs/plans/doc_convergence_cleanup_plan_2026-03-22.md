# Document Convergence Cleanup Plan (2026-03-22)

> Purpose: define the first cleanup wave for duplicate document surfaces, same-basename divergence, and missing metadata across ToneSoul's authored documentation.
> Status: active cleanup plan for convergence phase 596.
> Last Updated: 2026-03-22

---

## Why This Exists

The repository has crossed the point where file search alone is reliable.
Too many authored documents now share the same basename, mirror similar content across different lanes, or omit explicit metadata that would tell later agents what the document is for.

The generated inventory at `docs/status/doc_convergence_inventory_latest.json` is the machine-readable scan.
This plan is the human-authored cleanup order that prevents random renames or destructive "dedupe" work.
The engineering mirror family now also has an explicit owner contract in
`docs/architecture/ENGINEERING_MIRROR_OWNERSHIP_MAP.md` and a generated status
surface at `docs/status/engineering_mirror_ownership_latest.json`.
The same-basename but non-duplicate set is now distilled in
`docs/architecture/BASENAME_DIVERGENCE_DISTILLATION_MAP.md`,
`spec/governance/basename_divergence_registry_v1.json`, and
`docs/status/basename_divergence_distillation_latest.json`.
The remaining nested memory shadow now also has a dedicated boundary map in
`docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md` and a generated
status surface at `docs/status/private_memory_shadow_latest.json`.
The paradox casebook/fixture lane now also has an ownership contract in
`docs/architecture/PARADOX_FIXTURE_OWNERSHIP_MAP.md` and a generated status
surface at `docs/status/paradox_fixture_ownership_latest.json`.

## Input Artifacts

- `docs/status/doc_convergence_inventory_latest.json`
- `docs/status/doc_convergence_inventory_latest.md`
- `docs/status/doc_convergence_inventory_latest.mmd`

## Convergence Rules

1. Same basename does not imply same role.
   `manifesto.md`, `academic_grounding.md`, and status snapshots with the same basename must be reviewed by meaning, not by filename alone.
2. Exact mirrors need a canonical owner.
   If `docs/engineering/` and `law/engineering/` carry the same text, the repo should declare one source-of-truth and one mirror direction.
3. Entrypoint documents should declare their role explicitly.
   Public entrypoints and high-authority specs should expose at least `Purpose` and `Last Updated`.
4. Generated artifacts are not hand-edited.
   `*_latest.json`, `*_latest.md`, and `*_latest.mmd` should be regenerated from scripts, not patched directly.
5. Cleanup should preserve authority boundaries.
   Do not merge conceptual notes, private-memory traces, test fixtures, and public architecture docs into one lane for the sake of neatness.

## First-Wave Priorities

### 1. Engineering mirror family

Priority: high

Current signal:
- `docs_law_engineering_mirror = 14`
- Most pairs are exact or near-exact mirrors between `docs/engineering/` and `law/engineering/`

Action:
- declare one canonical owner per mirrored engineering text
- decide whether the mirror remains intentional or should collapse into one lane
- add one note explaining mirror direction if both surfaces stay
- keep `docs/engineering/` as canonical owner and resync `law/engineering/` from it when drift appears

### 2. Same-basename divergent documents

Priority: high

Current manual-review collisions:
- `constitution/manifesto.md` vs `docs/philosophy/manifesto.md`
- `docs/philosophy/academic_grounding.md` vs `memory/narrative/threads/academic_grounding.md`
- `docs/status/autonomous_registry_schedule_latest.json` vs `docs/status/runtime_probe_watch/autonomous_registry_schedule_latest.json`
- `memory/.semantic_index/metadata.json` vs `memory/vectors/metadata.json`
- `memory/.hierarchical_index/vows_meta.json` vs `memory/memory/.hierarchical_index/vows_meta.json`

Action:
- keep or rename by semantic role, not by convenience
- document source-of-truth for status or memory metadata twins
- do not assume these are safe dedupe candidates
- for nested private-memory shadows, stop at the dedicated shadow contract/report and defer mutation

### 3. Entry-point metadata backfill

Priority: high

First documents to normalize:
- `README.md`
- `README.zh-TW.md`
- `SOUL.md`
- `MGGI_SPEC.md`
- `TAE-01_Architecture_Spec.md`

Action:
- backfill `Purpose` and `Last Updated`
- keep the header short so public readability does not collapse

### 4. Paradox fixture mirror policy

Priority: medium

Current signal:
- `paradox_fixture_mirror = 7`
- Some fixtures are exact mirrors, some are intentionally divergent test copies

Action:
- declare whether `PARADOXES/` or `tests/fixtures/paradoxes/` is the source-of-truth
- if divergence is intentional, say so in the boundary doc or fixture README
- keep `PARADOXES/` as canonical casebook and treat test fixtures as exact mirrors or reduced projections

### 5. Private-memory shadow lane

Priority: high

Current signal:
- `memory/.hierarchical_index/*` vs `memory/memory/.hierarchical_index/*`
- the basename-divergence registry still contains one deferred private-shadow case

Action:
- treat `memory/.hierarchical_index/` as the active lane in this public convergence phase
- treat `memory/memory/.hierarchical_index/` as a deferred shadow or legacy lane
- inspect via `docs/architecture/PRIVATE_MEMORY_SHADOW_BOUNDARY_MAP.md` and `docs/status/private_memory_shadow_latest.json`
- do not rewrite, dedupe, or delete memory data files during this public cleanup wave

## What Not To Do

- do not mass-rename every `README.md`
- do not merge `memory/` surfaces into public docs just to reduce counts
- do not treat generated probe families as hand-authored naming debt
- do not hand-edit generated `docs/status/*_latest.*` outputs

## Success Criteria

- the repo has one documented cleanup order instead of ad hoc renaming
- same-basename collisions are separated into mirror, divergence, and generated-series categories
- the main public entrypoints expose explicit purpose/date metadata
- later agents can open one inventory report and one cleanup plan before proposing structural changes
