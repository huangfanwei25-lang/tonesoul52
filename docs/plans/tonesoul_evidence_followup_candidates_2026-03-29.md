# ToneSoul Evidence Follow-Up Candidates (2026-03-29)

> Purpose: bounded next implementation candidates for evidence-level upgrades, ordered by impact
> Last Updated: 2026-03-29
> Produced By: Claude Opus
> Related Documents:
>   - docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md
>   - docs/architecture/TONESOUL_CLAIM_TO_EVIDENCE_MATRIX.md
>   - docs/architecture/TONESOUL_TEST_AND_VALIDATION_TOPOLOGY_MAP.md

---

## Candidate 1: Deepen Compaction & Checkpoint Tests (E3 → E1)

`test_save_compaction.py` has 2 tests. `test_save_checkpoint.py` has 2 tests. These are the primary handoff mechanisms — they carry context between sessions — and they have the thinnest test coverage of any continuity-critical surface.

Add 5-8 tests per file covering:
- Compaction with empty carry_forward
- Compaction with maximum-length summary
- Checkpoint save and restore round-trip (write → read → compare)
- Checkpoint with missing optional fields
- Edge case: concurrent writes to same compaction surface

**Scope**: ~60-80 lines of test code per file. No runtime code changes.

**Why first**: highest impact-to-effort ratio. These 2-test files back some of ToneSoul's most important operational claims (context preservation). Moving them from E3 to E1 directly strengthens the continuity narrative's credibility.

---

## Candidate 2: Add Subject Snapshot Round-Trip Tests (E3 → E1)

`test_save_subject_snapshot.py` has 2 tests. Subject snapshot is the durable identity surface (TTL 30 days, Lane 3: Working Identity). Add tests for:

- Snapshot save with all 5 field families populated
- Snapshot save with minimal fields (only required)
- Snapshot load and verify all fields survived round-trip
- Snapshot schema validation (verify output matches `subject_snapshot_v1.schema.json`)
- Snapshot with expired TTL handling

**Scope**: ~50-70 lines of test code. No runtime code changes.

**Why second**: subject snapshot backs claims about durable working identity. 2 tests for a 30-day identity surface is a visible weakness. Adding round-trip verification moves the claim from "code exists" to "code works correctly."

---

## Candidate 3: Add Council Dossier Shape Verification Test (E4 → E3)

The Dossier Contract defines 12 fields. No test verifies that runtime council output actually produces all required fields. Add a test that:

- Runs a council deliberation with known input
- Extracts the dossier-shaped output
- Asserts all 5 required fields are present and non-empty
- Asserts all 3 recommended fields are present (may be empty)
- Flags if any of the 4 optional fields are missing (warning, not failure)

**Scope**: ~40-50 lines of test code. No runtime code changes. May require a small helper to extract dossier fields from `build_council_summary()` output.

**Why third**: the dossier is the council's primary auditable output. The contract (E4) says it should have 12 fields. A single test verifying the shape moves the claim from "documented" to "runtime-present with verification."

---

## Candidate 4: Add Evidence-Level Annotation To Existing Contract Documents

Add a one-line evidence level annotation to each claim or section in the top 5 most-referenced architecture contracts:

```markdown
> Evidence Level: E1 (test-backed) — see test_vow_system.py
```

or

```markdown
> Evidence Level: E4 (document-backed) — no automated test verifies this property
```

Target documents:
1. `TONESOUL_CONTINUITY_SURFACE_LIFECYCLE_MAP.md` — lane claims are all E4
2. `TONESOUL_COUNCIL_DOSSIER_AND_DISSENT_CONTRACT.md` — field claims range E1-E4
3. `TONESOUL_CONTINUITY_IMPORT_AND_DECAY_CONTRACT.md` — import posture is E4
4. `TONESOUL_RECEIVER_INTERPRETATION_BOUNDARY_CONTRACT.md` — receiver rules are E4
5. `TONESOUL_ADAPTIVE_DELIBERATION_MODE_CONTRACT.md` — mode selection is E4

**Scope**: ~5-10 annotation lines per document. No code changes.

**Why fourth**: makes evidence posture visible at point of consumption. Later agents reading a contract immediately see whether the described behavior is tested or aspirational. Zero effort to maintain — the annotation is static until evidence level changes.

---

## Candidate 5: Add Risk Calculator Edge-Case Tests (E3 → E1)

`test_risk_calculator.py` has 3 tests for a complex scoring system that determines risk posture. Add tests for:

- All risk factor inputs at zero (baseline)
- All risk factor inputs at maximum (should produce high/critical)
- Single high factor with all others low (isolation test)
- Boundary values at each threshold (caution ↔ high ↔ critical)

**Scope**: ~40-50 lines of test code. No runtime code changes.

**Why fifth**: risk scoring influences task routing and deliberation depth. 3 tests for a multi-factor scoring system is thin. Edge-case tests prevent silent regression if threshold logic is modified.

---

## Summary

| # | Candidate | Current Level | Target Level | Scope | Code Change |
|---|---|---|---|---|---|
| 1 | Compaction & checkpoint tests | E3 | E1 | ~60-80 lines test | Test only |
| 2 | Subject snapshot round-trip | E3 | E1 | ~50-70 lines test | Test only |
| 3 | Dossier shape verification | E4 | E3 | ~40-50 lines test | Test only |
| 4 | Evidence-level annotations | — | — | ~30-50 lines docs | Docs only |
| 5 | Risk calculator edge cases | E3 | E1 | ~40-50 lines test | Test only |

All candidates are test-only or docs-only. None change runtime code, schema, or frontend. Total: ~220-300 lines of new test code + ~30-50 lines of documentation annotations.
