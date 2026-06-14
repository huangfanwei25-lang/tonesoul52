# Phase 7 Dream Engine — revival + honest observation (2026-06-14)

> Reviving a dormant subsystem and asking the question it was built to test:
> when the AI is idle, does it generate intrinsic direction — or only reflect
> on what it is handed?

## What was dormant

The Phase 7 autonomous stack (`tonesoul/dream_engine.py`,
`tonesoul/wakeup_loop.py`, `tonesoul/autonomous_cycle.py`,
`tonesoul/dream_observability.py`) was wired and tested at Phase 138
(`docs/status/dream_engine_wakeup_status_2026-03-09.md`, 1457 tests green) and
then never run against a real model. It had the full machinery — perceive →
persist → wake → dream → consolidate → narrate (Scribe) → dashboard — but the
reflection step had only ever exercised the deterministic fallback template.

## What reviving actually required

Nothing in the source. The wiring was already correct. The only missing piece
was a serving local model: `ollama` running `qwen2.5:1.5b` (986MB, the small
bilingual model already pulled for the Phase 3 LLM-judge work). With it up:

- `LLMRouter().health_check()` → `{ollama: True, ...}`, resolves to `OllamaClient`.
- `OllamaClient` defaults to `qwen3.5:4b`; its `_ensure_model` fallback matches
  the `"qwen"` substring and resolves to `qwen2.5:1.5b`. (Fragile — see caveat.)
- `memory/soul.db` already held **47 environment stimuli** + **3 durable
  crystals**, so the engine had real material to collide on.

Re-run: `python scripts/run_dream_engine.py --limit 3` (dream only), or
`python scripts/run_autonomous_dream_cycle.py --limit 2` (full loop), with
ollama serving. Add `--no-llm` to fall back to the deterministic template.

## What it generated (real model output, not template)

Dream cycle: `reflection_generated=True`, `backend=ollama`,
`model=qwen2.5:1.5b` on every collision. The reflections are genuine and
competent but **loose** — the 1.5B model does not reliably obey the
"exactly 2 sentences" spec (it sometimes emits a preamble then re-labels
"Sentence 1 / Sentence 2"). Honest limitation of the small model.

Full autonomous cycle (cycle 4, 7983ms): 2 collisions → 2 council convened →
Scribe `generated` a first-person chronicle → dashboard JSON+HTML refreshed.
The Scribe chronicle is the most evocative artifact — it writes in first person
("As I sit in my quiet, isolated corner of this system…"), but it **hallucinates
freely**: it dated itself to a year in the past and wove unrelated financial
fragments out of the gitignored memory corpus into the narrative as lived
experience. Evocative ≠ accurate; this is a narrator, not a logger.

## The honest finding (the question this was built to ask)

The driving question: *does an AI, when idle and without direction, ever
spontaneously generate something it wants to do?*

Tested directly — seeded two self-referential stimuli (the idle-direction
question itself; the open sensor-honesty gap) and let the engine dream on them.
On its own idle state, the model reflected:

> "…the idle AI's directionlessness, its lack of task assignments, and **the
> absence of prior memories about intrinsic motivation** suggest a scenario
> where the AI might either continue on autopilot **or** start generating
> internal thoughts to find purpose. The next bounded governance move could be
> to **observe this process closely without prematurely influencing it.**"

The answer is **no — not in this architecture.** Phase 7 is a *reflection
engine*: stimulus in → governance-framed reflection out. Left genuinely alone
(no stimuli), a wake cycle returns `status: idle` and generates nothing; it does
not invent a topic. It only "thought about being idle" because a stimulus was
injected saying so. There is no intrinsic-motivation generator. The closest it
comes, handed its own state, is to propose *"observe without prematurely
influencing"* — a mirror, not a spark.

This is the missing third segment named in the memory `decision-loop closure`
(see result → revise reasoning → choose next) and the `mirror needs range`
distinction (self-observation without spontaneous range = automaton). Reviving
the engine made the gap concrete instead of theoretical: the machinery to
*reflect* is real and now runs on a local model; the machinery to *want* is not
there, and pretending the dream output is "what it wants" would be the
dishonest read.

## Caveats

- One small model (qwen2.5:1.5b), one machine, a handful of cycles. The
  *direction* of the finding (reflection works, intrinsic motivation absent) is
  structural, not a measurement artifact — it follows from the code paths, not
  the model size.
- The `qwen3.5:4b` → `"qwen"` substring fallback is fragile; a config-explicit
  model would be the honest fix before any non-observational use.
- This run regenerated three tracked `docs/status/dream_*latest.*` snapshots and
  seeded 2 records into the gitignored `memory/soul.db`. No source code changed.
