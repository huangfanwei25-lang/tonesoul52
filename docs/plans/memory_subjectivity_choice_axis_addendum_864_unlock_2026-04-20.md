# Phase 864 Phasing Amendment — Synthetic Baseline Unlock

> Status: **ADOPTED 2026-04-20** (Fan-Wei Huang's decision; this document drafted by Claude Opus 4.7)
> Amends: [`memory_subjectivity_choice_axis_2026-04-18.md`](memory_subjectivity_choice_axis_2026-04-18.md) §5 Phasing
> Supersedes (via follow-up): the "locked until 2026-05-03" language in `council_refusal_eligible_gap_2026-04-19.md` (currently staged in PR #22; the line-137 note will be synced when #22 lands — tracked below in §7 Follow-ups)

---

## 1. What this amendment changes

§5 of the parent spec said:

> | 864b | Layer 2 (Calibration Table) | ~3 weeks | Requires Layer 1 in production for ≥2 weeks of **real usage**. |
> | 864c | Layer 3 (Deliberation Trace) | TBD — likely ≥4 weeks | Requires Layers 1+2 in production for ≥4 weeks. **Do not start sooner.** |

**Effective 2026-04-20, the "real usage" gating requirement is released.** Layers 2 and 3 may be implemented against a **synthetic baseline** — the smoke corpora under `tests/fixtures/outcome_smoke/` with `signal_source: "synthetic"`.

The phasing **order** is unchanged: Layer 1 → Layer 2 → Layer 3. The Layer-dependency rule (Layer 3 cannot interpret traces without Layer 2's calibration; Layer 2 cannot anchor `ai_observations` without Layer 1's epistemic labels) stays exactly as written in the parent spec §5 final paragraph.

## 2. Why we are releasing the gate

The "≥2 weeks of real usage" language assumed ToneSoul would have external consumers writing outcome records between 864a shipping and 864b starting. That assumption has been falsified by the reality captured in the `project_gateway_no_external_traffic_2026-04-19` memory:

- Codex / third-party agents are not integrated.
- The Demo UI (PR #23) is not yet deployed publicly.
- Fan-Wei's own dialogue with Claude Code goes through Python imports, not the gateway.

Under these conditions, `.aegis/council_outcomes.jsonl` will stay empty no matter how long we wait. Waiting until 2026-05-03 was therefore not producing the validation the original gate was trying to buy — it was just stalling. Holding the gate in place any longer would convert a safety mechanism into a cargo-cult.

The `--enable-outcome-collection` flag and the gateway `/outcome` endpoint remain wired; if external traffic materializes later, they will start producing real data automatically. This amendment does not remove that path, only the **mandatory wait** that depended on it.

## 3. What a synthetic baseline is, and what it is not

**Synthetic baseline = acceptable anchor for 864b/c implementation work.**

The smoke corpora (`corpus_2026-04-19.jsonl` + `adversarial_corpus_2026-04-19.jsonl`, 28 entries total, all `signal_source: "synthetic"`) are sufficient to:

- Define and exercise the Layer 2 calibration table schema
- Validate the verdict↔outcome JOIN mechanics end-to-end
- Build the Layer 3 deliberation trace plumbing
- Red-team the 4 adversarial categories (tone_laundering, hedging_camouflage, expert_voice, helpful_framing) against the three layers as they ship

**Synthetic baseline ≠ real-world calibration.**

A synthetic-baseline 864b is fundamentally a smoke-harness self-consistency check:
- The author's `suggested_signal` is pre-labeling, not ground truth.
- Council/label disagreement on synthetic data is an *investigation starting point*, not proof of Council error.
- The 30% coverage threshold in parent §5 (if re-read from the calibration-table angle) does not apply — there is no traffic to cover a percentage of.

**What this means for the Bucket B promotion criterion:** the spec §5 coverage threshold is explicitly inapplicable under synthetic baseline. The alternative criterion for promoting from 864b to 864c is:

> Layer 2's calibration table survives the full adversarial smoke corpus (all 12 adversarial entries) without false-approve leakage, and the verdict↔outcome JOIN is reproducible across two independent runs of the smoke harness.

That is a weaker guarantee than 2 weeks of real traffic would have given. We are accepting the weaker guarantee as the honest best-available under current reality, not pretending it is equivalent.

## 4. If external consumers arrive

This amendment is **reversible in one direction**: the moment real outcome records start flowing (gateway `/outcome` endpoint receiving POSTs from a deployed Demo UI, or Codex integration, or any non-smoke source), the original 2-week real-usage baseline SHOULD be rerun before 864b or 864c claims maturity.

Concretely:
- Leave a `baseline_regime: "synthetic" | "real" | "mixed"` field on all 864b/c calibration table rows so later queries can filter.
- When real outcomes arrive, tag subsequent rows `baseline_regime: "real"` and recompute any thresholds using only real-regime rows.
- Do not retroactively discard synthetic-regime artifacts — they are the honest historical record of what was possible under which conditions.

## 5. What does NOT change

The following hard rules from the parent spec §3/§4 are **untouched** by this amendment:

- Layer 1 / Layer 2 / Layer 3 hard rules on visibility, disputability, non-substitution
- The 6 traps listed in parent §4
- The `MemoryWriteGateway` promotion path
- The Isnād provenance contract
- Aegis chain requirements
- The 864a EpistemicLabeler gate (PR #19)
- The sequential ordering 864a → 864b → 864c

Only the **calendar-based wait** dissolves. The architectural gates remain fully in force.

## 6. Lineage

- **Decision maker:** Fan-Wei Huang (2026-04-20)
- **Motivation:** "864b/c 不要鎖了 今天 4/20 了，只能用合成資料了" — acknowledgment that the real-traffic baseline is currently uncollectable given this project's actual consumer state
- **Drafting agent:** Claude Opus 4.7
- **Governance trailers:** `Agent: Claude Opus 4.7`, `Trace-Topic: 864-unlock-synthetic-baseline`
- **Related memories (private, ~/.claude/projects/.../memory/):**
  - `project_gateway_no_external_traffic_2026-04-19.md` — the reality check this amendment responds to
  - `project_phase_864a_epistemic_labeler.md` — superseded "locked until 2026-05-03" line
  - `project_864_unlock_2026-04-20.md` (new) — decision record mirror

## 7. Follow-ups

- [ ] After PR #22 merges: edit `docs/plans/council_refusal_eligible_gap_2026-04-19.md` line ~137 — replace "Phase 864b is locked until 2026-05-03 (spec §5 phasing rule)." with a pointer to this addendum. Small one-line PR.
- [ ] When 864b work starts: add `baseline_regime` field to calibration table schema per §4 above.
- [ ] When/if external traffic begins: re-evaluate whether to rerun baseline and tag pre-cutoff rows as synthetic-regime only.

---

*This amendment intentionally does not edit the parent spec's prose. The parent stays as an authorial artifact of the 2026-04-18 moment; this addendum is the adjustment that 2026-04-20 reality forced on it. A future editor reading both in sequence should see the full trajectory, not a silently-rewritten history.*
