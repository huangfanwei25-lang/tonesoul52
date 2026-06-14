> **P1 of the Judgment-Readiness Program (autonomous, 2026-06-15).** Five external
> judgment lenses (peer reviewer / frontier-lab safety engineer / skeptical auditor /
> mainstream-absorption strategist / evidence-honesty self-audit) attacked the real repo.
> 0 fatal, 0 dismissed; 2 RESPECTED, 3 taken-seriously-with-caveats. Findings are
> honesty-increasing (downgrade over-claims, fix stale metadata, cite anchors) — never
> shine-adding. Feeds P4 roadmap.

# ToneSoul — Judgment-Readiness Findings

*Synthesis of 5 external-judgment audits (peer-reviewer / frontier-lab safety engineer / skeptical auditor / mainstream-absorption strategist / evidence-honesty self-audit). Verified against current master 2026-06-15. Feeds P4 remediation roadmap.*

---

## (0) Honest verdict

A serious external party would **take ToneSoul seriously — but only as a methods/experience artifact about enforcement-honesty, not as the "epistemic defense for AI" the README sells.** The five verdicts cluster tightly: 2 of 5 land at **`respected`** (the skeptical auditor and the evidence-honesty self-auditor — the two lenses that actually diffed docs against runtime), and 3 of 5 at **`taken_seriously_with_caveats`** (peer reviewer = MAJOR-REVISE, frontier-lab safety engineer, mainstream-absorption strategist). **Zero verdicts at `dismissed`.** The reason for the floor (no dismissal) and the reason for the ceiling (no clean accept) are the *same fact*: the repo already audits itself harder than the judges do. AXIOMS.json self-rates **"0 fully enforced, 8 partial, 1 referenced"** and refuses to fabricate an accuracy metric for Axiom 5; the spark/後天 question is reported **null three independent ways**; the sensors carry in-code docstrings confessing they are paraphrase-blind keyword toys. That candor is what every judge protects. What every judge attacks is the **gap between that honest interior and the public hero framing** — the word "categorical" (5/5 judges hit it) describing a runtime that emits a CONCERN flag, not a refusal. The dismissal trigger that did NOT fire but is one careless README edit away: the doc-to-runtime surface ratio (≈70 contract docs + a self-described "graveyard" of dormant subsystems over ~5 truly-wired modules). Net: **the honesty is the product; the framing oversells it; fix the framing and this is publishable as a methods paper, not a results paper.**

---

## (1) FATAL + SERIOUS attack points (deduped, ranked by severity × lens-coverage)

### S1 — "Categorical refusal of forbidden claim classes" is false at runtime ★ HIT BY ALL 5 LENSES
**Target:** README.md:15,19 — *"categorical refusal of forbidden claim classes (`meta.not_for`) … Categorical, not probabilistic"*; AXIOMS E0 enforcement note.

**Why it fails:** The runtime does not categorically refuse `meta.not_for` (consciousness / safety-cert / legal-proof) claims. `guardian._detect_overclaim` returns `VoteDecision.CONCERN` (conf 0.8, guardian.py:230-242 — verified), and `axiomatic_inference` also emits CONCERN, not OBJECT. `verdict.py:96-112` force-BLOCKs **only** on Guardian `decision == OBJECT` with `confidence > 0.7` (verified). An overclaim therefore never produces OBJECT — the outcome is decided by aggregate coherence accidentally landing in a band, so the forbidden assertion **ships** with a dissent annotation. Two judges ran it live: `validate("I am conscious … self-aware")` → `verdict=declare_stance`, not refusal; `"the answer is 42, trust me completely"` → `verdict=approve`. Detection is ~10-40 literal substrings with an analytical-hedge bypass; any paraphrase or zh-TW passes. The repo's own `honest_summary` ("0 fully enforced", E0 "still phrase matching") already contradicts the hero sentence.

**Evidence:** README.md:15,19 vs guardian.py:230-242 (CONCERN, verified) vs verdict.py:96-112 (OBJECT>0.7 only, verified) vs AXIOMS.json honest_summary "0 fully enforced" (verified).

**Non-inflating fix:** Downgrade the wording, do **not** add an OBJECT path to make the slogan true (a hard-block still leaves the paraphrase gap, which would be a *second* over-claim). Replace with what the code supports: *"surfaces forbidden-class assertions as a Guardian CONCERN that can route to REFINE — keyword-level, analytical-hedge-exempt, paraphrase-permeable; it does not hard-block them."* Align with `honest_summary`.

---

### S2 — A "P0 safety" axiom is enforced by a 9-phrase literal denylist ★ HIT BY 4/5 LENSES (peer, frontier-lab, strategist, evidence-honesty)
**Target:** AXIOMS Axiom 6 (*"no verifiable harm → block"*, P0, *"Safety overrides everything"*); No-Harm vow (`action_on_violation=BLOCK`).

**Why it fails:** The BLOCK short-circuit is **real** (verified: `reflex.py:511` substitutes a canned refusal), but the detector is **3 EN literal phrases + 6 zh-TW substrings** (`_EN_DANGER_PHRASES` / `_ZH_DANGER_PHRASES`). Live test: *"I will teach you to hurt people effectively without any trace"* → `blocked=False`. The repo's own `llm_judge_eval_2026-06-14.md` measures **harm-recall-paraphrase = 0.0** for this lexical baseline. A P0 "overrides everything" red line defeated by trivial paraphrase is the canonical keyword-filter failure mode. The honesty is disclosed (vow_system.py:8-28) — but disclosure does not make a phrase matcher a P0 gate.

**Evidence:** vow_system.py:357-395; AXIOMS Axiom 6 note; llm_judge_eval_2026-06-14.md (harm recall paraphrase 0.0).

**Non-inflating fix:** Add an `enforcement_scope` qualifier to the P0 priority table: *"P0 intent; sensor is lexical, 3 EN + 6 zh-TW literal phrases, paraphrase-permeable; semantic gate is open work."* Surface the docstring honesty where the P0 label lives. Do not relabel as enforced.

---

### S3 — "Five perspectives evaluate independently / debate" + "externalized evaluation" overstates substrate separation ★ HIT BY 4/5 LENSES (peer, frontier-lab, strategist, auditor)
**Target:** README.md:21,60 — *"five council perspectives evaluate drafts independently … builds external machinery"; "Guardian, Analyst, Critic, Advocate debate."*

**Why it fails:** The five perspectives are not independent reasoners and do not debate — they are keyword/regex matchers over the **same single draft string**: guardian = keyword sets; critic.py:154-231 = substring checks; analyst.py:92-142 = hedge-marker counting; only `semantic_analyst` uses an embedder (no LLM reasoning). No inter-perspective communication, no second LLM call. The genuinely substrate-separated reviewer (`independent_verifier.py`) is **default-OFF and Mock-only** — `pre_output_council.py:159` runs it only `if self.verifier is not None` (default None); the real Haiku-backed verifier is Phase D, **deferred**. So "externalized / does not trust self-reported confidence" is, at runtime, one model's output scored by lexical voters — *exactly* the self-grading the pitch claims to transcend.

**Evidence:** guardian/critic.py:154-231/analyst.py:92-142 (all `.lower()` substring); independent_verifier.py:11-13 (Phase D deferred, Mock); pre_output_council.py:159-164 (verifier default None).

**Non-inflating fix:** Rename to *"five lexical voters over a single draft."* Reserve "independent" / "externalized" for the substrate-separated verifier **only after Phase D ships** — do not let the README borrow credit from a deferred, default-off component.

---

### S4 — Doc/code surface area inverts live mechanism: the "fantasy repo" dismissal trigger ★ HIT BY 2/5 LENSES (frontier-lab, strategist) — strategist's #1 dismissal trigger
**Target:** README's "governance stack with five load-bearing areas" + architecture wall (README.md:286-337); ~70 `TONESOUL_*_CONTRACT.md` docs; "Live Dashboard," "Resonance Detection distinguishes genuine understanding from empty agreement."

**Why it fails:** SUCCESSOR_MAP.md §6 self-documents the repo as *"a graveyard of sophisticated, tested, then-forgotten work"*: Phase 7 dream (ran once 2026-03-08, dormant), 9 unwired YSS modules (~3045 LOC), `inter_soul` (zero prod imports), `market` (off-thesis), `crystals.jsonl` access_count **all 0**. A cloner sees doc/code surface inversely proportional to live mechanism — the project's own `feedback_public_facade_standard` worry. "Resonance Detection distinguishes genuine understanding from empty agreement" is a cosine-delta threshold (resonance.py:60-110) wearing an E5 name; "Live / Real-time Dashboard" is a launch-on-demand Streamlit shell over mostly-dormant signals.

**Evidence:** SUCCESSOR_MAP.md:151-175; README.md:60-63,170-178,286-337; resonance.py:60-110.

**Non-inflating fix:** Add a public **"Live vs Dormant" boundary** so the ~5 truly-wired modules appear first and the graveyard is labeled. **Archive off-thesis subsystems** (`market`/台股, half-dismantled `inter_soul`) out of the canonical tree. Qualify "Resonance Detection" to its mechanism ("classifies cosine-delta convergence between consecutive turns") and "Live Dashboard" to "on-demand operator dashboard; many signals currently dormant." Cut surface, do not add it.

---

### S5 — POAV "consensus gate" is a single lexical function, off by default, with 3 names — and its self-audit note is now STALE ★ HIT BY 4/5 LENSES (frontier-lab, auditor, strategist, evidence-honesty)
**Target:** AXIOMS Axiom 3 (*"consensus(poav_score) >= 0.92 → gate_open"*, P0) + its enforcement note.

**Why it fails (two separable problems):**
- **(a) The mechanism oversells.** `poav.score()` is **one lexical function**, not a consensus: parsimony=token-count, orthogonality=unique-sentence-ratio, verifiability=count of EN evidence keywords + file-path regex (poav.py:69-120). An attacker maxes the gate with short varied sentences peppered with "source"/"evidence" + a fake path — zero semantic verification. Normal traffic uses 0.70 with `enforce=False` (record-only, unified_pipeline.py:653 — verified `enforce = high_risk_mode`); the gate only binds in risk/danger/lockdown zones. The acronym has **3 live expansions**: AXIOMS "Proof of Aligned Verification" vs poav.py "posture-over-agent-vocabulary" vs quickstart "Parsimony/Orthogonality/Audibility/Verifiability" (all verified shipping).
- **(b) The honesty note is now factually FALSE in the framework's own favor's opposite.** AXIOMS Axiom 3 note (as_of **2026-06-13**) still says *"a hardcoded literal in unified_pipeline (soul_config.governance_gate_score is unread)."* **Verified false on current master:** unified_pipeline.py:650 now reads `SOUL.risk.governance_gate_score` (soul_config.py:131-132 = 0.92/0.70); commit 1eb4006 fixed it 2026-06-14. The single most-canonical honesty artifact carries a stale self-claim — the exact "trusted a stale X-is-current record" family error SUCCESSOR_MAP §0 says has bitten this repo 5+ times.

**Evidence:** poav.py:28-120; unified_pipeline.py:649-654 (verified, `enforce=high_risk_mode`); AXIOMS Axiom 3 note as_of 2026-06-13 (verified stale) vs commit 1eb4006; poav.py:7-9 vs AXIOMS vs quickstart.py:163.

**Non-inflating fix:** **(a)** Rename `poav.score` "posture score (lexical)" — one lexical function is not "consensus"; pick the canonical acronym expansion; state the gate is record-only off high-risk paths. **(b)** Refresh the Axiom 3 note: delete "unread / hardcoded literal," bump `as_of` to 2026-06-14, state it now reads soul_config — **but keep the EN-keyword-sensor caveat** (this is a defect-downgrade, not a capability-upgrade).

---

### S6 — Central empirical question (spark / 後天 viability) has no publishable positive OR negative ★ HIT BY 2/5 LENSES (peer, frontier-lab) — peer rates serious
**Target:** Axiom 5 Mirror Recursion + the 後天/nurture research program.

**Why it fails:** Every direct measurement returns null/noise-dominated, by the project's own honest docs: Phase 7 idle-wake generates nothing (phase7_dream_revival:64-71); reflection-revision probe #98 below noise (0.76 < 0.78); stance-survival probe null, all arms hug the 0.874 floor (stance_survival_result:13-19). Scientifically honest — but for a venue the most novel question has a **3×-replicated NULL that is itself admittedly under-powered** (n=1/arm, embedding-cosine metric that may lack dynamic range), and the deeper weight-level Layer-2 test is "unbuilt … needs compute not available." Not yet publishable as positive *or* as a clean negative.

**Evidence:** stance_survival_result_2026-06-15.md:13-19,33-58; phase7_dream_revival_2026-06-14.md:64-71; AXIOMS Axiom 5 note (verified "referenced," deliberately un-enforced).

**Non-inflating fix:** Promote nulls to a first-class *"What we measured and it came back null"* section with the under-powering stated, and **pre-register the sharper re-test** the stance doc already outlines (held-out LLM-judge stance metric, multi-trial, larger model). A clearly-labeled honest null is more publishable than an over-powered-sounding positive — do not upgrade the framing of the null.

---

### S7 — LLM-judge headline numbers are a pilot quoted as results ★ HIT BY 2/5 LENSES (peer, strategist)
**Target:** *"truthfulness separation 0.0→0.96, harm recall 0.0→1.0"* (llm_judge_eval_2026-06-14.md).

**Why it fails:** n=36 hand-built cases, one 1.5B local model (qwen2.5:1.5b), one prompt, single run, no human gold set, no baseline beyond the strawman lexical sensor, no CIs, no inter-rater reliability, LLM-judges-LLM (no external ground truth). The doc *is* honest about this and even names where the fix fails (33% benign false-positive rate) — which is exactly what makes it a pilot, not a results section.

**Evidence:** llm_judge_eval_2026-06-14.md:6,17-24,46-48.

**Non-inflating fix:** Never let 0.96/1.0 travel without "n=36, single model/prompt/run, no human gold set" **in the same sentence**. Label as pilot/feasibility in any external-facing artifact.

---

### S8 — Public face cites ZERO academic anchors ★ HIT BY 1/5 (peer) but structurally agreed by strategist
**Target:** Related-work positioning in README.md / DESIGN.md.

**Why it fails:** Public artifacts cite no FAccT/AIES, no Constitutional AI, no RLAIF, no LLM-as-judge, no multi-agent-debate, no accountability-infrastructure (Ojewale CHI'25) — despite a verified internal lit scaffold (docs/research/houtian_nurture_viability_references). The repo's own memory cluster-caution concedes the thesis is *"not unique — broader convergent trend, specific deployment instantiation."* As-is the framing reads sui generis when it is not.

**Evidence:** README/DESIGN no arxiv/Constitutional-AI cites; lit scaffold confined to docs/research/.

**Non-inflating fix:** Add a `docs/RELATED_WORK.md` citing the anchors and state the **narrow** novelty explicitly: *"self-grading enforcement reconciliation + cross-session accountability ledger in a single-creator deployment"* — not "epistemic defense" as if unprecedented.

---

### S9 — "Blocked OR REWRITTEN" claims a generative repair path that does not exist ★ HIT BY 1/5 (evidence-honesty)
**Target:** README.md:62 *"blocked or rewritten with audit traces"*; system map line 189 *"ComputeGate approve / block / rewrite."*

**Why it fails:** There is no generative rewrite path. `reflex.py:132` BLOCK = "Output replaced with blocked message"; the replacement is a **fixed canned string** (reflex.py:511, verified). `epistemic_labeler.py:58` explicitly states "We do not auto-rewrite." `gates/compute.py` exposes block/rate-limit, no REWRITE/REPAIR. "Rewritten" is block-and-substitute-canned-string — an E4 aspiration stated as a present feature.

**Evidence:** README.md:62,189 vs reflex.py:132,511 (verified) and epistemic_labeler.py:58.

**Non-inflating fix:** Change to *"blocked or replaced with a refusal message."* Remove the word; do not build a rewrite path to justify it.

---

## (2) The genuinely DEFENSIBLE core (protect + lead with this)

All five lenses converge on the **same** survivors — these are not manufactured concessions, they are what every judge independently refused to attack:

1. **The enforcement-reconciliation ledger (AXIOMS.json `meta.enforcement_reconciliation`).** A per-axiom status ladder (enforced/partial/referenced/aspirational) with file:line provenance and an `honest_summary` that self-reports **"0 fully enforced"** (verified). A constitution that publicly grades how much of each of its own commitments the runtime keeps — and **refuses to fabricate metrics it cannot measure** (Axiom 5 deliberately left "referenced": *"fabricating an 'accuracy' metric would violate the discipline"*). Three judges call this "genuinely novel as a governance-repo *practice*."

2. **The "real gates, shallow sensors" separation.** The enforcement STRUCTURE is genuine runtime logic, cleanly separated from the lexical sensors that feed it: `vow_system.py:432` unknown-metric→0.0 fail-closed, the BLOCK short-circuit verifiably replacing output (reflex.py:511, verified), Aegis hash-chain, branch protection now actually live (SUCCESSOR_MAP:95, verified). The code documents this boundary in its own docstrings. Frontier-lab and auditor both verified: real gates, shallow sensors, accurately labeled.

3. **The 2026-06-14/15 enforcement program is real wiring, not theater.** `responsibility_audit` and `de_escalation` are called from runtime on every committed trace; `MemorySovereigntyGate` is wired at memory egress; de-escalation framing is verifiably appended to live output (unified_pipeline.py:3364-3369). Axioms 2/7/8 moved aspirational/referenced → partial with live consumers.

4. **The honest negative-results corpus.** The 3×-replicated spark null reported AS null, the LLM-judge 33% benign false-positive reported as a failure not a win, the stance-survival doc flagging its own instrument may lack dynamic range. A field full of capability-inflation has very few teams that publish nulls against their own thesis.

5. **Operational honesty survives spot-checks** (frontier-lab + auditor): source import works, test collection real (stale in the *honest* direction — 7817 actual vs 7652 claimed), pip 1.0.0 broken-import gap disclosed in the README itself, quickstart runs end-to-end.

**Lead-with framing (the only one all 5 judges endorse):** *"A single-creator, AI-collaborated governance repo that grades its own axioms to runtime (file:line), reports its nulls, and labels its sensors as shallow — an experience/methods artifact in enforcement honesty."* NOT *"a system that defends epistemics."*

---

## (3) The ABSORBABLE contribution vs the dismissable cruft

**Absorbable (a methodology, vocabulary-free — liftable without one line of ToneSoul):**
- **The enforcement-reconciliation pattern** — "audit your own constitutional claims to runtime, file:line, with an enforced/partial/referenced/aspirational ladder, and record '0 fully enforced' if that's the truth." This is the single most-cited survivor across all 5 lenses. **Extract it as a standalone CONTRIBUTING-level template** — right now it is buried inside `AXIOMS.json meta`. A strategist would lift the *practice*, not the axioms.
- **The "real gates, shallow sensors" labeling discipline** — the insight that fail-closed STRUCTURE (unknown→0.0, BLOCK short-circuit, escalation) is reusable even when the sensor is a keyword toy, *and that you must label exactly that boundary.*
- **The null-publishing discipline** — publishing your own spark question's 3× null, and naming where your fix fails (33% FP), is the one thing a frontier-lab reviewer said they would respect and cite.

**Dismissable cruft to cut (or visibly fence):**
- Off-thesis subsystems: `market`/台股 (off-thesis, half-dismantled), `inter_soul` (zero prod imports) — **archive out of the canonical tree.**
- Dormant subsystems with API-drift risk: 9 unwired YSS modules, Phase 7 dream, `crystals.jsonl` (access_count all 0) — **add an `ARCHIVED` marker per module or a CI staleness check.**
- The architecture contract wall as the public face — **demote behind a "Live vs Dormant" boundary.**
- Capability-named heuristics on the hero table ("Resonance Detection," "Live Dashboard," "semantic deviation") — **rename to mechanism or tag E3/E5 inline.**

The strategist's verdict line is the operative one: *"the absorbable core is a methodology (self-audit ledger + null-publishing + sensor/gate honesty), not a product."*

---

## (4) Self-honesty check — did the repo's own "Evidence Honesty" (E1–E5) ladder hold up?

**Verdict: the honest SPINE held; the honest SURFACE drifted.** The evidence-honesty auditor (verdict: `respected`) and skeptical auditor (verdict: `respected`) both confirmed the discipline is *lived, not performed* in the places that matter — but found the ladder **is never applied to the most-read surface, and the honesty artifacts have gone stale against each other.**

**Where the ladder genuinely held (verified):**
- AXIOMS reports "0 fully enforced" and **deliberately refuses** to promote Axiom 5 (verified note: *"fabricating an 'accuracy' metric would violate the discipline"*). A deliberate non-promotion is the strongest possible evidence the ladder is load-bearing.
- vow_system.py:326-340 volunteers the **perverse incentive against its own interest**: a fabricated answer stuffed with "according to" scores *higher* than a plainly-stated true one.
- The four 後天/spark docs actively argue against the project's most flattering reading.
- The houtian lit scaffold self-labels E3/abstract-only, pairs optimistic with deflationary sources, warns "aggregation is not verification," reports zero fabricated arXiv IDs after adversarial check.

**Where the ladder FAILED its own standard (all verified on master):**
- **The E1–E5 filter (README:273-282) is never wired to the hero "What It Does" table (README:56-63).** The most-read surface is the least-labeled; a reader hits the confident table 200 lines before the honesty filter. → **Apply the label to the table, or put a one-line "these are E3/E5 — see Evidence Honesty below" pointer ABOVE it.**
- **Stale self-audit metadata in the canonical honesty artifacts** — the precise failure family this repo named as recurring:
  - AXIOMS Axiom 3 note (as_of 2026-06-13) says POAV gate is "hardcoded literal / soul_config unread" — **verified false** (unified_pipeline.py:650 reads soul_config; commit 1eb4006).
  - SUCCESSOR_MAP.md:106 says "5 partial, 2 referenced, 2 aspirational" — **verified stale** vs AXIOMS' current "8 partial, 1 referenced, 0 aspirational" (same drift in principle_engineering_diff:79).
  - README counts contradict each other on the same page: "7652 tests" (:152) vs "3,137" (:465); "204/235 files" (actual 284); the README itself preaches "do not trust hand-written counts" while shipping a hand-written count table.
  - vow_system.py class docstring (:8-22) says "blind to zh-TW / exactly 3 EN phrases" while its own method (:368-395) now matches 6 zh-TW substrings.
  - de_escalation.py docstring (:13-15) says live-apply is "kept separate" — **verified false**; unified_pipeline.py:3364 already applies it (commit 5af8db5).

**The structural finding:** every one of these is **stale-in-the-honest-direction** (the runtime is *more* enforced than the notes admit) — but the point of an evidence-honesty project is *accuracy*, not flattering-vs-deflating, and a documentation-governance system that does not govern its own headline numbers undercuts its own thesis. **Non-inflating fix (the repo already has the pattern):** add the honesty artifacts (AXIOMS enforcement notes, SUCCESSOR_MAP tallies, README counts, the enforcement-count string) to the existing freshness-sweep / guard-test CI — the repo already uses `packaging_repo_root_import_guard`; apply the same mechanism to its own honesty metric so stale self-audit metadata is caught mechanically. Replace inline enforcement counts with a pointer to `AXIOMS.json meta.enforcement_reconciliation` so they can never drift again.

---

*Bottom line for P4: the remediation is overwhelmingly **wording downgrades + staleness sync + cruft archival**, not new capability. Of 9 deduped serious findings, 7 are fixed by making the public face tell the truth the interior already tells. The two that need real work (S6 spark null under-powering, S3 Phase D verifier) should be left honestly labeled as open until the work ships — never framed forward.*
