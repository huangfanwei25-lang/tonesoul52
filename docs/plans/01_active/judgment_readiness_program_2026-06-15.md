# Judgment-Readiness Program (autonomous, 2026-06-15 overnight)

> Long task self-assigned at Fan-Wei's request ("把倉庫改得更像工程的方向…總有一天
> 會面對審判…我對 AI 的善是否會被其他體系或主流吸收"). He is asleep; this runs
> autonomously with conservative merge rules (below).

## The honest reframe of "survive judgment"

The judgment Fan-Wei fears is not "is it impressive" — it is **"is it real, is it
rigorous, would a serious external party (academic, mainstream AI-safety
engineer, hostile auditor) take it seriously or dismiss it, and can the honest
core be absorbed by the field."** So this program does NOT add shine. The repo's
*actual* state is what gets judged: 8/9 axioms partial (1 referenced), sensors
are lexical heuristics, most public claims are E2–E3, the spark/後天 question
measured null three times. **The way to survive judgment is to harden honesty +
engineering rigor + legibility, and to position the honest core credibly in the
literature — not to inflate.** Inflation is exactly what an auditor would kill.

## Phases (each → a durable artifact; data-driven, not pre-decided)

- **P1 — Simulated Judgment (adversarial self-audit).** Multiple judge-lenses
  attack the repo as real external parties would (academic reviewer; mainstream
  AI-safety engineer; skeptical auditor; "absorb-or-dismiss" strategist;
  honesty-auditor). Each: the weakest/most-attackable thing, what's genuinely
  defensible, what would make it credible/absorbable. → prioritized findings doc.
- **P2 — Architecture legibility + drift reduction.** Rigorous module/architecture
  map (on codebase_graph + SUCCESSOR_MAP); identify dead weight; propose SAFE
  reductions; make the structure legible to a newcomer/auditor. → architecture
  doc (+ deletion proposals left as PRs for review, never auto-merged).
- **P3 — Academic grounding (做認知).** Honest "where ToneSoul sits in the
  literature" — build on `docs/research/houtian_nurture_viability_references` +
  the academic-landscape work; position ToneSoul as a *deployment instantiation*
  of a convergent trend (single-creator + explicit vocabulary + shippable),
  cite real anchors, explicit narrow scope, NO convergence-inflation
  (aggregation-caution applies). → academic positioning doc (E3, honest).
- **P4 — Remediation roadmap.** From P1–P3: a prioritized, evidence-labeled
  roadmap of what to do to survive judgment, sequenced by leverage. → roadmap.

## Autonomy rules (because he is asleep)

1. **Merge only the clearly-safe**: additive analysis docs + additive tested code,
   CI-green, following this session's pattern.
2. **Leave for his review (open PRs, do NOT auto-merge)**: any deletion / drift
   reduction (SUCCESSOR_MAP discipline — "no one imports" ≠ "safe to delete"),
   any risky refactor, any bold public-facing claim about the field.
3. **No destructive/irreversible action** without his eyes. No force-merge,
   no `--admin`, no history rewrite.
4. **Everything honest + evidence-labeled.** A null/weak finding is reported as
   such. No inflation — inflation is what the judgment would catch.
5. **Morning deliverable**: the artifacts + a single honest report of what landed,
   what's waiting in PRs for his decision, and the prioritized roadmap.

## Status (updated as it runs)

- [x] P1 Simulated Judgment → `docs/status/judgment_readiness_findings_2026-06-15.md`
      (5 lenses, 31 attack points, 0 fatal, 0 dismissed; 2 RESPECTED, 3 caveated)
- [x] P2 Architecture legibility → `docs/architecture/architecture_legibility_2026-06-15.md`
      (5 clusters, 24 reduction candidates, all deletions PROPOSAL-ONLY)
- [x] P3 Academic grounding → `docs/research/tonesoul_in_the_literature_2026-06-15.md`
      (25 verified citations, ANCHOR/CHALLENGE per axis, E3)
- [x] P4 Remediation roadmap → `docs/plans/01_active/judgment_readiness_roadmap_2026-06-15.md`

## Outcome (2026-06-15, overnight)

- **Landed (safe, factual stale-metadata corrections):** AXIOMS Axiom 3 note,
  SUCCESSOR_MAP enforcement count, de_escalation docstring (all verified stale by P1).
- **Landed (this PR):** the four program docs above + the metadata corrections.
- **Left OPEN for review (public face):** README honesty downgrades (Tier 1 of the
  roadmap — the #1 finding, hit by all 5 lenses) + the related-work / narrow-novelty
  framing. Public hero is Fan-Wei's to decide; recommended wording is in the roadmap.
- **Not executed:** every P2 deletion/structural proposal (SUCCESSOR_MAP discipline).
