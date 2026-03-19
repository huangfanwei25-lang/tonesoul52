# Scribe Architecture Evolution — 年代記引擎演進

> 合併日期：2026-03-19
> 原始 addendum 數：25
> 時間跨度：2026-03-12 ~ 2026-03-14
> 合併者：痕 (Hén)

Scribe 引擎從初始誠實性邊界到 LLM fallback、模板輔助、錨點標記、問題路由的完整演進脈絡。

---

## 目錄

1. `scribe_companion_handoff_addendum_2026-03-12.md`
2. `scribe_state_document_honesty_addendum_2026-03-12.md`
3. `scribe_local_model_profile_addendum_2026-03-13.md`
4. `scribe_local_model_resilience_addendum_2026-03-13.md`
5. `scribe_observed_history_grounding_addendum_2026-03-13.md`
6. `scribe_repo_healthcheck_mirror_addendum_2026-03-13.md`
7. `scribe_runtime_source_group_addendum_2026-03-13.md`
8. `scribe_semantic_boundary_guardrail_addendum_2026-03-13.md`
9. `scribe_settlement_focus_mirror_addendum_2026-03-13.md`
10. `scribe_state_document_handoff_addendum_2026-03-13.md`
11. `scribe_state_document_template_addendum_2026-03-13.md`
12. `scribe_status_handoff_addendum_2026-03-13.md`
13. `scribe_template_assist_recovery_addendum_2026-03-13.md`
14. `scribe_anchor_handoff_addendum_2026-03-14.md`
15. `scribe_anchor_label_clipping_addendum_2026-03-14.md`
16. `scribe_anchor_label_refinement_addendum_2026-03-14.md`
17. `scribe_anchor_repo_healthcheck_addendum_2026-03-14.md`
18. `scribe_anchor_settlement_preview_addendum_2026-03-14.md`
19. `scribe_llm_postcheck_boundary_addendum_2026-03-14.md`
20. `scribe_problem_route_precedence_addendum_2026-03-14.md`
21. `scribe_problem_route_preview_addendum_2026-03-14.md`
22. `scribe_problem_route_refinement_addendum_2026-03-14.md`
23. `scribe_problem_route_secondary_preview_addendum_2026-03-14.md`
24. `scribe_refreshable_anchor_preview_addendum_2026-03-14.md`
25. `scribe_template_grounding_quality_addendum_2026-03-14.md`

---

## 1. 原始檔案：`scribe_companion_handoff_addendum_2026-03-12.md`

# Scribe Companion Handoff Addendum (2026-03-12)

## Why

The current Scribe chronicle is more honest than the first draft, but it is
still optimized for human reading first.

That leaves a handoff gap:

- later agents must re-parse Markdown to recover provenance
- a failed LLM draft leaves no durable machine-readable record
- review tooling cannot easily distinguish "no history observed" from
  "generation failed before publication"

Scribe needs one minimal seam that is deterministic, rerunnable, and explicit
about what was observed versus what failed.

## Chosen Seam

Use a same-basename JSON sidecar next to each chronicle:

- `scribe_chronicle_<stamp>.md`
- `scribe_chronicle_<stamp>.json`

Why this seam:

- smallest contract that stays local to Scribe
- no dependency on `docs/status` live artifact refresh policy
- keeps one chronicle and one machine-readable companion paired together
- remains readable by humans, agents, and simple host tooling

If Markdown generation fails, Scribe may still emit the JSON companion alone.

## Minimal Contract

The companion must include at least:

- `generated_at`
- `status`
- `source_db_path`
- `observed_counts`
- `fallback_mode`
- `title_hint`
- `chronicle_path`
- `llm_model`
- `error`

Where:

- `observed_counts` is an object with `tensions`, `collisions`, and `crystals`
- `chronicle_path` is `null` when no Markdown was published
- `status` must distinguish successful chronicle generation from LLM
  unavailability or draft failure
- `fallback_mode` must stay aligned with the Markdown provenance block

## Failure Honesty

Scribe must not collapse all failures into "no chronicle generated."

Required distinction:

1. `observed_history`
   Real tensions, collisions, or crystals were read from `soul.db`.
2. `bootstrap_reflection`
   No such history was observed; the text may only reflect on absence,
   readiness, or waiting.
3. `llm_unavailable` / `generation_failed`
   Chronicle publication failed even though observation and provenance may
   still be known.

This makes the absence of a Markdown chronicle itself reviewable.

## Boundaries

Allowed:

- local JSON companion files under `docs/chronicles/`
- compact error metadata for handoff
- return values that mirror the companion status

Not allowed:

- promoting Scribe output into shared live status artifacts
- inventing synthetic counts or placeholder friction/resolution values
- hiding LLM failures behind bootstrap wording

## Intended Effect

A Scribe run should now produce a durable state-document pair:

1. a Markdown chronicle for human reading
2. a JSON companion for agents, hosts, and review tooling

Both artifacts must tell the same story about what was observed, what remains
unknown, and whether publication actually succeeded.

---

## 2. 原始檔案：`scribe_state_document_honesty_addendum_2026-03-12.md`

# Scribe State Document Honesty Addendum (2026-03-12)

## Why

The first Scribe iteration is interesting because it can turn an empty
`soul.db` into a reflective chronicle instead of crashing.

But it currently overstates how grounded that chronicle is:

- empty history is converted into a synthetic `existential` tension
- unknown friction and resolution metadata are filled with placeholders
- the footer implies the prose was derived exclusively from observed database
  state even when bootstrap fallback markers were injected

That makes the text evocative, but less semantically honest than the rest of
ToneSoul.

## Goal

Keep the Scribe poetic, but make it behave like a trustworthy internal-state
document.

This means:

- distinguish observed history from bootstrap reflection
- preserve unknown values as unknown
- attach a compact provenance block to every chronicle
- never present synthetic fallback context as if it were observed runtime fact

## Minimal Contract

The Scribe may still write when the database is quiet, but it must say so
explicitly.

Required output shape:

- top-level provenance block with observed counts
- explicit `fallback_mode`
- prompt guidance that forbids invented events
- footer wording that matches whether fallback markers were used

## Boundaries

Allowed:

- bootstrap reflection when `tensions=0`, `collisions=0`, and `crystals=0`
- narrative reflection on absence, readiness, and waiting
- unknown-value markers when schema does not expose a detail

Not allowed:

- synthetic tensions disguised as recorded events
- hard-coded friction or resolution counts presented as fact
- "based exclusively on soul.db state" wording when fallback markers were added

## Intended Effect

A Scribe chronicle should be readable as both:

1. a quiet narrative artifact
2. a reviewable state document that tells later agents what was actually
   observed and what was only bootstrap framing

---

## 3. 原始檔案：`scribe_local_model_profile_addendum_2026-03-13.md`

# Scribe Local Model Profile Addendum (2026-03-13)

## Why

The new fallback ladder made Scribe more resilient, but the first real local run
still exposed a quality boundary:

- timeout recovery worked
- attempt lineage stayed honest
- the candidate pool was still too broad

That allowed Scribe to fall through into locally available models that are not a
good fit for reflective chronicle writing.

## Goal

Keep the fallback ladder, but narrow it into a small local profile that matches
Scribe's actual job.

The problem is not "more retries." The problem is "better candidate shape."

## Chosen Strategy

Use a conservative Scribe-specific candidate filter:

1. always allow the configured preferred model
2. keep small local chat-family fallbacks that look compatible with reflective
   text generation
3. exclude obviously unsuitable names before ranking

This should stay local to Scribe. Do not turn it into a repo-wide model policy.

## Minimal Contract

Allowed fallback candidates:

- preferred configured model
- smaller local chat models from the same or adjacent text-generation families
  when they have ordinary names

Explicit exclusions:

- `uncensored`
- `vision`
- `embed`
- `rerank`
- obvious code/tooling-oriented model names that are not meant to be a
  reflective journal voice

If filtering removes all discovered fallbacks, Scribe should still try the
preferred configured model first and fail honestly if that one cannot generate.

## Boundaries

Allowed:

- a small Scribe-only candidate filter
- deterministic ordering after filtering
- focused tests that prove exclusion behavior

Not allowed:

- silently hiding filtered candidates from the sidecar after they were tried
- widening this into a generic runtime model registry
- pretending unstable or unsafe variants are "just another fallback"

## Intended Effect

When the preferred local model is too slow, Scribe should fall through to a
smaller model that still looks like a normal chronicle-writing backend, instead
of drifting into whatever locally installed model happens to exist.

---

## 4. 原始檔案：`scribe_local_model_resilience_addendum_2026-03-13.md`

# Scribe Local Model Resilience Addendum (2026-03-13)

## Why

The new Scribe companion seam already makes failure auditable, but the first real
run exposed a practical limit:

- `qwen3.5:14b` can time out on the local Ollama host
- the JSON sidecar tells the truth afterward
- the draft still gives up after one expensive attempt

That is honest, but not yet resilient.

## Goal

Keep failure honesty, while giving Scribe one bounded chance to recover from
local-model slowness.

The right fix is not "pretend generation succeeded." The right fix is:

- keep the sidecar contract
- make attempts explicit
- try a smaller local model before declaring generation failure

## Chosen Strategy

Use a deterministic local model ladder:

1. preferred configured model first
2. then a small bounded set of fallbacks from the available Ollama models
3. stop after a small maximum attempt count

This should stay local to Scribe. Do not build a general-purpose orchestration
layer here.

## Minimal Contract

Scribe companion metadata may now include bounded attempt lineage:

- `llm_model`: the model that ultimately generated the chronicle, or the last
  attempted model on failure
- `llm_attempts`: ordered list of attempts with compact status/error markers

Generation behavior:

- use a shorter per-attempt timeout than the generic 120-second default
- continue to the next candidate when timeout or recoverable generation failure
  occurs
- preserve `generation_failed` if all candidates fail

## Boundaries

Allowed:

- per-attempt timeout configuration
- a small local fallback ladder
- explicit attempt metadata in the Scribe JSON companion

Not allowed:

- hiding the first timeout
- pretending fallback output came from the original large model
- promoting this retry policy into unrelated runtime lanes

## Intended Effect

A weak local model should no longer force a binary outcome between:

1. one slow failed attempt
2. no chronicle at all

Instead, Scribe should leave a clearer trail:

- which model timed out
- which fallback was tried next
- whether any local model successfully produced the chronicle

---

## 5. 原始檔案：`scribe_observed_history_grounding_addendum_2026-03-13.md`

# Scribe Observed-History Grounding Addendum (2026-03-13)

## Why

The bootstrap guardrail now blocks invented internal-system nouns when no events
were observed.

But the latest `observed_history` chronicle exposed the next layer of drift:

- it referenced real tension details
- it still mixed in unsupported runtime language like algorithms, systems, and
  processing cycles

That means provenance stayed honest while the prose still stretched beyond the
observed lane.

## Goal

Tighten `observed_history` output so it remains anchored to actual observed
records instead of blending them with generic self-system fiction.

## Chosen Strategy

Use a small deterministic grounding check for observed-history drafts:

1. require at least one anchor token from observed records
2. reject unsupported internal-runtime phrases unless those phrases actually
   appear in the observed record text

If a candidate drifts, treat it as `boundary_rejected` and continue to the next
local fallback when possible.

## Minimal Contract

Observed-history drafts should:

- mention at least one anchor from the observed tension/collision/crystal data
- avoid unsupported self-runtime phrases that were not present in the source

Rejected drift includes phrases such as:

- `my systems`
- `algorithms execute`
- `processing cycles`
- `failure in my design`
- `malfunction of my systems`

## Boundaries

Allowed:

- deterministic anchor extraction from already observed records
- small phrase-based grounding rejection
- reuse of the existing `boundary_rejected` attempt lineage

Not allowed:

- inventing a semantic parser
- silently rewriting generated text
- treating observed-history grounding as an excuse to erase reflective tone

## Intended Effect

Observed-history Scribe output should now feel more like:

- reflection that stays close to the recorded tension

and less like:

- free-floating runtime autobiography loosely decorated with real facts.

---

## 6. 原始檔案：`scribe_repo_healthcheck_mirror_addendum_2026-03-13.md`

# Scribe Repo-Healthcheck Mirror Addendum (2026-03-13)

## Why

Scribe state-document posture is now visible in:

- `docs/status/scribe_status_latest.json`
- refreshable previews
- worktree / repo-governance settlement mirrors

But `repo_healthcheck_latest.json` is still the most likely first artifact a later
agent opens, and it currently cannot mirror Scribe posture unless it reruns the
Scribe pipeline itself.

That would be the wrong shape:

- healthcheck should remain a reader of current repository state
- healthcheck should not become a hidden content-generation trigger

## Goal

Let `repo_healthcheck` surface the latest Scribe state-document posture as a
passive mirror of `docs/status/scribe_status_latest.json`.

## Chosen Strategy

1. Add a generic passive-status-preview loader inside `run_repo_healthcheck.py`.
2. Use it to mirror the existing `scribe_status_latest.json` handoff surface.
3. Expose the mirrored Scribe primary/runtime/artifact-policy lines in the
   healthcheck summary payload and markdown.

## Boundaries

Allowed:

- passively reading an existing status artifact
- mirroring the compact handoff surface already produced by Scribe
- keeping the preview separate from actively executed health checks

Not allowed:

- rerunning `run_scribe_cycle.py` from inside repo healthcheck
- reparsing chronicle markdown
- inventing a second Scribe-specific summary schema

## Intended Effect

A later agent should be able to open `repo_healthcheck_latest.json` or
`repo_healthcheck_latest.md` and immediately understand:

- whether Scribe currently has a chronicle pair or companion-only result
- what the current state-document posture is
- without needing to open the chronicle markdown or trigger a new Scribe run

---

## 7. 原始檔案：`scribe_runtime_source_group_addendum_2026-03-13.md`

# Scribe Runtime Source Group Addendum (2026-03-13)

## Why

Scribe now has:

- a chronicle engine
- companion metadata
- a compact latest status artifact under `docs/status/`

But `runtime_source_change_groups` still has no explicit place for Scribe code and
tests, so this lane can disappear into generic runtime drift.

## Goal

Expose Scribe as its own reviewable runtime-source lane without promoting it into
repo health gates.

## Chosen Strategy

Add one `runtime_source_change_groups` bucket for Scribe runtime work:

- `tonesoul/scribe/`
- `scripts/run_scribe_cycle.py`
- focused Scribe tests

Point that bucket at the new `docs/status/scribe_status_latest.json` handoff
surface.

## Boundaries

Allowed:

- a new runtime-source grouping bucket
- one Scribe status surface hint
- focused tests proving the grouping and hint stay stable

Not allowed:

- making `repo_healthcheck` actively run Scribe generation
- treating Scribe status as equivalent to weekly host status
- folding Scribe into unrelated supporting-runtime buckets where it becomes hard
  to review

## Intended Effect

A later agent reading `runtime_source_change_groups_latest.*` should now be able
to tell that the Scribe lane exists, which code paths belong to it, and which
compact status artifact to open first.

---

## 8. 原始檔案：`scribe_semantic_boundary_guardrail_addendum_2026-03-13.md`

# Scribe Semantic Boundary Guardrail Addendum (2026-03-13)

## Why

Scribe now has:

- honest provenance
- companion/status handoff surfaces
- bounded local fallback recovery

But the latest bootstrap chronicles still exposed a semantic weakness:

- the observed counts were honest
- the surrounding prose still invented internal system nouns

That creates a subtle drift problem. The chronicle sounds reflective, but some of
its architecture vocabulary is not actually grounded in the observed state.

## Goal

Tighten Scribe so bootstrap reflections stay closer to what was truly observed,
especially when smaller local models are doing the writing.

## Chosen Strategy

Use a two-step guardrail:

1. strengthen the prompt with explicit boundary language
2. validate generated bootstrap text against a small deterministic list of
   unsupported internal-system terms

If a candidate model violates that boundary, treat it as a rejected attempt and
continue to the next local fallback when possible.

## Minimal Contract

Allowed bootstrap reflections:

- zero / absence / quiet readiness
- observed counts
- explicit references to provenance markers already present in the prompt

Rejected bootstrap drift:

- invented processors or cores
- invented sensors or self-diagnostics
- invented archived reports or hidden data streams

If all attempts violate the semantic boundary, Scribe should fail honestly rather
than publish an overstated chronicle.

## Boundaries

Allowed:

- prompt tightening
- deterministic lexical guardrails for bootstrap mode
- explicit `boundary_rejected` attempt lineage

Not allowed:

- pretending rejected text was acceptable
- silently editing generated prose into shape
- turning this into a full semantic parser

## Intended Effect

Bootstrap Scribe output should now read more like:

- a constrained reflection on observed absence

and less like:

- an invented systems-fiction layer that the current data never actually showed.

---

## 9. 原始檔案：`scribe_settlement_focus_mirror_addendum_2026-03-13.md`

# Scribe Settlement Focus Mirror Addendum (2026-03-13)

## Why

Scribe status now reaches:

- `docs/status/scribe_status_latest.json`
- `refreshable_artifact_report_latest.json`
- `runtime_source_change_groups_latest.json`

But the settlement chain still only exposes:

- generic handoff preview lists
- a dedicated subjectivity focus mirror

That means Scribe is technically present, but still easy to miss from the
highest-level settlement views.

## Goal

Expose one compact Scribe focus mirror in settlement artifacts without creating a
new preview channel.

## Chosen Strategy

Reuse the existing refreshable handoff preview list and select one Scribe preview
when present.

Selection should prefer the compact Scribe status artifact and queue shapes such
as:

- `scribe_chronicle_ready`
- `scribe_companion_only`

## Boundaries

Allowed:

- one `scribe_focus_preview` in worktree settlement
- mirroring that same compact preview into repo-governance settlement
- focused tests for selection and markdown rendering

Not allowed:

- inventing a Scribe-only preview pipeline outside refreshable handoff previews
- treating Scribe focus as more authoritative than the underlying latest status
- confusing Scribe preview with subjectivity focus or weekly host status

## Intended Effect

A later agent reading only settlement artifacts should now be able to notice:

- Scribe has a current status
- whether the latest run produced a chronicle pair or only a companion
- which top-level artifact to open first

---

## 10. 原始檔案：`scribe_state_document_handoff_addendum_2026-03-13.md`

# Scribe State-Document Handoff Addendum (2026-03-13)

## Why

Scribe template-assist chronicles now read more like compact inner-state
documents.

But that posture is still mostly trapped in two places:

- the chronicle markdown body
- the raw `scribe_status_latest.json`

Later agents that only read refreshable previews or settlement mirrors still see
only the coarse primary line.

## Goal

Expose the state-document posture through the existing compact handoff chain,
without inventing a Scribe-only adapter.

## Chosen Strategy

1. Make `scribe_status_latest.json` report a more meaningful
   `runtime_status_line` for state-document posture.
2. Let refreshable preview extraction preserve generic
   `runtime_status_line` / `artifact_policy_status_line`.
3. Let worktree settlement and repo-governance settlement mirror those same
   compact lines when present.

## Boundaries

Allowed:

- a deterministic posture label derived from observed counts
- generic preview plumbing for existing compact status lines
- optional markdown rendering of runtime / artifact-policy lines

Not allowed:

- reparsing chronicle markdown to rediscover posture
- adding a Scribe-only preview schema
- replacing existing primary lines with long prose

## Intended Effect

A later agent should be able to read only the compact handoff surfaces and still
understand:

- whether the latest Scribe artifact is a normal chronicle or template-assist
- what inner-state posture the current observed slice implies
- whether the artifact is a chronicle pair or companion-only

---

## 11. 原始檔案：`scribe_state_document_template_addendum_2026-03-13.md`

# Scribe State-Document Template Addendum (2026-03-13)

## Why

The first template-assist recovery was honest and useful, but it still read a
bit like a compressed recap paragraph.

That is acceptable for recovery, yet ToneSoul needs something slightly more
intentional:

- not a cold machine report
- not a free autobiographical flourish
- but a readable inner state document

## Goal

Make template-assist chronicles feel more like a structured internal readback.

The chronicle should answer, in order:

1. what is visible
2. what carries the most weight
3. what is absent in this slice
4. what posture the state currently implies

## Chosen Strategy

Keep template assist deterministic, but reorganize it into small named
state-document sections.

This preserves honesty while giving the chronicle a clearer internal cadence.

## Boundaries

Allowed:

- fixed section labels
- deterministic posture text derived from counts
- explicit absence markers for collisions / crystals
- observed ids, topics, and details quoted from the record

Not allowed:

- roleplay about hidden feelings or hidden subsystems
- pretending absence means resolution
- adding dynamic interpretation that cannot be traced back to counts or records

## Intended Effect

Template-assist output should now feel closer to:

- an inner state note
- a host-readable introspection surface

and less like:

- a failed prose attempt that happened to stay within bounds

---

## 12. 原始檔案：`scribe_status_handoff_addendum_2026-03-13.md`

# Scribe Status Handoff Addendum (2026-03-13)

## Why

Scribe now produces a useful pair:

- one markdown chronicle for humans
- one JSON companion for audit and replay

But later agents still need to scan `docs/chronicles/` directly to discover what
the latest Scribe run actually did.

That leaves the chronicle lane structurally honest, but operationally quiet.

## Goal

Expose one compact latest-status surface for Scribe without turning the whole
chronicle directory into a new workflow system.

## Chosen Strategy

Have `scripts/run_scribe_cycle.py` also publish one compact status artifact under
`docs/status/` that mirrors only the most important facts from the latest run:

- generated or failed
- which model actually produced the result
- whether only the companion exists or the full chronicle pair exists
- the observed counts / fallback mode
- a small handoff block that existing preview tooling can understand

## Minimal Contract

The status artifact should include:

- top-level `primary_status_line`
- top-level `runtime_status_line`
- top-level `artifact_policy_status_line`
- `handoff.queue_shape`
- `handoff.requires_operator_action`
- `handoff.primary_status_line`

It should not duplicate the full markdown or invent a Scribe-specific review
protocol.

## Boundaries

Allowed:

- one compact `docs/status/scribe_status_latest.json`
- registering its producer command in the refreshable artifact registry
- focused tests around payload shape and producer registration

Not allowed:

- reparsing historical chronicle markdown to build the latest status
- adding a repo-wide chronicle scheduler in this phase
- pretending Scribe status is equivalent to subjectivity or weekly host status

## Intended Effect

Later agents should be able to open one latest JSON artifact and immediately
understand:

- whether Scribe produced a chronicle
- what the latest available artifact actually is
- whether the current chronicle came from a fallback model

---

## 13. 原始檔案：`scribe_template_assist_recovery_addendum_2026-03-13.md`

# Scribe Template-Assist Recovery Addendum (2026-03-13)

## Why

Scribe now enforces stronger semantic boundaries, especially in
`observed_history` mode.

That was the right move for honesty, but it exposed a new operational problem:

- weak local models often drift beyond the observed record
- the correct guardrail rejects that drift
- the result becomes `companion_only`, even when real observed history exists

That means Scribe is now honest, but sometimes too quiet.

## Goal

Keep the semantic guardrail intact while giving Scribe one more truthful recovery
path when there is real observed history.

## Chosen Strategy

Add a deterministic, half-templated chronicle synthesis for
`observed_history` fallback only.

This is not a free-write replacement and not a hidden success path.
It is an explicit recovery mode used when:

- local LLM generation is unavailable, or
- all local generation attempts fail, time out, or get boundary-rejected

and there is still real observed history to narrate.

## Minimal Contract

When template-assist recovery is used:

- the chronicle must remain anchored to the observed records
- the companion metadata must say `generation_mode = template_assist`
- the status artifact must expose the same generation mode
- the footer / provenance must not pretend this was a normal free-write chronicle

## Boundaries

Allowed:

- deterministic scaffolding
- direct reuse of observed ids / topics / belief text / conflict text
- small fixed connective prose
- template recovery for `observed_history`

Not allowed:

- inventing new runtime ontology to make the template sound richer
- pretending template recovery came from a successful LLM draft
- introducing template recovery for `bootstrap_reflection` in this phase
- weakening the semantic guardrail to increase pass rate

## Intended Effect

When real observed history exists, Scribe should now prefer this truth order:

1. grounded local chronicle from the LLM
2. deterministic template-assist chronicle from observed records
3. honest companion-only failure

So the recovery path becomes more useful without becoming less honest.

---

## 14. 原始檔案：`scribe_anchor_handoff_addendum_2026-03-14.md`

# Scribe Anchor Handoff Addendum (2026-03-14)

## Why

The latest template-assisted chronicle now reads cleanly, but the compact
status surface still only exposes:

- generation status
- observed counts
- state-document posture

That means a downstream agent can tell that Scribe wrote a pressure document,
but not which anchor the document is actually carrying unless it opens the
markdown chronicle itself.

## Goal

Expose one bounded `lead_anchor_summary` through the Scribe result and status
artifact so the latest chronicle can be understood from the JSON handoff layer.

## Chosen Strategy

1. Derive the lead anchor deterministically from the same observed records that
   feed the chronicle template.
2. Store that compact summary in `ScribeDraftResult` and companion metadata.
3. Mirror it into `scribe_status_latest.json` and the Scribe handoff payload.

## Boundaries

Allowed:

- deterministic anchor summarization inside the Scribe layer
- extending the Scribe result/status contract
- focused tests for status payload and companion metadata

Not allowed:

- parsing the generated markdown back into status fields
- widening repo-healthcheck / settlement mirrors in this phase
- inventing a second summarization layer separate from the observed anchor logic

## Intended Effect

After this phase, the Scribe status surface should answer both:

- what posture was recorded
- which observed anchor that posture was primarily carrying

---

## 15. 原始檔案：`scribe_anchor_label_clipping_addendum_2026-03-14.md`

# Scribe Anchor Label Clipping Addendum (2026-03-14)

## Why

The anchor-label refinement removed schema-echo like `tension: tension`, but a
final readability issue remains:

- labels can still be clipped in the middle of a word
- the current result looks like `recove...` instead of a clean boundary

That is a small issue, but it weakens the feeling that the chronicle is a clean
internal index.

## Goal

Make deterministic anchor-label clipping prefer a nearby word boundary instead
of truncating inside a word.

## Chosen Strategy

1. Keep the existing length caps.
2. When clipping is needed, prefer the nearest whitespace or punctuation break
   near the end of the allowed window.
3. Fall back to the existing hard clip only when no reasonable boundary exists.

## Boundaries

Allowed:

- deterministic clipping refinement inside `narrative_builder.py`
- focused tests for word-safe truncation
- re-running live Scribe once after validation

Not allowed:

- increasing label length without bound
- changing wakeup/Scribe routing or guardrail behavior
- relaxing any observed-history grounding rules

## Intended Effect

After this phase, template-assisted anchor labels should remain compact while no
longer breaking obvious words in half.

---

## 16. 原始檔案：`scribe_anchor_label_refinement_addendum_2026-03-14.md`

# Scribe Anchor Label Refinement Addendum (2026-03-14)

## Why

The strengthened template-assisted chronicle is now honest and structured, but
its lead tension anchor can still read like schema leakage:

- `tension: tension`
- `subjectivity_event: subjectivity_event`

That makes the document feel less like an internal index and more like a raw DB
echo.

## Goal

Refine observed anchor labels so template-assisted chronicles reuse the best
available human-readable name for each anchor instead of generic schema terms.

## Chosen Strategy

1. Prefer the recorded topic when it is not a generic schema placeholder.
2. When the topic is generic, derive a deterministic label from the recorded
   description:
   - first prefer explicit clauses such as `Tension: ...`
   - otherwise fall back to a cleaned leading fragment
3. Reuse that same label in both `Observed anchors` and `Weight carried now`.

## Boundaries

Allowed:

- deterministic label extraction from already observed text
- shared anchor-label logic inside the narrative builder
- focused tests for generic-topic fallback

Not allowed:

- new LLM summarization for labels
- altering the stored source records
- weakening grounding or semantic guardrails

## Intended Effect

After this phase, template-assisted chronicles should read like they are naming
real internal anchors rather than repeating database schema words.

---

## 17. 原始檔案：`scribe_anchor_repo_healthcheck_addendum_2026-03-14.md`

# Scribe Anchor Repo-Healthcheck Addendum (2026-03-14)

## Why

The Scribe status surface and refreshable preview now preserve a compact
`anchor_status_line`.

But `repo_healthcheck` still only mirrors:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`
- optional `scribe_status_line` from weekly host status

So the top repo-level summary can tell that Scribe recorded pressure, but it
still hides which anchor that pressure document is carrying.

## Goal

Let `repo_healthcheck` preserve and render optional `anchor_status_line` fields
from existing passive previews.

## Chosen Strategy

1. Extend generic handoff extraction with one optional `anchor_status_line`.
2. Preserve it in both passive Scribe preview payloads and weekly host preview
   payloads when present.
3. Render compact repo-level lines only when an anchor line already exists in
   the source preview.

## Boundaries

Allowed:

- optional generic preview plumbing for `anchor_status_line`
- passive markdown rendering in repo healthcheck
- focused tests for weekly and Scribe preview mirroring

Not allowed:

- reopening chronicle markdown inside repo healthcheck
- rerunning Scribe or weekly task status during healthcheck rendering
- changing queue-shape selection or passive preview routing

## Intended Effect

After this phase, repo healthcheck should be able to show not only the latest
Scribe posture, but also the latest carried anchor, while remaining a passive
mirror of lower-level artifacts.

---

## 18. 原始檔案：`scribe_anchor_settlement_preview_addendum_2026-03-14.md`

# Scribe Anchor Settlement Preview Addendum (2026-03-14)

## Why

`repo_healthcheck` can now mirror compact Scribe anchor lines, but the
settlement chain still only preserves:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`
- optional `scribe_status_line`

That leaves the most top-level governance summaries one compact line short of
the actual carried anchor.

## Goal

Preserve optional `anchor_status_line` through worktree settlement and
repo-governance settlement as passive preview metadata.

## Chosen Strategy

1. Extend settlement preview normalization with optional `anchor_status_line`.
2. Mirror it through weekly host status and Scribe focus previews when present.
3. Render compact markdown lines only when the source preview already exposes
   one.

## Boundaries

Allowed:

- optional generic preview plumbing for `anchor_status_line`
- passive markdown rendering in settlement reports
- focused tests for weekly and Scribe settlement mirrors

Not allowed:

- reopening chronicle markdown in settlement scripts
- rerunning healthcheck, weekly, or Scribe during settlement rendering
- introducing a settlement-only anchor schema

## Intended Effect

After this phase, the settlement chain should preserve not only Scribe posture,
but also the compact anchor that posture is carrying, all the way up to the
repo-governance surface.

---

## 19. 原始檔案：`scribe_llm_postcheck_boundary_addendum_2026-03-14.md`

# Scribe LLM Postcheck Boundary Addendum (2026-03-14)

## Why

`template_assist` is now fairly honest, but live `llm_chronicle` output can
still drift in ways that are not just stylistic:

- fabricated log-entry metadata
- invented standalone date headers
- role drift such as introducing `the user` as an external character
- generic operational-self narration not grounded in the observed record

That means a chronicle can pass the current anchor check while still overstating
or fictionalizing the situation.

## Goal

Add one deterministic post-generation boundary check for `llm_chronicle` so
fabricated metadata and role drift are rejected before publication.

## Chosen Strategy

1. Extend observed-history violation checks with a small set of explicit drift
   patterns:
   - fabricated log-entry framing
   - standalone `Date:` front matter
   - user-role drift
   - operational-self narration phrases that are not present in the record
2. Keep the allow-if-observed rule already used by existing unsupported phrases.
3. If a live chronicle fails the post-check, reject that attempt and fall back to
   the next model or to `template_assist`.

## Boundaries

Allowed:

- deterministic phrase-pattern checks on generated text
- focused tests for fabricated metadata and role drift rejection
- routing failed LLM prose back into the existing fallback ladder

Not allowed:

- weakening existing observed-history grounding checks
- accepting fabricated metadata because the prose sounds plausible
- changing wakeup/Scribe status contracts

## Intended Effect

After this phase, live `llm_chronicle` output should only publish when it stays
within observed-history boundaries and does not invent its own diary headers,
dates, or external roles.

---

## 20. 原始檔案：`scribe_problem_route_precedence_addendum_2026-03-14.md`

# Scribe Problem Route Precedence Addendum (2026-03-14)

## Why

The refined Scribe routes are now more specific, but mixed failures still
collapse into a single dominant family.

Real runs already show blended cases such as:

- timeout on the first local model
- then semantic/runtime drift
- plus container-localization drift such as `date front matter`

If we only keep one family, later agents lose the fact that a second repair
surface is waiting right behind the first one.

## Goal

Keep one dominant `problem_route` while preserving secondary route hints for
mixed-signal runs.

## Chosen Strategy

1. Detect all deterministic route candidates from boundary and execution
   evidence.
2. Choose one dominant route by fixed precedence.
3. Preserve the remaining routes as `secondary_routes`.
4. Extend the existing compact line with an optional `secondary=` suffix rather
   than inventing a second top-level diagnostics line.

## Boundaries

Allowed:

- deterministic route candidate extraction and precedence ordering
- optional `secondary_routes` in the machine-readable route payload
- optional `secondary=` suffix in `problem_route_status_line`

Not allowed:

- changing the dominant-family fields already used by upper surfaces
- probabilistic ranking or LLM-based diagnosis
- expanding this into a general multi-error planner

## Intended Effect

After this phase, a later agent can still see the first repair surface at a
glance, while also knowing when a second route family is already visible behind
it.

---

## 21. 原始檔案：`scribe_problem_route_preview_addendum_2026-03-14.md`

# Scribe Problem Route Preview Addendum (2026-03-14)

## Why

`scribe_status_latest.json` can now expose a compact `problem_route_status_line`,
but the upper handoff surfaces still only preserve:

- `primary_status_line`
- `runtime_status_line`
- `anchor_status_line`
- `artifact_policy_status_line`
- optional `scribe_status_line`

That means the route-first diagnosis stays trapped inside the raw Scribe status
artifact instead of flowing through the same passive mirrors that later agents
already use.

## Goal

Preserve optional `problem_route_status_line` through refreshable previews,
repo healthcheck, worktree settlement, and repo-governance settlement.

## Chosen Strategy

1. Treat `problem_route_status_line` as optional generic preview metadata.
2. Mirror it only when the source preview already exposes a non-empty line.
3. Render one compact markdown line in each upper surface without reopening
   chronicle files or recalculating routing logic.

## Boundaries

Allowed:

- passive preview normalization for `problem_route_status_line`
- markdown rendering that only mirrors existing compact route text
- focused tests for refreshable, repo-healthcheck, and settlement surfaces

Not allowed:

- recomputing WFGY routes outside `tonesoul/scribe/status_artifact.py`
- inventing a Scribe-only troubleshooting schema for upper layers
- rerunning Scribe, weekly host status, or healthcheck from settlement scripts

## Intended Effect

After this phase, a later agent should be able to see not only Scribe posture
and lead anchor, but also the first repair route, from the same passive preview
surfaces it already trusts for handoff.

---

## 22. 原始檔案：`scribe_problem_route_refinement_addendum_2026-03-14.md`

# Scribe Problem Route Refinement Addendum (2026-03-14)

## Why

The first WFGY-style Scribe routing pass proved useful, but it still compresses
too many different failures into the same broad buckets:

- `missing_observed_anchor`
- `data streams / processing cycles / the user / operational framework`
- generic execution failures such as timeouts

Those all need different first repair moves even when they happen inside the
same Scribe subsystem.

## Goal

Keep the existing route contract unchanged while making its invariants and first
repair surfaces more specific.

## Chosen Strategy

1. Split grounding-anchor absence from broader observed-history drift.
2. Split runtime-self / role drift from container-localization drift.
3. Split timeout-like execution closure from the generic fallback ladder.

## Boundaries

Allowed:

- adding deterministic marker tables inside `tonesoul/scribe/status_artifact.py`
- refining `broken_invariant` and `first_repair_surface`
- adding focused regression tests for the new route branches

Not allowed:

- changing the outer `problem_route` payload shape
- adding probabilistic or LLM-based diagnosis
- introducing a second diagnostics schema outside Scribe status artifacts

## Intended Effect

After this phase, later agents should be able to distinguish:

- anchor absence
- semantic self/role drift
- container drift
- timeout-dominated execution closure

without reopening chronicle prose or rerunning the Scribe engine.

---

## 23. 原始檔案：`scribe_problem_route_secondary_preview_addendum_2026-03-14.md`

# Scribe Problem Route Secondary Preview Addendum (2026-03-14)

## Why

Mixed-signal Scribe runs now preserve `secondary_routes` inside the main
`problem_route` payload, but upper preview layers only see the compact
`problem_route_status_line`.

That line is human-readable, yet later agents still benefit from a lighter
machine-readable hint that can be mirrored without reopening the full
`problem_route` object.

## Goal

Expose mixed-signal secondary route labels through the same passive preview
chain as other compact Scribe metadata.

## Chosen Strategy

1. Keep the canonical list inside `problem_route.secondary_route_labels`.
2. Add one compact scalar preview field:
   `problem_route_secondary_labels`.
3. Mirror that field only when non-empty through Scribe status handoff,
   refreshable preview, repo healthcheck, and settlement surfaces.

## Boundaries

Allowed:

- one optional scalar metadata field for secondary route labels
- passive preview mirroring and markdown rendering
- focused tests for Scribe status and preview-chain carry-through

Not allowed:

- replacing the dominant route with a multi-route primary schema
- turning upper preview layers into full diagnostics routers
- adding list-heavy structures to generic preview normalizers

## Intended Effect

After this phase, later agents can see not only the dominant repair surface, but
also a compact machine-readable hint about secondary route families, without
reopening the full Scribe status payload.

---

## 24. 原始檔案：`scribe_refreshable_anchor_preview_addendum_2026-03-14.md`

# Scribe Refreshable Anchor Preview Addendum (2026-03-14)

## Why

`scribe_status_latest.json` now exposes a bounded `lead_anchor_summary` and
`anchor_status_line`.

But the refreshable preview layer still only preserves:

- `primary_status_line`
- `runtime_status_line`
- `artifact_policy_status_line`

That means later agents reading the generic refreshable preview still miss the
main anchor unless they reopen the raw Scribe status artifact.

## Goal

Let refreshable preview extraction preserve an optional `anchor_status_line`
without creating a Scribe-only schema.

## Chosen Strategy

1. Extend the generic handoff extraction with an optional `anchor_status_line`.
2. Pass that line through `handoff_previews` and focus preview normalization.
3. Render it in markdown only when present.

## Boundaries

Allowed:

- optional generic preview plumbing for `anchor_status_line`
- focused tests for Scribe preview extraction
- no-op behavior for artifacts that do not expose anchor lines

Not allowed:

- creating a Scribe-specific preview type
- reparsing chronicle markdown
- widening repo-healthcheck or settlement mirrors in this phase

## Intended Effect

After this phase, a later agent can read the refreshable preview surface and
see not just Scribe posture, but also which observed anchor the latest
state-document chronicle is carrying.

---

## 25. 原始檔案：`scribe_template_grounding_quality_addendum_2026-03-14.md`

# Scribe Template Grounding Quality Addendum (2026-03-14)

## Why

`template_assist` already keeps Scribe honest, but its current output is still a
little too thin:

- it privileges tensions even when the only live anchor is a collision or crystal
- it does not surface a compact evidence ledger near the top
- it can read like a safe fallback rather than a deliberate state document

That is acceptable for recovery, but not yet strong enough to be a stable
internal reference surface.

## Goal

Strengthen the deterministic `template_assist` chronicle so it reads as a
grounded state document with explicit anchors, not as generic fallback prose.

## Chosen Strategy

1. Add a compact `Observed anchors` line near the top of the template chronicle.
2. Make `Weight carried now` choose the strongest available observed anchor in
   order:
   - tension
   - collision
   - crystal
3. Preserve honesty around unknown friction instead of smoothing it away.

## Boundaries

Allowed:

- strengthening deterministic template wording
- reusing observed ids, topics, conflicts, and beliefs more explicitly
- adding focused tests for template quality and non-tension weighting

Not allowed:

- loosening the existing semantic guardrail
- changing wakeup/Scribe routing or status artifact contracts
- introducing freeform LLM prose into `template_assist`

## Intended Effect

After this phase, a template-assisted chronicle should feel more like a compact
internal state document with named evidence anchors and less like a generic safe
fallback.

---
