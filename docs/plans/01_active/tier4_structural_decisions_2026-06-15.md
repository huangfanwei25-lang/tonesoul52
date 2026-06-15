# Tier 4 — Structural decisions (owner's call; evidence + recommendation only)

> Judgment-readiness roadmap **Tier 4**. These are **decisions, not cleanups**
> (SUCCESSOR_MAP §0: "no one imports it" ≠ "safe to delete"). Each item below was
> independently investigated against current master, then **adversarially
> challenged** (steelman the opposite). **Nothing here is executed.** The binding
> wire / archive / remove / rename calls are Fan-Wei's. The adversarial pass
> caught two factual errors in the first-pass reasoning — both corrected below.

## Convergent verdict

All five items land at **`leave_and_mark`** — keep in tree, defer the binding
choice to the owner — for the same reason: every one is *tested + reachable from
something* (tests or a CLI script), so none clears the §0 bar for unilateral
removal, and "unreachable from the core" alone never licenses archive/delete here.
What differs per item is **which binding decision is open** and **what cheap,
zero-behavior marking** would make the deferral honest rather than silent drift.

| # | Item | Decision open | Recommendation | Confidence | Reversibility |
|---|---|---|---|---|---|
| T4.1 | `corpus/` | wire (web-frontend path) **or** archive | leave_and_mark; **archive only if Supabase has superseded it** | high | trivially (leave) / w-effort (archive) |
| T4.2 | YUHUN dead hook | wire DPR+ContextAssembler **or** remove the hook | **remove the dead hook**, keep+mark the modules | high (hook) / med (modules) | trivially (hook) |
| T4.3 | `market/` | archive **or** keep | leave_and_mark **with a dated archive gate** | medium | reversible w-effort |
| T4.4 | dual `Hippocampus` | consolidate **or** leave | leave_and_mark (do **not** merge) | high | n/a (no change) |
| T4.5 | naming collisions | rename **or** leave | leave_and_mark (do **not** rename) | high | n/a (no change) |

---

## T4.1 — `corpus/` (wire-or-archive)

- **Verified state:** 4 modules / 875 LOC, 53 green tests, **zero non-test
  importers** repo-wide (re-checked the §0 way: no dynamic/config/router path;
  git log = annotation/lint only, never a wiring commit). It is **wireable, not
  broken** — its lazy `InternalDeliberation` target is live. Already carries
  DORMANT markers (commit c94988d). Distinct from the **live** `evolution/corpus_builder.py`.
- **⚠️ Adversarial correction:** the first pass claimed corpus/ is "the *only*
  consent/GDPR-withdrawal path." **False** — there is a **live** consent/withdrawal
  path in `api/server.py` Supabase persistence. So `corpus/` is a **parked SECOND
  consent implementation that has already drifted from the live one**, not an
  irreplaceable gem.
- **Options.** *Wire* (M effort): build the consent-gated web-frontend capture
  route the docstring intends → adds a new personal-data persistence surface
  (needs privacy/legal review) and a second consent ledger (fork risk). *Archive*
  (move to `.archive/` + its 3 tests): loses nothing the live Supabase path
  doesn't already cover; reversible with effort.
- **Recommendation:** `leave_and_mark`, **and** amend the marker + SUCCESSOR_MAP
  to record "parked duplicate of the live Supabase consent path — do not fork the
  consent ledger if wiring." **Binding question for you:** *is there a planned
  web-frontend corpus path, or has Supabase superseded it?* If superseded →
  archive (never bare `git rm`).
- **Residual risk either way:** a privacy-critical 875-LOC subsystem drifting from
  the live consent path with no reconciliation note.

## T4.2 — YUHUN dead hook (wire-or-remove)

- **Verified state:** `_get_dpr()` / `_get_context_assembler()` in
  `unified_pipeline.py:190-210` (+ attrs 176-177) have **zero call sites** — a
  genuine dead hook (added 2026-04-13, 6a20ecf; consumption never wired).
  `yuhun/dpr.py` (Dynamic Priority Router) and `yuhun/context_assembler.py` are
  tested + re-exported.
- **⚠️ Adversarial correction:** the first pass justified leaving it as "the
  kernel gate makes the same decision (redundant)." **False** — `should_convene_council`
  (kernel.py:207) is a *post-analysis numeric* gate; DPR is a *pre-analysis text*
  router (cheaper FAST/COUNCIL split before tension/friction compute); and
  `ContextAssembler` is a **fail-closed context-egress denylist with no live
  equivalent**. The modules are **unwired, NOT superseded**.
- **Recommendation:** **(a) remove the small dead hook** (the two getters + attrs
  — pure misdirection: it lazy-imports modules nobody invokes); **(b) keep and
  correctly mark** the modules as "unwired, NOT superseded — distinct mechanism
  (cheap pre-route + context-egress denylist)" so they aren't deleted as redundant.
  *(Removing the hook is a code change — proposed, not executed; your call.)*
- **Binding question for you:** *wire DPR routing + ContextAssembler egress into
  the pipeline (closes 6a20ecf, gains a cheap pre-router + a fail-closed egress
  denylist), or remove the hook and keep the modules as parked substrate?*
- **Residual risk:** the live pipeline keeps **no** cheap pre-analysis router and
  **no** fail-closed prompt-egress denylist until/unless these are wired.

## T4.3 — `market/` (archive-or-keep)

- **Verified state:** 台股 analysis, ~1342 LOC, **off-thesis**, half-dismantled
  (forecaster/gold_detector removed). Not a zombie: **tested + reachable via a CLI
  script** (`run_market_scanner.py` → `market.world_model`/`analyzer`), with a
  live `market → llm.ollama_client` coupling no governance test guards.
- **⚠️ Marking gap:** `market/` has **no `# DORMANT` marker** and is **absent from
  SUCCESSOR_MAP §6a** (added the same day) — its §6 row still reads "strongest
  archive candidate" with nothing flagging the files themselves.
- **Recommendation:** `leave_and_mark` (do not remove a tested, script-reachable
  unit unilaterally), **but make the mark load-bearing**: add the uniform DORMANT
  marker to all four `market/*.py`, fix the §6 row, and **attach a dated decision
  gate** ("archive at next consolidation unless a governance wire-in lands") so
  "pending" can't become permanent drift.
- **Binding question for you:** *archive `market/` to `.archive/` now (off-thesis),
  or keep it parked behind the dated gate?*
- **Residual risk:** a 1342-LOC off-thesis subsystem with an unguarded LLM coupling
  living in the canonical tree.

## T4.4 — dual `Hippocampus` (consolidate-or-leave)

- **Verified state + ⚠️ correction:** this is **not** "two parallel live recall
  paths." `openclaw/hippocampus.py` is the live recall (every request). On the
  **root** `hippocampus.py`, only the **static `compute_error_vector` is live**;
  `recall` / `recall_corrective` / `_apply_tension_context_boost` are
  **tested-but-no-live-caller** (parked RFC-012 asset; class never instantiated at
  runtime). The corrective branch is **default-ON** (unified_pipeline.py:173) and
  runs every request, but in the dominant no-rewrite case computes a **~zero error
  vector** — a silent near-no-op swallowed by a print-and-continue `except`.
- **Recommendation:** `leave_and_mark` — **do not** do the merge (M-effort/M-risk,
  behavior-affecting, zero current functional gain, master green). Add a marker on
  root `hippocampus.py` ("live use = static `compute_error_vector` only; recall\* =
  parked RFC-012") and a note at `unified_pipeline.py:2690-2710` about the
  latent-zero-vector branch; add both files to the SUCCESSOR_MAP table.
- **Binding questions for you:** *(1) leave as-is (mark only) or schedule a
  consolidation? (2) separately — should the default-ON, usually-zero corrective
  recall branch stay default-ON, or flip to opt-in to drop silent per-request compute?*
- **Residual risk:** an every-request branch whose query vector is usually ~zero,
  silent, asserted by no test.

## T4.5 — naming collisions (rename-or-leave)

- **Verified state:** already adjudicated by the P2 audit (P7: "execution risk
  HIGH, PROPOSAL ONLY, do NOT execute") — renames touch live importers
  (`apps/api/server.py:31`, `api/_shared/core.py:24`), CI, and the PR1 packaging
  guard. **⚠️ correction:** only **one** is a true live-vs-live grep trap:
  `tonesoul/evolution/` (live API) vs `tonesoul/council/evolution.py` (council
  weights). `yss` is *distinct words*, not a namesake; a top-level `yuhun.*` module
  doesn't exist in the tracked tree — so don't propagate the "4 collisions" wording.
- **Recommendation:** `leave_and_mark` — **do not rename**. Add a one-line
  cross-pointer header on `tonesoul/evolution/__init__.py` and
  `tonesoul/council/evolution.py` each ("live twin at <path>; not the same module").
- **Binding question for you:** *accept the deferred rename (legibility tax) — or
  schedule it as ARCHITECTURE_BOUNDARIES work?* (Recommend accept + cross-pointer.)
- **Residual risk:** `tonesoul.evolution` vs `council.evolution` stays
  grep-ambiguous; a time-pressured future agent could conflate them.

---

## The cheap, zero-behavior marking actions (ready on your nod)

Independent of the binding decisions, these are Tier-2-style legibility fixes
(comments + SUCCESSOR_MAP rows only, no behavior change) the investigation
surfaced. I can land them as one safe PR **on your nod**:

1. **corpus** — amend marker + SUCCESSOR_MAP: "parked duplicate of the live
   Supabase consent path; don't fork the consent ledger if wiring."
2. **yuhun** — mark `dpr.py` + `context_assembler.py` "unwired, NOT superseded —
   distinct mechanism"; *(separately, proposed code change: delete the dead hook.)*
3. **market** — add the missing DORMANT markers to `market/*.py`, fix §6 row, add
   a dated archive gate.
4. **hippocampus** — mark root `hippocampus.py` (static-method-only live) + the
   latent-zero-vector note; add SUCCESSOR_MAP rows.
5. **evolution** — add the live-twin cross-pointer to the two `evolution` modules.

> None of the binding wire / archive / remove / rename actions will be taken
> without an explicit per-item decision from you.
