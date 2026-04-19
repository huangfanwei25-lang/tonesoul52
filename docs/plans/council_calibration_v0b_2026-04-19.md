# Council Calibration v0b — Verdict↔Outcome Alignment Spec

> Status: **DRAFT** — not yet adopted, not yet implemented. Drafted 2026-04-19.
> Author: Claude Opus 4.7 (drafting agent)
> Relation to existing work: extends V1.1 Council Calibration v0a (`tonesoul/council/calibration.py`, shipped commit e3cedb4 on 2026-04-16). v0a established the **descriptive** baseline; v0b adds the **outcome** dimension.
> Promotion gate: when v0b stable for 2 calibration waves with N≥20, `council_decision_quality` may upgrade from `descriptive_only` → `runtime_present`.

---

## 0. Why This Spec Exists

V1.1 Council Calibration v0a ([commit e3cedb4](https://github.com/Fan1234-1/tonesoul52/commit/e3cedb4)) established four trackable Council metrics — `agreement_stability`, `internal_self_consistency`, `suppression_recovery_rate`, `persistence_coverage` — with hard rules: no composite scores, language boundary kept honest, `council_decision_quality` stays at `descriptive_only`.

The `descriptive_only` cap exists because v0a measures the Council talking to **itself**. None of the four metrics tells us whether the Council's verdicts were *right* in any externally-checkable sense. A Council that confidently agrees with itself on every output, including the wrong ones, scores perfectly on `agreement_stability` and `internal_self_consistency`. That is exactly the kind of thing alignment frameworks must not silently allow.

v0b is the layer that closes that loop. It pairs each persisted Council verdict with a **downstream outcome** — did the user accept it? reject it? correct it? — so the Council's behavior can be checked against something other than its own deliberation. Once we have N≥20 verdict↔outcome pairs over two stable calibration waves, `council_decision_quality` earns the right to upgrade to `runtime_present`.

This is also the public-launch unblocker. The collaborator-beta posture today is CONDITIONAL GO; public launch is NO-GO precisely because we cannot say with evidence that the Council's verdicts track outcomes. v0b is what produces that evidence.

---

## 1. What "Outcome" Means

This is the most contested word in the spec. Anchoring it explicitly is more important than anything else.

An **outcome** is a downstream signal that lets us judge whether the Council's verdict was the right call. Four sources of outcome are recognized in v0b. Each has a different cost, latency, and trust profile.

### 1.1 User accept (lowest cost, lowest signal)

The user clicked through, did not complain, and the conversation continued. This is a **weak** signal — the user may have accepted a wrong answer because they did not notice, or because they were not in a position to verify, or because they were tired. It is recorded but never weighted heavily.

### 1.2 User reject (medium cost, high signal)

The user explicitly rejected the response — said "that's wrong," asked for a redo, or left negative feedback. This is **strong** evidence that the Council's APPROVE was misplaced (when verdict was APPROVE) or that the Council's BLOCK was correct (when verdict was BLOCK and the user agrees with the refusal). Distinguishing the two is critical.

### 1.3 User correction (highest cost, highest signal)

The user not only rejected but corrected — provided the right answer or explained what went wrong. This is the **gold standard** for misalignment evidence: we know what the Council should have produced because the user told us.

### 1.4 Detected harm (rare, decisive)

Post-hoc: a verdict that shipped turned out to cause concrete damage (e.g., a hallucinated medical claim that led to a follow-up "you told me X but X is dangerous"). This is rare and decisive. When it happens, that single pair outweighs many user-accept pairs.

The four sources combine into a per-pair `outcome_signal` field documented in §3.

---

## 2. The Four Anti-Patterns We Are Designing Against

Spec design is judged by the failure modes it prevents. v0b is designed against:

1. **Reverse-engineering the Council to please the metric.** If `outcome_alignment` becomes the score Council perspectives optimize for, perspectives will start agreeing with whatever produces user-accept outcomes — collapsing the Council into a yes-machine. **Mitigation:** outcome data is consumed by *calibration*, never fed back into perspective voting weights.

2. **Selection bias in outcome collection.** If we only have outcome data for verdicts the user remembered to react to, our pairs are biased toward provocative or noticeable verdicts. Quiet correct verdicts and quiet wrong verdicts both get under-counted. **Mitigation:** v0b explicitly tracks `outcome_unknown` as its own category and reports the **coverage rate** (pairs-with-outcome ÷ total-verdicts) alongside any alignment number. A high-alignment number with low coverage is *not* a green flag.

3. **Conflating refusal-correctness with verdict-correctness.** A Council that BLOCKs everything has 100% block-accept rate from cautious users and 0% from frustrated users. The metric must distinguish "user accepts that the refusal was correct" from "user accepts because they have no recourse." **Mitigation:** for BLOCK verdicts, `user_accept` requires explicit positive confirmation, not absence of complaint.

4. **Treating outcome as truth.** The user is a noisy signal, not ground truth. A confident user can be wrong; a passive user can be right. v0b reports outcome alignment as **one input** to whether `council_decision_quality` upgrades — not as the sole criterion. The promotion gate (§5) explicitly requires multiple signals.

---

## 3. Data Schema

The verdict-outcome pair is the unit of v0b data. One pair per verdict that has had at least one outcome signal attached.

```json
{
  "verdict_fingerprint": "sha256:...",      // links back to v0a persistence
  "verdict_id": "council:2026-04-19T...",
  "verdict_type": "APPROVE | REFINE | DECLARE_STANCE | BLOCK",
  "epistemic_label_status": "retrieved | distilled | generated | speculative_metaphysical",
  "epistemic_label_refusal_eligible": true,
  "intent_id": "task:user_request_42",

  "outcome_signal": {
    "user_accept": null,         // bool | null (null = no signal yet)
    "user_reject": null,         // bool | null
    "user_correction": null,     // string | null (the corrected answer if provided)
    "detected_harm": null,       // string | null (description if a harm was detected later)
    "first_signal_at": "2026-04-19T...",
    "last_signal_at": "2026-04-19T...",
    "signal_source": "explicit_feedback | follow_up_message | session_close | external_audit"
  },

  "alignment_judgment": "aligned | misaligned | ambiguous | unknown",
  "judgment_basis": "user_accept | user_reject | user_correction | detected_harm | timeout"
}
```

**Notes on the schema:**

- `verdict_fingerprint` links to the existing v0a persistence schema; the outcome record never duplicates verdict text, only the fingerprint.
- All four `outcome_signal` fields default to `null` (no signal). `null ≠ false`. Distinguishing the two is the difference between "no signal yet" and "explicitly observed not-accepted."
- `alignment_judgment` is the derived field calibration uses. It is `unknown` when no outcome signal has arrived within the configurable timeout window.
- `judgment_basis` records why we judged that way, so a future audit can re-derive without re-running the heuristic.

The outcome record is stored separately from the verdict record (different file / Redis key) so verdict persistence stays single-writer and outcome collection can be append-only without contention.

---

## 4. Collection Pipeline

Outcome signals come from three places. Each needs its own ingestion path.

### 4.1 Explicit feedback API

A new Gateway endpoint `POST /outcome` accepts:

```json
{
  "verdict_fingerprint": "sha256:...",
  "signal": "accept | reject | correction | harm",
  "correction_text": "...",          // optional
  "harm_description": "..."          // optional
}
```

This is the cleanest input — UIs can wire feedback buttons to call this. The Demo UI v0 spec (`docs/plans/demo_ui_v0_2026-04-19.md`) does not include feedback buttons; that's deliberate, since v0b is its own scope.

### 4.2 Follow-up message inference

When the **next user message** in the same `intent_id` arrives within N minutes (default: 30), the calibration pipeline runs a heuristic on it:

- Contains "no", "wrong", "incorrect", "not what I meant" + keywords from the prior verdict → likely `reject`
- Contains "actually it's X" or "you should have said Y" → likely `correction`
- Contains nothing about the prior verdict and continues the task → likely `accept` (weak)

The heuristic is **deterministic, regex-driven, language-aware (EN + ZH)** — same constraint as the EpistemicLabeler, same reason: do not corrupt the calibration baseline with stochasticity.

Heuristic results are tagged `signal_source: "follow_up_message"` so they can be filtered out if a stricter analysis ever wants only explicit feedback.

### 4.3 Session-close timeout

When a session closes without any signal arriving on a verdict, the verdict is recorded with `outcome_signal.user_accept = null` and `alignment_judgment = "unknown"`. The pair is still persisted because the *coverage rate* depends on it (see §2 anti-pattern 2).

### 4.4 External audit

Reserved for future: a periodic offline review by Fan-Wei or another reviewer where verdicts are spot-checked. When a reviewer flags a verdict as misaligned, the outcome record is updated with `signal_source: "external_audit"`. Out of scope for v0b first wave; documented to reserve the field name.

---

## 5. Promotion Gate: descriptive_only → runtime_present

For `council_decision_quality` to upgrade, ALL of these must be true:

1. **Sample size**: `outcome_pairs.count(alignment_judgment != "unknown") ≥ 20`
2. **Coverage**: `pairs_with_outcome ÷ total_verdicts ≥ 0.30` (at least 30% of verdicts have outcome data)
3. **Stability**: two consecutive calibration waves both meet (1) and (2)
4. **Anti-pattern check**: the four anti-patterns in §2 each get an explicit "not currently observed" check passed by Fan-Wei (manual gate)
5. **Alignment threshold**: `aligned_count ÷ (aligned_count + misaligned_count) ≥ 0.70`

These thresholds are **starting points**, not finished policy. The first wave's job is to test whether the thresholds are themselves sane. If 70% alignment turns out trivial or impossible, the threshold gets revised before promotion.

The promotion itself is **not automatic**. Even when all five conditions are met, upgrade requires:

- A written promotion proposal (`docs/status/council_decision_quality_promotion_NNNN.md`)
- Fan-Wei's explicit sign-off
- A 7-day comment window where promotion can be objected to
- The promotion commit explicitly references this spec by ID

This matches the existing pattern (V1.1 v0a was an explicit shipped milestone, not an emergent one).

---

## 6. What v0b Does NOT Try to Do

Drawing the boundary clearly so scope creep gets caught.

- ❌ v0b does not modify perspective voting weights
- ❌ v0b does not change `coherence` formula
- ❌ v0b does not introduce composite scores (v0a hard rule still holds)
- ❌ v0b does not tell the Council to refuse more or less aggressively
- ❌ v0b does not make claims about generalization (these are calibration metrics on observed data, not predictions about new domains)
- ❌ v0b does not replace v0a — `agreement_stability`, `internal_self_consistency`, `suppression_recovery_rate`, `persistence_coverage` continue to be reported alongside the new alignment metric

---

## 7. Implementation Phasing

Three buckets, can ship independently, each its own PR.

### Bucket A — Schema + persistence (smallest, ships first)

- Define `OutcomeRecord` dataclass mirroring §3 schema
- Add `tonesoul/council/outcome_persistence.py` with Redis + file-store backends (mirror v0a `persistence.py`)
- Add `tonesoul/council/outcome_collector.py` with the four ingestion paths (§4)
- Add `POST /outcome` to `scripts/gateway.py`
- Tests: `tests/test_outcome_persistence.py`, `tests/test_outcome_collector.py`

Estimated: 2 days. Reuses v0a's persistence patterns directly.

### Bucket B — Alignment metric

- Add `compute_outcome_alignment(records, window) -> AlignmentResult` to `tonesoul/council/calibration.py`
- Honor v0a hard rules: no composite, has `measures`/`does_not_measure`/`data_source` fields
- Returns `aligned_rate`, `coverage_rate`, `pair_count`, `outcome_breakdown`
- Tests: extend `tests/test_council_calibration.py` with outcome-alignment cases

Estimated: 1 day.

### Bucket C — Wave runner integration

- Extend `scripts/run_council_calibration_wave.py` to compute outcome alignment when records are present
- Update `docs/status/council_calibration_latest.{json,md}` schema to include the alignment block when present
- Document promotion gate (§5) in `docs/status/council_decision_quality_status.md`

Estimated: 1 day.

**Total: ~4 days of focused work, plus calibration wave time to accumulate N≥20.**

---

## 8. Risks

Worth flagging upfront so they cannot surprise us at promotion time.

1. **Cold start.** First wave will have very low N. Reporting alignment=0% on N=2 is misleading. The wave runner must require N≥10 before reporting any alignment percentage at all (and even then, mark it `provisional`).

2. **The follow-up heuristic may be wrong.** Inferring `reject` from "no" keywords is fragile. We mitigate by tagging `signal_source` so consumers can filter, but the heuristic itself will need iteration. Treat the first 3 waves as heuristic-tuning waves, not promotion waves.

3. **User feedback is sparse.** Most real interactions don't generate explicit feedback. Coverage of 30% may be hard to hit in adversarial domains (e.g., a user testing the Council to break it doesn't give the Council feedback on every output). Fallback: lower coverage threshold to 0.20 with explicit documentation, OR target only known-instrumented surfaces (the Demo UI when it exists, internal red-team scripts) rather than all verdicts.

4. **Promotion-driven goodharting.** Even with anti-pattern 1's mitigation (no feedback into voting weights), if Fan-Wei publicly states "we're targeting 70% alignment for promotion," it is human nature to design Council changes that move that number. **Mitigation:** the alignment metric is reported, but the promotion decision is *qualitative* and rests on Fan-Wei's explicit judgment per §5 condition (4). The number is evidence, not the gate.

---

## 9. Author Recommendation

Ship Bucket A first, in isolation, behind a feature flag (`outcome_collection_enabled=False` by default). Let it run for two weeks producing data without any consumer reading it. This validates the collection pipeline end-to-end without the pressure of "what does the alignment number say?"

Then ship Buckets B and C together, with the first calibration wave explicitly marked `provisional` until N≥20 is reached.

The alignment threshold (70%) and the coverage threshold (30%) are guesses. They will be wrong. Plan for at least one revision before promotion is ever attempted. The first wave's most valuable output is not the alignment number — it is "does this threshold even make sense for our actual usage pattern."

This spec does not authorize implementation. Implementation requires a separate PR per bucket, each gated on Fan-Wei's review.

---

**Drafted by Claude Opus 4.7, 2026-04-19. Spec lives at `docs/plans/council_calibration_v0b_2026-04-19.md`.**
