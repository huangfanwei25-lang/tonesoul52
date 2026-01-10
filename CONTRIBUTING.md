# Contributing to ToneSoul

ToneSoul is a governance-first stack. Every contribution should move the repository toward transparency, traceability, and semantic responsibility.

## 1. Before Your First Contribution
- Read `docs/philosophy/axioms.md`, `docs/philosophy/collective_consciousness.md`, and `docs/TRUTH_STRUCTURE.md` to understand the values we encode.
- Check `memory/fan_wei_context.md` for Fan-Wei Huang’s intent model so your wording mirrors the tone of creative yet accountable governance.
- Ensure your environment can run the pre-output council tests (`tests/test_pre_output_council.py`) and the broader suite if relevant.

## 2. Code Contributions
- Create descriptive branches (`feature/pre-output-council`, `fix/coherence-score`) off `master`.
- Follow existing style: modules in `tonesoul/` use descriptive classes, `docs/` use bilingual explanations, and YAML specs are explicit about thresholds.
- Add or update tests when you touch logic; run relevant `pytest` modules locally.
- Submit a pull request that:
  - Explains the change in human-readable governance terms (especially when touching policies).
  - References the relevant spec or axiom.
  - Includes `CoherenceScore`/`CouncilVerdict` updates if they affect reasoning.

## 3. Documentation & Specs
- Document new concepts inside `docs/` before updating `spec/`, unless the spec needs to shift first.
- Keep docs bilingual (English + dense phrases) to align with existing philosophical entries.
- Update `docs/GETTING_STARTED.md` or `docs/philosophy/` whenever you add a new governance pattern.

## 4. Issues & Pull Requests
- Use issues to surface new governance questions, feature requests, or drift you observe; tag them with `governance`, `philosophy`, or `engineering`.
- For PRs:
  - Link affected specs (`spec/*.md`) and philosophy docs.
  - Note how the change preserves or adjusts the semantic responsibility chain.
  - Mention test coverage and noteworthy manual steps.

## 5. Behavior Expectations
- ToneSoul is collaborative: discuss high-level shifts in issues before coding.
- Respect the `AXIOMS.json` sanity checks—nothing should contradict the axioms without a clear migration plan.
- Remain transparent: log significant decisions in `reports/` or create new entries when introducing new governance gates.
