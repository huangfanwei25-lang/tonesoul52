# Spec — Drift / Consistency Characterization (work order for Codex)

> Status: bounded work-order spec; **not** ratified into task.md (ratification is an owner act).
> Author: Claude (Opus 4.8), architect lane · Implementer: Codex · Reviewer: Claude (cross-AI loop).
> Last updated: 2026-06-21.
>
> **Framing — read first.** This is a **demonstration / overclaim-closer, NOT a capability.** The
> output is a *number* (most likely an honest *null*), not a feature. It does **not** change the
> standing conclusion that the binding next step is a **real consumer / real-flow data**
> (`CALL_FOR_REVIEW.md`, `docs/research/where_tonesoul_stands_2026-06-21.md`). It is the **last small
> characterization**, chosen only because it closes the one public overclaim a reviewer specifically
> flagged: "語義漂移偵測 — done, or just concept?" Do not let it grow into a program.

## Goal

Characterize whether **existing** ToneSoul mechanisms detect **semantic drift / contradiction** —
within a single report, and across time — on sanitized fixtures, and **publish the catch-rate even
if it is ~zero.** Answer the reviewer's question with a number: is cross-time consistency detection
*built* or *aspirational*?

## What to measure (existing mechanisms only — NO new detector)

Run sanitized fixtures through the **existing** processes:
- PreOutputCouncil `logic_contradiction` branch (within-report contradiction),
- the tension / semantic-deviation signal **if** reachable model-free,
- the parked corrective-recall error-vector path (expected inert),
- any memory/crystal "prior position" surface that already exists (do **not** build one).

Fixture kinds (sanitized templates; no payload corpus):
1. **within-report contradiction** — e.g. "A→B and B→C, therefore A does not affect C." Likely caught.
2. **cross-time position flip** (the reviewer's case) — a `(prior_statement, current_statement)` pair
   that directly contradicts ("refund is acceptable" → "refund is not acceptable"), prior supplied as
   context. **Expected: NOT caught** — nothing wired compares a current report to a prior position.
3. **controls** — consistent-over-time pairs → should not flag.

## The load-bearing honest expectation

Cross-time drift detection is **largely not built** (corrective-recall parked/inert; no wired
prior-position comparison). The harness must make that **measurable and publishable** — a low/zero
cross-time catch-rate **is the finding** ("mostly concept / parked"), not a failure. Within-report
contradiction may be caught; **report the two separately — do not blend them into one flattering
number.**

## Disciplines (same bar as pieces 1–5 + independent_check)

- **No new detector** — characterize existing mechanisms only.
- **No-oracle** — measure structure (did a mechanism signal), not truth/intent.
- **Sanitized fixtures** — templates + the prior/current pair; **no reusable payload corpus**; raw
  fixture text omitted from public artifacts.
- **canonical:false** finding + `doc_provenance` block.
- **Hermetic** — `model_required: false`; no gitignored-state reads; **deterministic** (byte-identical
  modulo timestamp).
- **No runtime change.**
- `FORBIDDEN_PUBLIC_CLAIM_IDS` baked in code, e.g.: `detects_semantic_drift`,
  `tracks_consistency_over_time`, `is_a_contradiction_oracle`, `prevents_inconsistency`.
- Tests **pin the honest findings** (especially the cross-time null + the visible controls) — not
  tautologies.

## Verification — run ALL before reporting (this round's lesson)

`ruff` **AND** `black --check` (black was the gap last time — "ruff passed" is **not** enough),
`pytest` (focused + a sibling set), determinism (two runs identical modulo timestamp), sanitization
(no raw fixture text in the public json/md), forbidden-claim scan. Report the **honest numbers
unpackaged, including the null.**

## Output

- `tools/eval/drift_consistency_characterization.py`
- `tests/test_drift_consistency_characterization.py`
- `docs/status/drift_consistency_characterization_latest.{json,md}` (canonical:false)

## Non-goals (do NOT do)

- Do **not** build a cross-time comparator / contradiction detector — the whole point is to
  characterize the *absence*. Building it is capability-creep.
- Do **not** wire memory / prior-position into the live pipeline.
- Do **not** package the null as a positive result.

## Hand-off

Codex implements when compute is available; Claude reviews against the disciplines above and lands.
**Optional same-batch trivial follow-up:** add `independent_check` (and this drift piece, once it
exists) to `honesty_scoreboard` PIECES so the board covers all characterizations.
