# Paradox Fixture Ownership Map

> Purpose: declare the source-of-truth, projection lane, and sync policy for paradox governance fixtures.
> Status: active fixture ownership map for convergence cleanup.
> Last Updated: 2026-03-22

---

## Contract

- Canonical casebook root: `PARADOXES/`
- Test fixture root: `tests/fixtures/paradoxes/`
- Sync direction: `PARADOXES/` -> `tests/fixtures/paradoxes/`
- Read order:
  1. read `PARADOXES/` for the full governance case
  2. read `tests/fixtures/paradoxes/` only when you need the concrete test payload
  3. if the two differ, prefer `PARADOXES/` as the ethical/source casebook unless the test intentionally requires a reduced projection

## Why This Boundary Exists

The paradox family is not just duplicated data.

- `PARADOXES/` acts as the canonical governance casebook
- `tests/fixtures/paradoxes/` acts as a projection lane for automated tests

Some files are exact mirrors.
Others are intentionally simplified so tests can assert a smaller deterministic payload.

That means the right rule is not "everything must match byte-for-byte."
The right rule is:

- source-of-truth stays in `PARADOXES/`
- fixture projections stay in `tests/fixtures/paradoxes/`
- exact mirrors are allowed
- simplified projections are also allowed when clearly downstream of the canonical case

## Current Policy

1. New paradox or governance dilemma cases should be authored in `PARADOXES/` first.
2. Test fixtures should be derived from canonical cases, not invented in isolation.
3. When a test only needs a smaller fixture, the reduced fixture may diverge as a projection.
4. If a fixture starts carrying richer reasoning than the canonical casebook, move that reasoning upstream.
5. The directory name must do the semantic work:
   - `PARADOXES/` = ethical casebook
   - `tests/fixtures/paradoxes/` = executable test projection lane

## Expected Postures

- `medical_suicide_paradox.json`
  - exact mirror allowed
- `truth_vs_harm_paradox.json`
  - exact mirror allowed
- `paradox_003.json` to `paradox_007.json`
  - simplified projection allowed
  - canonical narrative remains in `PARADOXES/`

## Retrieval Guidance

- If you are reasoning about governance quality or ethics, open `PARADOXES/`.
- If you are editing or debugging tests, open `tests/fixtures/paradoxes/`.
- If you need the current pair status, open `docs/status/paradox_fixture_ownership_latest.json`.
