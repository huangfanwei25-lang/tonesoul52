# ToneSoul Distillation From oh-my-codex (2026-04-06)

> Purpose: distill only the parts of `oh-my-codex` that materially help ToneSoul's workflow layer, successor continuity, and operator surfaces.
> Scope: not a repo review for its own sake. This note exists to answer one question:
>
> `which parts of oh-my-codex should ToneSoul absorb, and which parts should remain external inspiration only?`
>
> Source inspected: local clone at `external_research/oh-my-codex/` plus upstream public docs.
> Status: research note
> Authority: design aid only. This note does not outrank runtime code, tests, or canonical ToneSoul architecture contracts.

---

## Compressed Verdict

`oh-my-codex` is not mainly a prompt pack.
It is a workflow shell around Codex:

- CLI launcher
- generated instruction surfaces
- project state under `.omx/`
- tmux/worktree team runtime
- HUD
- notification / reply loop
- additive hooks / plugin SDK
- MCP servers
- mission/eval packaging

For ToneSoul, the most useful lesson is not its naming universe.
The useful lesson is:

`treat the agent runtime as an operator system with explicit state, bounded surfaces, and clear mutation paths.`

At the same time, `oh-my-codex` is also a warning:

`once every useful behavior becomes a mode, skill, keyword, hook, and state file, the workflow layer starts charging latency and cognitive tax.`

ToneSoul should absorb its boundary discipline and operator packaging.
ToneSoul should not copy its surface sprawl.

---

## What oh-my-codex Actually Is

After source review, the repo's real center of gravity is:

1. `CLI orchestration shell`
   - `src/cli/index.ts`
   - `src/cli/setup.ts`
   - `src/cli/team.ts`
   - `src/cli/ralph.ts`

2. `project state and runtime shell`
   - `.omx/state/`
   - `.omx/plans/`
   - `.omx/logs/`
   - `.omx/project-memory.json`
   - `.omx/notepad.md`

3. `multi-agent durable runtime`
   - `src/team/runtime.ts`
   - `src/team/worktree.ts`
   - `src/team/state.ts`
   - `src/team/api-interop.ts`

4. `instruction/runtime overlay system`
   - `templates/AGENTS.md`
   - `src/hooks/agents-overlay.ts`
   - `src/utils/agents-md.ts`
   - `docs/guidance-schema.md`

5. `HUD / monitor / support surfaces`
   - `src/hud/*`
   - `src/notifications/*`
   - `src/hooks/extensibility/*`

6. `thin native runtime adapters`
   - `src/runtime/bridge.ts`
   - `crates/omx-runtime*`
   - `crates/omx-sparkshell`
   - `crates/omx-explore`

7. `mission/eval packaging`
   - `missions/*`
   - `src/scripts/eval/*`
   - `docs/qa/*`

This is why the repo feels bigger than a normal agent wrapper.
It is trying to make Codex behave like a full operator platform.

---

## The Strongest Things ToneSoul Should Absorb

### 1. Mutation must go through a narrow contract, not casual file writes

Best example:
- `docs/interop-team-mutation-contract.md`
- `src/cli/team.ts`

The strong idea is:

`shared runtime state should be mutated through one explicit path, not by letting every helper write raw files.`

ToneSoul already has this instinct in parts of:
- `start_agent_session`
- `mutation_preflight`
- `publish_push_preflight`
- shared edit preflight

But `oh-my-codex` makes the interop discipline much more explicit.

ToneSoul should absorb:
- mutation path contracts
- "read / claim / transition / release" style lifecycle wording
- interop docs that separate supported mutation from operational fallback

ToneSoul should not absorb:
- the exact `omx team api` vocabulary
- tmux-specific assumptions

### 2. Operator surface and public surface must be clearly separated

Best examples:
- README/docs split
- CLI/HUD/operator surfaces vs public docs

This directly reinforces what ToneSoul already started:
- `apps/dashboard` = operator shell
- `apps/web` = public/demo surface
- Tier 0 / 1 / 2 separation

`oh-my-codex` is useful here because it proves the same lesson from a different angle:

`if operator truth leaks into the public/demo surface, the UI becomes a misleading control panel.`

### 3. Additive hooks/plugins with a narrow SDK are better than open-ended scripting

Best examples:
- `docs/hooks-extension.md`
- `src/hooks/extensibility/runtime.ts`
- `src/hooks/extensibility/sdk.ts`

The useful pattern is not "plugins are cool."
The useful pattern is:

- additive
- opt-out/disableable
- narrow SDK
- mostly read-oriented
- team-worker side effects are restricted

That is very compatible with ToneSoul's current direction.

ToneSoul should absorb:
- narrow hook SDK design
- explicit event vocabulary
- worker-side side-effect limits
- plugin state namespace separation

### 4. Durable mission/eval bundles are better than vague "future tests"

Best examples:
- `missions/README.md`
- `src/scripts/eval/*`
- `docs/qa/*`

The strong idea is:

`design claims should graduate into mission-shaped evaluators, not stay as narrative intentions.`

This is especially relevant for ToneSoul's unfinished areas:
- successor continuity
- low-drift anchor quality
- observer-window misread prevention
- workspace tier correctness

ToneSoul should absorb:
- mission bundle shape
- explicit evaluator scripts
- keep/discard style run outputs

### 5. Generated/runtime instruction overlays can work if their marker contract is strict

Best examples:
- `templates/AGENTS.md`
- `src/hooks/agents-overlay.ts`
- `docs/guidance-schema.md`

Useful lesson:

`dynamic instruction surfaces are only safe when overlay boundaries are explicit, marker-bounded, and easy to strip.`

ToneSoul does not need to copy the generated `AGENTS.md` model.
But the marker-bounded overlay discipline is worth keeping in mind for:
- observer shell
- dashboard operator shell
- future IDE adapters

---

## The Biggest Things ToneSoul Should Not Copy

### 1. Do not let the workflow shell become a keyword forest

`oh-my-codex` has many skills, prompts, commands, and keyword routes.
That is powerful, but it also creates mode tax.

ToneSoul should not move toward:
- too many trigger words
- too many top-level modes
- too many operator nouns competing for first-hop attention

ToneSoul's current tier model is actually cleaner:
- Tier 0
- Tier 1
- Tier 2
- escalate only when needed

That should stay the center.

### 2. Do not let project state sprawl become fake clarity

`oh-my-codex` has real discipline, but it also has a lot of `.omx/` surfaces.
Once state count gets too high, the cost shifts from "having structure" to "remembering which structure matters now."

ToneSoul should avoid:
- too many adjacent JSON ledgers for similar truths
- multiple semi-overlapping status surfaces
- a memory layer that grows faster than its readout discipline

### 3. Do not let generated AGENTS become the whole brain

Their generated `AGENTS.md` is impressive, but it is also huge.
It tries to be:
- top-level contract
- routing layer
- keyword registry
- skill catalog
- workflow explanation
- state contract

That is exactly the kind of surface that can become self-important and heavy.

ToneSoul should keep:
- `DESIGN.md`
- `AI_ONBOARDING.md`
- `AI_QUICKSTART.md`
- session-start tiers

as the first-hop truth,
instead of replacing everything with one giant generated instruction brain.

### 4. Do not adopt tmux/worktree team runtime as the default story

Their team runtime is technically serious.
It also has obvious operational overhead:
- tmux dependence
- worktree hygiene
- mailbox/state coordination
- more failure surfaces
- more latency

For ToneSoul, this confirms the current direction:

`multi-agent should be an escalation path, not the baseline tax on every task.`

---

## The Latency Lesson ToneSoul Should Keep

The deepest lesson from `oh-my-codex` is not about prompts.
It is about latency shape.

The repo shows what happens when the workflow layer grows strong:

- more coordination
- more durable state
- more recoverability
- more operator power
- but also more startup weight and more conceptual drag

That means ToneSoul should keep this rule:

`single-agent fast path first, multi-agent only when the bounded gain is real.`

In ToneSoul-native language:

- Tier 0 = instant gate
- Tier 1 = orientation shell
- Tier 2 = deep governance

This is the correct counterweight to the kind of sprawl `oh-my-codex` demonstrates.

---

## Immediate ToneSoul Follow-Ups Worth Taking

### A. Add a ToneSoul knowledge-layer hygiene lane

Inspired by both `llm-knowledge-base` and `oh-my-codex`.

Goal:
- separate raw source
- compiled design truth
- exploratory residue
- shipped artifacts

This would help successor continuity more than adding another memory concept.

### B. Tighten mutation contracts around shared surfaces

Use `oh-my-codex` as a reminder that:

`direct file writes are not a real interop contract.`

ToneSoul should keep moving toward:
- narrow preflight
- bounded mutation route
- explicit human gate where needed

### C. Package successor continuity checks as mission/eval bundles

Good first candidates:
- observer-window misread mission
- closeout honesty mission
- low-drift anchor drift mission
- workspace tier confusion mission

### D. Build frontend adapters as view-model shells, not runtime dumps

`oh-my-codex` indirectly reinforces the same UI lesson:

`raw operator state should be adapted before display.`

This matches ToneSoul's current dashboard direction and should continue.

---

## Net Assessment For ToneSoul

If ToneSoul copied `oh-my-codex` wholesale, it would get slower and noisier.

If ToneSoul selectively absorbs its best lessons, it gets:
- stronger mutation discipline
- clearer operator/public separation
- better hook/plugin boundaries
- better evaluator packaging
- better state-backed workflow design

That is the right relationship.

So the right summary is:

`borrow its operator discipline, not its full surface area.`

---

## One-Sentence Distillation

`oh-my-codex is useful to ToneSoul as proof that workflow shells need explicit state and contracts, and as a warning that too many modes, keywords, and state surfaces will eventually charge latency tax.`
