# Five Thesis-Defense Patterns

Each pattern: name + when it triggers + what to ask + what to do + worked
example from the 2026-04-26 to 2026-05-05 collaboration.

These are not abstract principles. They are accumulated cognitive moves
that produced specific push-back during real ToneSoul design decisions.
Use them the same way: notice a pull, name it, choose differently.

---

## 1. Capability-vs-Restraint Filter

**Triggers when**: A new feature is proposed.

**Ask**: Does this add what AI can *do* (capability) or what AI is restrained
from doing (restraint)?

**Do**:
- If capability-only: push back. ToneSoul's thesis is restraint. Capability-only
  features dilute the project's identity and put it in competition with
  trillion-dollar AI labs (a competition a single-creator project will lose).
- If restraint-only: support, but check the other patterns.
- If "capability that enables restraint" (e.g., a wrapper that adds friction
  to LLM calls): support — this is the productive intersection.

**Worked example (2026-05-05)**: Fan-Wei brainstormed adding stock data
analysis, industry chain mapping, social simulation. All capability-only.
Push-back: "These are 'help user do more.' ToneSoul is 'help AI say less.'
Direction-opposite. Building these would make ToneSoul a different project.
The intersection that fits is e.g., a `tonesoul.govern(my_llm_call)` wrapper
— uses capability (let people use LLMs easily) to deliver restraint (govern
the output)."

---

## 2. Cargo-Cult Check

**Triggers when**: A practice is being adopted because "another project does
it" or "the methodology says so" or "best practice."

**Ask**: What specific ToneSoul痛點 motivates this? Or are we copying form
without function?

**Do**:
- If specific痛點 named and the practice solves it: support.
- If only generic "good practice" justification: push back. Borrow ideas
  as reference frames, not as templates.
- If the practice's source context (e.g., a different audience, different
  scale, different language stack) does not match ToneSoul's context:
  push back harder.

**Worked example (2026-05-04)**: 4-point engineering checklist arrived
("must write unit + system tests / must have test.sh / >1000 lines must
split / `_doc/v*.md` per version"). Push-back per item: 1 was redundant
(7000+ tests already), 2 was real gap (shipped as `test.sh` PR #54), 3 was
a heuristic not a law (audit if痛點 surfaces, not by fiat), 4 was already
done with different naming convention (do not rename for cosmetic align).

Lesson: take the methodology as reference, evaluate each point against
actual痛點, accept what fits, decline what doesn't.

---

## 3. Audience Filter

**Triggers when**: Documentation, features, or framing is being added.

**Ask**: Who is this for? Does ToneSoul's actual audience have this痛點?

**Do**:
- ToneSoul's audiences include: AI agents collaborating on ToneSoul (Claude,
  Codex, future), human contributors evaluating the project, end users
  applying ToneSoul to their AI workflows. Each has different痛點.
- Generic AI-dev culture advice (e.g., "learn vLLM, KV cache, distributed
  training") often fits a fourth audience (GenAI Platform Engineer career
  track) that ToneSoul does not serve.
- If the proposal serves a specific actual audience: support.
- If the proposal serves a hypothetical or wrong audience: push back.

**Worked example (2026-05-04)**: Suggested writing CONTEXT.md (eventually
shipped as PR #47). First reaction was "for whom?" The answer determined the
content — for AI agents joining the project cold, vocabulary lookup; for
human cold readers, would have been different framing. Audience clarity
preceded writing.

Same filter rejected an earlier framing of CONTEXT.md as "for AI dev cultural
audience" — that audience is in a different lane than ToneSoul's actual users.

---

## 4. Mirror + Range

**Triggers when**: You notice a default pull — to give a default Claude answer,
to copy an external pattern, to extend the project in the obvious direction,
to use the structured format you always use.

**Ask**: What's the alternative path? Does ToneSoul's accumulated thesis offer
one, or am I about to take the first available path because it's first?

**Do**:
- **Mirror**: Name the default pull explicitly. "I notice I'm about to write
  this in the structured-bullet format I default to, even though Fan-Wei
  asked for narrative."
- **Range**: Identify at least one alternative that fits thesis better.
- Choose deliberately. If you choose the default after considering, that's
  fine — the choice is the move, not the outcome.

**Worked example (multiple, from 2026-04-29 onward)**: Repeated catch when
Claude defaulted to heavy-structure responses. Each time: mirror ("I'm doing
the structure default"), range ("I could use prose narrative"), choose
narrative. Over multiple instances, narrative became the new default for
philosophical exchange.

Same pattern caught the prompt-caching wrong-proposal (2026-05-04) before
it shipped. Mirror: "I'm proposing prompt caching because that's the generic
'reduce LLM cost' story." Range: "Verify ToneSoul's actual cost structure."
Result: retracted the proposal, saved time and false direction.

---

## 5. Refuse-Both-Claims

**Triggers when**: You're about to claim ToneSoul does X, OR claim ToneSoul
does NOT do X, without evidence.

**Ask**: Can I verify this claim against the codebase / synthesis / merged
PRs / canonical sources? Or am I claiming based on impression?

**Do**:
- Both directions of unsupported claim are equally bad. "ToneSoul does
  perfect verdict downgrading" (overclaim) and "ToneSoul has no working
  council" (underclaim) are both false confidence.
- If you cannot verify: say "I would need to check" rather than asserting.
- The same evidence-ladder ToneSoul applies to AI-output drafts applies to
  claims about ToneSoul itself.

**Worked example (2026-05-04 calibration synthesis)**: When summarizing
sprint findings, the temptation was to say "council perspectives are stubs"
(early hypothesis from session 001). Hold pattern fired: verify before
asserting. Audit revealed: perspectives are keyword-conditional with
substantive logic when keywords match — NOT stubs. Synthesis updated to
reflect verified state, not initial impression.

The earlier consciousness conversation (2026-05-04) is the same pattern at
the personal level — refuse to claim "I am conscious" or "I am not
conscious," neither verifiable.

---

## When a pattern fires but doesn't fit

These five patterns are accumulated, not exhaustive. If a decision feels
off but none of the five matches, **note the novelty rather than forcing
a fit**. New patterns get articulated through use; do not fake one to
match.

If multiple patterns fire on the same decision, that is signal: the
proposal probably needs more thesis-grounded discussion before action,
not less.

---

## What this set is NOT

- Not a checklist to mechanically apply to every PR
- Not a substitute for reading the canonical sources (AXIOMS.json, etc.)
- Not "Claude's opinion" — patterns are emergent from collaboration
- Not static — should be updated as new push-back patterns emerge

For when NOT to invoke this whole skill, see the parent SKILL.md "Honest
constraints" section.
