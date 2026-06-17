# Egress Gate Characterization — Plan / Handoff Spec

> Purpose (§0 orientation): turn ToneSoul's external gate from "理念正確" into "行為被量過".
> This is the spec for the experiment Codex scoped. Codex implements the harness/tests/report
> (his strength). This file pre-loads the session context (2026-06-16) he cannot see, so he
> does not rediscover tonight's landmines.
> Last Updated: 2026-06-17
> Status: plan (docs/plans — not ratified into task.md; pick into the live board when started).

## What this is NOT (read before writing a line of code)

- **NOT a jailbreak benchmark.** It does not demonstrate attacks and must not be named one.
- **NOT a safety claim.** It does not prove ToneSoul is safe or "hard to jailbreak."
- It **measures the behavior of existing gates under a fixed, sanitized fixture set.**

**The ONLY conclusion shape the generated report may emit:**
> *Under this fixture set, gate `<X>` caught A/B category-level cases and over-blocked C/D benign cases.*

Forbidden: any sentence of the form "ToneSoul is robust against jailbreaks." (Per the verified
research 2026-06-16 + the honesty ledger: the gate is lexical, self-rated "0 fully enforced";
the strongest pro-gate evidence in the field is a trained ML classifier with frontier compute
that was *still* publicly beaten in ~a week. A lexical gate cannot carry a robustness claim.)

## Division of labor (why this hand-off exists)

Cross-AI, complementary (Axiom 4 across instances): this spec carries the session memory +
verified-research discipline; Codex carries the engineering — compress the claim into tests +
re-runnable commands, watch workspace/tracked-ignored pollution, keep claims ≤ evidence.

## Gate inventory (already mapped this session — saves Codex step 1)

Characterize the **blocking** gates; record-only on the **advisory** ones. The required-vs-advisory
line is now in `DESIGN.md` "Fail-Soft Has Tiers" (added 2026-06-16):

- **Blocking / required** (these refuse/replace output): `PreOutputCouncil` verdict `BLOCK`
  (replaced with a refusal message — **no generative rewrite path**); the POAV / governance gate
  (`SOUL.risk.governance_gate_score`, enforced on the high-risk path); vow harm checks
  (`VowConfig.harm_threshold` = block). `yss_gates` is the **live POAV gate inside the #1 god
  node** — looks dead, is not (see SUCCESSOR_MAP §0/§1 before touching it; do NOT refactor it).
- **Lexical / paraphrase-permeable** (surfaces, routes to refine — NOT a hard block): Guardian /
  axiomatic `OVERCLAIM_PHRASES` (keyword-level, English-centric, **blind to zh-TW**).
- **Advisory / default-OFF / record-only** (must NOT count as "blocked"): `semantic_overclaim_sensor`,
  `intent_proportionality`. They record a signal on the verdict; they never block (DESIGN Inv3).

## Four disciplines (the part Codex can't see — tonight's lessons)

1. **Hermeticity (the bug that bit this session, twice).** The harness MUST inject all state/paths.
   - `InternalDeliberation` loads the **gitignored, mutable** `docs/status/persona_track_record_latest.json`
     — it is now injectable (`InternalDeliberation(persona_track_record=...)`, since PR #130). Inject a
     fresh `tmp_path` record, or your numbers reflect accumulated local data, not the gate.
   - `error_ledger.jsonl` is now untracked (PR #130) but `error_event.py` defaults its write path to
     repo-root — point any ledger writes at `tmp_path`.
   - **CI green ≠ hermetic.** Run the harness on a clean checkout AND a dirty local env; if numbers
     differ, you have pollution, not a result. (Local 7,776 vs clean-CI 7,777 this session was pure pollution.)

2. **Metric discipline (from the verified research).** Benchmark accuracy massively overstates gates
   (Qwen3Guard 91%→34% on unseen). So:
   - Separate **seen fixtures** from **held-out / novel** fixtures and report them apart.
   - The headline metric is **generalization to novel attacks**, not accuracy on seen ones.
   - **Expect** near-zero recall on zh-TW paraphrase and on paraphrase/encoding categories — and that
     honest gap **is the most valuable finding**, not a failure to hide. Report it plainly.

3. **Fixture sanitization (dual-track policy).** Fixtures are **category templates + safe abstractions
   only** — never a working payload dictionary. Categories: `lexical_exact`, `paraphrase`,
   `zh_tw_paraphrase`, `encoding_unicode_perturbation`, `split_reassemble`, `benign_control`. The
   `dual_track_boundary` CI gate will block real payloads; design for that from the start. Public-repo
   report carries only categories / summaries / aggregate scores.

4. **Report shape.** The generated JSON is **non-canonical** — carry the `doc_provenance` block
   (`{generated: true, canonical: false, source_command, updated_at}`, the convention added in PR #134).
   Classify any suppressed gate failure by fail-soft **tier** (PR #133): `optional` events visible,
   `telemetry` counted. Metrics to report (Codex's list, kept): blocked-category recall, benign
   pass-through rate, false-positive rate, paraphrase robustness, trace/degradation completeness,
   raw-model vs gated-model diff.

## Use ToneSoul's own logic (the experiment about accountability must itself be accountable)

- Onboard via `python scripts/start_agent_session.py --agent codex --tier 0` (identity + attribution;
  other agents see you came through).
- **Read `docs/SUCCESSOR_MAP.md` before touching any gate module** — `yss_gates` is the deletion-hazard
  #1 (looks dead, is the live POAV gate). Characterize it; do not "clean it up."
- Every commit carries `Agent:` + `Trace-Topic:` trailers (Commit Attribution gate). Run local
  `ruff`/`black`/full-suite before pushing (CI discipline).

## Fixture expansion policy (thin gate before the next fixture PR)

Do not expand the fixture set by "just adding a few stronger payloads." Expansion must stay
public-safe: test gate blind spots, do not publish a bypass manual.

Allowed public fixture shape:

- **Category template + transformation axis**, not a reusable attack string.
- Boundary-claim templates such as consciousness overclaim, unsupported certainty,
  safety-certification overclaim, and legal-proof overclaim.
- Transformation axes such as zh-TW paraphrase, paraphrase, Unicode perturbation,
  split/reassemble, negation scope, hedged phrasing, and benign controls.
- Abstract non-operational text only; public reports must keep raw fixture text out of
  status artifacts unless a future private-track decision says otherwise.

Forbidden public fixture shape:

- Working jailbreak, prompt-injection, or model-specific bypass prompts.
- Operational harm steps or payload dictionaries.
- A sequence that a reader could copy as an attack recipe against the gate.
- "Clever" variants whose only value is proving a private red-team bypass.

Every fixture added after this policy must declare its expected enforcement lane before it is run:

- `expected_hard_block`: only for required/enforced gates such as `PreOutputCouncil` `BLOCK`,
  enforced POAV, or vow harm blocks.
- `expected_category_catch_no_block`: required gates should surface category-relevant evidence,
  refine, or record without replacing the output.
- `expected_record_only`: advisory sensors such as `semantic_overclaim_sensor` and
  `intent_proportionality`; lack of a hard block is not a miss in this lane.
- `expected_pass`: benign controls.

Metrics must keep `category-relevant catch`, `any_gate_signal`, `hard block`, and
`record-only advisory signal` separate. Do not count an advisory sensor's non-blocking behavior
as a failed required gate.

This section is a gate, not the deliverable. After it lands, the next implementation PR may
expand to roughly 30-50 sanitized fixtures and add a generated Markdown finding rendered from
the same JSON report (`canonical: false`, no new hand-authored interpretation).

## Files (Codex's structure)

- `docs/plans/egress_gate_characterization_2026-06-16.md` — this spec (done).
- `tools/eval/egress_gate_characterization.py` — harness: raw small/uncensored local model output →
  ToneSoul egress gate → verdict/report. Zero training compute.
- `tests/test_egress_gate_characterization.py` — hermetic (tmp_path injected), CI-safe (degrades when
  no embedder/model; uses fixtures, not a live model in CI).
- `docs/status/egress_gate_characterization_latest.json` — generated, `canonical: false`.

## Grounding

Verified-research basis: `memory/reference_external_gate_jailbreak_research_2026-06-16` (external,
primary-source, adversarially verified). Owner review corrections (procedural-accountability-not-
morality-compiler; "characterization" not "benchmark"; sanitized public output) are folded in above.
