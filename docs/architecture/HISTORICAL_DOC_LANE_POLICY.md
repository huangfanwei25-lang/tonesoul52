# Historical Document Lane Policy

> Purpose: define how `docs/archive/` and `docs/chronicles/` are governed so historical and generated record lanes do not pollute active documentation cleanup.
> Last Updated: 2026-03-23

---

## Why This Policy Exists

ToneSoul now has two document lanes that are intentionally not the same as active architecture, spec, or guide surfaces:

- `docs/archive/`
- `docs/chronicles/`

Without an explicit policy, retrieval agents and cleanup scripts treat these files like ordinary authored docs and keep pushing them to the top of the missing-metadata backlog.

That is incorrect.

## Lane Definitions

### `docs/archive/`

- Purpose:
  preserve deprecated, superseded, or reference-only material that still has historical value
- Is not:
  current canonical policy or active runtime authority
- Editing rule:
  prefer lane-level or README-level metadata, avoid rewriting historical bodies unless factual correction is required

### `docs/chronicles/`

- Purpose:
  store generated ToneSoul Scribe chronicles and their structured sidecars as a historical narrative lane
- Is not:
  canonical architecture, active product docs, or hand-maintained knowledge surfaces
- Editing rule:
  do not hand-edit generated chronicle bodies to satisfy ordinary metadata cleanup

## Chronicle-Specific Rules

For `docs/chronicles/scribe_chronicle_*`:

1. Filename timestamp is an accepted date source.
2. Internal `Generated at` markers are an accepted provenance source.
3. Per-file `Purpose` backfill is not required once this lane policy, the chronicle README, and the generated lane report are present.
4. Use `docs/chronicles/README.md` to explain lane semantics instead of rewriting every generated chronicle.

## Retrieval Rule

If you are trying to understand current ToneSoul behavior:

1. do not start from `docs/archive/` or `docs/chronicles/`
2. open canonical architecture anchors first
3. use historical lanes only when you explicitly need lineage, previous drafts, or generated chronicle context

## Inventory Rule

When this policy and the corresponding generated status report are present:

- `docs/archive/` and `docs/chronicles/` should be treated as contract-managed historical lanes
- generated chronicle files should not dominate the ordinary missing-metadata backlog
- historical-lane upkeep becomes contract maintenance, not per-file manual triage

