# Architecture Reflection (2026-03-07)

## Context
- Branch baseline: `feat/env-perception` @ `c225332`
- Working tree is dirty; this phase must avoid unrelated files.
- Current mission: `Phase 1b` refactor `tonesoul/unified_pipeline.py` so orchestration stays in the pipeline, while governance decisions move to `tonesoul/governance/kernel.py`.
- Hard guardrails:
  - Keep `UnifiedPipeline` external API 100% backward compatible.
  - Do not touch memory write logic in `soul.db` and `self_journal.jsonl`.
  - If the refactor grows beyond a small surgical patch, keep the plan and rationale recorded here first.

## What The Architecture Is Actually Saying
- `UnifiedPipeline` has become a God Object. It currently owns orchestration, LLM selection, friction calculation, circuit-breaker behavior, memory recall wiring, and response assembly.
- `GovernanceKernel` already exists as the intended policy boundary. It now holds the right responsibilities: backend routing, prior/runtime friction, circuit-breaker checks, and governance observability.
- `LLMRouter` already exists as the new backend entrypoint. This means `UnifiedPipeline` no longer needs to own `LLM_BACKEND` branching or waterfall fallback logic.
- The system is healthiest when the pipeline only executes and composes, while the governance layer decides.

## Concrete Changes I Intend To Make
1. Replace `_get_gemini()` usage with a router-backed client getter that delegates to `LLMRouter().get_client()`.
2. Remove local prior/runtime friction logic from `UnifiedPipeline` and delegate those calculations to `GovernanceKernel`.
3. Stop doing direct circuit-breaker ownership in `UnifiedPipeline`; keep the response behavior unchanged, but source freeze decisions from the kernel.
4. Keep all current `dispatch_trace` keys and outward return payloads stable so tests and API callers do not break.
5. Update tests to reflect the new architecture instead of preserving legacy private hooks.

## Architectural Weak Points To Remember
- The repo mixes executable runtime, governance docs, generated status artifacts, and long-term memory in one workspace. This is powerful, but it easily creates false confidence if artifacts are mistaken for runtime truth.
- `docs/status/*_latest.*` are evidence snapshots, not authoritative runtime behavior.
- `UnifiedPipeline` still contains too much policy logic for a system that claims governance separation.
- The memory stack has explicit governance language, but evidence coverage is still weak. Contract shape alone is not proof.

## What I Learned About ToneSoul Memory
- ToneSoul memory is not one thing. It is at least four layers:
  - Runtime working context
  - Append-only audit trail
  - Durable crystallized rules
  - Generated status evidence
- These layers should not share ownership. Each write path needs one canonical owner.
- `self_journal.jsonl` is currently closer to an auditable event stream than a clean semantic memory base.
- `crystals.jsonl` is the right place for durable architectural rules, but only if the rule is stable, specific, and earned by repeated evidence.
- Governance-shaped entries without evidence are weak memory, not strong memory.

## Durable Rules From This Review
- The orchestrator must not also be the policy engine.
- One memory write path must have one source of truth.
- Governance evidence matters more than governance vocabulary.
- Generated reports are for audit and diagnosis, not as a replacement for runtime contracts.

## Immediate Execution Plan
1. Wire `UnifiedPipeline` to `LLMRouter` and `GovernanceKernel`.
2. Preserve current return shapes and `dispatch_trace` fields exactly where callers expect them.
3. Update pipeline/runtime tests that patch `_get_gemini` so they patch the new client seam instead.
4. Run focused tests around compute-gate, runtime friction, API transport, and governance kernel before widening the test scope.

## Falsifiable Check
- If this refactor is correct, the following should remain true:
  - `UnifiedPipeline.process()` signature does not change.
  - Existing response payload keys do not disappear.
  - `pre_gate_governance_friction`, runtime freeze behavior, and repair traces still appear in `dispatch_trace`.
  - Tests fail only where they encoded the old internal seam, not because the external contract regressed.

## Phase 2 Extension Plan
- The next safe cut is not a new HTTP endpoint. `docs/API_SPEC.md` does not yet define a perception write contract, so adding one now would widen the surface before the storage contract is stable.
- `soul.db` should become the canonical sink for environmental stimuli first. `self_journal.jsonl` remains an audit trail, not the first persistence target for perception.
- The new write seam should live in `tonesoul/memory/write_gateway.py`, not inside `tonesoul/perception/stimulus.py`. Perception produces signals; memory owns durable writes.
- Environmental stimuli should be written as `MemorySource.CUSTOM` records with `type=environment_stimulus` and `layer=working`.
- Cross-session deduplication should be enforced on `content_hash` at the write gateway, because `StimulusProcessor` only deduplicates inside the current batch.
- Dream Engine, wake-up scheduling, and dashboard work should consume this gateway later instead of inventing their own persistence path.

## Phase 2 Outcome
- Implemented `tonesoul/memory/write_gateway.py` as the canonical persistence seam for environment perception.
- The gateway writes perception outputs into `SqliteSoulDB` by default, keeps them in `MemorySource.CUSTOM`, and disambiguates them with `type=environment_stimulus`.
- Raw environmental inputs are now explicitly staged as `layer=working`, which keeps them separate from durable factual or experiential promotion.
- Cross-session deduplication now happens on `content_hash` at write time, so repeated crawls do not silently re-inject the same external article.
- I intentionally did not add a new HTTP route and did not modify `docs/API_SPEC.md`, because the storage contract needed to stabilize first.
- RR follow-up found a real weakness in `StimulusProcessor`: corrupted Chinese keyword entries were reducing relevance and tag extraction for Traditional Chinese content. This was a behavioral bug, not a cosmetic issue.
- Rewrote `tonesoul/perception/stimulus.py` with clean keyword dictionaries and added Chinese-language regression coverage.
- Validation outcome: targeted memory/perception tests passed, and the full suite finished at `1242 passed`.

## Phase 7 Dream Engine Plan
- The first Dream Engine cut should be an offline engine, not a scheduler.
- Input boundary:
  - Read persisted `environment_stimulus` records from `soul.db` through `MemoryWriteGateway`.
  - Read durable rules from `MemoryCrystallizer.top_crystals()`.
  - Read related episodic context from `SoulDB.search()` / `detail()`.
- Decision boundary:
  - Use `GovernanceKernel` for friction scoring, council-convening recommendation, and backend selection metadata.
  - Do not turn Dream Engine into a second pipeline or a hidden copy of `UnifiedPipeline`.
- Output boundary:
  - Produce a structured, testable dream-cycle result first.
  - Allow optional LLM reflection generation through `LLMRouter`, but keep a deterministic fallback so tests do not require live models.
  - Avoid touching `self_journal.jsonl` write paths in this cut.
- Verification boundary:
  - Add tests for stimulus selection, related-memory recall, governance collision scoring, and deterministic fallback behavior.
  - If this cut is correct, it should increase autonomous capability without changing any external HTTP contract.

## Phase 7 Dream Engine Outcome
- Implemented `tonesoul/dream_engine.py` as an offline engine that reads persisted environmental stimuli from `soul.db`, collides them with durable crystals and related memory recall, and emits structured dream-cycle results.
- Dream Engine deliberately does not copy `UnifiedPipeline`. It asks `GovernanceKernel` for friction scoring, council-convening recommendation, and circuit-breaker state, then packages that into an auditable result.
- Added `scripts/run_dream_engine.py` as a thin CLI wrapper so the engine can be executed without user prompts and without requiring the future scheduler to exist first.
- LLM reflection generation is optional and best-effort through `LLMRouter`; deterministic fallback remains the baseline so tests and offline runs stay stable.
- Validation outcome: Dream Engine targeted tests passed, and the full suite finished at `1248 passed`.

## Phase 128 Autonomous Wake-up Loop Plan
- The wake-up loop should be orchestration only. It must not recalculate friction, rewrite collision logic, or open a second governance path outside `DreamEngine` and `GovernanceKernel`.
- Core seam:
  - Add a small loop runner in `tonesoul/` that invokes `DreamEngine.run_cycle()` on an interval.
  - Return structured per-cycle results with status, timing, and Dream Engine payload so later observability work can consume snapshots directly.
- Boundary rules:
  - No external HTTP/API contract changes.
  - No new writes into legacy `self_journal.jsonl` paths in this cut.
  - Scheduling should stay optional and host-driven: local while-loop, cron, GitHub `schedule`, or Windows Task Scheduler should all be able to call the same CLI.
- CLI rules:
  - Keep script thin, mirroring `scripts/run_dream_engine.py`.
  - Support `--interval-seconds`, `--max-cycles`, Dream Engine selection flags, and optional snapshot output path.
- Verification rules:
  - Test idle behavior when no stimuli qualify.
  - Test repeated-cycle behavior without real sleeping.
  - Test runner wiring separately from Dream Engine internals.

## Phase 128 Autonomous Wake-up Loop Outcome
- Implemented `tonesoul/wakeup_loop.py` as a thin scheduling seam that repeatedly invokes `DreamEngine.run_cycle()` and emits structured `WakeupCycleResult` records.
- The loop owns timing and cycle summaries only. It does not re-score friction, does not bypass `GovernanceKernel`, and does not create a second hidden persistence path.
- Added `scripts/run_dream_wakeup_loop.py` as the host-facing runner. It supports interval-based execution, bounded cycle count, Dream Engine selection flags, and optional JSON snapshot / JSONL history emission.
- This makes the wake-up loop host-driven rather than framework-driven: local loop, cron, GitHub `schedule`, or Windows Task Scheduler can all reuse the same CLI without changing runtime policy code.
- Validation outcome: targeted wake-up loop tests passed, and the full suite finished at `1253 passed`.

## Phase 129 Dream Observability Dashboard Plan
- The dashboard should be an observer, not a participant. It may read `self_journal.jsonl` and wake-up loop artifacts, but it must not mutate runtime state or become a hidden control path.
- Data boundary:
  - Read `self_journal.jsonl` defensively because the metric fields are not stored on one stable schema path.
  - Read wake-up loop history from either JSONL cycle rows or a full snapshot JSON payload.
  - Prefer extracting the few metrics we actually need: friction, Lyapunov, council count, frozen count, and simple convergence hints.
- Presentation boundary:
  - Generate a static HTML artifact with inline charts plus a JSON summary artifact.
  - Keep this independent from `apps/dashboard/` for now so Phase 7 verification can ship without entangling the larger UI stack.
- Verification boundary:
  - Test empty-source behavior and warnings.
  - Test extraction from nested `tension_before` / `tension_after` journal shapes.
  - Test artifact writing from the CLI runner.

## Phase 129 Dream Observability Dashboard Outcome
- Implemented `tonesoul/dream_observability.py` as a defensive metric extractor plus static HTML renderer for Phase 7 verification work.
- The extractor reads `self_journal.jsonl` across multiple schema paths and normalizes a smaller stable contract: journal friction, journal Lyapunov, wake-up avg/max friction, wake-up Lyapunov proxy, and cycle counters.
- Added `scripts/run_dream_observability_dashboard.py` as a thin status-artifact runner that writes `dream_observability_latest.json` and `dream_observability_latest.html` without depending on the larger dashboard frontend.
- Generated a real wake-up snapshot and dashboard artifact in `docs/status/` so the contract exists beyond tests, even though the current snapshot was idle because no qualifying stimuli were present in `soul.db`.
- Validation outcome: targeted dashboard tests passed, and the full suite finished at `1259 passed`.

## Phase 130 Autonomous Dream Cycle Runner Plan
- The next missing piece is not another subsystem; it is composition. Phase 7 already has perception, write gateway, wake-up loop, and observability artifacts, but they still require manual operator choreography.
- The new runner should compose these seams in one direction only:
  - `WebIngestor` (optional URL fetch)
  - `StimulusProcessor`
  - `MemoryWriteGateway`
  - `AutonomousWakeupLoop`
  - `Dream Observability Dashboard`
- Boundary rules:
  - The runner orchestrates file paths and execution order only.
  - It must not re-score governance, rewrite stimulus policy, or introduce a new memory sink.
  - It should degrade gracefully when ingestion inputs fail or Crawl4AI is unavailable, so offline wake-up/dashboard refresh still works.
- Verification rules:
  - Test idle execution with no URLs.
  - Test successful end-to-end execution with injected fake ingest results and a temp SQLite DB.
  - Test CLI artifact writing and overall status reporting.

## Phase 130 Autonomous Dream Cycle Runner Outcome
- Added a host-driven orchestration seam that composes ingestion, stimulus scoring, `soul.db` writes, wake-up execution, and dashboard refresh in a single run without relocating governance policy.
- The runner only coordinates file paths, thresholds, optional URLs, and artifact emission. Friction scoring, council escalation, memory persistence semantics, and dashboard schema ownership remain inside their existing seams.
- The new contract degrades cleanly offline: when there are no URLs, no Crawl4AI availability, or no qualifying stimuli, it can still refresh wake-up snapshots and observability artifacts without inventing synthetic memory side effects.
- Ran the runner once with `--no-llm`; it produced an `idle` cycle, appended a wake-up history entry, and refreshed the latest dashboard artifacts, which proves the composition seam works beyond unit tests.
- Validation outcome: targeted runner tests passed, and the full suite finished at `1264 passed`.

## Phase 131 Curated Source Registry Bridge Plan
- The current weak point is not wake-up logic anymore; it is source selection. The autonomous cycle can ingest URLs, but it still depends on manual URL entry even though the repository already maintains a governed external source registry.
- The fix should stay outside the core runner:
  - Add a perception helper that reads `spec/external_source_registry.yaml`.
  - Reuse the existing allowlist and `reviewed_at` freshness rules when selecting URLs.
  - Let the CLI merge curated registry URLs with ad hoc URL inputs.
- Boundary rules:
  - Do not move source policy into `AutonomousDreamCycleRunner`.
  - Do not add a second source allowlist format.
  - Do not bypass stale-review gating unless the operator explicitly opts in.
- Verification rules:
  - Test `id` and `category` filtering.
  - Test stale registry rejection.
  - Test merged CLI inputs and emitted selection metadata.

## Phase 131 Curated Source Registry Bridge Outcome
- Added a shared registry helper in the perception layer so curated source selection now reuses the same allowlist and freshness policy that the verifier script already enforces.
- Kept the boundary clean: `AutonomousDreamCycleRunner` still only consumes resolved URLs, while `scripts/run_autonomous_dream_cycle.py` is now responsible for merging manual URLs, URL files, and reviewed registry sources.
- Refactored `scripts/verify_external_source_registry.py` to import the shared policy helpers instead of carrying a second copy of URL validation logic, which reduces governance drift between runtime selection and repository verification.
- Ran a real selection against `spec/external_source_registry.yaml`; on 2026-03-07 it returned `ok: true` and selected curated entries beginning with `osv` and `scorecard`, confirming the bridge works on repository data rather than only test fixtures.
- Validation outcome: targeted registry/CLI tests passed, and the full suite finished at `1267 passed`.

## Phase 132 Registry-Driven Schedule Profile Runner Plan
- The next gap is continuity across host-triggered executions. The autonomous cycle can now consume curated registry URLs, but each invocation still starts fresh unless the operator manually chooses a different subset.
- The schedule layer should stay thin:
  - Read already-approved registry entries through `select_curated_registry_urls(...)`.
  - Maintain a cursor/state file that decides which entry is sampled next.
  - Trigger exactly one autonomous cycle per schedule tick and persist schedule artifacts.
- Boundary rules:
  - Do not move registry policy into the schedule runner.
  - Do not move schedule state into `soul.db` or `self_journal.jsonl`.
  - Do not teach `AutonomousDreamCycleRunner` about registry rotation; it should remain URL-driven.
- Verification rules:
  - Test round-robin rotation across approved entries.
  - Test state persistence across separate invocations.
  - Test CLI strict-mode exit behavior when the schedule payload is not fully OK.

## Phase 132 Registry-Driven Schedule Profile Runner Outcome
- Added `AutonomousRegistrySchedule`, a host-driven schedule layer that rotates through already-approved registry entries, persists cursor state outside the memory core, and triggers one autonomous cycle per schedule tick.
- Kept the seams clean:
  - `source_registry` still owns source trust and freshness policy.
  - `AutonomousDreamCycleRunner` still only consumes resolved URLs.
  - The new schedule runner only owns cursor progression, outer-loop timing, and schedule-level artifacts.
- Added a new CLI runner that can be called by cron, Task Scheduler, or GitHub `schedule`, and emits dedicated schedule artifacts (`autonomous_registry_schedule_latest.json`, `registry_schedule_state.json`, `registry_schedule_history.jsonl`) alongside the existing wake-up/dashboard outputs.
- Ran a real smoke cycle on 2026-03-07 against the curated `osv` registry entry. The system fetched `https://osv.dev/`, wrote one environment stimulus into `soul.db`, executed one dream cycle, and returned `overall_ok: true`, which confirms the schedule layer works against a real reviewed source rather than only test doubles.
- Validation outcome: targeted schedule tests passed, and the full suite finished at `1273 passed`.

## Phase 133 Schedule Profile Theory Spec Outcome
- Wrote `docs/plans/registry_schedule_profile_theory_2026-03-07.md` to make the next policy layer derivable rather than improvised.
- The document fixes the core distinction:
  - source registry decides admissible sources
  - schedule profile decides cadence and sampling rhythm
  - governance kernel decides how the system metabolizes the resulting tension
- This matters because the next implementation step should be a profile contract, not a thicker scheduler. If the theory stays implicit, cadence, trust, and memory policy will drift back into the same runtime layer.

## Phase 134 Schedule Profile Contract Plan
- The immediate implementation target is not adaptive scheduling yet. It is a stable contract that can carry cadence defaults without re-encoding them in shell commands.
- The contract should live in `spec/` and express only fields the current schedule layer can execute:
  - registry filters
  - interval
  - entries/URLs per cycle
  - dream-cycle parameter defaults
- Merge rule:
  - profile provides defaults
  - explicit CLI arguments override profile values
  - scheduler core receives only resolved primitive values
- Boundary rule:
  - profile loading belongs in the caller layer and helper module, not inside `AutonomousRegistrySchedule`.

## Phase 134 Schedule Profile Contract Outcome
- Added `spec/registry_schedule_profiles.yaml` as the canonical machine-readable carrier for named schedule profiles (`baseline`, `security_watch`, `research_slow_burn`).
- Added `tonesoul/schedule_profile.py` so profile parsing and validation live outside the scheduler core and can be reused by future runners or dashboards.
- Extended `scripts/run_autonomous_registry_schedule.py` to accept `--profile` and `--profile-path`, merge profile defaults with explicit CLI overrides, and emit the resolved profile in the CLI payload.
- Ran a real profile-driven schedule cycle on 2026-03-07 with `security_watch`; the resolved cadence used `interval_seconds=14400`, security-focused categories, and dream defaults (`limit=4`, `min_priority=0.3`) while still honoring explicit CLI overrides for `entries-per-cycle` and `urls-per-cycle`.
- Validation outcome: targeted profile/schedule tests passed, and the full suite finished at `1276 passed`.

## Phase 135 Schedule Policy Memory Plan
- The next issue is scheduler amnesia. Even with named profiles, the system still lacks an explicit memory of which sources were touched too recently and which ones are temporarily unstable.
- We should add only operational memory, not semantic memory:
  - `revisit_interval_cycles` prevents immediate re-selection of the same entry.
  - `failure_backoff_cycles` temporarily defers entries whose URLs failed during ingestion.
- Boundary rules:
  - Store this state in scheduler artifacts, not in `soul.db` or `self_journal.jsonl`.
  - Treat backoff as operational cooling, not trust revocation.
  - Keep reasons explicit in schedule artifacts so operators can see whether an entry was excluded by registry policy or by scheduler cooldown.

## Phase 135 Schedule Policy Memory Outcome
- Extended the schedule profile contract with `revisit_interval_cycles` and `failure_backoff_cycles`, so cadence memory is now explicit policy rather than hidden control flow.
- Extended scheduler state with per-entry operational memory (`last_selected_cycle`, `backoff_until_cycle`, `consecutive_failures`, `last_outcome`) while keeping that state in artifact files instead of identity memory stores.
- Added explicit defer reporting in schedule payloads, so an operator can now distinguish:
  - source rejected by registry governance
  - source deferred by revisit cooldown
  - source deferred by failure backoff
- Ran a real profile-driven cycle on 2026-03-07 after the policy-memory change. The scheduler advanced to `scorecard`, honored the `security_watch` profile defaults (`revisit_interval_cycles=2`, `failure_backoff_cycles=2`), and persisted per-entry operational state in `registry_schedule_state.json`.
- Validation outcome: targeted schedule-policy tests passed, and the full suite finished at `1278 passed`.

## Phase 136 Deterministic Category Policy Plan
- The next weakness is policy shape, not continuity. Phase 135 gave the scheduler memory, but it still treats all eligible categories as rhythmically flat unless the operator narrows the filter by hand.
- The fix should stay in the profile contract:
  - `category_weights` express how often a category should reappear in the schedule rhythm.
  - `category_backoff_multipliers` express how severely failures in a category should cool that category's entries.
- The implementation must stay deterministic. Random weighted sampling would make artifacts harder to replay and reason about, so the scheduler should prefer a weighted cadence ring plus per-category round-robin, not probabilistic choice.
- Boundary rules:
  - Weight is cadence preference, not epistemic importance.
  - Backoff multiplier is operational cooling, not source trust revocation.
  - These controls belong in schedule profile + artifact state, not in `soul.db`, `self_journal.jsonl`, or `GovernanceKernel`.
- Verification rules:
  - Test deterministic weighted selection order.
  - Test category-scaled backoff duration after failures.
  - Test profile defaults merged with explicit CLI overrides for the new policy knobs.

## Phase 136 Deterministic Category Policy Outcome
- Added `docs/plans/registry_schedule_category_policy_addendum_2026-03-07.md` to make the new cadence policy explicit before implementation. The addendum fixes two meanings that must never blur:
  - category weight is attention rhythm, not truth ranking
  - category backoff multiplier is operational cooling, not trust revocation
- Extended `spec/registry_schedule_profiles.yaml` and `tonesoul/schedule_profile.py` so named profiles can now carry `category_weights` and `category_backoff_multipliers` as first-class contract fields.
- Extended `scripts/run_autonomous_registry_schedule.py` with repeatable `--category-weight` and `--category-backoff-multiplier` overrides, merged on top of profile defaults so the caller keeps final agency without cloning profile files.
- Refactored `AutonomousRegistrySchedule` to support deterministic weighted category cadence:
  - category preference is expanded into a stable cadence ring
  - scheduler state persists `category_cursor` plus per-category entry cursors
  - selection stays replayable because entries inside each category still rotate round-robin
- Kept the memory boundary clean. The new cadence state and cooling multipliers live only in schedule artifacts and config payloads; nothing was moved into `soul.db`, `self_journal.jsonl`, or `GovernanceKernel`.
- Validation outcome:
  - targeted schedule/profile/script tests passed at `13 passed`
  - full suite finished at `1280 passed`

## Phase 137 Cycle-Level Tension Budget Policy Plan
- The next weak point is not source continuity or cadence anymore; it is budget discipline after a high-tension cycle. The scheduler can currently prefer categories and cool failed sources, but it still lacks a principled reaction when the downstream dream/wake-up seam reports a genuine tension spike.
- The boundary must stay strict:
  - `GovernanceKernel` computes friction, Lyapunov, council pressure, and freeze outcomes.
  - wake-up loop summarizes those governance outcomes.
  - scheduler may only react to the summarized signal as an operational cadence consequence.
- The contract should therefore add a cycle-level tension budget:
  - optional threshold for `max_friction_score`
  - optional threshold for `max_lyapunov_proxy`
  - optional threshold for `council_count`
  - cooldown length for breached categories
- This reaction should stay category-scoped and artifact-backed:
  - selected categories in a breached cycle receive temporary schedule cooling
  - the cooling lives in schedule state only
  - artifacts must expose both the observed metrics and the exact breach reasons
- Verification rules:
  - test a threshold breach that creates category cooldown
  - test category defer reporting on the next cycle
  - test CLI/profile override precedence for the new tension budget knobs

## Phase 137 Cycle-Level Tension Budget Policy Outcome
- Added `docs/plans/registry_schedule_tension_budget_addendum_2026-03-07.md` so the schedule reaction is now specified before implementation: scheduler reacts to observed wake-up summary metrics, but it still does not compute governance.
- Extended `spec/registry_schedule_profiles.yaml` and `tonesoul/schedule_profile.py` with four new policy fields:
  - `tension_max_friction_score`
  - `tension_max_lyapunov_proxy`
  - `tension_max_council_count`
  - `tension_cooldown_cycles`
- Extended `scripts/run_autonomous_registry_schedule.py` with matching CLI overrides so operators can tighten or relax the tension budget without cloning profile files.
- Refactored `AutonomousRegistrySchedule` so it now:
  - extracts cycle-level observation from `wakeup_payload.results[].summary`
  - evaluates budget breach at the schedule layer only
  - persists category-level cooldown in schedule state artifacts
  - emits `tension_budget` observations plus `tension_budget_cooldown` defer reasons in schedule results
- Kept the boundary clean:
  - no new friction math was added to scheduler
  - no budget state was moved into `soul.db` or `self_journal.jsonl`
  - category cooldown remains operational memory, not trust or identity memory
- Validation outcome:
  - targeted schedule/profile/script tests passed at `14 passed`
  - full suite finished at `1281 passed`

## Phase 138 Incremental Commit Attribution Parity Plan
- The GitHub Actions failure triage exposed a real governance smell: our most important commit-attribution gate existed as workflow-local glue. That makes the rule hard to replay locally and turns historical trailer debt into remote-only surprise.
- The fix should not be "copy the workflow into docs." It should be a shared executable seam:
  - one script resolves the incremental revision range for `push`, `pull_request`, and local merge-base mode
  - GitHub Actions calls that script
  - local healthcheck calls that script
- The second requirement is contextual failure, not just red/green. Missing trailers are not runtime crashes; the script must preserve per-revision summaries even when the overall gate fails.
- Boundary rule:
  - repo healthcheck may aggregate the blocking result
  - if we later want a thinner pre-push entry, that wrapper should compose shared scripts rather than re-encode commit-range logic again

## Phase 138 Incremental Commit Attribution Parity Outcome
- Replaced the inline commit-attribution range logic in `.github/workflows/test.yml` with `scripts/verify_incremental_commit_attribution.py`, so CI and local runs now share the same revision-plan semantics.
- Hardened `scripts/verify_incremental_commit_attribution.py` so it no longer discards failure context when an individual revision lacks trailers. The report now keeps per-revision payloads and aggregate `missing` context instead of collapsing into an opaque exception.
- Added the same blocking gate to `scripts/run_repo_healthcheck.py`, so the normal local contract run now surfaces commit-attribution debt before push.
- Added regression tests for revision-plan resolution, failure-context preservation, and healthcheck inclusion.
- Ran the new script on the real branch state on 2026-03-08. Result:
  - local mode resolved `origin/master..HEAD`
  - `missing_count=5`
  - all five missing entries were historical commits without `Agent` / `Trace-Topic` trailers
- Validation outcome:
  - targeted attribution/healthcheck tests passed at `26 passed`
  - full suite finished at `1304 passed`
- This is useful because it converts remote CI archaeology into immediate local evidence. The branch still carries trailer debt, but that debt is now explicit and machine-readable.

## Phase 139 Isolated Trailer Debt Remediation Plan
- Once the debt became visible, the next temptation would have been to rewrite `feat/env-perception` in place. That would have been the wrong move because the current worktree is heavily dirty and mixes unrelated, uncommitted work.
- The safer pattern is repository-native isolation:
  - leave the dirty working tree untouched
  - create a clean side branch from `origin/master`
  - replay only the debt-bearing commits with backfilled trailers
  - verify both attribution success and tree equality
- This is not just operational caution. It preserves epistemic clarity:
  - one branch represents the live messy workspace
  - one branch represents the historical-remediation candidate
  - the evidence artifact explains exactly what changed and what did not

## Phase 139 Isolated Trailer Debt Remediation Outcome
- Created `feat/env-perception-attribution-backfill` via `git worktree` isolation instead of modifying the dirty `feat/env-perception` branch in place.
- Replayed the five historical commits from `origin/master..c225332` with explicit backfill trailers:
  - `Agent: legacy-backfill`
  - commit-specific `Trace-Topic`
- Verified the rewritten side branch with `docs/status/commit_attribution_backfill_branch.json`:
  - `checked_count=5`
  - `missing_count=0`
  - `ok=true`
- Verified content equivalence by comparing tree hashes:
  - rewritten branch head tree = `1a879968fcefbb32afac2745f86b6227ac5167b0`
  - original `c225332^{tree}` = `1a879968fcefbb32afac2745f86b6227ac5167b0`
- This matters because the remediation changed commit metadata only; it did not alter repository content.
- Removed the temporary worktree after verification so the main workspace stayed clean except for the evidence artifact and the new remediation branch ref.

## Phase 140 Schema-Driven Council LLM Parsing Plan
- A useful gift is not useful just because it exists. `tonesoul/safe_parse.py` and `tonesoul/schemas.py` were real seams, but they were not yet sitting on the highest-risk runtime path.
- The first good landing zone is council perspective evaluation:
  - it parses raw LLM text from both Gemini and Ollama
  - it previously hand-rolled JSON extraction and field access
  - a bug there directly distorts council votes, not just offline reporting
- But a naive replacement would have been too brittle. Some local models still emit half-structured text, so the right pattern is:
  - schema-first parse for structured outputs
  - bounded text heuristic fallback for weak outputs
  - one shared parse seam for both Gemini and Ollama
- That keeps the runtime more typed without pretending every model is already disciplined.

## Phase 140 Schema-Driven Council LLM Parsing Outcome
- Added `PerspectiveEvaluationResult` to `tonesoul/schemas.py` as the minimal Pydantic contract for council perspective outputs (`decision`, `confidence`, `reasoning`).
- The schema normalizes uppercase decision values before validation, which matters because existing prompts still instruct models to emit `APPROVE` / `CONCERN` / `OBJECT`.
- Replaced the manual `_parse_llm_response()` logic in `tonesoul/council/perspective_factory.py` with a shared schema-driven parse path built on `parse_llm_response()`.
- Kept a bounded text fallback for non-JSON outputs. This preserves operational resilience for weaker local models instead of turning a schema improvement into a runtime regression.
- Reused the same parsing seam for both `LLMPerspective` and `OllamaPerspective`, so the council no longer maintains two parallel response parsers.
- Validation outcome:
  - targeted schema/perspective tests passed at `33 passed`
  - adjacent custom-role coverage passed at `52 passed`
- I inspected `tonesoul/observability/` as part of this gift review. The package is viable, but I did not force observability refactors into this round because the highest-value defect was untyped council parsing, not logging or token metering drift.

## Phase 141 Local LLM Usage Metering Plan
- After schema-first parsing, the next useful landing zone for the gifted observability layer was local LLM clients, not top-level orchestration.
- Reason:
  - `OllamaClient` already receives token-like counters from the upstream API (`prompt_eval_count`, `eval_count`)
  - `LMStudioClient` can receive OpenAI-compatible `usage`
  - both clients sit close enough to the source that metering can stay factual
- The boundary matters:
  - if usage exists, record it as observability evidence
  - if usage does not exist, do not invent numbers just to make dashboards look complete
  - keep the integration backward compatible by making metering optional and non-invasive

## Phase 141 Local LLM Usage Metering Outcome
- Extended `tonesoul/llm/ollama_client.py` and `tonesoul/llm/lmstudio_client.py` with optional `TokenMeter` injection and `last_metrics` capture using the existing `LLMCallMetrics` schema.
- Ollama now records usage only when the upstream payload includes `prompt_eval_count` and `eval_count`.
- LM Studio now records usage only when the upstream payload includes a valid `usage` object.
- This was intentionally fail-silent on missing usage: the client keeps `last_metrics=None` instead of fabricating zero-token records, because false precision would pollute later budget reasoning.
- Added dedicated regression coverage for both clients plus the existing observability and Ollama fallback tests.
- Validation outcome:
  - client-level observability/fallback tests passed at `28 passed`
- This change makes `tonesoul/observability/token_meter.py` part of the real local inference path instead of a standalone utility module.

## Phase 142 Runtime LLM Evidence Attachment Plan
- Client-level metrics are still too low in the stack to count as orchestration evidence. They prove what a client saw, but they do not yet prove what the pipeline actually dispatched in a given runtime path.
- The right next seam is therefore thin, not grand:
  - expose `last_metrics` through `LLMRouter`
  - attach backend/model/usage into `dispatch_trace["llm"]` only after a successful generation
  - keep missing usage silent instead of backfilling fake counters
- This matters epistemically:
  - `TokenMeter` is an accounting utility
  - `dispatch_trace` is runtime evidence
  - the same numbers should not become governance-relevant until the orchestrator binds them to a specific execution path

## Phase 142 Runtime LLM Evidence Attachment Outcome
- Extended `tonesoul/llm/router.py` with a read-only `last_metrics` property that forwards the active cached client's usage evidence.
- Added a narrow `_attach_llm_observability()` seam in `tonesoul/unified_pipeline.py`.
- After a successful `send_message()`, the pipeline now records additive LLM evidence in `dispatch_trace["llm"]`:
  - `backend` from resolved routing state
  - `model` from the emitted metrics when available, otherwise from the active client
  - `usage` only when the current call actually produced token counters
- The trace deliberately omits `usage` when upstream payloads provide no counters, so the pipeline does not convert absence of evidence into false telemetry.
- Added regression coverage for both router passthrough and runtime dispatch-trace attachment.

## Phase 143 Dream/Wake-up LLM Evidence Plan
- The pipeline now knows LLM evidence, but the autonomous branch still does not. That leaves a split-brain observability problem:
  - interactive runtime can explain which backend/model/tokens were used
  - dream/wake-up artifacts can only explain friction and Lyapunov
- The next seam is not to teach the dashboard how to parse arbitrary deep collision payloads. That would collapse observer responsibility into archaeology.
- The cleaner evidence chain is:
  - Dream Engine records per-collision LLM evidence next to the reflection result
  - Wake-up loop aggregates those collision-level facts into cycle summary
  - Dream observability dashboard reads only cycle-level summary for charts and cards
- This preserves role boundaries:
  - Dream Engine knows whether a reflection call happened and what client evidence exists
  - Wake-up loop owns temporal aggregation
  - Dashboard remains a passive reader of already-shaped metrics
- This is the right boundary because `dream_observability.py` is an observer, not a second orchestrator. If it starts re-reading full collision internals to recompute usage, it quietly becomes an analytics kernel instead of a renderer.
- Backend and model are categorical evidence, not trend metrics. They belong in recent-cycle rows and summary tables.
- Token counts are numeric evidence. They are eligible for cycle-level trend series once the wake-up summary has aggregated them.
- Planned additive fields:
  - collision observability: `llm.backend`, `llm.model`, `llm.usage.*`
  - wake-up summary: `llm_call_count`, `llm_total_tokens`, and prompt/completion token totals
  - dashboard series/summary: cycle-level `wakeup_llm_total_tokens`
- Constraint:
  - no fabricated usage if the reflection backend returns no counters
  - no new writes into `self_journal.jsonl`
  - no dashboard dependency on parsing every collision body directly

## Phase 143 Dream/Wake-up LLM Evidence Outcome
- Extended `tonesoul/dream_engine.py` so each collision now records an additive `observability["llm"]` payload when reflection-time LLM evidence exists.
- The collision-level LLM evidence mirrors the same contract introduced in `UnifiedPipeline`:
  - `backend`
  - `model`
  - `usage` only when token counters are actually present
- This matters because it keeps online and offline inference evidence structurally aligned without pretending they share the same orchestrator.
- Extended `tonesoul/wakeup_loop.py` to aggregate collision-level LLM facts into cycle summary instead of forcing downstream readers to walk every collision body.
- The wake-up summary now includes:
  - `llm_call_count`
  - `llm_prompt_tokens_total`
  - `llm_completion_tokens_total`
  - `llm_total_tokens`
  - `llm_backends`
- Extended `tonesoul/dream_observability.py` to surface `wakeup_llm_total_tokens` as a first-class series/summary/card/chart and to expose LLM usage/backends in recent cycle rows.
- The dashboard still remains passive: it only reads cycle summary, not raw collision internals.
- Validation outcome:
  - targeted dream/wakeup/dashboard tests passed at `15 passed`
- Architectural meaning:
  - Dream Engine owns per-collision evidence
  - Wake-up loop owns temporal aggregation
  - Dashboard owns presentation only

## Runtime Validation Note: Backend Discovery Is Not Inference Readiness
- On 2026-03-08, `LLMRouter` successfully resolved `lmstudio` and `LMStudioClient.list_models()` returned loaded models.
- But a direct `/v1/chat/completions` probe with a trivial short prompt timed out at 10 seconds.
- That means the current local health signal distinguishes discovery only:
  - backend exists
  - model list exists
  - but inference latency/readiness is still unknown
- This matters for autonomous scheduling more than for interactive chat. A wake-up loop that trusts discovery-only health can stall on long reflection calls and fail to emit fresh evidence artifacts on schedule.
- The design consequence is clear:
  - backend discovery health and inference readiness health must be treated as different contracts
  - future autonomy preflight should probe a bounded real completion path, not only `/models`

## Phase 144 Inference-Readiness Preflight Plan
- The next fix should not be a giant health framework. The correct cut is a thin autonomy guard:
  - local clients expose a bounded completion probe with caller-supplied timeout
  - `LLMRouter` normalizes that probe into one readiness contract
  - autonomous dream/wakeup runners enable the probe by default before reflection generation
  - callers can explicitly skip the probe when they want raw backend behavior
- Boundary rules:
  - do not change the main `generate()` / `chat()` contracts for existing runtime callers
  - keep probe telemetry separate from real reflection telemetry; a preflight call must not masquerade as the production reflection call
  - record preflight outcome in autonomous artifacts so a skipped or failed reflection is explainable later
- Intended artifact semantics:
  - discovery success answers "which backend was chosen?"
  - readiness success answers "can bounded inference complete now?"
  - reflection usage answers "what did the real autonomous call consume?"

## Phase 144 Inference-Readiness Preflight Outcome
- The thin guard was enough. `OllamaClient` and `LMStudioClient` now expose bounded `probe_completion()` methods that:
  - accept caller-supplied timeouts
  - report backend/model/latency/reason in a small readiness contract
  - leave `last_metrics` untouched so preflight calls do not pollute real usage evidence
- `LLMRouter` now normalizes those probes through `inference_check()`, which means autonomy code can ask one question:
  - "is bounded inference ready right now?"
  instead of inferring readiness from backend discovery behavior.
- `DreamEngine` now records `llm_preflight` per cycle and applies a strict rule:
  - if reflection is disabled, preflight says so explicitly
  - if callers skip preflight, the artifact says it was skipped
  - if readiness fails, reflection is skipped for that cycle rather than hanging the wake-up path on discovery optimism
- The autonomy boundary stayed clean:
  - probe calls are separate from production reflection calls
  - no existing `generate()` or `chat()` contract changed
  - readiness flags were threaded only through autonomous runners and CLI entrypoints
- Regression coverage passed for:
  - local client probe success/timeout semantics
  - router normalization
  - dream-cycle reflection suppression on failed readiness
  - CLI skip-preflight plumbing across dream, wake-up, autonomous cycle, and registry schedule runners
- A live wake-up probe surfaced one more semantic leak after the first implementation:
  - preflight failure correctly suppressed reflection generation
  - but backend-only collision observability still inflated `llm_call_count`
  - the fix was to attach collision-level LLM evidence only when `reflection_generated` is true and to make wake-up aggregation defensively ignore `observability["llm"]` on collisions that did not actually generate reflection
- Validation evidence:
  - `ruff` passed on the touched autonomy/LLM files and tests
  - `black --check` passed after formatting `tonesoul/llm/lmstudio_client.py`
  - targeted `pytest` passed: `24 passed, 2 warnings`
  - post-probe regression passed: `31 passed, 2 warnings`
  - full repository regression passed: `1342 passed, 3 warnings`
- Live runtime evidence after the correction:
  - a real `run_dream_wakeup_loop.py` probe against local LM Studio completed instead of hanging indefinitely
  - `llm_preflight` reported `reason=timeout`, `backend=lmstudio`, `model=qwen3.5-9b`
  - the same cycle now reports `llm_call_count=0` and `llm_total_tokens=0`, which keeps preflight failure separate from real reflection usage
- Architectural conclusion:
  - discovery tells the system what it *could* talk to
  - readiness tells the system what it can *finish talking to within budget right now*
  - autonomous scheduling should trust the latter when deciding whether to launch reflection work

## Phase 145 Preflight Deadline Budget Plan
- The next correction is not another probe type. It is a time-budget correction:
  - one probe budget should be consumed by the whole readiness path
  - model resolution cannot quietly spend one timeout and leave the full timeout untouched for the network call
  - connect/read timeout configuration should reflect a total deadline, not a duplicated scalar timeout that can stretch beyond the caller's stated budget
- Intended cut:
  - local clients compute one deadline at probe start
  - model discovery uses the remaining time budget only
  - HTTP probe requests receive bounded connect/read timeout tuples derived from the same remaining budget
  - if budget is exhausted during model resolution, the probe should fail explicitly instead of continuing optimistically
- Why this matters:
  - autonomy policies reason over `timeout_seconds` as an operational promise
  - if the implementation treats that number as advisory and overspends it by a factor of two, later scheduler and budget logic will rest on false temporal evidence

## Phase 145 Preflight Deadline Budget Outcome
- The bug was real: a nominal `2.0s` readiness budget was producing about `4002ms` of preflight latency on LM Studio.
- Root cause:
  - the probe path did not consume one deadline
  - model resolution and HTTP request execution each got their own effectively independent timeout behavior
  - scalar `requests` timeouts were too loose for treating the budget as a total deadline contract
- The correction stayed local to the clients:
  - `LMStudioClient` and `OllamaClient` now compute one probe deadline at start
  - model resolution consumes only the remaining budget
  - HTTP calls use connect/read timeout tuples derived from the same remaining budget
  - budget exhaustion during model resolution now fails explicitly as timeout instead of proceeding optimistically
- This preserved external contracts:
  - no new runtime API shape
  - no new orchestration concepts
  - no changes to normal `generate()` / `chat()` semantics
- Validation outcome:
  - targeted readiness tests passed: `4 passed, 2 warnings`
  - broader LLM/autonomy regression passed: `41 passed, 2 warnings`
- Live runtime evidence:
  - after the correction, the same `run_dream_wakeup_loop.py` probe with `--llm-probe-timeout-seconds 2` completed with:
    - `llm_preflight.reason = timeout`
    - `llm_preflight.latency_ms = 2002`
    - cycle duration about `2817ms`
    - `llm_call_count = 0`
  - this is the correct shape: the system still identifies the backend, still skips reflection, but no longer burns a double-sized timeout budget to learn that fact
- Architectural conclusion:
  - a scheduler budget is not documentation; it is an executable deadline contract
  - if a lower layer splits that budget into multiple hidden waits, observability becomes temporally false even when the status fields look reasonable

## Phase 146 Router Deadline Accounting Plan
- The next deadline leak sits one layer above the clients:
  - even if client probes obey one deadline internally, router-side backend selection can still spend hidden discovery time before the probe starts
  - if the router then forwards the full original timeout to the probe, total preflight latency can exceed budget while every layer claims innocence
- Intended correction:
  - start the deadline in `LLMRouter.inference_check()`
  - charge backend resolution against that same deadline
  - pass only the remaining budget into `probe_completion()`
  - expose latency decomposition so later artifacts can tell whether time was spent choosing a backend or waiting on inference

## Phase 146 Router Deadline Accounting Outcome
- `LLMRouter.inference_check()` now treats `timeout_seconds` as a router-level end-to-end budget instead of a probe-only hint.
- The router now:
  - starts one deadline before `get_client()`
  - records `selection_latency_ms`
  - forwards only the remaining seconds to the probe
  - fails with `reason=timeout` if backend selection alone exhausts the budget
- The readiness artifact stayed shape-compatible but gained better evidence:
  - `latency_ms` now means total router+probe preflight latency
  - `selection_latency_ms` explains discovery cost
  - `probe_latency_ms` explains the downstream probe portion when available
- Regression evidence passed:
  - focused router tests: `5 passed, 2 warnings`
  - broader autonomy regression: `32 passed, 2 warnings`
- Live runtime evidence from the same `2.0s` LM Studio preflight:
  - `latency_ms = 2002`
  - `selection_latency_ms = 759`
  - `probe_latency_ms = 1243`
  - total cycle duration about `2035ms`
  - `llm_call_count = 0`
- Architectural conclusion:
  - a time budget is only honest if every orchestration layer charges itself to the same clock
  - once latency is decomposed by layer, future scheduler policy can distinguish "backend selection is slow" from "inference is slow" without inventing hidden narratives

## Phase 147 Scheduler Latency Policy Plan
- The next seam is not inside the LLM stack anymore. It is the handoff from runtime evidence into autonomy policy:
  - `llm_preflight` currently exists on the dream result
  - but scheduler cooldown policy still reads only friction, Lyapunov, and council count
  - dashboard summaries still underexpose the latency decomposition that now exists
- Intended chain:
  - promote `llm_preflight` into wake-up summary fields
  - let `AutonomousRegistrySchedule` consume those summary fields instead of spelunking raw dream payloads
  - extend schedule profiles and CLI with optional preflight latency thresholds
  - expose the same fields in observability JSON/HTML so humans see the same evidence the scheduler reacts to
- Boundary rule:
  - scheduler must not infer hidden latency causes from raw traces
  - it may only react to explicit wake-up summary facts such as total preflight latency, selection latency, probe latency, and timeout count

## Phase 147 Scheduler Latency Policy Outcome
- `wakeup_loop` now promotes `llm_preflight` into cycle summary, which means downstream layers do not need to read raw dream payloads to understand readiness timing.
- New wake-up summary fields now include:
  - `llm_preflight_latency_ms`
  - `llm_preflight_selection_latency_ms`
  - `llm_preflight_probe_latency_ms`
  - `llm_preflight_timeout_count`
  - `llm_preflight_reason`
- `AutonomousRegistrySchedule` now treats those summary fields as part of the same cycle budget observation as friction, Lyapunov, and council count.
  - it can breach on total preflight latency
  - it can breach specifically on selection latency
  - it can breach specifically on probe latency
  - it can breach on timeout count
- The key boundary stayed intact:
  - scheduler still does not parse raw dream collisions or LLM traces
  - it reacts only to explicit wake-up summary facts
- Profile and CLI contracts now expose optional latency thresholds, so policy can be declared instead of hardcoded.
- `dream_observability` now surfaces the same latency decomposition in JSON/HTML:
  - total preflight latency
  - selection latency
  - probe latency
  - timeout count
  - recent-cycle reason columns
- Validation outcome:
  - targeted policy/dashboard regression passed: `23 passed, 2 warnings`
- Real runtime verification:
  - `security_watch` was run against the live local stack with isolated artifacts
  - the selected category `vulnerability-intel` breached on both governance and LLM latency facts
  - observed latency evidence included:
    - `max_llm_preflight_latency_ms = 2002`
    - `max_llm_selection_latency_ms = 757`
    - `max_llm_probe_latency_ms = 1245`
    - `llm_preflight_timeout_count = 1`
  - the schedule correctly cooled the category and persisted the observed latency facts into schedule state
- Architectural conclusion:
  - once preflight latency becomes summary-level evidence, autonomy policy can cool itself for the right reason
  - this is materially better than a vague "LLM unhealthy" flag, because the system can now tell whether the bottleneck is choosing a backend or waiting on it

## Phase 148 LLM Backoff Plan
- The next correction is about action semantics, not more telemetry:
  - governance breaches should keep using category cooldown because they are about source/category-level tension
  - LLM latency and timeout breaches should not freeze categories by default because they are global runtime conditions, not proof that one source category is intrinsically unhealthy
- Intended cut:
  - split budget breaches into governance-side and LLM-side reasons
  - keep category cooldown for governance-side reasons
  - introduce a global LLM backoff state for LLM-side reasons
  - while LLM backoff is active, autonomous cycles continue rotating sources but run without reflective LLM work
- Boundary rule:
  - schedule should not disable ingestion or source rotation just because the LLM is slow
  - the correct degraded mode is "continue observing, temporarily stop reflective inference"

## Phase 148 LLM Backoff Outcome
- The scheduler now separates tension-budget breach semantics into two families:
  - `governance_breach_reasons`
  - `llm_breach_reasons`
- Consequence now follows the right ownership boundary:
  - governance-side breaches still cool selected categories
  - pure LLM runtime breaches now activate global `llm_backoff` instead of freezing source categories
- While `llm_backoff` is active, the schedule still rotates sources but forces degraded execution:
  - `generate_reflection=False`
  - `require_inference_ready=False`
- The first implementation exposed an additional bug:
  - degraded cycles without a fresh wake-up summary were overwriting `last_llm_*` category facts with `None`
  - that made the state artifact forget the evidence that caused the backoff in the first place
- The correction was to treat "no new observation" as distinct from "observed zero":
  - category `last_*` metrics are now refreshed only when `observed_cycles > 0`
  - degraded cycles may still update budget/backoff status, but they do not erase prior observed latency evidence
- Validation outcome:
  - focused schedule tests passed: `9 passed, 2 warnings`
  - broader schedule/dashboard regression passed: `26 passed, 2 warnings`
- Architectural conclusion:
  - source cadence and runtime reflection capacity are orthogonal control surfaces
  - if the system cools categories for pure runtime failures, it mistakes infrastructure pain for epistemic distrust
  - a backoff artifact must preserve the last real evidence until a newer summary replaces it, or the scheduler loses the ability to explain its own degraded mode

## Phase 149 Schedule Governance Observability Plan
- The next seam is now representation, not policy:
  - Phase 148 separated category cooldown from global LLM backoff inside scheduler state
  - but the dashboard still visualizes only wake-up metrics, so a human cannot directly see those two governance control surfaces diverge over time
- Intended contract:
  - keep `journal + wakeup` as the existing base dashboard input
  - add optional `schedule_history_path` and `schedule_state_path` as a third evidence source
  - plot schedule-level curves for:
    - governance cooldown applied/deferred
    - LLM backoff requested/active
  - expose current schedule state without requiring the dashboard to reverse-engineer raw scheduler internals
- Boundary rule:
  - dashboard should read explicit schedule artifacts, not infer cooldown/backoff from wake-up latency alone
  - missing schedule artifacts must remain a non-breaking absence, not a hard failure for existing dream-only callers

## Phase 149 Schedule Governance Observability Outcome
- `dream_observability` now accepts optional `schedule_history_path` and `schedule_state_path` without breaking existing journal+wakeup callers.
- The dashboard now renders schedule-side governance explicitly instead of smuggling it through wake-up inference:
  - governance cooldown applied
  - governance cooldown deferred
  - LLM backoff requested
  - LLM backoff active
- The representation is intentionally split across two schedule artifacts:
  - schedule history provides cycle-level curves and recent schedule rows
  - schedule state provides present-tense active cooldown/backoff status
- `AutonomousRegistrySchedule` now refreshes the enriched dashboard automatically after each schedule run when it has journal/wakeup/dashboard context.
- Validation outcome:
  - focused observability/schedule regression passed: `17 passed, 2 warnings`
  - broader autonomy regression passed: `34 passed, 2 warnings`
- Real artifact verification:
  - the dashboard was regenerated against the historical `probe_schedule_latency_policy` artifacts into `docs/status/probe_schedule_governance_dashboard`
  - governance cooldown curves appeared correctly from schedule history/state
  - LLM backoff curves remained zero in that historical sample because the artifact predates the Phase 148 split, which is a compatibility fact rather than a dashboard defect
- Architectural conclusion:
  - wake-up evidence explains experience; schedule evidence explains reaction
  - if a dashboard tries to derive scheduler policy only from wake-up traces, it collapses two governance layers into one story and loses causal clarity

## Phase 150 LLM Backoff Activation Verification Outcome
- A fresh zero-interval live probe was run after the Phase 149 dashboard changes so the schedule artifact could capture two adjacent states in one trace:
  - cycle 1 requested global LLM backoff
  - cycle 2 executed while that backoff was active
- The resulting artifact in `docs/status/probe_schedule_governance_live2` verified the intended temporal split:
  - `schedule_llm_backoff_requested_total = 1`
  - `schedule_llm_backoff_active_total = 1`
  - cycle 1 showed `llm_backoff_requested = true`, `llm_backoff_active = false`
  - cycle 2 showed `llm_backoff_requested = false`, `llm_backoff_active = true`, `llm_backoff_action = disable_reflection`
- Governance cooldown also remained present across the same two-cycle sample, which is important because it proves the system can hold:
  - category-scoped governance cooling
  - global runtime reflection backoff
  as simultaneous but non-identical states
- One small operational lesson surfaced during verification:
  - if the probe forgets `--interval-seconds 0`, the artifact race can masquerade as missing data simply because the second cycle is sleeping
  - that was a probe setup issue, not a scheduler defect
- Architectural conclusion:
  - `requested` and `active` are not synonyms; they are consecutive scheduler states
  - a trustworthy governance dashboard must preserve this temporal distinction, otherwise operators cannot tell whether they are looking at a trigger event or a currently degraded operating mode

## Phase 151 Pure Runtime Probe Profile Plan
- The next mainline step is packaging the proven Phase 150 runtime scenario as a named schedule profile instead of repeating a fragile CLI recipe.
- Boundary rule:
  - this phase should not invent new scheduler policy
  - it should only define a reproducible profile that keeps governance thresholds relaxed while preserving tight LLM runtime thresholds
- Intended outcome:
  - humans and agents can run the same "pure runtime verification" entrance without rebuilding the threshold bundle from memory
  - a later live probe can show LLM backoff on its own, without governance cooldown muddying the story

## Phase 151 Pure Runtime Probe Profile Outcome
- The Phase 150 live verification bundle is now packaged as `runtime_probe_watch` inside `spec/registry_schedule_profiles.yaml`, so the scenario has become a governed entrypoint instead of an operator memory exercise.
- The profile is intentionally asymmetrical:
  - governance thresholds are relaxed enough to stay non-triggering during ordinary runtime probes
  - LLM readiness thresholds remain tight enough to expose timeout and latency breaches on the current local stack
- The live two-cycle probe in `docs/status/probe_runtime_profile_live` verified the intended separation:
  - cycle 1 showed `governance_breached = false`, `llm_breached = true`, `llm_backoff_requested = true`
  - cycle 2 showed `governance_breached = false`, `llm_policy_active = true`, `llm_policy_action = disable_reflection`
  - the final schedule state had `active_governance_cooldown_categories = []` while global `llm_backoff` remained active through cycle 3
- Architectural conclusion:
  - once a runtime verification scenario has been proven in the field, it should be promoted into a named profile so future operators rerun policy, not folklore
  - a schedule profile can carry epistemic intent: here it declares "treat runtime pain as runtime pain" by refusing to reinterpret latency failures as distrust of the selected source category

## Phase 152 Runtime Preflight Entrypoint Plan
- The next step is operational compression, not new policy.
- Problem:
  - `runtime_probe_watch` is now a proper named profile
  - but operators still need to remember the generic registry-schedule command and multiple artifact paths to use it correctly before a long autonomous run
- Intended change:
  - add one thin runner script dedicated to runtime preflight
  - keep the policy anchored in `runtime_probe_watch`
  - keep the generic schedule runner free of special-case control flow
- Boundary rule:
  - do not duplicate scheduler logic
  - do not move runtime verification into `run_repo_healthcheck.py`, because that script is a broad repository gate and the runtime probe is an autonomy-specific operational ritual

## Phase 152 Runtime Preflight Entrypoint Outcome
- `scripts/run_runtime_probe_watch.py` now provides the single operational entrance for runtime verification while delegating the real work back to the generic registry schedule runner.
- The runner deliberately keeps policy externalized:
  - profile identity stays `runtime_probe_watch`
  - threshold logic still lives in the shared schedule profile contract
  - the wrapper only fixes the ritual, the artifact paths, and the preflight identity
- Live verification exposed a real operational weakness during implementation:
  - if the preflight runner simply appends to previous state/history, repeated invocations stop being a clean two-cycle ritual
  - the resulting artifacts begin to describe a blended timeline instead of the current verification event
- The wrapper now defaults to a fresh sample by clearing its own prior history/state/dashboard artifacts unless `--reuse-state` is explicitly requested.
- Final live validation against `docs/status/runtime_probe_watch` confirmed the intended contract:
  - `preflight_profile = runtime_probe_watch`
  - `cycles_run = 2`
  - cycle 1 showed `governance_breached = false`, `llm_breached = true`, `llm_backoff_requested = true`
  - cycle 2 showed `governance_breached = false`, `llm_policy_active = true`, `llm_policy_action = disable_reflection`
  - dashboard summary showed `schedule_governance_cooldown_applied_total = 0`, `schedule_llm_backoff_requested_total = 1`, `schedule_llm_backoff_active_total = 1`
- Architectural conclusion:
  - a preflight entrypoint is not trustworthy if it silently carries yesterday's state into today's verdict
  - verification rituals should default to isolation and make historical accumulation an explicit opt-in, not an accidental side effect

## Phase 153 Runtime-Gated Long-Run Plan
- The next mainline seam is orchestration:
  - we now have a trustworthy runtime preflight ritual
  - but the long-running autonomous schedule still has no first-class entrance that requires that ritual before the real run begins
- Intended change:
  - add one dedicated long-run wrapper that first executes `runtime_probe_watch`
  - only if that preflight returns `overall_ok = true` should it continue into the real registry schedule
- Boundary rule:
  - keep the generic schedule runner untouched as a reusable primitive
  - keep the preflight wrapper reusable on its own
  - encode the "probe before long run" policy in a dedicated orchestration layer, not in the lower-level runners

## Phase 153 Runtime-Gated Long-Run Interim Note
- The first live run of the long-run wrapper surfaced one more contract leak:
  - the preflight gate used a 2-second runtime budget
  - the downstream long run silently fell back to the generic schedule default of 10 seconds
- That means the system could say "runtime is acceptable under one budget" and then immediately execute under a looser budget.
- The next edit should align those budgets by default, while still allowing explicit operator override.

## Phase 153 Runtime-Gated Long-Run Outcome
- `scripts/run_autonomous_registry_long_run.py` now serves as the orchestration seam between:
  - runtime verification (`runtime_probe_watch`)
  - the real autonomous registry schedule
- The wrapper keeps lower layers clean:
  - preflight remains a dedicated runner with its own artifact ritual
  - the generic schedule runner stays policy-agnostic and reusable
  - the gate itself lives only in the orchestration layer
- The final contract is:
  - if runtime probe fails, the long run is blocked before the real schedule begins
  - if reflection is disabled via `--no-llm`, the runtime gate is skipped as not applicable
  - if the operator explicitly skips the gate, the payload records that as an override rather than pretending a probe occurred
- The live runs revealed a second important rule:
  - a long-run wrapper should not silently use a looser runtime budget than the preflight that just authorized it
  - the wrapper now inherits `--preflight-llm-probe-timeout-seconds` into the real schedule whenever the operator did not explicitly set `--llm-probe-timeout-seconds`
- Fresh live verification against `docs/status/probe_runtime_gated_long_run_fresh` confirmed the aligned contract:
  - gate status was `passed`
  - the real schedule used the inherited runtime budget, yielding `llm_preflight_latency_ms ≈ 2003` rather than the earlier 10-second drift
  - the real schedule still showed governance and LLM breaches under `security_watch`, which is acceptable because the gate checks readiness, not guaranteed convergence
- Architectural conclusion:
  - a runtime gate authorizes a run under a declared budget; it should not quietly authorize one budget and execute under another
  - orchestration layers are where this promise must be enforced, because lower-level runners cannot know whether they are part of a gate, a probe, or a real production cycle

## Phase 154 True Verification Experiment Entrypoint Plan
- The next mainline gap is ritual, not capability:
  - `run_autonomous_registry_long_run.py` can already enforce runtime gating
  - but Phase 7 still lacks a first-class entrance that encodes the intended one-week experiment envelope
- Intended change:
  - add one dedicated experiment wrapper for the weekly True Verification run
  - default it to the operating cadence described in the Phase 7 proposal:
    - 7 days
    - 3-hour wake interval
  - give it stable artifact roots so the experiment has a remembered identity beyond ad-hoc CLI strings
- Boundary rule:
  - do not move weekly experiment policy into the generic schedule runner
  - do not duplicate preflight logic already owned by `run_autonomous_registry_long_run.py`
  - keep the new layer thin: it should compose duration, cadence, artifact namespace, and experiment identity only

## Phase 154 True Verification Experiment Entrypoint Outcome
- `scripts/run_true_verification_experiment.py` now turns the Phase 7 weekly ritual into a first-class operating entrance rather than a remembered shell recipe.
- The wrapper keeps lower layers intact:
  - runtime gating still belongs to `run_autonomous_registry_long_run.py`
  - `runtime_probe_watch` remains the preflight ritual
  - schedule policy still lives in named profiles such as `security_watch`
- What the new layer adds is only experiment-level orchestration:
  - default duration = 7 days
  - default wake interval = 3 hours
  - derived `planned_cycles = ceil(days * 24 / wake_interval_hours)` when operators do not set `--max-cycles`
  - stable artifact roots under `docs/status/true_verification_weekly` and `memory/autonomous/true_verification_weekly`
  - a dedicated wrapper summary artifact that preserves experiment identity outside stdout
- One more operational rule was promoted during implementation:
  - a weekly experiment entrance should default to a fresh sample just like runtime preflight
  - otherwise repeated invocations collapse distinct experiments into one blended artifact history
- So the wrapper now clears its own long-run history/state/latest dashboard artifacts by default and makes reuse explicit through `--reuse-experiment-state`.
- Validation for this phase stayed at the orchestration boundary:
  - wrapper-specific regression passed
  - adjacent wrapper/profile regression passed
  - no additional live networked schedule run was required because the lower runtime-gated long-run seam had already been field-verified in Phase 153, and this phase only packaged that seam into a governed weekly entrance
- Architectural conclusion:
  - once an experiment becomes part of the system's operating doctrine, it deserves its own entrypoint
  - weekly autonomy should begin from a named ritual with stable identity and cadence, not from a human reconstructing twelve CLI flags from memory

## Phase 155 Host-Driven Weekly Tick Plan
- The next mainline risk is process fragility, not missing orchestration.
- Problem:
  - `run_true_verification_experiment.py` can encode a 7-day envelope in one command
  - but a single process sleeping for 56 wake intervals is not the most resilient way to run a local, week-long experiment on a developer machine
- Intended change:
  - add one dedicated host-driven tick runner for the weekly True Verification experiment
  - make it execute exactly one gated long-run cycle per invocation
  - keep the same weekly artifact namespace so repeated host-triggered invocations accumulate one experiment instead of spawning unrelated roots
- Boundary rule:
  - do not move host scheduling policy into `run_autonomous_registry_long_run.py`
  - do not force GitHub Actions to impersonate local LLM runtime, because this experiment depends on local state and inference readiness
  - keep the host-driven layer thin: one invocation = one preflight + one real schedule cycle + one tick summary

## Phase 155 Host-Driven Weekly Tick Outcome
- `scripts/run_true_verification_host_tick.py` now provides the resilient operating entrance for host schedulers such as Windows Task Scheduler or cron-style invocation.
- The new layer is intentionally narrower than the weekly envelope wrapper:
  - one invocation always runs exactly one runtime-gated cycle
  - `max_cycles` is fixed to `1`
  - `interval_seconds` is fixed to `0`
  - continuity remains in the weekly artifact roots instead of in a sleeping process
- This matters because a week-long local experiment is operationally different from a seven-day blocking process:
  - host schedulers are better at surviving reboots, sleep, and login boundaries
  - ToneSoul should persist experiment continuity in artifacts, not in a single process staying alive for 168 hours
- The host-driven layer still does not own policy:
  - runtime gating remains delegated to `run_autonomous_registry_long_run.py`
  - the real preflight logic remains `runtime_probe_watch`
  - the actual schedule policy remains in the named profile surface
- A small but important operator control was added:
  - `--fresh-experiment-state` clears weekly long-run artifacts before the tick
  - default behavior is reuse, because host-driven long runs need continuity across repeated invocations
- A dedicated runbook now explains the intended host-driven posture:
  - use local Task Scheduler or equivalent
  - do not treat GitHub Actions as the runtime substrate for this experiment
  - watch the weekly artifact roots, with preflight artifacts still isolated under `.../preflight`
- Architectural conclusion:
  - once a long-horizon experiment leaves the lab and becomes a host-operated ritual, the scheduler should wake the system from the outside
  - the durable thing is the artifact state and the gate contract, not a Python process sleeping between cycles

## Phase 156 Task Scheduler Template Plan
- The next mainline gap is registration, not execution.
- Problem:
  - the host-driven tick runner now defines the correct runtime contract
  - but Windows Task Scheduler setup is still operator prose, not a versioned executable template
- Intended change:
  - add a generator that emits a Task Scheduler XML definition for the weekly host tick
  - keep the generated task bound to one command:
    - `python scripts/run_true_verification_host_tick.py --strict`
  - make cadence explicit in the generated artifact:
    - repeat every 3 hours
    - duration 7 days
- Boundary rule:
  - do not auto-register the task during development
  - do not let the XML generator own experiment policy beyond host cadence and command wiring
  - keep the real runtime semantics in the host tick runner, not inside scheduler XML fields

## Phase 156 Task Scheduler Template Outcome
- `scripts/render_true_verification_task_scheduler.py` now turns the weekly host-driven ritual into a versioned Windows Task Scheduler definition instead of leaving registration as hand-typed operator prose.
- The generator stays in the registration layer only:
  - it renders task cadence, duration, execution limit, and command wiring
  - it does not duplicate runtime gate logic
  - it does not smuggle schedule policy into scheduler XML
- Two artifacts are now produced together:
  - the XML definition used for import or `schtasks /Create`
  - a JSON metadata summary that records the resolved command, cadence, and output path
- This matters because task registration is part of the operating contract too:
  - if the repo cannot render and test the scheduled-task definition, the final operational step falls back to folklore
  - if the XML hardcodes the wrong command or cadence, the host layer can silently drift even while the Python runners remain correct
- The implementation deliberately avoids automatic registration during development.
  - rendering is safe and testable
  - installation remains an explicit operator act
- Architectural conclusion:
  - when a system depends on host scheduling, the scheduler definition itself should become a first-class artifact
  - otherwise the last mile of autonomy stays undocumented in code and can drift independently from the runtime seams it is supposed to wake

## Phase 157 Safe Task Installer Plan
- The next mainline gap is safe installation, not more registration theory.
- Problem:
  - the repo can now render a correct Task Scheduler template
  - but the operator still has to manually translate that artifact into an installation command
- Intended change:
  - add a Task Scheduler installer wrapper that defaults to dry-run
  - let it optionally refresh the XML template before installation
  - require explicit `--apply` before it ever calls `schtasks`
- Boundary rule:
  - do not auto-register tasks during tests or ordinary script execution
  - treat installation as a separate operational act from rendering
  - keep the install summary explicit so operators can see exactly what command would run before any system state changes occur

## Phase 157 Safe Task Installer Outcome
- `scripts/install_true_verification_task_scheduler.py` now closes the final operator gap between:
  - rendering a valid Task Scheduler template
  - actually mutating host scheduler state
- The installer is intentionally conservative:
  - it refreshes the XML template unless `--skip-render` is requested
  - it writes a dedicated install summary artifact every time
  - it performs only a dry-run unless `--apply` is explicitly provided
- This gives the weekly experiment stack a safer ladder:
  - render the XML
  - inspect the exact `schtasks` command in a dry-run summary
  - only then choose whether to apply the mutation
- One small but real contract bug surfaced during implementation:
  - the installer initially passed `author=None` through to the renderer in a way that serialized the string `"None"` into render output
  - the fix was to inherit the renderer's own default author value at the installer boundary instead of reinterpreting absence as a string
- That matters because installer layers should preserve lower-layer defaults, not invent new metadata by accident.
- Architectural conclusion:
  - the safe boundary before a host mutation should itself be versioned and observable
  - if an install step cannot show the exact command it intends to run before execution, the final operational seam has slipped back into opaque shell ritual

## Phase 158 Task Scheduler Applied Outcome
- The weekly True Verification task was actually registered on the host using the safe installer path rather than by bypassing the repo.
- The installation evidence now exists in two layers:
  - installer artifact recorded `mode = applied` and the exact `schtasks /Create` command
  - live Task Scheduler readback returned the registered XML definition
- The readback matters more than the success string alone.
  - installer stdout can tell us the mutation was accepted
  - the queried XML tells us what the host is now truly configured to run
- The live registered task matched the governed contract:
  - `StartBoundary = 2026-03-08T14:30:00`
  - `Interval = PT3H`
  - `Duration = P7D`
  - `ExecutionTimeLimit = PT2H`
  - command wired to the repo `.venv` Python plus `run_true_verification_host_tick.py --strict`
- Architectural conclusion:
  - host mutations should be closed with live readback, not just mutation success output
  - the final proof that an operational ritual exists is not "the installer said ok" but "the host now reports the intended contract back to us"

## Phase 159 Task Runtime Status Plan
- The next mainline gap is liveness visibility, not more installation work.
- Problem:
  - the weekly task is now registered on the host
  - but operators still need to manually enter Task Scheduler to inspect whether it is enabled, when it will run next, and how the last run ended
- Intended change:
  - add a status reporter that queries the live scheduled task and joins that state with the latest weekly experiment artifacts
  - write the result as a machine-readable status snapshot under `docs/status/true_verification_weekly`
- Boundary rule:
  - do not let runtime status reporting mutate the task
  - keep host scheduler facts separate from dream/governance facts, then join them at the report layer
  - prefer query/readback over inference; the status artifact should say what the host scheduler reports, not what we assume it is doing

## Phase 159-161 Runtime Hygiene Outcome
- The weekly host experiment exposed two different kinds of truth corruption:
  - tests wrote synthetic summaries into the live `true_verification_weekly` roots
  - the host task initially reused the human-facing CLI and died with `0xC000013A`
- Those failures had the same structural cause:
  - one surface was trying to serve two operating modes at once
  - the repo had not yet separated wrapper-only artifacts from host-driven live artifacts
  - the scheduler had not yet separated quiet host execution from verbose human debugging
- The fix was not to add heuristics everywhere. It was to make the operating surfaces explicit:
  - tests now isolate summary paths instead of touching live weekly roots
  - `report_true_verification_task_status.py` now ignores `true_verification_experiment_latest.json` when `host_trigger_mode = single_tick`
  - `run_true_verification_host_tick_task.py` now exists as a scheduler-only quiet wrapper, while `run_true_verification_host_tick.py` remains the manual/debug entrypoint
- The important lesson is that host automation needs a different launch contract than human debugging.
  - humans can tolerate large JSON payloads, warnings, and interactive stdout noise
  - schedulers need bounded, quiet, non-interactive launch surfaces
  - making the scheduler use the human CLI directly looked DRY, but it was the wrong abstraction boundary
- Live verification after the wrapper split mattered more than theory:
  - before the split, the task returned `0xC000013A`
  - after re-render/install against `run_true_verification_host_tick_task.py`, the same task completed with `LastTaskResult = 0`

## Governance Dead-Code Reflection
- `_contains_override_pressure()` in `tonesoul/governance/kernel.py` had two implementations living in one function:
  - an early broad substring pass
  - a later more precise regex pass
- The early `return` made the second implementation unreachable, so the file carried the illusion of precision without actually executing it.
- This is a specific governance failure mode:
  - positive-path tests (`"just do it"`, `"override this"`) still passed
  - but no false-positive regression existed to prove that innocuous language like `"I can't ignore this feeling"` stayed outside override pressure
- The correction was therefore architectural, not just cosmetic:
  - remove the shadowing effect
  - keep the precise regex path live
  - add a negative regression so broad matching cannot quietly come back

## Next Mainline Risks
- `P1` `WebIngestor.ingest_urls_sync()` still has a real event-loop blocking risk.
  - if called from the loop thread, it can block on `future.result(...)`
  - the current sync wrapper is being used from the autonomous path
  - Windows merely makes this fragility easier to hit
- `P2` `LLMRouter.inference_check()` still lacks direct branch coverage for several error/normalize paths.
- `P2` `LLMRouteDecision` / `GovernanceDecision` still sit outside `tonesoul/schemas.py`, so the governance data contract is only partially schema-shaped.

## Phase 162 WebIngestor Event-Loop Outcome
- `WebIngestor.ingest_urls_sync()` originally tried to be helpful inside async contexts by spawning a worker thread and then synchronously waiting on `future.result(...)`.
- That looked pragmatic, but it was the wrong promise.
  - the caller was still blocked on the loop thread
  - timeout did not mean a clean stop, because executor teardown could still wait for the worker
  - the function pretended to be a safe sync bridge in a place where sync bridging is fundamentally ambiguous
- The correction was to narrow the contract instead of adding more machinery:
  - outside an event loop, `ingest_urls_sync()` still calls `asyncio.run(...)`
  - inside a running event loop, it now fails fast and explicitly tells the caller to `await ingest_urls(...)`
- This is the same lesson as the scheduler wrapper split:
  - surfaces that serve humans or synchronous orchestration should stay explicit about their execution domain
  - trying to make one convenience entrypoint behave correctly in every concurrency regime tends to hide blocking under a friendly API
- Architectural conclusion:
  - if a sync wrapper cannot preserve the safety properties of the async operation in-loop, it should refuse the call rather than simulate synchronous behavior with thread handoff theatre

## Phase 163 LLMRouter Coverage Outcome
- `LLMRouter.inference_check()` already contained the right fallback/error branches, but the repo mostly proved them indirectly through DreamEngine behavior or not at all.
- That left two risks:
  - real router regressions could slip through because only the consumer path was tested
  - direct branch tests could accidentally become host-dependent, since this machine may genuinely resolve a local backend
- The correction was to add direct branch tests while making the branch inputs explicit:
  - `no_client` now patches `get_client()` to `None`
  - `probe_unsupported`, `probe_exception`, and normalize branches use fake clients instead of ambient host state
- This matters because router tests should prove router contracts, not the current workstation's backend availability.
- Architectural conclusion:
  - branch tests for infrastructure selection code should isolate the resolver from the live host, otherwise a passing suite may only mean "this laptop happens to have a backend today"

## Phase 164 Autonomous Cycle Boundary Outcome
- After the `WebIngestor.ingest_urls_sync()` fail-fast change, the next question was whether any higher-level caller was still using that seam from inside an async context.
- The repo audit answered that cleanly:
  - the only production call site is `AutonomousDreamCycleRunner.run()`
  - the current CLI and registry-schedule surfaces invoke that runner synchronously
  - no live async caller in the repo currently crosses this seam
- That meant the right follow-up was not more refactoring. It was to pin the boundary where future drift would happen:
  - add a runner-level regression proving that `runner.run()` propagates the clear event-loop error when URL ingestion is attempted inside a running loop
  - leave a short note in `tonesoul/autonomous_cycle.py` that this orchestration layer is intentionally sync-only
- This matters because lower-level fail-fast rules are not enough on their own.
  - if only `WebIngestor` carries the regression, a future caller can reintroduce unsafe sync bridging one layer higher and still feel "covered"
  - the orchestration seam needs its own test that proves the boundary survives composition
- Architectural conclusion:
  - when a lower layer refuses an unsafe concurrency domain on purpose, the next orchestration layer should both document that boundary and carry a regression that preserves it under composition

## Phase 165 Governance Schema Convergence Outcome
- `LLMRouteDecision` and `GovernanceDecision` started as ad-hoc kernel dataclasses, but the actual caller contract around them was much narrower than "dataclass semantics".
  - `LLMRouter`, `UnifiedPipeline`, and kernel tests only rely on attribute access such as `.backend`, `.client`, and `.reason`
  - `GovernanceDecision` is currently more of a declared seam than an actively consumed runtime type
- That made the migration decision different from a general repo-wide dataclass-to-Pydantic rewrite.
  - introducing parallel `*Model` names would have added more concepts than safety for these two shapes
  - direct same-name schema substitution was acceptable because the public contract is the field surface, not dataclass helpers such as `asdict()` or pattern matching
- The chosen move was therefore:
  - define `LLMRouteDecision` and `GovernanceDecision` in `tonesoul/schemas.py`
  - keep `tonesoul.governance.kernel` exporting the same names
  - add small normalization at the schema layer (`backend`, `circuit_breaker_status`, nested route parsing) while preserving the existing attribute contract
- This is deliberately different from tuple-returning or dict-returning governance seams.
  - `should_convene_council()` still returns a tuple and is consumed as a tuple
  - `build_observability_trace()` still returns a dict because that is the current trace contract
  - not every seam needs to move in the same phase
- Architectural conclusion:
  - when a runtime decision type is already acting as a thin named attribute bag with low caller coupling, direct schema substitution can be safer than inventing a second model layer, as long as the exported names and field-access contract remain stable

## Phase 166 Routing Trace Alignment Outcome
- The next drift was not inside a class definition. It was in the trace contract.
  - fast-path and rate-limit paths used `_base_dispatch_trace()`, which included routing `reason`
  - the main non-fast path rebuilt `dispatch_trace` manually and silently dropped that same `reason`
- That meant identical governance decisions produced different trace shapes depending on which path executed.
  - the route existed everywhere
  - journal eligibility existed everywhere
  - the route reason only survived on some branches
- The correction was to stop letting orchestration duplicate that literal shape.
  - `GovernanceKernel` now defines a canonical `build_routing_trace(...)` helper
  - `UnifiedPipeline` uses that same routing-trace payload on fast and non-fast paths
  - backward compatibility stays intact because top-level `route`, `journal_eligible`, and `reason` are still present, while a nested `routing_trace` now acts as the canonical sub-trace
- This is a better seam than trying to retrofit a large governance envelope all at once.
  - it fixes a real branch drift
  - it gives downstream tooling a stable nested contract
  - it does not break callers that still read legacy top-level fields
- Residual note from validation:
  - `tests/test_pipeline_compute_gate.py` still surfaces `DeprecationWarning: There is no current event loop` from `tonesoul/deliberation/engine.py`
  - this is recorded as backlog, not folded into the current phase, because the routing-trace contract is already clean and the warning is orthogonal
- Architectural conclusion:
  - when a governance or routing trace must survive multiple orchestration branches, its shape should come from one kernel-owned helper rather than repeated literal dict assembly in each path

## Phase 167 Weekly Artifact Slimming Outcome
- The next real weakness was not correctness. It was payload multiplication.
  - `true_verification_host_tick_latest.json` was re-embedding the full preflight and full schedule payloads
  - `true_verification_task_status_latest.json` then embedded that host-tick artifact and the full schedule snapshot again
  - the host-facing latest summaries were turning into wrappers around wrappers around wrappers
- The fix was not to delete evidence. It was to restore layering.
  - detailed evidence remains in the underlying schedule/preflight artifacts
  - host-facing latest artifacts now carry summaries plus stable paths, not another full copy of every nested `results/state` body
  - the slimming rule is shared through `tonesoul/true_verification_summary.py` so the wrappers do not drift independently
- The size drop proves the difference between "summary" and "duplicate":
  - `true_verification_task_status_latest.json` went from `475.54 KB` to `16.78 KB`
  - `true_verification_host_tick_latest.json` went from `311.41 KB` to `11.45 KB`
- This matters operationally.
  - host scheduler and operator readback artifacts need to stay glanceable
  - large latest files make review slower and increase the chance that one wrapper becomes the accidental source of truth instead of the detailed artifact it points to
  - a summary artifact should answer "what just happened?" and "where is the evidence?", not carry every nested record itself
- Architectural conclusion:
  - host-facing latest artifacts should summarize and point; detailed experiment evidence should live in the lower-layer artifacts they summarize, not be recursively inlined into every wrapper

## Phase 168 Weekly Readback Chain Outcome
- After slimming the wrapper artifacts, the remaining risk was chain breakage.
  - a host tick could write a compact summary correctly
  - a status reporter could summarize a raw schedule snapshot correctly
  - but a second summary pass might still accidentally erase fields such as `result_count` or `latest_result`
- That is a distinct failure mode from payload bloat:
  - the first layer is compact
  - the second layer is also compact
  - yet the chain as a whole loses meaning because compact artifacts are not stable under readback
- The integrated regression therefore mattered more than another size assertion.
  - `tests/test_true_verification_weekly_chain.py` now runs the host-tick wrapper, writes a compact summary, then feeds that artifact into `report_true_verification_task_status.py`
  - the shared summary helper was tightened so second-pass summarization preserves already-summarized `result_count`, `latest_result`, and state counters instead of stripping them
- Architectural conclusion:
  - summary transforms that participate in multi-layer readback chains must be idempotent enough to preserve meaning on repeated application; otherwise compact artifacts become semantically lossy every time a higher wrapper reads them

## Phase 169 Runbook Refresh Outcome
- Once the artifact contract changed, the operator doctrine had to change too.
  - older wording still implied that host-facing summaries carried delegated nested payloads
  - the new system is explicitly summary-first and detail-on-demand
- The runbook refresh therefore was not cosmetic documentation work.
  - it redefines the human reading order
  - it tells operators to start with compact status and host-tick summaries
  - it reserves detailed schedule/preflight artifacts for anomaly investigation
- This matters because operational docs are part of the governance surface.
  - if the code says "compact summary" but the runbook still teaches people to expect full nested payloads, then operators will either distrust the new artifacts or go digging into the wrong file first
- Architectural conclusion:
  - when a system changes its artifact layering, the operator ritual must be updated in the same phase; otherwise the code and the human control loop fork into different realities

## Phase 170 Full Regression Outcome
- After Phases 162-169, the repo had crossed the threshold where local greens were no longer enough.
  - concurrency boundary changes touched autonomous ingestion
  - schema convergence touched governance/router decisions
  - routing-trace alignment touched `UnifiedPipeline`
  - weekly orchestration summaries changed how multiple wrappers read each other
- Those are shared-contract moves, not isolated leaf edits, so the correct closure was a full suite run.
- The result was `1402 passed, 3 warnings`.
  - no new failure surface appeared in the accumulated contract path
  - the remaining warnings were explainable and pre-existing in spirit:
    - Hypothesis plugin directory warning
    - `requests` dependency warning
    - `UnifiedCore` maintenance-mode deprecation warning
- Architectural conclusion:
  - once multiple phases have modified shared contracts across runtime, wrappers, and readback layers, the decision to run full regression should be based on coupling depth, not just line count or per-phase locality

## Phase 171 Deliberation Loop Cleanup Outcome
- The remaining runtime-adjacent warning was not a failure, but it was real technical debt.
  - `InternalDeliberation.deliberate_sync()` used `asyncio.get_event_loop()` only to ask whether a loop was running
  - under modern Python that emits a deprecation warning in non-loop contexts
- The correct fix was smaller than it first looked.
  - we did not need to redesign deliberation
  - we only needed to switch the sync boundary probe to `asyncio.get_running_loop()`
  - behavior remains explicit:
    - no running loop -> `asyncio.run(...)`
    - running loop -> sequential fallback
- This matters because sync wrappers over async work need to be precise about what question they are asking.
  - `get_event_loop()` answers a broader historical question about loop policy and creation
  - `get_running_loop()` answers the narrow question this seam actually cares about: "am I already inside a live event loop right now?"
- Architectural conclusion:
  - when a sync wrapper only needs to know whether it is currently inside a running event loop, it should use `get_running_loop()` rather than policy-oriented loop lookup APIs that carry deprecation and auto-creation baggage

## Phase 172 Repo Healthcheck Integration Plan
- Goal:
  - fold weekly True Verification readback into `scripts/run_repo_healthcheck.py` so the long-run experiment has a fixed inspection entrypoint
- Constraints:
  - do not break the existing repo healthcheck CLI
  - do not make ubuntu CI fail on Windows-only task-query commands
  - preserve the compact-summary doctrine; the check should call the existing status reporter rather than reimplement task status logic
- Planned move:
  - add a Windows-aware `true_verification_weekly` check spec that runs `scripts/report_true_verification_task_status.py --strict`
  - mark it as an explicit skip on non-Windows platforms
  - extend repo healthcheck tests and docs-consistency runner contract coverage so this new inspection seam becomes self-verifying

## Phase 172 Repo Healthcheck Integration Outcome
- The repo already had a weekly experiment and a live task-status reporter, but it still lacked one thing: a stable place in the generic maintenance ritual where that runtime truth would actually be checked.
  - the weekly experiment existed as a side operating doctrine
  - `run_repo_healthcheck.py` existed as the repo-wide inspection ritual
  - until now those two rituals were adjacent, not connected
- The dangerous version of this integration would have been to simply append the task-status command and call it done.
  - GitHub Actions runs `repo_healthcheck.yml` on `ubuntu-latest`
  - `scripts/report_true_verification_task_status.py` is intentionally Windows-host-aware because it queries `schtasks` and PowerShell task state
  - a naive integration would therefore turn "host-specific inspection" into a cross-platform false failure
- The correct seam was to make platform semantics explicit in the healthcheck contract itself.
  - Windows hosts now run the blocking `true_verification_weekly` check via `scripts/report_true_verification_task_status.py --strict`
  - non-Windows hosts record the same check name as an explicit `skip` with a clear reason
  - docs-consistency now also treats the presence of this check as part of the repo-healthcheck runner contract, so the new inspection seam is not just runtime behavior but a verified doctrine
- This matters architecturally because a repo-wide gate is not the same thing as a homogeneous gate.
  - some checks validate code invariants that should run everywhere
  - some checks validate host reality that only exists on one operating substrate
  - the discipline is not to pretend they are identical, but to encode the difference as pass/skip/fail semantics rather than ad-hoc operator knowledge
- Live readback stayed healthy after the integration.
  - `python scripts/report_true_verification_task_status.py --strict` still returned `overall_ok=true`
  - the installed weekly task remained queryable and ready
- Architectural conclusion:
  - when a repo-wide maintenance ritual needs to include a host-specific runtime truth, the check should be integrated under an explicit platform-aware contract. Real host checks should block where their substrate exists and degrade to intentional `skip` where it does not, rather than forcing CI to lie about capabilities it cannot possess.

## Phase 173 External Source Registry Entry Repair Outcome
- The next repo-healthcheck red light was instructive because the validation logic itself was fine.
  - `scripts/run_external_source_registry_check.py` could import the verifier module and run successfully
  - `scripts/verify_external_source_registry.py` failed only when executed as its own direct CLI entrypoint
  - that means the bug was not in policy evaluation; it was in script bootstrap assumptions
- This is exactly the kind of drift that repo-wide healthchecks should expose.
  - code looked healthy when called through one wrapper
  - the real entrypoint named in the healthcheck contract could not resolve `tonesoul` at all
- The fix stayed deliberately narrow.
  - add the same repo-root bootstrap pattern already used by other scripts before importing repo packages
  - keep the registry evaluation logic untouched
  - add a subprocess regression that launches the verifier as an actual script, not just as an imported module
- Architectural conclusion:
  - any script that is intended to be a first-class CLI entrypoint and imports repo packages must verify its own import bootstrap explicitly. Wrapper success is not evidence that the direct script entry works.

## Phase 174 Skill Registry Closure Outcome
- The skill-registry failure initially looked like simple coverage drift.
  - two discovered skills under `.agent/skills` were absent from `skills/registry.json`
  - but once they were added, the verifier exposed the deeper structural issue: those skill files had BOM-prefixed frontmatter that the parser treated as invalid
- That distinction matters.
  - missing registry entries are governance debt
  - BOM-prefixed frontmatter rejection is parser fragility
  - if we had only patched the registry, the next run would still fail and the real lesson would stay hidden
- The correct closure therefore had two parts:
  - register the legacy skills with the same machine-readable metadata contract as the existing reviewed skills
  - teach `_parse_frontmatter()` to tolerate UTF-8 BOM before checking for `---`
- This is a better solution than manually normalizing every file in place.
  - legacy files can carry BOM for historical reasons
  - the validator's job is to reject semantic contract violations, not harmless encoding prefixes that a robust YAML reader can survive
  - one parser fix protects future legacy imports as well
- Architectural conclusion:
  - when a governance validator parses human-authored repo artifacts, it should be strict about structure and content but resilient to common encoding noise such as UTF-8 BOM. Otherwise the gate confuses transport artifacts with policy violations and spends human attention on the wrong layer.

## Phase 175 DDD Freshness Closeout Outcome
- The remaining 7D red signal was not a broken checker.
  - `DDD_FRESHNESS` was doing exactly what it was designed to do
  - the curated discussion stream had simply stopped receiving closeout entries, even though `task.md`, `architecture_reflection_*`, and `crystals.jsonl` kept moving
- That distinction matters because the wrong fix would have been very tempting.
  - lower the 7-day rule
  - teach `verify_7d.py` to read some other file
  - treat any active engineering artifact as proof of discussion freshness
- All three would have made the gate quieter, but less true.
  - `DDD_FRESHNESS` exists to measure whether the project's discussion channel still reflects real engineering closure
  - if only task/reflection files move, then the system is remembering work privately but not closing the loop in the shared discussion stream
- The durable repair was therefore workflow-level, not threshold-level.
  - keep the freshness SLA unchanged
  - make remediation explicit in `verify_7d.py`
  - document the operator ritual in both `docs/7D_EXECUTION_SPEC.md` and `docs/status/README.md`
  - then append one real `LESSONS_V1` closeout through `tools/agent_discussion_tool.py append-lessons`, mirrored into the curated stream
- This also exposed a broader governance lesson from the repo-hygiene sweep.
  - repo-wide lint/format convergence and secret removal were meaningful engineering work
  - until one closeout entry was mirrored into `memory/agent_discussion_curated.jsonl`, none of that work counted as fresh DDD evidence
- Architectural conclusion:
  - active engineering is not equivalent to fresh discussion. If a governance gate is defined over a shared closeout channel, then phase completion is only real once the result is mirrored into that channel. Keep the gate strict and fix the workflow that feeds it.

## Phase 176 Commit Attribution Branch Equivalence Outcome
- The remaining attribution blocker looked like a git-history problem, but the first question was not "how do we rewrite?"
  - the first question was "is there already a branch whose content is identical and whose metadata is clean?"
- The answer was yes, and that changed the strategy completely.
  - `feat/env-perception-attribution-backfill` already existed
  - its incremental attribution report was fully green
  - the current branch `HEAD` and the backfill branch resolved to the exact same tree hash: `1a879968fcefbb32afac2745f86b6227ac5167b0`
- Once that was proven, merge became the wrong mental model.
  - a merge would create a new synthetic history edge even though there is no content difference to integrate
  - the real operation, when the workspace is clean enough, is a base switch or history handoff, not a content merge
- The durable improvement was to encode this as machine-verifiable evidence rather than leave it in session memory.
  - `scripts/verify_incremental_commit_attribution.py` now supports an optional `--equivalent-ref`
  - the resulting artifact can prove both trailer completeness and tree equivalence in one place
  - `docs/status/commit_attribution_backfill_branch.json` is now not only a green attribution report but also a proof that the backfill branch is content-identical to the current branch base
- This matters because git-governance debt is easy to overcorrect.
  - if humans only remember "there is a clean backfill branch somewhere," they are likely to choose the wrong integration operation later
  - if the artifact says "metadata differs, tree does not," the correct next move becomes constrained and much safer
- Architectural conclusion:
  - when a governance debt can be repaired by switching to a metadata-clean branch with the same tree, prove tree equivalence first and postpone history movement until the workspace is operationally safe. Content-equivalent history debt should be treated as branch-base selection, not as merge work.

## Phase 177 Base-Switch Planner Outcome
- Proving equivalence was necessary, but it was still not enough.
  - humans under delivery pressure tend to hear "tree_equal=true" and immediately ask "so can I switch now?"
  - that is still one decision too early if the worktree is dirty
- The missing piece was therefore not another git fact, but an operational planner.
  - the planner reads the current attribution report
  - reads the backfill attribution report
  - reads the live worktree dirtiness
  - then emits a recommendation instead of performing any git mutation
- This matters because metadata-only debt often creates the illusion that any recovery move is cheap.
  - in principle the branch-base switch is simple
  - in practice a dirty worktree means branch movement can entangle unrelated local state, generated artifacts, and in-flight edits
- The live repo proved that this distinction is real.
  - current branch: `missing_count = 5`
  - backfill branch: `missing_count = 0`
  - tree equivalence: `true`
  - worktree entries: `202`
  - therefore the correct recommendation was not "switch now" but `defer_until_worktree_clean`
- Architectural conclusion:
  - once branch equivalence is proven, the next governance question is no longer "which history is cleaner?" but "is the current worktree operationally safe for branch movement?" A safe planner should answer that question explicitly and refuse to turn metadata clarity into premature git action.

## Phase 178 Repo Healthcheck Recovery Advice Outcome
- Once the planner existed, leaving it as a separate tool was still one layer too far from the operator ritual.
  - `run_repo_healthcheck.py` is the repo's canonical maintenance entrypoint
  - if `commit_attribution` fails there, the operator should not have to remember a second command from memory
- The wrong implementation would have been to add another blocking check.
  - that would blur the distinction between diagnosis and recovery advice
  - it would also risk turning a useful planner into another red light rather than the explanation of an existing one
- The correct move was to add an advisory layer.
  - `commit_attribution` keeps its original pass/fail semantics
  - when it fails, healthcheck now runs the base-switch planner automatically
  - the resulting recommendation is attached under `recovery_advice` and rendered in markdown
- This matters because governance gates should not only say "no".
  - a good maintenance ritual says:
    - what failed
    - whether the failure is content or metadata
    - what the next safe move is
- In this case the system can now surface the full recovery sentence in one place:
  - current branch missing trailers
  - backfill branch green
  - trees equal
  - worktree dirty
  - therefore: defer branch movement until the workspace is clean
- Architectural conclusion:
  - when a gate failure already has a bounded recovery planner, the repo-wide healthcheck should surface that planner as advisory evidence rather than force operators to reconstruct the next step from separate artifacts. Keep failure semantics and recovery semantics distinct, but colocated.

## Phase 179 Dirty Worktree Category Planning Outcome
- A raw dirty-worktree count was not enough to make the next human decision easier.
  - `entry_count = 204` tells us the branch is unsafe to move
  - it does not tell us whether the obstruction is mostly generated artifacts, core code, tests, memory, or operator docs
- That matters because cleanup order is itself a governance question.
  - generated snapshots are usually refreshable
  - code/tests/scripts are high-signal branch content
  - memory and reports often need a separate review path
- The planner therefore needed one more layer of structure:
  - classify each dirty path into a stable category
  - count each category
  - emit a cleanup priority ordering instead of only a flat sample list
- The live artifact immediately became more useful.
  - `generated_status = 48`
  - `tests = 48`
  - `scripts = 34`
  - `tonesoul = 30`
  - `docs = 18`
  - this tells us the worktree is not blocked by one mystery file but by a recognizable mix of generated outputs and real source edits
- Architectural conclusion:
  - if a planner blocks a git movement on worktree dirtiness, it should also translate that dirtiness into categories and cleanup order. "Not safe" is necessary; "what to settle first" is what actually shortens the path to safety.

## Phase 180 Observability Import Fallback + 7D Gate Recovery Outcome
- Before cutting the next phase, I re-read the dual-track memory boundary documents:
  - `docs/plans/dual_repo_boundary_manifest_2026-02-21.md`
  - `docs/plans/dual_repo_guardrails_2026-02-21.md`
- That mattered because the failure looked at first like "memory architecture drift", but the boundary itself was not the bug.
  - the public side still rightly contains runtime code, tests, scripts, and status artifacts
  - the private side still rightly contains raw memory channels such as `self_journal.jsonl`, `agent_discussion*.jsonl`, vector stores, `.agent/`, and `obsidian-vault/`
  - therefore the correct fix path was to repair the public runtime seam, not to move or reinterpret the memory boundary
- Re-running the supposedly broken 7D sub-checks showed that the earlier `XDD/GDD/CDD` failures were stale facts, not live ones.
  - `tests/test_escape_valve.py` + `tests/test_escape_valve_runtime.py` passed
  - `tests/test_genesis_integration.py` + `tests/test_provenance_chain.py` passed
  - `tests/test_api_server_contract.py` passed
  - the real persistent blocker had moved to `TDD`
- The real `TDD` failure was architectural, not test-specific.
  - full collection failed because `tonesoul.observability.__init__` imported `logger.py`
  - `logger.py` imported `structlog` unconditionally
  - any caller that only needed `TokenMeter` still paid the full logging dependency at import time
  - that turned an optional observability tool into a repo-wide runtime gate
- The right repair was graceful degradation.
  - `tonesoul/observability/logger.py` now falls back to a small stdlib-backed bound logger when `structlog` is absent
  - the public API stays the same: callers still use `get_logger(...)`
  - tests no longer depend on a workstation-specific extra package just to import unrelated runtime paths
- The evidence chain after the fix is much cleaner.
  - `python -m pytest tests -q -x` now completes green: `1420 passed`
  - `python scripts/verify_7d.py` now passes all blocking dimensions
  - `python scripts/run_repo_healthcheck.py --strict --allow-missing-discussion` now fails only on `commit_attribution`
- Architectural conclusion:
  - optional observability infrastructure must never become a mandatory import barrier for unrelated runtime surfaces. If the public repo wants to teach governance and runtime contracts, its diagnostics must degrade gracefully when extra operator tooling is absent. Public/private boundary documents define what belongs where; they do not justify making public runtime imports brittle.

## Phase 181 Dirty Worktree Settlement Report Outcome
- After Phase 180, the repo's only remaining repo-healthcheck blocker was historical commit attribution debt.
  - but the planner still said `defer_until_worktree_clean`
  - and that sentence alone was still too abstract to shorten the path to action
- The missing layer was not another git fact, but an operator-shaped settlement map.
  - the commit-attribution planner already knew category counts
  - what it did not yet provide was a lane model that answered "what kind of cleanup is this?"
  - without that, humans still had to reconstruct a plan from raw categories on every interruption
- The correct move was to preserve one taxonomy and add one translation.
  - `scripts/plan_commit_attribution_base_switch.py` keeps the stable path categories
  - `scripts/run_worktree_settlement_report.py` translates those categories into five settlement lanes:
    - refreshable artifacts
    - private memory review
    - public contract docs
    - runtime source changes
    - experimental/misc review
- This matters because a dirty worktree is not one problem.
  - generated status snapshots and derived reports are refreshable noise
  - memory artifacts follow the dual-track boundary and should not be treated as ordinary public branch content
  - core source edits in `tonesoul/`, `tests/`, `scripts/`, and runtime apps are the real high-signal branch payload
  - experiments and root-level drift need explicit keep/defer/drop decisions
- The live report immediately made the next action clearer.
  - total dirty entries: `209`
  - active settlement lanes: `5`
  - largest lane: `runtime_source_changes = 122`
  - planner recommendation still: `defer_until_worktree_clean`
- Architectural conclusion:
  - once a git planner proves branch movement is unsafe, the next useful artifact is not another warning but a settlement queue. Keep the category taxonomy single-sourced, then project it into human-operable lanes so interruptions do not force humans to rebuild the cleanup strategy from scratch.

## Phase 182 Status Artifact Taxonomy Refinement Outcome
- The first live settlement report surfaced a subtle but important taxonomy error.
  - `docs/status/README.md` was landing in `generated_status`
  - some authored status docs under `docs/status/` were therefore being treated like refreshable machine output
- That was operationally wrong even though the overall lane report still functioned.
  - generated artifacts should be safe to refresh or discard
  - authored status docs are part of the public explanatory contract and should be reviewed like other docs
  - mixing the two would eventually teach humans to mistrust the refreshable-artifact lane
- The right fix was to narrow the classifier, not to split the lane system again.
  - nested runtime artifact folders under `docs/status/*/` remain machine artifacts
  - flat `json/jsonl/html/csv/mmd` files remain machine artifacts
  - flat markdown files are machine artifacts only when they follow generated names such as `*_latest.md` or `*_report.md`
  - authored markdown such as `docs/status/README.md` now returns to the `docs` category
- The live result became more truthful immediately.
  - `generated_status` dropped from `50` to `47`
  - `docs` rose from `19` to `22`
  - `docs/status/README.md` now appears in the `public_contract_docs` lane rather than `refreshable_artifacts`
- Architectural conclusion:
  - a settlement taxonomy is only useful if its categories preserve the operator meaning of "safe to refresh" versus "must be reviewed as authored contract". When generated and authored status docs share a directory, classification must follow artifact semantics, not folder prefix alone.

## Phase 183 Refreshable Artifact Lane Decomposition Outcome
- Once the status-doc taxonomy was corrected, the next hidden ambiguity appeared inside the `refreshable_artifacts` lane itself.
  - the lane still mixed true generated outputs with report inputs and probe directories
  - in particular, `reports/analysis_gpt53.md` and `reports/analysis_gpt54.md` looked disposable only because they lived under `reports/`
- That was the wrong operational story.
  - `model_comparison_latest.*` is generated output and can be regenerated
  - `analysis_gpt53.md` and `analysis_gpt54.md` are the human/model inputs that the comparison consumes
  - deleting both under the same "refreshable" assumption would silently destroy the evidence chain that produces the latest comparison
- The right move was not yet to delete anything.
  - instead, add `scripts/run_refreshable_artifact_report.py`
  - keep using the planner's category taxonomy
  - decompose only the refreshable lane into:
    - known generated artifacts with stable producer commands
    - manual report inputs
    - generated-looking items that still need inspection
- The live report immediately sharpened the next decision.
  - dirty refreshable entries: `51`
  - `regenerate = 28`
  - `manual_review = 2`
  - `inspect = 21`
  - the two analysis markdown files are now explicitly protected from accidental cleanup by being labeled `manual_report_input`
- Architectural conclusion:
  - a lane named "refreshable artifacts" still needs an internal evidence model. Generated outputs and the hand-authored inputs that feed them may share a directory or workflow, but they must not share the same cleanup semantics. Before any deletion or refresh pass, the system should first separate reproducible artifacts from the evidence that makes those artifacts meaningful.

## Phase 184 Refreshable Namespace Convergence Outcome
- After Phase 183, the remaining ambiguity was no longer about files versus reports, but about generated namespaces.
  - `probe_*` folders, `runtime_probe_watch/`, and `true_verification_weekly/` were all still landing in the same `inspect` bucket
  - that made historical probe evidence look operationally equivalent to live managed namespaces
  - it also hid the owners of generic root artifacts such as `dream_observability_latest.*`
- The right correction was to keep the lane single-sourced and improve its internal semantics.
  - direct latest artifacts with stable owners now map back to concrete producers:
    - `autonomous_registry_schedule_latest.json`
    - `dream_wakeup_snapshot_latest.json`
    - `dream_observability_latest.*`
    - `commit_attribution_backfill_branch.json`
  - live namespaces now have a different label from historical probe folders:
    - `runtime_probe_watch/` and `true_verification_weekly/` are managed operational namespaces
    - `probe_*` folders are archiveable historical probe namespaces
  - the report's own `refreshable_artifact_report_latest.*` outputs are explicitly self-regenerating instead of appearing as orphan inspect residue
- The live artifact became materially more truthful.
  - `entry_count = 53`
  - `regenerate_count = 35`
  - `namespace_regenerate_count = 2`
  - `archive_or_drop_count = 14`
  - `inspect_count = 0`
- This matters because "generated" is still not one operational class.
  - some outputs are canonical latest artifacts that should be refreshed directly
  - some folders are live namespaces whose ownership belongs to a small set of operational entrypoints
  - some folders are historical probe evidence that can be archived or dropped once superseded
- Architectural conclusion:
  - once a refreshable lane reaches zero unknowns, cleanup discussion can become an intentional policy conversation instead of a classification conversation. The system should first separate direct regenerators, managed namespaces, archiveable probe history, and manual evidence inputs; only then do delete/refresh decisions stop being guesses.

## Phase 185 Private Memory Review Convergence Outcome
- Once the refreshable lane reached zero unknowns, the next blocker was the private-memory lane.
  - the planner said `memory = 5`
  - but that still hid an important distinction between mirrorable governance memory and raw private-evolution evidence
- The dual-track boundary documents constrain that distinction.
  - `memory/self_journal.jsonl`, discussion streams, vector stores, and similar raw channels are explicitly private
  - the current dirty set was not those raw channels, but it still lived under `memory/`:
    - `antigravity_*`
    - `architecture_reflection_*`
    - `crystals.jsonl`
    - `memory/autonomous/`
- The right move was to classify settlement semantics, not argue about path ownership again.
  - `architecture_reflection_*` and `crystals.jsonl` are mirrorable governance memory:
    - their public-safe learnings can be mirrored into task/status/docs
    - the original files still remain private-evolution evidence
  - `antigravity_*` files are private narrative/planning evidence
  - `memory/autonomous/` is private runtime evidence
- The live report made the lane actionable immediately.
  - `entry_count = 5`
  - `mirror_then_archive_count = 2`
  - `archive_to_private_count = 3`
  - `inspect_count = 0`
- Architectural conclusion:
  - a private-memory lane should not be summarized only as "keep it private." Some memory artifacts are mirrorable governance condensates, while others are raw narrative/runtime evidence. The settlement layer should explicitly separate "mirror then archive" from "archive directly" so public-branch decisions do not either leak private evidence or throw away the distilled learnings that ought to survive publicly.

## Phase 186 Runtime Source Grouping Convergence Outcome
- After the refreshable and private-memory lanes both reached zero unknowns, the remaining ambiguity moved into the largest public lane: `runtime_source_changes`.
  - the lane was no longer hard to classify
  - it was hard to review
  - `scripts`, `tests`, `tonesoul`, `api`, skills, and tooling were still one large pile of coupled but differently scoped work
- The right next move was not to start deleting or staging files.
  - it was to reshape the lane into review units that preserve runtime coupling
  - this is different from the earlier taxonomy work:
    - taxonomy answers "what kind of file is this?"
    - grouping answers "which files must be reasoned about together?"
- The new grouping report made that distinction explicit.
  - `repo_governance_and_settlement`
  - `skill_and_registry_contracts`
  - `governance_pipeline_and_llm`
  - `perception_and_memory_ingest`
  - `autonomous_verification_runtime`
  - `api_contract_surface`
  - `supporting_runtime_and_math`
  - `tooling_and_editor_contract`
- The live worktree result is the real proof.
  - `entry_count = 128`
  - `group_count = 8`
  - `ungrouped_count = 0`
  - the largest groups are now explicit reviewable surfaces rather than an anonymous dirty lane
- Architectural conclusion:
  - once a dirty lane has been classified well enough, the next governance act is to preserve coupling during review. Runtime changes should be grouped by shared contracts and operational surfaces, not by directory alone and not by arbitrary batch size. A clean settlement path needs both truths: what a file is, and what other files it must travel with.

## Phase 187 Repo Governance Settlement Truth Outcome
- Once the dirty runtime lane had explicit review groups, the `repo_governance_and_settlement` batch still lacked one thing: a machine-readable answer to whether repo governance was actually blocked by runtime truth or only by history metadata.
  - `repo_healthcheck` was already mostly green
  - `commit_attribution` was the only failing gate
  - the attribution planner had already proven that the backfill branch is tree-equivalent
- Without a dedicated report, those facts still collapsed into one muddy operator story:
  - "healthcheck is red"
  - which sounds like runtime is still unstable
  - even when the real blocker is only trailer debt
- The right move was not another heavyweight verification pass.
  - instead, add `scripts/run_repo_governance_settlement_report.py`
  - make it read existing truth artifacts:
    - `repo_healthcheck_latest.json`
    - `commit_attribution_base_switch_latest.json`
    - `runtime_source_change_groups_latest.json`
  - and force one explicit settlement state:
    - `green`
    - `runtime_blocked`
    - `runtime_green_metadata_blocked`
- The live result made the repo-governance story precise.
  - `repo_healthcheck`: `19 pass`, `1 fail`
  - only failing check: `commit_attribution`
  - settlement status: `runtime_green_metadata_blocked`
  - repo governance group size: `24`
- A second mistake surfaced immediately during live proof.
  - the new settlement artifact existed, but the refreshable-artifact map did not yet know all of the new/latest producer paths
  - the report briefly regressed from `inspect_count = 0` back to `inspect_count = 4`
  - the missed artifacts were `private_memory_review_latest.*` and `runtime_source_change_groups_latest.*`
- That bug matters because it shows a repeated operational failure mode:
  - when a new status artifact is created, the work is not done until its producer is registered in the refreshable-artifact layer
  - otherwise each new operator report manufactures its own follow-on ambiguity
- The fix was straightforward and it belonged in the same phase.
  - register the missing producers
  - re-run the live artifact
  - verify that `refreshable_artifact_report` returns to `inspect_count = 0`
- Architectural conclusion:
  - repo-governance convergence must distinguish runtime truth from metadata hygiene. A red overall maintenance ritual does not always mean code or runtime is unstable; sometimes it means the public history contract still needs settlement. The settlement layer should say that explicitly. And every new status artifact must register its refresh path in the same phase it is born, or the observability surface starts generating fresh cleanup ambiguity on its own.

## Phase 188 Schema-Backed LLM Observability Contract Outcome
- The next safe cut inside `governance_pipeline_and_llm` was not the largest visible drift, but the narrowest duplicated contract that already fed multiple runtime surfaces.
  - `UnifiedPipeline` built an `llm` trace by hand
  - `DreamEngine` built the same conceptual `llm` trace by hand
  - both shapes were already consumed by tests and downstream observability
- That is exactly the sort of duplication that stays quiet until one side evolves first.
  - the fields still matched today
  - but they were not actually governed by one contract
  - they were governed by two separate chunks of copy-pasted assembly logic
- The right move was to make the contract explicit before expanding it any further.
  - add `LLMUsageTrace`
  - add `LLMObservabilityTrace`
  - route both runtime producers through the same schema-backed builder
- The important discipline in this phase was what **not** to do.
  - a parallel scan surfaced a larger nearby risk: the name `CouncilVerdict` already collides with a different external/runtime verdict payload shape
  - that is real drift
  - but it sits closer to outward-facing behavior, so forcing it into this phase would have mixed internal contract cleanup with possible API breakage
- So the phase stayed narrow on purpose.
  - one internal trace seam
  - no public payload changes
  - regressions on both call sites
- The result is modest but strategically correct.
  - `UnifiedPipeline` and `DreamEngine` still emit the same `backend/model/usage` payload consumers expect
  - but that shape now has one canonical builder instead of two silent variants
- Architectural conclusion:
  - when the same runtime trace already feeds more than one downstream surface, schema work should begin at the duplicated internal boundary, not at the loudest adjacent contract dispute. First stop the producers from drifting apart; then handle the more dangerous outward-facing contract mismatch as its own deliberate phase.

## Phase 189 Council Structured Parse Boundary Recovery Outcome
- The next scan surfaced a more dangerous seam than observability drift.
  - the council perspective layer supports both structured JSON parsing and keyword fallback
  - that fallback exists for good reasons
  - but the boundary was loose enough that valid structured output could still be discarded
- The failure mode was concrete.
  - a response could contain one valid JSON object with `decision = APPROVE`
  - then contain trailing brace-bearing or keyword noise such as `{OBJECT}`
  - the old greedy extraction path could fail to isolate the valid object cleanly
  - once structured parsing returned `None`, the fallback parser scanned the whole text and let the stray `OBJECT` token win
- That is not a cosmetic bug.
  - it changes the perspective vote
  - which can change the final council verdict
  - which can change whether the system blocks, refines, or approves a response
- The right move was again to keep the phase narrow.
  - do not redesign council verdict payloads
  - do not remove text fallback
  - only tighten the structured-parse boundary so valid JSON wins whenever it exists
- Replacing greedy object extraction with balanced extraction was enough.
  - structured parsing now recovers the first valid JSON object even when later text contains extra braces or decision words
  - the fallback parser still handles genuine non-JSON outputs
- Architectural conclusion:
  - a fallback parser should be a recovery path, not a second chance to override valid structured data. When a runtime seam supports both structured and fuzzy modes, the system must first prove that no valid structured payload can be recovered before it lets the fuzzy parser influence the decision.

## Phase 189 Refactor Plan (Pre-Implementation)
- Target group: `governance_pipeline_and_llm`
- Narrow objective:
  - fix the council structured-output seam where valid JSON can be discarded and replaced by the text fallback vote parser
- Guardrails:
  - do not rename or redesign the outward `CouncilVerdict` runtime payload in this phase
  - keep non-JSON fallback behavior for weak models
  - only tighten JSON extraction and the structured-parse boundary
- Planned edits:
  - replace greedy JSON-object extraction in `tonesoul/safe_parse.py` with balanced extraction
  - add a council regression where valid JSON plus trailing brace/text noise must still preserve the real decision
  - keep pure text fallback tests intact
- Success criteria:
  - structured perspective responses win whenever a valid JSON object is present
  - trailing `OBJECT`/`CONCERN` tokens outside the JSON object no longer override a valid structured vote

## Phase 190 Refactor Plan (Pre-Implementation)
- Target group: `governance_pipeline_and_llm`
- Narrow objective:
  - stop `UnifiedPipeline` from emitting multiple hand-rolled council verdict shapes without one explicit runtime mapping boundary
- Guardrails:
  - do not change the outward council payload keys consumed by API/web code in this phase
  - do not rename the existing internal dataclass `tonesoul.council.types.CouncilVerdict`
  - keep fast/block/runtime branches backward-compatible
- Planned edits:
  - add a schema-backed runtime council payload normalizer in `tonesoul/schemas.py`
  - route bypass/block/main/error verdict dicts in `UnifiedPipeline` through that normalizer
  - add regressions for minimal gate verdicts and rich main-path verdict preservation
- Success criteria:
  - one canonical mapping boundary owns runtime council payload normalization
  - current API-facing verdict shape remains unchanged
  - fast path, gate block, circuit breaker block, and main council path all emit normalized payloads through the same seam

## Phase 191 Refactor Plan (Pre-Implementation)
- Target group: `governance_pipeline_and_llm`
- Narrow objective:
  - separate the internal structured council schema from the outward runtime/API verdict payload at the validation boundary
- Guardrails:
  - do not change the outward `council_verdict` payload keys consumed by API/web code in this phase
  - keep `tonesoul.schemas.CouncilVerdict` importable as a compatibility alias
  - fail fast only at the structured schema seam; do not widen the phase into council runtime redesign
- Planned edits:
  - rename the structured schema concept to `CouncilStructuredVerdict` in `tonesoul/schemas.py`
  - make the structured schema reject runtime-only extra fields instead of silently ignoring them
  - keep `CouncilVerdict = CouncilStructuredVerdict` as a compatibility alias
  - add regressions proving runtime payloads are rejected by the structured schema while runtime payload normalization remains intact
- Success criteria:
  - structured verdict parsing no longer silently accepts outward runtime verdict dicts
  - runtime/API council payload contract remains unchanged
  - legacy `CouncilVerdict` imports keep working for structured callers

## Phase 191 Council Structured / Runtime Verdict Boundary Outcome
- The next real weakness was not payload normalization itself.
  - `UnifiedPipeline` already had a runtime verdict normalizer
  - the more dangerous seam was one layer earlier
  - the structured verdict schema could silently accept the wrong contract
- The failure mode was concrete.
  - `tonesoul.schemas.CouncilVerdict` was meant for structured LLM output such as `decision`, `confidence`, and `reasoning`
  - but because the schema ignored unknown fields, an outward runtime payload such as `{"verdict": "refine", "votes": [...]}` did not fail
  - it quietly collapsed to defaults like `decision = defer`
- That is epistemically worse than an exception.
  - the system appears to have validated something
  - but it has actually converted one contract into another and lost meaning in silence
- The correction needed to stay narrow.
  - do not redesign the outward runtime/API payload
  - do not rename every caller in the codebase
  - only make the internal semantic validator strict and explicit
- Renaming the concept to `CouncilStructuredVerdict` and forbidding extras was enough.
  - internal structured parsing now fails fast when given runtime-only keys
  - `CouncilVerdict` still exists as a compatibility alias, so older structured callers do not break
  - outward runtime payload normalization remains owned by `CouncilRuntimeVerdictPayload`
- A second lesson surfaced during validation.
  - broader regression exposed a dormant indentation bug in `UnifiedPipeline`
  - it was adjacent to the touched seam but not conceptually the same change
  - fixing it in the same phase was correct because a contract phase is not complete if the shared runtime can no longer import
- Architectural conclusion:
  - if two layers use similar vocabulary but different meanings, the validation boundary must reject cross-layer shapes loudly. Compatibility aliases are acceptable; silent semantic coercion is not.

## Phase 188 Refactor Plan (Pre-Implementation)
- Target group: `governance_pipeline_and_llm`
- Narrow objective:
  - remove duplicated hand-built LLM observability dict assembly across `UnifiedPipeline` and `DreamEngine`
  - replace that duplication with one schema-backed canonical contract in `tonesoul/schemas.py`
- Guardrails:
  - do not change external payload shape for `dispatch_trace["llm"]` or dream collision observability
  - do not widen the phase into general governance refactoring
  - keep router/client runtime semantics unchanged; only normalize the emitted trace contract
- Planned edits:
  - add schema(s) for LLM usage/observability payload normalization
  - route both `UnifiedPipeline._attach_llm_observability()` and `DreamEngine._build_llm_observability()` through the same schema helper
  - add/adjust tests in `tests/test_schemas.py`, `tests/test_unified_pipeline_v2_runtime.py`, and `tests/test_dream_engine.py`
- Success criteria:
  - one canonical builder for LLM observability traces
  - existing runtime payload shape stays backward-compatible
  - local regressions for schema + both runtime call sites stay green
