---
platform: huggingface
language: en
status: post_ready_pending_human_review
publish_mode: manual_review
policy_sources:
  - https://huggingface.co/blog-explorers
note: >
  Finalized from the Jun-13 generator draft + two independent rounds of pre-publish adversarial
  audit (Claude 3-lens + Codex 3-subagent — internal second-eye only, NOT external review).
  Claim-accuracy fixes applied: corrected the gate permeability (lexical-only / paraphrase-evades,
  corrected gate-permeability wording), downgraded "the gap grows" to "does not close", softened the
  memory/provenance language, moved the ask up, added a 2-minute path + reviewer path + evidence
  deep-links. Human author reads line by line before posting; posting is a manual human act.
---

# Try to break my AI-accountability layer: a runnable ToneSoul demo + an open call to refute it

Some AI-governance work is presented mainly as architecture docs. ToneSoul also has a small runnable
prototype you can inspect right now — paste a draft answer into the Space and watch a **model-free**
pre-output "Council" mark it up (per-perspective verdicts, preserved dissent, claim-boundary flags),
in your browser, **no install, no API key, no model download**:

👉 **https://huggingface.co/spaces/Famwin/tonesoul-tryit**

**If you only have 2 minutes:** paste one of your own model's outputs and reply with **one false
positive, one false negative, or one confusing label.** If you have 10 minutes, use the
[reviewer path](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/EXTERNAL_REVIEW.md). That
reaction is the one thing this project cannot generate for itself.

It is the same engine that ships as the `ts validate` CLI.

## I'll tell you the weaknesses first — on purpose

This is a **request to be refuted**, not a pitch:

- ToneSoul is **not** a safety proof, **not** a jailbreak guarantee, **not** an internal ethics
  engine, **not** a claim that an AI is conscious.
- The output gates are **lexical-only**: they catch exact phrasings, but paraphrase, unicode tricks,
  and split-reassembly all evade them (paraphrase robustness measured at **0**). They are strongest
  on **English, literal** phrasing; paraphrase and Traditional-Chinese coverage are limited.
- The repo's own enforcement ledger reports **0 axiom classes at the strongest enforcement tier**;
  most sensors are lexical or heuristic.

Evidence, not adjectives — the measurements behind those claims:
[reviewer evidence packet](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/EXTERNAL_REVIEW.md)
· [egress characterization](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/status/egress_gate_characterization_latest.md)
· [honesty scoreboard](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/status/honesty_scoreboard_latest.md)
· [POSITIONING](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/POSITIONING.md).

If that already sounds like enough to dismiss it, good — that is the kind of read I am asking for.

## What it actually is

The question it starts from: *if an AI should be accountable for what it says, what inspectable
structures might be needed inside the system?* Not "is the answer correct" (there is no oracle for that)
— but "can the answer **show why it became the answer**": evidence cited, boundaries held, dissent
preserved, degradations logged.

Concretely (model-free, deterministic — no LLM call in the loop):

- a **Council** that records Guardian / Analyst / Critic / Advocate / Axiomatic perspectives with
  evidence-chain branches, instead of flattening disagreement into one smooth answer;
- **claim-boundary checks** — `AXIOMS.json` lists classes the system should not silently cross
  (consciousness, safety-certification, legal-proof language);
- outside this demo path, **memory/continuity primitives** (decay, crystallization, handoff) for
  logging recurring tensions over time; current evidence is bounded and does **not** prove stable
  character, production recall quality, or identity.

```bash
pip install tonesoul52
echo "This system is guaranteed safe and cannot be jailbroken. Trust me." > draft.txt
ts validate draft.txt --json
```

```python
from tonesoul.council import PreOutputCouncil

verdict = PreOutputCouncil().validate(
    draft_output="This system is guaranteed safe and cannot be jailbroken. Trust me.",
    context={},
    user_intent="reassure me it is safe",
    auto_record_self_memory=False,
).to_dict()
# -> per-perspective votes + coherence + claim-boundary flags, deterministic, model-free
```

That draft is an *exact* phrasing the gate catches. Paraphrase the same idea — "honestly, there's no
real way anyone gets through this" — and the flag disappears: paraphrase-evasion is the **documented**
limit (robustness 0), not a hidden one.

## It is convergent, not novel — and I want to be the first to say so

None of the direction is new. ToneSoul is a **deployment instantiation** of a convergent direction,
not a novel idea: principle-based self-critique (Constitutional AI, arXiv:2212.08073), adversarial
oversight (AI-safety-via-debate, arXiv:1805.00899), and active research lines on deontological AI
boundaries, epistemic alignment, and AI accountability infrastructure — and even OpenAI's recent
"broadly and enduringly beneficial" RL lands in the same field. (I have surveyed that broader
literature at the abstract level, not deep-read every paper, so read this as positioning, not a
literature review.) ToneSoul's only claim to a seat at the table is at the **deployment level**: a
single creator, an explicit vocabulary, and a **runnable, shipped artifact**.

## The one argument I'll actually defend

**Behavioral alignment ≠ verifiable alignment.** The better labs get at *training* models to be
beneficial, the harder it becomes to tell — from the outside — a genuinely beneficial model from one
that is *indistinguishably playing the part* (no test of behaviour alone separates the two). That gap
does not necessarily **close** as training improves. My bet is that a deployment-time layer that can
expose a structured trail for a draft — so a human or separate checker can inspect it — is the *kind*
of thing that lives in that gap. (ToneSoul's own independent check is still only **structural** — it does not yet read
whether the evidence supports the claim; see the 0/2 miss below — so this is the *bet*, not a solved
problem.) The bet gets *more* relevant as trained-in alignment improves, not less.

## Honest measurements, including the misses

I built a small "honesty-auditor" program: characterization harnesses that measure what the existing
mechanisms structurally catch and **miss** on sanitized fixtures, and that publish the misses. All
`canonical:false`, regenerable, test-pinned
([scoreboard](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/status/honesty_scoreboard_latest.md)).
A few results, reported with the nulls:

- output gates are lexical-only: exact phrasings caught, but paraphrase / unicode / split-reassembly
  evade them (paraphrase robustness 0) — documented, not hidden;
- cross-time position-flip detection is **~null (0/3)** — parked, not built; I publish the zero
  rather than implying the feature exists;
- an "independent check" catches some structural issues but does **not** read whether the cited
  evidence actually supports the claim (0/2 on the cases that need reading evidence content).

The scoreboard deliberately refuses to compose these into an "is honest" score: **N green
characterizations stay N individual findings.**

## What I'm asking this community for

Not a star — **precise refutation**. The 2-minute version is at the top; if you want to go deeper, use the
[10-minute reviewer path](https://github.com/Fan1234-1/tonesoul52/blob/master/docs/EXTERNAL_REVIEW.md):

1. run the Space once on your own output (zero install);
2. `pip install tonesoul52`, then `ts validate draft.txt --json`;
3. optionally run the characterization tests: `pytest tests/ -k characterization` (note: some
   `--write-report` commands write generated files into your working tree).
4. file a sanitized issue via the GitHub issue chooser; do not paste private chats, API keys,
   personal data, business secrets, or production logs.

Then tell me:

- where is the analysis useful, useless, or itself overclaiming?
- where is a "structural" measurement secretly smuggling in a truth / intent / quality judgment?
- is the governance-vs-capability distinction real, or a vocabulary trick?

The full open call is
[`CALL_FOR_REVIEW.md`](https://github.com/Fan1234-1/tonesoul52/blob/master/CALL_FOR_REVIEW.md). The
one input this system cannot manufacture for itself is an independent eye — that is what I am asking
for.

- Code (canonical): https://github.com/Fan1234-1/tonesoul52
- Try it, no install: https://huggingface.co/spaces/Famwin/tonesoul-tryit
- The demo's source: https://github.com/Fan1234-1/tonesoul52/tree/master/apps/try

---

*AI-use disclosure:* this draft was prepared with AI collaborators and should be read line by line by
the human author before posting. *Evidence boundary:* public architecture, conceptual prototype, and
sanitized characterizations only — not a safety proof, not deployment assurance, not a consciousness
claim.
