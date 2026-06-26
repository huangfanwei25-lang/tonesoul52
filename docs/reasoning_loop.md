# The Reasoning Loop — 語魂 thinking loop

> Adapted from Peter Steinberger's *"You shouldn't be prompting AI anymore — you should be
> designing loops"* (INPUT → ACTION → OUTPUT → FEEDBACK, self-correcting over time), applied
> not to task output but to **honest reasoning**. Every trap in the catalog below was a real
> one this collaboration hit and caught — this doc is the loop's own trace, and it was itself
> revised after three adversarial critics ran it through its own stage 4.
> Author: Fan-Wei Huang × Claude (Opus 4.8). Date: 2026-06-26. Status: reference / discipline doc.

**The inversion (the point):** Steinberger says *stop prompting for outputs; design loops that
get better.* Here: **stop giving answers; run a reasoning loop that catches its own overclaims.**
The answer is disposable; the loop — the self-correcting honesty discipline — is the durable thing.

## Fire-able checklist (the weld — use this at the decision moment; the prose below is the why)

```
Before you assert:
 1 INPUT    — is each input CURRENT + HERMETIC?  run: python scripts/run_freshness_sweep.py
              state E0–E4 per assumption; surface the "if".
 2 ACTION   — did I drop an "if"? scan the draft against the trap-catalog
              (esp. dropped-if · activity-as-confirmation · aggregation · build-instead-of-measure).
 3 OUTPUT   — claim ≤ evidence?  run: ts review <file>   ·  did I keep the dissent + state cannot_verify?
 4 FEEDBACK — who is the EXTERNAL eye for THIS claim? name it (a reviewer subagent / a PR / ts review —
              not the context that wrote it). log the result back into this catalog.
```

---

## The 4 stages

### 1 · INPUT — frame the question, surface the conditions

- **TRIGGER:** name the claim or decision actually on the table.
- **Surface the "if".** Every claim about the world is conditional. State the antecedents
  (assumptions) explicitly and **evidence-level each** (E0 guess → E4 independently replicated).
- **Verify the inputs are CURRENT, not stale.** "X is the current state" / "X exists" / "X does
  not exist" requires evidence sampled **now**, over the right **scope** — concretely:
  `python scripts/run_freshness_sweep.py` (git fetch + branch drift + graph TTL + open-PR state),
  re-run the analyzer, check the timestamp, enumerate the scope before asserting. *(stale-reference family)*
- **Hermetic, not just current.** "the tests pass / the badge is green" is evidence about *a clean
  checkout under the harness*, not about polluted local state or architectural health.
  **CI green ≠ hermetic; a green badge = inventory completeness, not health.** Re-run on a clean
  *and* a dirty env before trusting a number. *(SUCCESSOR_MAP §4; the #130 runtime-state-pollution lesson)*
- **Input traps:** trusting a stale static record; trusting a dirty local env; assuming scope/state
  without verifying; inheriting a prior directive a newer one already overrode.

### 2 · ACTION — reason conditionally, never unconditionally

- **The move:** produce **"if X then Y"** and keep X visible. The single rule that carries this
  whole stage: **never collapse "if X then Y" into "Y".** Every overclaim is a silently dropped
  antecedent.
- **Run the trap-catalog** (each = a condition quietly dropped, or a category error). These are
  standard epistemics / forecasting hygiene — *named* here, not invented here:
  - **Dropped-if** — asserting Y without its condition ("便宜" from "*if* peak-EPS holds";
    "市場看好" from "*if* not arbitrage").
  - **Activity-read-as-confirmation** — reading a signal that is about *risk / volatility / hedging*
    as *directional* confirmation (leverage-into-inventory ≠ confidence; CB demand ≠ bullish;
    MoE routing ≠ deliberation).
  - **Vocabulary projection** — using one's own words to manufacture similarity/convergence with
    external or sibling work (calling routing "deliberation"; relabelling a sibling artifact in
    this loop's vocabulary to fake a parallel).
  - **Aggregation** — N weak/abstract pieces ≠ one strong piece; N green findings stay N
    individual findings (no auto-inflation to "verified").
  - **Base-rate ≠ fate** — a measured historical frequency is not a prediction of the next
    instance (n = 1).
  - **Peak extrapolation** — extrapolating a cyclical peak as the baseline (low-P/E-at-peak trap).
  - **False objectivity** — putting a guess into code or a number does not make it reliable; it
    makes it *look* reliable (+ overfitting / Goodhart). A program that predicts a direction is
    still a prediction.
  - **Build-instead-of-measure** — reaching for a new engine/feature when the honest move is to
    *measure* the gap or light up the dark path that already exists; capability-building
    masquerading as progress. *(measure-don't-build; POSITIONING / honesty_auditor_program)*
  - **Refuse both claims** — do not overclaim **and** do not underclaim; calibrate to the
    evidence, and refuse to fake a certainty you do not have. (The refusal is part of the output.)

### 3 · OUTPUT — make the claim ≤ the evidence

- **GENERATE** the answer with the claim **bounded by the evidence**; label what is a guess.
  Concretely, the lexical overclaim check is shipped: `ts review <file>` (`tonesoul/reviewer/`,
  exit-0 reviewer aid) flags overclaim wording.
- **Preserve the dissent** — give the other side; do not flatten to one smooth answer.
- **State `cannot_verify`** — name what is genuinely unknowable (the future, the unprovable
  assumption), rather than papering over it.
- **Publish the nulls/misses** — do not hide them.

### 4 · FEEDBACK — external eye, measure, learn

- **INFORM:** the output is checked — by an **external, rotating** eye, by regression/measurement,
  and by the real-world result. Concretely, in this repo the external eye is *a separate reviewer
  subagent / a PR review / `ts review` on the artifact* — **not the context that wrote it.**
- **Auditor ≠ auditee.** A system (or model) checking *its own* output is the **audit-washing**
  structure, not merely a weaker check — same-source blind spots correlate, so self-audit cleans
  the artifact but does **not** exempt it from an external eye. *(RELATED_WORK §3 A5; the
  self-review's own footnote: 「同源的腦,盲點會相關」.)*
- **ADJUST:** the result updates the INPUT framing **and** the trap-catalog — new traps get added.
- **Catch-once ≠ immune.** A caught trap recurs on a new surface. The defense must be
  **structural** (welded to the action — a command you run, a test that pins it), not vigilance or
  memory (which fail under decision pressure). *(That is why the fire-able checklist above exists.)*
- **Publish rejects/nulls. Silence ≠ validation.**

---

## Design principles (Steinberger's five, mapped)

- **CLOSURE** — every claim has a feedback path; a claim with no way to be wrong is not in the loop.
- **LEVERAGE** — the loop compounds: it makes reasoning more honest *over time*, not one good answer.
- **AUTONOMY** — checks welded to actions run with minimal in-the-moment vigilance (because vigilance fails).
- **ADAPTABILITY** — the trap-catalog grows as new traps surface.
- **RESILIENCE** — when a trap slips through (it will), the external eye + the published null *can*
  recover it — **only if the eye is actually run and the null actually published.**

---

## How it connects to the rest of the repo

- `README.md` describes the repo-level **accountability layer** (boundary checks / dissent
  preservation / evidence-bounded reporting); this doc is the same discipline at the *cognition*
  level. (PR #198, open, adds a repo-level accountability-*loop* diagram to the README.)
- The **claim-to-evidence auditor** (`tonesoul/reviewer/`, merged) is a stage-3 guard
  (output ≤ evidence) made into running code. **StockLens** (`apps/stocklens/`) and the
  **honest backtest** are *planned* (open PRs #197/#199), **not yet merged** — named here as
  intent, not as running code.
- When the honest backtest ships, its first additions to this catalog will be the backtest traps
  it actually hits — survivorship and look-ahead bias — **not before** (adding un-hit traps would
  itself break claim ≤ evidence).

*This loop is convergent, not novel; its only discipline is refusing to drop the "if". It was
revised by its own stage 4 — three critics found this doc had itself dropped an "if" (claiming
StockLens/the README loop as running code while they sat in unmerged PRs). The fix is this version.*
