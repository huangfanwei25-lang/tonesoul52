# Paradox Fixture Projections

> Purpose: test projection lane for paradox cases authored in `PARADOXES/`.
> Status: downstream fixture surface; prefer `PARADOXES/` when the casebook and the test fixture diverge.
> Last Updated: 2026-03-22

This directory is not the canonical casebook.

- `PARADOXES/` holds the full governance dilemma cases
- `tests/fixtures/paradoxes/` holds the executable test fixtures derived from those cases

Some fixtures are exact mirrors.
Some fixtures are intentionally reduced so tests can stay deterministic and bounded.

If a paradox needs richer ethical narrative or reasoning, update `PARADOXES/` first.
