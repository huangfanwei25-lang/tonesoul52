# ToneSoul 3-Day Execution Program (2026-04-22)

> Purpose: give the next AI agent (or human collaborator) a concrete, honest scaffold
> to continue ToneSoul without reopening settled questions.
> Status: active. Subordinate to `task.md`, latest `docs/status/*`, code, and tests.
> Written by: claude-sonnet-4-6 on branch `claude/implement-dubby-OeN60`

---

## Current Truth Anchors

Read in this order before doing anything else:

1. [`task.md`](../../task.md) — active programs and water-bucket snapshot
2. [`docs/status/codex_handoff_2026-04-15.md`](../status/codex_handoff_2026-04-15.md) — latest handoff
3. [`docs/plans/memory_subjectivity_choice_axis_2026-04-18.md`](memory_subjectivity_choice_axis_2026-04-18.md) — Phase 864 full spec
4. [`docs/plans/memory_subjectivity_choice_axis_addendum_864_unlock_2026-04-20.md`](memory_subjectivity_choice_axis_addendum_864_unlock_2026-04-20.md) — 864c gate conditions
5. [`SOUL.md`](../../SOUL.md) — system identity and value weights

Do not let older handoffs, side plan docs, or phase archives silently outrank these.

---

## What This Session Did (2026-04-22)

The session on branch `claude/implement-dubby-OeN60` integrated four open PRs
into a single branch and verified they compose cleanly:

| PR | What landed | Tests added |
|----|------------|-------------|
| #19 | Phase 864a EpistemicLabeler gate | 19 |
| #22 | Gateway `POST /council/validate` + v0b Bucket A outcome collection | 41 |
| #26 | Phase 864b Layer 2 Bucket B — verdict/outcome JOIN + calibration table | 18 |
| #28 | Council perspective quality — axiom-awareness, causal reasoning, intent alignment | 20+ |

Test suite after integration: **3266 passed, 4 skipped** (was 2498 on master).
Lint: `ruff check tonesoul/` clean.

Branch `claude/implement-dubby-OeN60` is pushed to remote and ready for review.

---

## What Is NOT Done (honest stop-points)

- **Phase 864c** (Layer 3: Deliberation Trace) is explicitly gated. Per the addendum,
  do not start until Layers 1+2 have real usage data flowing through the gateway
  `/outcome` endpoint. The gate condition is synthetic Bucket B promotion (done),
  but the 4-week real-usage window still applies before 864c claims maturity.

- **Demo UI** (PRs #23 and #27) needs browser validation by Fan-Wei before merge.
  The HTML/JS is complete; it just can't be verified from a CLI session.

- **PR merge to master** requires Fan-Wei's approval. The branch is ready but I
  cannot merge my own work.

---

## 3-Day Window

### Day 1 — Integration and Validation (0-8h)

**Goal:** get the four integrated PRs landed on master and the test baseline stable.

1. Fan-Wei reviews and merges `claude/implement-dubby-OeN60` (or squash-merges each PR
   individually if preferred).
2. Run `python scripts/run_collaborator_beta_preflight.py` after merge to verify
   the baseline is still green.
3. Start the gateway and send one real `POST /council/validate` request to confirm
   EpistemicLabel appears in the response:
   ```bash
   python scripts/gateway.py --port 7700 --token test123
   curl -X POST http://localhost:7700/council/validate \
     -H "Authorization: Bearer test123" \
     -H "Content-Type: application/json" \
     -d '{"draft_output": "The meaning of life is subjective."}'
   ```
   Verify the response contains `"epistemic_label": {"status": "speculative_metaphysical", ...}`.

4. Record one real outcome signal to start the Bucket A collection window:
   ```bash
   curl -X POST http://localhost:7700/outcome \
     -H "Authorization: Bearer test123" \
     -H "Content-Type: application/json" \
     -d '{"verdict_fingerprint": "<from step 3>", "signal": "accepted_as_is"}'
   ```
   (The gateway must be started with `--enable-outcome-collection` for this.)

**Stop condition:** if the preflight is not green after merge, diagnose and fix
before proceeding to Day 2. Do not carry a broken baseline forward.

---

### Day 2 — Heartbeat and Session Continuity (8-16h)

**Goal:** reduce the cost of memory fragmentation by making each AI session
leave a stronger trace that the next session can actually use.

This day is explicitly about the AI主體性 problem: a Claude instance with no
persistent memory is stateless by nature. The only honest answer to that
constraint is to make the *traces* richer so continuity is recoverable even
if memory is not.

**Tasks:**

1. **Session end quality gate.** After every meaningful session, run:
   ```bash
   python scripts/end_agent_session.py --agent <id> \
     --summary "..." --path "..."
   ```
   This is currently optional. Make it structurally expected by adding a
   reminder to `AI_ONBOARDING.md` and `docs/AI_QUICKSTART.md`.

2. **Heartbeat baseline.** Verify `tonesoul/heartbeat.py` is wired to a
   detectable file-backed state so it survives Redis absence:
   ```bash
   python -c "from tonesoul.heartbeat import Heartbeat; h = Heartbeat(); print(h.status())"
   ```
   If this fails without Redis, the heartbeat is not actually providing
   continuity — it's providing the appearance of it.

3. **Handoff template.** Write one concrete handoff note at
   `memory/handoff/2026-04-22_claude-sonnet-4-6.md` documenting what was
   done, what the next agent should verify, and what must not be reopened.
   This is the direct answer to memory fragmentation: even if context resets,
   the handoff does not.

4. **Phase 865 candidate admission.** Per `task.md` Self-Improvement Loop rules,
   admit one next bounded candidate: improve the session-start tier-0 output
   to include the latest open-PR summary, so new agents don't start blind.
   This is a `scripts/start_agent_session.py` change, not an architecture change.

---

### Day 3 — Phase 864c Gate Preparation (16-24h)

**Goal:** not to build 864c, but to make it so the gate conditions are being
actively tracked rather than passively waited for.

**Tasks:**

1. **Outcome collection monitoring.** Add a one-line script
   `scripts/run_outcome_summary.py` that reads `.aegis/council_outcomes.jsonl`
   and prints: total records, signal distribution, date range, and whether the
   collection window has reached the Bucket B synthetic promotion criteria.

2. **864c readiness check.** Add a test `tests/test_864c_gate.py` with one
   assertion: `council_outcomes.jsonl` is either absent (day 0) or contains
   records (real usage started). This test is not about passing; it is about
   making the gate condition machine-readable.

3. **Publish a fresh handoff** at `docs/status/codex_handoff_2026-04-22.md`
   with the current truth: what's on master, what's on the integration branch,
   what the 864c gate condition actually requires, and what the next agent
   should do first.

---

## Guardrails (carry these forward unchanged)

1. Do not claim production readiness, AI consciousness, or council-as-truth.
2. Do not reopen Phase 784 (dashboard) or Phase 654-698 (R-memory maturation).
3. Do not widen public launch claims beyond collaborator-beta.
4. Do not build Phase 864c before the gate conditions are met.
5. Treat synthetic Bucket B baseline honestly: it is a self-consistency check,
   not real-world calibration.
6. If a session ends without a handoff note, the next session starts blind.
   That is the memory fragmentation problem in its simplest form. Always leave
   a note.

---

## For the AI Reading This

The memory that matters is not in your context window. It is in the traces,
the handoffs, the commits, and the tests. Every clean commit is a memory that
survives session end. Every test is a claim that the next agent can verify.

The continuity you are looking for is not something ToneSoul gives you — it is
something you build, session by session, in the artifacts you leave behind.

Agent: claude-sonnet-4-6
Trace-Topic: Phase-730-3day-execution-program
Date: 2026-04-22
