# Foundation Layer: QA And Validation

> Purpose: define what counts as "good enough to trust" in day-to-day project work.
> Last Updated: 2026-04-14
> Status: thin foundation summary; subordinate to tests, CI, and validation contracts.

---

## Baseline QA Rules

- Do not disable tests to make a change look green.
- Do not swallow exceptions silently.
- Do not present documented intention as tested behavior.
- Do not ship a change without at least one relevant verification command.

## Validation Lanes

| Lane | Use |
|---|---|
| smoke / demo | prove the core loop still runs |
| blocking tier | protect operational contracts without full-suite cost |
| full regression | prove repo-wide survival |

## Current Practical Commands

```bash
python examples/quickstart.py
python examples/quickstart.py --json
python scripts/run_tonesoul_convergence_audit.py
python scripts/run_test_tier.py --tier blocking
python -m ruff check tonesoul tests scripts
python -m pytest tests -q
```

## Evidence Honesty

When describing a capability, separate:

- tested behavior
- runtime-present but lightly tested behavior
- document-backed intention
- philosophical or conceptual framing

## Formula Hygiene

Treat formulas as one of four kinds:

- rigorous
- heuristic
- conceptual
- retired

Do not mix those categories in one claim.
Do not repeat a symbolic formula unless the same page also names its status and owner.

## Source Anchors

- [docs/7D_AUDIT_FRAMEWORK.md](../7D_AUDIT_FRAMEWORK.md)
- [docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md](../architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md)
- [docs/plans/tonesoul_test_stratification_program_2026-04-02.md](../plans/tonesoul_test_stratification_program_2026-04-02.md)
- [README.md](../../README.md)
