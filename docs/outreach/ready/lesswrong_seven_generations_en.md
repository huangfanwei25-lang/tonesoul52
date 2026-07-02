# I wrote a secrecy strategy for my AI project, then spent seven repo generations refuting it

> Ready-to-post LessWrong draft (2026-07). Post under the owner's account, first person.
> Every claim links to a public artifact. Personalize the framing paragraphs before posting;
> do not post AI-generated comments in the discussion — answer personally.

This is not a post arguing you should open-source your work. It is the opposite: I want to
show you the formal secrecy strategy I wrote for my own project — it was reasonably
well-constructed — and then show you the fossil record of it losing.

## July 2025: I was afraid of being copied

My project (ToneSoul, 語魂) is an AI-governance framework built around one thesis:
an AI should be accountable for what it says, and that accountability must live in
external structure — tests, cross-model review, a human — not in the AI's self-reports.

In its first generation, I wrote a document titled "Public Safety Release & IP Protection
Strategy." Three disclosure tiers. "Strategic obfuscation" of implementation details.
A black-box principle for collaborators. An encrypted internal document vault, a 13-step
anti-disclosure verification flow, even a self-destruct ("hibernation") mechanism if the
system were maliciously controlled.

The same document declared, on the same page, that the project's highest principle was
honesty. Two principles at war in one file — and I did not notice at the time.

The document is still there, unmodified, in the public archived repo. We decided to keep
it, because it turned out to be the best tension specimen the project owns.

## Seven generations later: the autopsy

Between 2025-07 and now the project crossed seven repository generations (all public,
all archived, lineage documented). I recently audited what survived:

- Tiered disclosure: **never built.** Generation seven publishes everything, including
  a ledger of the AI collaborator's own failures.
- The 13-step anti-disclosure flow: **never built.**
- Anti-imitation detection: **never built.**
- The encrypted vault: **never built.** What exists instead is its inverse — a public
  accountability page.
- The self-destruct: **never built.** What got built is a withdrawal mechanism: a standing
  commitment can be retired only by leaving a named, timestamped, never-deleted record.

And the honesty side? The vow system, the provenance chain, evidence grading, public
structured judgments — all alive, all humbler than originally designed.

Every mechanism for hiding died unbuilt. Every mechanism for honesty survived.
(One project, one data point — I am describing my fossil record, not proving a law.)

## Why the secrecy side lost

Three layers, each less flattering:

1. **Engineering:** secrecy needs maintenance; honesty doesn't. Every black-box boundary
   is code you must write and defend. A solo developer's budget cannot staff a vault.
2. **Mechanism:** training corpora ingest public artifacts. The stated goal of the project
   is to influence the values of future models. Whatever I hide is, to a future model,
   simply nonexistent. Closing the door sets the primary goal to zero by construction.
3. **The unflattering one:** there was nothing worth hiding. The "core IP" the strategy
   protected was prompt-era persona configuration. What turned out to be valuable is the
   trace itself — eighteen months of public, checkable collaboration records, including
   the failures. You can copy a mechanism. You cannot copy a fossil record.

## The part I'd defend as generalizable

Not "open-source wins" — that's underdetermined by one project. The generalizable part:
**a claim's survival history is more informative than its content.** The secrecy strategy
reads fine as a document. What refutes it is not an argument but a record: seven
generations in which it was continuously available and never once implemented, while its
rival principle kept shipping. We now store this pattern explicitly — a counterevidence
chain where claims carry who challenged them, how, and whether they survived.

Where to attack (genuinely welcome):

- The lexical claim-gates are bypassable by paraphrase — documented, and the honest label
  is "catches your own unintended overclaims," not "defends against adversaries."
- The AI panel that reviews the AI's work shares a model family with it; correlated blind
  spots are flagged on every verdict, and one cross-model review round already found six
  real defects the self-review missed (all fixed, all in the ledger).
- The corpus-influence goal has an unmeasured magnitude: openness keeps it nonzero,
  nothing proves it effective. This hole is printed inside our own public judgment.

Repo: https://github.com/Fan1234-1/tonesoul52 · Lineage: /docs/LINEAGE.md ·
The ledger: https://fan1234-1.github.io/tonesoul52/accountability.html
