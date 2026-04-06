# ToneSoul Compiled Knowledge Landing-Zone Spec

> Purpose: define where future compiled-knowledge artifacts should live, how they should be health-checked, and how they must stay separate from hot coordination and parked drafts.
> Authority: forward-looking architecture spec. Does not create a retrieval runtime by itself.

---

## Why This Exists

After the source taxonomy is clear, ToneSoul still needs a clean destination for compiled knowledge.

Without a landing zone, the repo drifts toward three bad defaults:

1. distillations remain mixed into `docs/research/` forever
2. compiled knowledge gets treated like runtime continuity
3. future retrieval work reuses ad hoc docs folders instead of a bounded corpus

This spec exists to prevent that sprawl before a retrieval runtime is built.

---

## Proposed Landing Zone

Future compiled knowledge should land in a dedicated repo-native root:

`knowledge/compiled/`

with four bounded lanes:

1. `knowledge/compiled/collections/`
   - collection manifests
   - source grouping and health metadata

2. `knowledge/compiled/artifacts/`
   - compiled markdown or JSON artifacts ready for bounded retrieval

3. `knowledge/compiled/indexes/`
   - machine-readable registries, lookup tables, and future query indexes

4. `knowledge/compiled/status/`
   - freshness, health-check, and ingestion status artifacts

This keeps compiled knowledge out of:

- hot coordination state
- parked drafts
- public teaching surfaces

---

## Entry Requirements

Every compiled artifact should eventually declare:

- `artifact_id`
- `schema_version`
- `compiled_at`
- `source_refs`
- `source_kind`
- `compile_lineage`
- `trust_posture`
- `freshness_posture`
- `consumer_safe_summary`

If an artifact cannot name its sources and compile lineage, it is not compiled knowledge yet.

---

## Health-Check Expectations

The landing zone should eventually enforce:

1. source refs must exist or resolve to explicit external references
2. parked exploratory drafts cannot be ingested directly without a distillation step
3. hot coordination fields must not appear in compiled artifacts
4. private or memory data must not leak into compiled artifacts
5. collection and artifact indexes must agree on membership and freshness posture

---

## Consumer Rules

1. `session-start` must not read the landing zone by default
2. `observer-window` must not become a compiled-knowledge reader
3. future operator retrieval should query compiled artifacts, not parked drafts
4. public teaching surfaces may summarize compiled knowledge, but they do not become the corpus

---

## Current Interim Rule

Until `knowledge/compiled/` exists:

- `docs/research/` remains compiled-knowledge-adjacent, not the final landing zone
- parked `docs/plans/` drafts remain exploratory residue
- `external_research/` remains raw source parking

That means:

`do not treat today's research notes as if the compiled corpus already exists.`

---

## Non-Goals

- choosing a vector database now
- promising graph retrieval now
- migrating existing docs immediately
- making compiled knowledge part of identity or continuity
