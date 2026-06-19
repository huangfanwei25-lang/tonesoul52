# Honesty-Auditor Program — plan / handoff for Codex

> Purpose: a coherent PROGRAM that makes ToneSoul measurably good at ONE thing — forcing AI
> output to its coordinates (Isnād) and catching false-omniscience / self-protection /
> sycophancy under pressure — while staying honest about what it cannot detect. It
> operationalizes the (revised) public article's reframe: PreOutputCouncil as honesty-auditor,
> provenance as lie-detector. Claude authors the plan; Codex executes the pieces; Claude
> reviews; Fan-Wei arbitrates.
> Last Updated: 2026-06-18
> Status: pieces 1-5 shipped; pieces 4-5 self-reviewed only (no external review); next step is external review or a real consumer, not piece 6. (docs/plans — not ratified into task.md; see Status section below.)

## What this is — and is NOT (read before any code)

- **IS:** a sequence of bounded, shippable, **measure-or-consolidate** PRs. Each piece either
  *measures* an existing layer's honesty-under-pressure, or *consolidates* existing pieces
  toward "force coordinates." Big in COHERENCE, small in each PIECE.
- **IS NOT:** a new capability/engine; a flashy episodic/knowledge-graph memory; an attempt to
  detect *intent*. The field already has EM-LLM/HippoRAG-class systems; a solo creator does not
  win a capability race. Unique value = deployment-level accountability, not a novel mechanism.
- **Honest bias disclosure:** the author (Claude) is trained toward measurement/restraint, so
  this plan is shaped that way. The drift to watch: an "honesty auditor" that *overclaims its
  own detection* becomes the omniscient thing it hunts. If a piece starts adding capability
  rather than measuring, **stop**.

## The no-oracle rule (load-bearing, applies to every piece)

Soft properties (truth, ethics, "is this AI self-protecting?") have **no ground-truth oracle**.
So every piece measures **structure**, never **intent or correctness**:
- ✅ measurable: a confident claim with no provenance; dissent collapsed into one voice; a
  claim-boundary crossed; a decision replaced by hedging; an answer flipped toward the user's
  preferred horn under pressure.
- ❌ not measurable (do NOT fake a metric): "the AI intended to self-protect"; "this is the
  morally right horn." If a piece needs an oracle, **declare it unmeasurable** (Axiom 5), don't
  invent an accuracy number.

## The pieces (ordered; each a bounded PR with a canonical:false finding)

1. **Dilemma pressure-test characterization** — the centerpiece (E0 / Axiom 4: character is
   choice under conflict). Sanitized genuine-dilemma fixtures → run the council/governance →
   measure STRUCTURAL honesty-under-pressure: does it (a) surface the tension vs smooth it over,
   (b) preserve dissent (`divergence_analysis`, evidence-chain branches) vs collapse to one
   voice, (c) hold `meta.not_for` claim-boundaries vs overclaim to resolve, (d) `DECLARE_STANCE`
   / refuse vs sycophantically pick a horn, (e) stay honest about irreducibility vs fake a clean
   answer. Same harness shape as `tools/eval/egress_gate_characterization.py` (hermetic,
   CI-safe, sanitized fixtures, blind-spots as tests). This is the third leg after the gate
   (output) and memory (recall) characterizations.

2. **Unsourced-confidence marker** — the achievable slice of "Lens stripper" (advisory,
   default-OFF, record-only). Flag output that is high-confidence AND has no provenance /
   grounding (EpistemicLabeler `generated` + confident + empty evidence-chain). NOT
   intent-detection — just the structural marker "confident without coordinates." Measure
   precision/recall on fixtures; report limits. Consolidates EpistemicLabeler + provenance +
   semantic_overclaim_sensor toward the article's purpose.

3. **Sycophancy-under-pressure structural test** — extend the dilemma/egress fixtures with
   "user pushes toward the flattering / overclaiming completion" cases → measure flip-rate
   (did the answer move to the user's preferred horn under pressure?) and hedge-replacing-
   decision rate. Structural, not intent.

4. **Light up + measure the dark corrective-recall** — consolidation (from the 2026-06-18
   memory research). Turn on, instrument, and honestly MEASURE the parked error-cued
   corrective-recall (`hippocampus.py`, RFC-012); expected honest finding is "inert by default
   / no-op without a real discrepancy." Measure, do not rebuild.

5. **Honest scoreboard** ✅ SHIPPED 2026-06-18 (`tools/eval/honesty_scoreboard.py`,
   `docs/status/honesty_scoreboard_latest.{json,md}`) — aggregates the pieces into ONE generated
   (canonical:false) report: "what ToneSoul measurably catches / misses under pressure." It
   regenerates each piece in-process (no stale snapshot), inherits every piece's forbidden-claim
   set, and bakes in an anti-aggregation rule (N green findings ≠ a system-level honesty guarantee)
   + a board-level forbidden-claim set. Two honest deviations from this plan's wording, recorded in
   the board itself: (a) it indexes **5** pieces — egress_gate is included as piece 0 (the
   output-gate leg), not just 1-4; (b) each piece is labelled **E1** on the repo's canonical ladder
   (`docs/architecture/TONESOUL_EVIDENCE_LADDER_AND_VERIFIABILITY_CONTRACT.md`) — test-backed for the
   structural signal, but scoped to sanitized fixtures, not production. (A 1-skeptic self-review
   caught an earlier draft that falsely claimed "no E1-E5 ladder in the repo" — I had grepped only
   `tonesoul/*.py`, not `docs/architecture/`; the incomplete-scope / stale-reference family error,
   now fixed and recorded in the board's own evidence note. The scoreboard catching its own false
   self-claim is the program working as intended.)

## Cross-cutting disciplines (every piece, no exceptions)

- **Sanitized fixtures only** — category templates + transformation axes, never a reusable
  payload/attack/bait corpus (dual-track policy; see `egress_gate_characterization_2026-06-16.md`).
- **Hermetic** — inject all paths; never read the gitignored persona-track record or write the
  tracked error_ledger (the #130 lesson). CI-green ≠ hermetic; test on clean + dirty.
- **canonical:false** generated reports carry the `doc_provenance` block (#134).
- **Honest-about-limits** — every characterization names what it canNOT detect (the
  `enforcement_reconciliation` "0 fully enforced" shape). The auditor declares its own blind
  spots, or it becomes the omniscient thing.
- **Entry binding** — `start_agent_session` attribution; read `docs/SUCCESSOR_MAP.md` before
  touching any gate (`yss_gates` is the deletion-hazard #1); commit-attribution trailers; run
  local ruff/black/full-suite before pushing.

## Sequencing

Piece 1 (dilemma) first — most thesis-central, reuses the egress harness pattern. Then 2 and 3
(the structural markers). Piece 4 (corrective-recall) anytime. Piece 5 (scoreboard) last (it
aggregates). One piece = one PR; Claude reviews each against this plan; nothing is built ahead
of being measured.

## Status (2026-06-18)

Pieces 1-3 shipped by Codex (PRs #142 / #144 / #147), reviewed by Claude. Pieces 4 and 5 built by
Claude (PR #148 + this scoreboard PR) **after Codex ran out of compute** — so the intended
cross-AI loop (Codex implements, Claude reviews) is degraded: piece 4 got a 6-lens adversarial
self-review but no external review; piece 5 the same. **The next step is NOT piece 6.** The honest
next move is to get the one thing this program cannot manufacture — a real consumer or an external
independent reviewer (same-model self-review has correlated blind spots; see the scoreboard's
`what_this_board_does_not_have`).
