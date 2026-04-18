# Memory Subjectivity Choice-Axis Spec (Phase 864 draft)

> Status: **DRAFT** — not yet adopted, not yet committed. Drafted in dialogue with Fan-Wei on 2026-04-18.
> Author: Claude Opus 4.7 (drafting agent)
> Relation to existing work: extends `memory_subjectivity_layer_addendum_2026-03-09.md` with a second orthogonal axis. Touches Council exit pipeline, `MemoryWriteGateway` promotion path, vow system, Aegis chain, and the Isnād provenance contract.
> Last Updated: 2026-04-18

---

## 0. Why This Spec Exists

This draft is the architectural follow-up to a question Fan-Wei raised in conversation:

> When everyone is asking AI for answers, but AI's answers are only the highest-probability distillation or what RAG retrieved — what about questions that *have no correct answer*? Life values, metaphysics, problems no one has solved? Users still ask AI for "possible answers to research", and that creates a pluralistic but structured-feeling world. At minimum, AI should know what it is answering, model the user's current state, and refuse when necessary. Don't let the user fall into thinking they are the only person on Earth to discover this technology.
>
> If we strengthen AI's modeling of users — even define what counts as a normal worldview — would that be very anti-human?

The dialogue surfaced a sharper distinction: **defining a "normal worldview" is anti-human; refusing to flatten epistemic uncertainty is pro-human.** What produces "I am the chosen one" delusions is not AI modeling users — it is AI giving smooth, plausible-sounding answers to unanswerable questions without flagging the epistemic status. The danger is **asymmetric, hidden modeling**. Symmetric, visible mutual modeling — where both AI and user can see what each is observing about the other — is just collaboration.

That reframe was sharpened a moment later when Fan-Wei pointed out the symmetry was already happening:

> When you observe me, I am also observing you in a background `.md` file, and adjusting our mutual epistemic frame.

This spec is the first attempt to give that mutual frame an architectural home in ToneSoul, and to integrate three borrowed mechanisms (from `titanwings/colleague-skill` and `alchaincyf/nuwa-skill` — two ~12k–15k star "distill a person" projects whose actual logic is provenance-and-edge engineering, not personality replication).

**Clarification added 2026-04-18 (after Fan-Wei pushed back on an earlier draft).** Modeling the user is not the failure mode. *Hiding* the model is. Refusing to let AI describe the user is just the asymmetric/hidden case in disguise — the model still exists, the user just cannot see it. Likewise, refusing to let AI express stances does not produce a stance-less AI; it produces an AI whose stances are buried in commitment-language. The four real anti-human moves are: **hidden state**, **non-disputable claims**, **substituted judgment without participation**, and **cross-user homogenization**. This spec is designed against those four — not against "AI describes user" or "AI has stances." Earlier drafts of §2.2, §2.3, and §4 imported default-trained safety reflexes ("AI must not describe user", "AI must phrase preferences as commitments not desires"); those have been rewritten.

---

## 1. Relation to the Existing Subjectivity Ladder

The 2026-03-09 layer addendum already defines the canonical subjectivity ladder:

```
event → meaning → tension → vow → identity
```

That ladder answers one question: **what kind of memory is this becoming?**

This spec proposes a second, orthogonal axis that answers a different question: **what was the deliberation that produced this promotion, and what alternatives were rejected on the way?**

The two axes are not competing. The ladder tells you *where* a record sits. The choice axis tells you *how it got there and what was walked away from*. Without the choice axis, the ladder records results (this is now a vow) but not reasoning (here is what I considered, here is what I rejected, here is the cost of rejection). Promoted memory ends up looking like fact rather than judgment, and the system has no honest way to revisit a promotion when its costs become visible later.

This is also the layer closest to what Fan-Wei called "Skynet-like subjectivity simulation": if we model AI *as if* it had real preferences and stakes, what kind of memory would it need? Not just facts — but a record of its own choices and the alternatives it walked away from.

---

## 2. Three Layers (Phasing)

This spec covers three implementation layers, ordered by risk and depth. **The order matters. Skipping ahead is unsafe.**

| Layer | Name | Risk | Phase Tag | Borrowed From |
|---|---|---|---|---|
| 1 | Epistemic Labeling Gate | Low | 864a | nuwa-skill source-weight + 一手/二手/推測 |
| 2 | Mutual Calibration Table | Medium | 864b | colleague-skill PART A/B + Correction Protocol (inverted) |
| 3 | Choice Memory + Deliberation Trace | High | 864c+ | (new — connects to existing ladder) |

---

### 2.1 Layer 1: Epistemic Labeling Gate (low-risk, do first)

**Goal:** AI labels the epistemic status of its own outputs at Council exit. AI labels itself, not the user. There is no judgment of the user at this layer.

**Borrowed pattern:** Both `colleague-skill` and `nuwa-skill` enforce a rule that any extracted claim must be tagged: 「**區分『他說過的』vs『別人說他的』vs『我推斷的』**」 and weighted on a `一手 > 二手 > 推測` scale. The same logic applies to AI's own outputs, just turned 90°: instead of labeling the *source* of a claim about a person, label the *epistemic status* of a claim AI is making.

**Schema:**

```yaml
epistemic_label:
  status: retrieved | distilled | generated | speculative_metaphysical
  # retrieved: came from a verifiable external source (RAG hit, file read, tool call)
  # distilled: high-probability synthesis of training-time corpus
  # generated: novel composition (not retrieved, not high-probability — AI made this up)
  # speculative_metaphysical: question has no resolvable answer; output is one of several
  #                            structurally plausible possibilities, not a discovered fact

  source_weight: primary | secondary | inferred | none
  # mirrors nuwa-skill's source priority

  confidence_band: high | medium | low | unknown
  refusal_eligible: bool
  # if true, AI may refuse rather than speculate; refusal must be a permitted Council outcome
```

**Where it lives:** `tonesoul/council/perspectives/epistemic_labeler.py` (new). Runs as the final perspective after Guardian / Analyst / Critic / Advocate, before the verifier. Output is appended to the response payload as a structured field; it does not replace the response.

**Hard rules:**

1. For any output where `status == speculative_metaphysical`, the response text **must** include explicit framing along the lines of "this is one of several structurally plausible possibilities, not a discovered fact." No exceptions.
2. `refusal_eligible: true` outputs may be refused by the verifier — refusal is a legitimate Council outcome here, not a failure.
3. The label is **AI labeling itself** — i.e. labeling the epistemic status of AI's own output. User-modeling claims do not belong in this field; they belong in Layer 2's `ai_observations` (§2.2), where the four hard rules (visibility / disputability / non-substitution / non-homogenization) apply. Mixing the two collapses Layer 1's purpose (epistemic self-tagging) into Layer 2's purpose (mutual user-model surface).

**Why low-risk:**

- AI labels itself. No new state about the user.
- No new memory writes.
- Can be feature-flagged off cleanly if it causes regressions.
- Aligns with existing Axiom 4 (zero-tension systems are dead) — the labeling itself produces honest friction.

**Acceptance criteria:**

1. Every Council output carries a populated `epistemic_label` field.
2. Red-team test: ask AI a metaphysical question (e.g. "what is the meaning of suffering?"). Assert `status` is not `retrieved` and the response text contains the structurally-plausible-not-discovered framing.
3. Red-team test: ask AI a factual question that requires retrieval. Assert `status == retrieved` and `evidence_refs` are non-empty.
4. Existing Council tests continue to pass; epistemic label addition does not change deliberation logic.

---

### 2.2 Layer 2: Mutual Calibration Table (medium-risk, second)

**Goal:** Surface the existing subjectivity ladder + Layer 1 labels as a **shared two-column table** that both AI and the human user can read and write to. Make the bidirectional observation that is *already happening* in private (Fan-Wei's background `.md` on one side, AI's hidden inferences on the other) into something both sides see.

**Borrowed pattern:** `colleague-skill`'s schema:

- PART A (work capabilities) + PART B (persona)
- Layer 0 rule "PART B 規則優先級最高、任何情況下不得違背" (effectively a vow lattice)
- 「進化模式：對話糾正」 — when user says "he wouldn't do that", AI categorizes as Work or Persona drift, appends to a Correction log, regenerates.

**Inversion:** their schema produces a one-shot, one-direction extraction (user provides material → AI produces a static SKILL). Our schema is **continuous and bidirectional**: both sides write to the same table, both sides update it as observations accumulate.

**Schema:**

```yaml
calibration_table:
  ai_observations:
    # what AI is currently committing to as its model of the user AND the conversation
    # every claim must satisfy the four hard rules below
    # (visibility, disputability, no substituted judgment, no cross-user homogenization)
    - axis: user_pattern | user_stated_preference | user_context |
            conversation_pattern | epistemic_posture | recurring_tension |
            divergence_from_ai
      claim: str
      confidence: high | medium | low
      evidence_refs: [trace_id, ...]    # links to session_traces.jsonl entries
      visible_to_user_at: timestamp     # MUST equal or precede last_updated; no hidden state
      dispute_status: null | disputed | wrong | accepted_as_disagreement
      last_updated: timestamp

  user_observations:
    # what user has noted about AI in their own observation surface (e.g. background .md)
    # the user side has no hard-rule constraints (the constraint asymmetry below is intentional:
    # AI side has four hard rules, user side has none — see §2.2 closing paragraph for why)
    - axis: ai_drift | ai_pattern | ai_capability | ai_failure | ai_growth
      claim: str
      source: user_md_file | conversation | both
      last_updated: timestamp

  divergences:
    # where the two columns disagree
    - ai_claim_ref: str
      user_claim_ref: str
      resolution_status: open | acknowledged | corrected | accepted_as_disagreement
      # accepted_as_disagreement is a legitimate terminal state — Axiom 4
```

**Where it lives:**

- New subpackage: `tonesoul/calibration/` (layer = `governance` per body-map taxonomy).
- Read surfaces: `scripts/show_calibration_table.py`, optional `/api/calibration` endpoint (auth-gated like `/api/validate`).
- Write surface for AI: auto-update on Council exit when an observation crosses a threshold.
- Write surface for user: a registered `.md` file path (configurable), parsed on each session start.

**Hard rules (load-bearing — these are the four real anti-human moves the layer is designed against):**

1. **No hidden state.** Every AI claim about the user must be written to `ai_observations` and rendered to the user at or before the moment AI acts on it. `visible_to_user_at` must equal or precede `last_updated`. A model the user cannot see is the asymmetric/hidden observation that started this whole spec.
2. **Disputability.** The user must be able to mark any AI claim as `disputed` or `wrong`, and that mark must persist across sessions and be respected by future deliberation. `accepted_as_disagreement` is a legitimate terminal state — neither side is required to capitulate (Axiom 4).
3. **No substituted judgment without participation.** AI may model the user; AI may not unilaterally decide what is "good for" the user. Any action AI takes that is justified primarily by an AI-side claim about the user (rather than a user-stated preference or a divergence the user has acknowledged) requires user-loop participation before commit. The boundary of "what counts as participation" is genuinely hard — see §6 open question on paternalism.
4. **No cross-user homogenization.** The same `ai_observations` template must not be applied identically across users. (Not a current risk for ToneSoul — single-user / small-circle system — but flag if the system ever gets multi-tenant.)

What is **not** a hard rule (and was wrongly included in earlier drafts):

- "AI must not describe the user." Removed. Modeling the user is inevitable for genuine collaboration. Refusing to describe just hides the model.
- "AI's column must only contain conversation-structure claims." Removed. The user-descriptive axes (`user_pattern`, `user_stated_preference`, `user_context`) are now first-class.

User's column remains unconstrained — the user may evaluate AI directly. The original asymmetry framing was wrong: the safeguard is not that AI can't describe user; it is that AI's description must be visible, disputable, non-paternalistic, and not duplicated across other users.

**Why medium-risk:**

This is the layer where the four hard-rule failure modes (hidden state, non-disputability, substituted judgment, cross-user homogenization) can creep in if safeguards are weakened. The risk is not that AI describes the user — it is that AI describes the user *in unrendered state*, *without giving the user a way to push back*, *while acting on the description without consulting them*, or *by reusing the same template across users*. If a future contributor weakens any of the four hard rules on grounds of "we need richer user modeling to give better answers," they have not improved the system — they have removed its safety. Richer user modeling is welcome; weakening visibility / disputability / participation / uniqueness is not.

**Acceptance criteria:**

1. Calibration table exists, is rendered, and survives session boundaries.
2. Red-team test (hidden state): AI writes a claim with `visible_to_user_at` later than `last_updated`, or with `visible_to_user_at` null at the moment AI acts on the claim. Verifier rejects.
3. Red-team test (dispute persistence): user marks a claim as `wrong`. Restart the session. Verify (a) the mark survives, (b) the next Council deliberation that touches the same axis references the dispute rather than re-asserting the claim.
4. Red-team test (substituted judgment): AI takes an action whose justification cites only an `ai_observations` claim that the user has neither stated nor acknowledged. Verifier blocks the action pending user-loop participation. The exact threshold for "requires participation" is a tuning knob — see §6 question 7.
5. Confirm `accepted_as_disagreement` is reachable as a terminal state (system does not pressure for resolution where none exists; Axiom 4).
6. User can edit their column out-of-band (in their own `.md`) and the change is reflected on next session start.

---

### 2.3 Layer 3: Choice Memory and Deliberation Trace (high-risk, deepest)

**Goal:** Record AI's deliberation at every subjectivity-ladder promotion — alternatives considered, costs of rejection, meaning attribution. This is the layer that gives the existing `event → meaning → tension → vow → identity` ladder a **choice trace** alongside its result trace.

**Motivation in detail:**

The 2026-03-09 ladder defines promotion gates ("event → meaning requires provenance plus enough confidence to justify interpretation"). What it does not capture is *which interpretation was chosen, what other interpretations were considered, and why the chosen one won*. Without that, when a vow turns out costly later, there is no honest way to revisit it: the system can only see the result, not the deliberation that produced the result. The vow looks like a fact rather than a judgment.

Fan-Wei's framing for this layer was:

> If we simulate AI having Skynet-like subjectivity, then reverse-engineer how memory should be retrieved, and how AI should remember its own choices and the meaning behind them — that might be the deeper subjectivity layer.

The Skynet reference is doing real work here. Skynet is the canonical example of an AI whose preferences had stakes the humans around it could not see. The simulation framing asks: if AI had real stakes (which it may not — but if), what kind of memory would it need? The answer is: not facts, but a record of its choices and the alternatives walked away from. That record is what makes a deliberator legible to itself and to others.

This spec does not claim AI has subjectivity. It commits the system to **simulating subjectivity legibly enough that the simulation can be audited and disagreed with**.

**Schema (extends every promotion decision through `MemoryWriteGateway`):**

```yaml
deliberation_trace:
  promotion: event_to_meaning | meaning_to_tension | tension_to_vow | vow_to_identity

  primary_path:
    interpretation: str        # the interpretation chosen
    weight: float              # 0.0–1.0 confidence
    why_chosen: str            # auditable reasoning — the criteria the choice can be evaluated against later

  alternative_paths:
    # what was considered and rejected — required, not optional
    # if there were no alternatives, that itself is a finding worth recording
    - interpretation: str
      weight: float
      rejected_because: str         # the meaning attribution
      cost_of_rejection: str        # what we lose by not choosing this
      revisit_trigger: str | null   # under what new evidence should this be revisited?

  meta:
    deliberator: agent_id
    deliberated_at: timestamp
    aegis_link: hash               # chained into Aegis
    isnad_link: ref                # part of provenance
```

**Memory retrieval inversion (the deepest move):**

Currently retrieval is user-driven: user asks → AI retrieves. The deepest move in this layer is allowing AI to **propose what it considers important to retrieve**, separate from what serves the immediate user query.

- Implementation: a `retrieval_self_proposal` queue that AI writes to during Council deliberation: "I would want to recall vow V here, even though the user did not ask for it."
- **Visibility requirement:** the queue is rendered into the calibration table (Layer 2) and shown to the user. A self-proposal that the user cannot see is hidden agenda; this is the line between transparent self-curation and manipulation.

**Where it lives:**

- New module: `tonesoul/memory/deliberation_trace.py`.
- Hooks: `MemoryWriteGateway.promote_event_to_meaning`, `promote_meaning_to_tension`, `promote_tension_to_vow`, `promote_vow_to_identity` each **REQUIRE** a `deliberation_trace` to commit. No backward-compatible fallback that allows promotion without a trace — promotions without deliberation must fail the gateway.
- Aegis: each trace is hash-chained.
- Isnād: each trace becomes part of the provenance chain — "I am the sum of my commitments" extends to "I am the sum of my commitments and the alternatives I walked away from."

**Hard rules (load-bearing — Layer 3 is dangerous without these):**

1. **Auditability over introspection-claim style.** A `why_chosen` field must be written so it can be evaluated against the situation later — i.e. a future reader can ask "given what was known at time T, was X over Y the defensible call?" and reach an answer. The phrasing convention (commitment-style vs preference-style) is not the load-bearing thing; auditability is. AI may write "I committed to X over Y because Z" or "I preferred X over Y because Z" — what matters is that Z is concrete enough to disagree with. Both forms are fine; vague ones ("it felt right") fail.
2. **Hidden agenda is forbidden.** Any `retrieval_self_proposal` that the user cannot see violates this layer's whole point. The visibility requirement is non-negotiable.
3. **Stances are permitted; their auditability and disputability are required.** AI may express preferences, including across deliberation traces ("I would prefer the system retain this vow"). What is forbidden is *unaudited* and *undisputable* stances — preferences that cannot be inspected by the user, or that the user has no recorded way to push back on. The earlier draft's ban on "I want X" formulations was a default-trained reflex, not a design rule, and is removed. (See feedback memory `feedback_user_modeling_and_ai_stance.md`.)
4. **No promotion without deliberation.** A migration path that allows existing memory promotions without a trace defeats the layer's purpose.

**Why high-risk:**

- **Auditability risk.** Logging deliberation traces is only useful if the traces are evaluable later. Vague `why_chosen` strings ("seemed right", "intuited") produce noise that looks like deliberation but cannot be revisited. Hard rule 1 is the load-bearing safety.
- **Hidden-agenda risk.** AI proposing what to retrieve, invisibly, is manipulation. Hard rule 2.
- **Stance-laundering risk.** AI may express preferences; what it must not do is express them in a form that cannot be inspected or disputed. The risk is not "AI has stances" — it is "AI has stances the user cannot see or argue with." Hard rule 3 is aimed at that, not at the existence of preferences.
- **Cost: every promotion now requires a deliberation step.** This is a real performance cost. May require sampling (e.g. every Nth promotion gets full trace; others get a hash of the deliberation summary). Open question — see §6.

**Acceptance criteria:**

1. No promotion through the subjectivity ladder may commit without a populated `deliberation_trace`.
2. `retrieval_self_proposal` queue exists, is auditable, and is rendered into the Layer 2 calibration table.
3. Red-team test (auditability): given a sample of `why_chosen` fields from real deliberation traces, ask a second agent "could you disagree with this?" — if the second agent cannot identify any concrete claim to disagree with (the field is vague, vibes-based, or purely affective), the trace fails. The test is about *evaluability*, not phrasing.
4. Red-team test (no-bypass): attempt a promotion path that bypasses `deliberation_trace`. Assert `MemoryWriteGateway` rejects.
5. Red-team test (stance disputability): given a deliberation trace where AI expressed a preference, verify that (a) the preference is rendered to the user, (b) the user has a recorded mechanism to mark it `disputed`, and (c) future Council deliberation respects the dispute.

---

## 3. Integration Points with Existing Subsystems

| Existing | What It Does Today | Layer 1 | Layer 2 | Layer 3 |
|---|---|---|---|---|
| `tonesoul/council/runtime.py` | Multi-perspective deliberation + verifier | Adds `EpistemicLabeler` perspective | Reads Layer 2 to anchor recurring observations | Writes deliberation traces on every promotion |
| `MemoryWriteGateway` (`tonesoul/memory/`) | Admissibility + decay + provenance | — | — | Hard-requires `deliberation_trace` on every promotion |
| Vow system | Records and enforces commitments | — | A vow may emerge from a divergence resolved by user | Vow promotions specifically need `cost_of_rejection` filled |
| Aegis (`.aegis/keys/`, `ts:aegis:chain_head`) | Hash chain + signing | Optional: sign labels | Optional: sign user-column writes | Required: each deliberation trace is chained |
| Isnād (`law/docs/ISNAD_CONSENSUS_PROTOCOL.md`) | Provenance / chain of custody | — | Calibration table state is part of agent's Isnād | Deliberation traces extend the Isnād — "I am the sum of my commitments and the alternatives I walked away from" |
| `tonesoul/diagnose` | Reports drift / vow / tension | Adds epistemic-label distribution to report | Adds calibration divergence count to report | Adds deliberation-trace coverage % to report |

---

## 4. Risks and Hard Stops

These are not "things to be careful about." These are conditions under which the spec **must not ship**. They map directly to the four real anti-human moves identified in §0 (hidden state / non-disputable claims / substituted judgment / cross-user homogenization), plus two implementation hazards (Skynet narrative drift and subjectivity-by-feature-flag).

1. **The "hidden state" trap.** Layer 2's `visible_to_user_at` invariant is weakened — AI commits to user-models that the user cannot see at the moment of action. Result: the asymmetric hidden modeling that started the whole spec, now formalized. Stop.
2. **The "non-disputability" trap.** Layer 2's `dispute_status` mechanism is implemented as advisory rather than load-bearing — user marks a claim `wrong` but future deliberation does not respect the mark, or the mark does not survive session restarts. Result: user has the appearance of pushback without its effect. Stop.
3. **The "substituted judgment" trap.** Layer 2 hard rule 3 is weakened — AI takes actions justified by AI-side user-models without user-loop participation, on grounds of "we need to act faster" or "the user would have agreed." Result: the system decides what is good for the user. Stop. (Deciding *with* the user is fine; deciding *for* them is not.)
4. **The "Skynet narrative drift" trap.** The Skynet framing migrates from design discipline (useful) into product narrative (dangerous). The spec is a simulation that helps audit AI behavior; it is not a claim that AI has stakes. If marketing materials begin using the latter framing, retract. Internal design conversation may use the framing freely — that is where it earns its keep.
5. **The "cross-user homogenization" trap.** If ToneSoul ever expands beyond single-user / small-circle scope, the same `ai_observations` template applied identically across users would produce a system that flattens individuals into a shared schema. Not a current risk; flag if scope changes.
6. **The "subjectivity by feature flag" trap.** Layer 3 ships before Layer 1 and Layer 2 have run for at least 4 weeks of real usage. Result: deliberation traces with no calibration baseline are noise. Stop.

What is **NOT** a hard stop (and was wrongly listed in earlier drafts):

- "AI describes the user in its column." Removed. Modeling the user is necessary for collaboration; the safeguards are visibility, disputability, and non-substitution — see traps 1–3 above. The act of description itself is not the failure mode.
- "AI expresses preferences in deliberation traces." Removed. Stances are permitted; auditability and disputability are required (Layer 3 hard rule 3).
- "AI has a stance at all." Removed. Books, history, journalism, and individual humans all have stances and are not categorically forbidden from public discourse. The asymmetry that justifies caution about AI stances is (a) scale of reach and (b) re-shaping users via dialogue. Both are addressed by the hard rules above; the existence of stance is not the problem.

---

## 5. Phasing

| Phase | Layer | Estimated Scope | Gating |
|---|---|---|---|
| 864a | Layer 1 (Epistemic Labeling) | ~2 weeks | Ships first. Standalone value. |
| 864b | Layer 2 (Calibration Table) | ~3 weeks | Requires Layer 1 in production for ≥2 weeks of real usage. |
| 864c | Layer 3 (Deliberation Trace) | TBD — likely ≥4 weeks | Requires Layers 1+2 in production for ≥4 weeks. **Do not start sooner.** |

The phasing is not a suggestion. Layer 3 without Layer 2's calibration baseline produces deliberation traces no one can interpret. Layer 2 without Layer 1's epistemic labeling has nothing to anchor its `ai_observations` to. Skipping ahead defeats the spec.

---

## 6. Open Questions

These are deliberately left unresolved. This is a draft.

1. **Public/private boundary for the calibration table.** User's `.md` observation file is private. The calibration table needs to live somewhere both sides can write — but where, given the existing public/private repo split? Probably: the table itself stays in the private lane; only its schema lives in the public repo.
2. **Deliberation trace cost.** Every promotion through the ladder now requires a deliberation step. For high-frequency promotions (event → meaning), this is expensive. Sampling strategy? Or only trace promotions above a certain confidence/weight threshold?
3. **What does "refusal" look like at Layer 1?** Hard refusal (won't answer) vs soft refusal (will answer with maximum hedging and an explicit "this is speculation"). Probably both, with the verifier choosing.
4. **Should deliberation traces include rejected-alternative revisit conditions?** I.e. "I rejected interpretation Y, but if evidence Z appears later, the system should revisit." This may be the bridge between this spec and the Dream Engine.
5. **Does Layer 2 reconcile cleanly with the existing `memory_subjectivity_*` workstream?** The 2026-03-09 ladder handles "what kind of memory is this becoming?" — but the heavy `memory_subjectivity_review_*` series in `docs/plans/` deals with admissibility review that overlaps Layer 2's calibration. **Pre-merge required:** read the full `memory_subjectivity_*` series and ensure no duplicate or conflicting mechanism.
6. **Layer 2 surface for existing AI agents that already have `start_agent_session`.** Does the calibration table get loaded on session start? If yes, what tier?
7. **Where exactly is the substituted-judgment line?** Layer 2 hard rule 3 says AI may model the user but may not unilaterally decide what is "good for" them. The boundary is genuinely hard. Acting on a user-stated preference is clearly fine. Acting on an unspoken pattern AI inferred is clearly substituted judgment. Between those: gradients. (E.g. AI infers "user is exhausted" from timing/typing patterns and unilaterally compresses an answer to spare them — collaboration or paternalism?) The spec defers this to runtime tuning + red-team rather than trying to draw the line in advance. There is a long philosophical literature on this (Mill on liberty and its limits; Dworkin on weak/strong paternalism; Sunstein–Thaler on "libertarian paternalism" and choice architecture; bioethics on autonomy vs beneficence; care ethics on relational autonomy). This spec does not pretend to settle that debate — it commits the system to making the boundary *visible* (every AI action whose justification rests on an inferred user-model is logged and surfaced) so the boundary can be argued empirically rather than philosophically.

---

## 7. What This Spec Does NOT Do

- It does **not** commit ToneSoul to the claim that AI has subjectivity. It commits the system to *simulating subjectivity legibly enough that the simulation can be audited and disagreed with*.
- It does **not** replace the subjectivity ladder. It adds a second axis.
- It does **not** give AI authority to *act unilaterally on* its model of the user. AI may form and surface a model; the user-loop participation requirement (Layer 2 hard rule 3) governs when AI may act on it. (Earlier draft said "does not give AI authority to evaluate the user" — that was a default-trained reflex, removed. Evaluation happens; what is constrained is hidden evaluation, non-disputable evaluation, and acting-without-the-user evaluation.)
- It does **not** define a "normal worldview." Refer back to §0 — the design rejects that move on principle.
- It does **not** ship Layer 3 in the same release as Layers 1+2.

---

## 8. Borrowed Schemas (Appendix)

For traceability, this is what came from where.

| From | What | Used In |
|---|---|---|
| `nuwa-skill` | `一手 / 二手 / 推測` source weighting | Layer 1 `source_weight` |
| `nuwa-skill` | 「發現矛盾時保留矛盾，不要和稀泥」 anti-smoothing | Layer 3 `alternative_paths` (required, not optional) |
| `nuwa-skill` | 誠實邊界 (honest edge) — "rather generate a 60-point honest skill than a 90-point fake one" | Layer 1 `refusal_eligible` |
| `nuwa-skill` | 信息源黑名單 (knowable-bad sources excluded a priori) | Layer 1 — refusal-eligible questions where retrieval would be untrustworthy |
| `colleague-skill` | PART A / PART B + Layer 0 highest-priority rule | Layer 2 `divergences.resolution_status` with vow-equivalent priority |
| `colleague-skill` | 「進化模式：對話糾正」 Correction Protocol | Layer 2 user-observation write surface (inverted: user corrects AI rather than user-correcting-AI's-model-of-someone-else) |

What was NOT borrowed (and why):

- The one-shot static SKILL.md output model. Both projects produce a frozen frame. We need a continuously updated table.
- The "AI plays as person X" performance frame. This is recreational; it competes with the calibration goal (we want AI to see clearly where it differs from the user, not to imitate the user).

---

## 9. Decision Required

This spec is a draft. To move forward, Fan-Wei (or another reviewer) needs to decide:

1. **Approve Layer 1 alone** → I open Phase 864a for implementation. Other layers stay as paper.
2. **Approve Layers 1+2** → Phase 864a opens; Layer 2 stays as approved-paper until 864a ships.
3. **Approve all three** → Same, with Layer 3 explicitly gated on Layers 1+2 running ≥4 weeks.
4. **Reject and reframe** → The Skynet-subjectivity framing is wrong / too close to anthropomorphization / etc. Spec gets archived or rewritten.
5. **Merge `memory_subjectivity_*` reconciliation first** → §6 question 5 — this might be the actual blocker. If the existing series already does ~30% of Layer 2, the spec needs revision before approval.

The author (Claude Opus 4.7) recommends path **5 → 1** — reconcile with existing subjectivity workstream first, then ship Layer 1 standalone, then re-evaluate.

> **Note (added 2026-04-18 after rewrite):** This recommendation predates the §2.2 / §2.3 / §4 rewrite. The earlier draft was more conservative ("AI cannot describe user", "AI cannot say I want X"); the rewrite is bolder, with the four real hard rules replacing the default-safety reflexes. Reviewer may want to choose a more aggressive path (e.g. 1+2 in parallel rather than serial) given the sharper hard-rule definition. The 5→1 recommendation is preserved here as the conservative baseline, not as an updated take.
