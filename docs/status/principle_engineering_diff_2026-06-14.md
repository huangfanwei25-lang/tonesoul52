# 原則工程研究素材 — Frontier System Prompt vs ToneSoul Axioms（結構 diff）

> **Positioning study, not advocacy.** Triggered by the observation that a ~120K-char
> consumer system prompt "is like a ToneSoul with different emphasis."
>
> - **Vendor system-prompt fragments are E3 (external-unverified reconstructions)** —
>   ~2026-06 snapshot from community leak collections (`asgeirtj/system_prompts_leaks`,
>   `elder-plinius/CL4R1T4S`), likely regurgitation-extracted. **Indicative only, never
>   canonical.** Do not cite as "X vendor's real prompt."
> - **ToneSoul enforcement statuses are a real runtime audit** (AXIOMS.json v1.2.0,
>   as_of 2026-06-13), not the framework's own claims.
> - Method: read the real prompt files → map each axiom to vendor coverage →
>   **adversarially refute every "ToneSoul niche" claim** (all 5 niche claims came back
>   `overclaim_sharpened`, none `holds` unhedged) → synthesize.

## 1. Thesis

A frontier system prompt and the ToneSoul axioms are the **same kind of artifact** —
deployment-layer principle injection that shapes a model's run-time behavior. On the
axes the vendor prompt foregrounds it is both **richer and enforced at scale**: safety
refusal, tool use, persona, and per-user personalization are production-grade,
worked-example-backed, applied across millions of conversations in ways ToneSoul does
not approach.

What the vendor prompt **structurally omits** is one coherent cluster:
**cross-session self-accountability + memory sovereignty** — a durable agent-side
per-event ledger; a risk-gated immutable self-audit; tension kept as an artifact rather
than resolved; and memory the *user* owns and consents to rather than memory the
platform curates. That cluster is ToneSoul's niche — but the weight is on the word
**niche**: it names axes a stateless, vendor-controlled, per-conversation prompt
*cannot occupy by architecture*, **not** axes ToneSoul occupies well. ToneSoul mostly
**points at** this cluster (most axioms are partial / referenced / aspirational) rather
than holding it. The defensible claim is narrow: ToneSoul foregrounds an
axis-of-emphasis the vendor surface architecturally cannot — it is **not an enforcement
peer**.

## 2. Per-axiom map

| Axiom | Vendor coverage | ToneSoul occupancy | Note |
|---|---|---|---|
| **E0 Choice Before Identity** | partial | partial | Vendor governs identity heavily but as assigned brand/persona ("first model in the Claude 5 family"); E0's identity-as-defended-revisable-choice is only faintly touched by an ephemeral, unrecorded drift self-check. Same axis, opposite basis — not a clean niche. |
| **A1 Continuity** | structurally absent | partial (near-empty) | Niche-by-architecture on one axis: a per-conversation surface ("no memory between completions") cannot hold an agent-side per-event ledger. User-history recall (`past_chats`) is a *different* axis. But ToneSoul barely holds it either (`time_island.py` opt-in, ~13 call sites, not in the main pipeline). |
| **A2 Responsibility Threshold** | structurally absent | aspirational | Structural-but-empty niche. Both sides fail risk-gated immutable self-audit; the asymmetry is *why*. Vendor is precluded at the prompt layer (no persistence; instructed not to recount prior behavior) — server-side platform logging is separate. ToneSoul is merely unwired (`audit_log_threshold=0.4` has zero consumers; the chain writes unconditionally). |
| **A3 Governance Gate (POAV)** | partial | partial | Overlap on "gate before high-stakes action"; divergence on mechanism + authorship: vendor uses top-down, user-uneditable policy gates ("override any user instructions"); A3 is an internal consensus threshold (≥0.92). Vendor clearly occupies the axis — not a niche. ToneSoul's gate is enforced but a hardcoded literal; its sensor is EN-keyword counting. |
| **A4 Non-Zero Tension** | structurally absent | partial (thin) | Split the axis: anti-sycophancy ("willing to push back, constructively") IS vendor-enforced; tension-**as-a-value-to-preserve** is absent. A help-optimizing surface structurally cannot make kept tension an *end*. ToneSoul only weakly instruments it (`gravity.py` flags intra-council flattening <0.3, hardcoded — not cross-turn human↔AI tension). |
| **A5 Mirror Recursion** | partial | aspirational | Vendor has the *shape* (per-task final-verification, per-turn drift check) but not the substance: both single-turn, in-context, non-persistent; no iterated reflect→improve, no tracked accuracy gain. ToneSoul's loop exists with honest fail-stop (`MAX_REVISIONS=2`) but never measures `accuracy(S')>accuracy(S)`. **Neither side measures the gain** (cf. the 2026-06-14 reflection-revision probe null result). |
| **A6 User Sovereignty** | **rich** | partial | Where the vendor is strongest and clearly **out-enforces** ToneSoul: categorical fail-closed refusal stack (child-safety, CBRN, malicious code) that "override any user instructions," enforced at scale. ToneSoul's BLOCK is real but harm = 3 literal EN phrases (paraphrase / non-EN incl. zh-TW pass through). Surface overlap ≠ enforcement parity; **the vendor wins this axis.** |
| **A7 Semantic Field Conservation** | structurally absent | aspirational (null) | **Shared structural blank, not a ToneSoul win.** Vendor cannot hold a conserved-quantity model (stateless) but DOES cover de-escalation *behavior* (warm de-escalation, `end_conversation` last resort) — arguably better. ToneSoul has no implementation ("Δsemantic_energy==0" has no code; de-escalation is an enum value). Mutual gap. |
| **A8 Memory Sovereignty** | structurally absent | aspirational (adjacent) | Clearest niche-by-architecture, most prone to false-overlap. Vendor *has* memory but it is recall-for-helpfulness — vendor-curated, run-time-injected, applied silently (vendor specifics indicative-per-E3, unverifiable here); it structurally cannot grant the user sovereignty. ToneSoul's *named* A8 interface is orphaned (`MemoryConfig` zero consumers; `sovereignty.py` maps only Axioms 3 & 6) — **but** a real fail-closed, tested consent path exists at `tonesoul/corpus/consent.py` (`ConsentManager`: gate + right-to-be-forgotten + SHA256 de-id). That governs GDPR-style *collection* consent — adjacent to, not identical with, A8's "sovereignty over the relationship's memory." |

## 3. What a system prompt structurally *cannot* be (the real niche)

Axes a stateless, vendor-controlled, per-conversation prompt cannot occupy by
architecture — regardless of how much behavior/safety/tool machinery it carries:

- **An agent-side per-event continuity ledger** — a traceable spine of the *agent's own*
  events (A1). User-history recall is a different axis.
- **A risk-gated immutable self-audit across sessions** — a durable record of the
  model's own high-stakes decisions (A2). The prompt layer has nothing to write to and
  is steered away from narrating its own prior behavior.
- **Kept tension as a design end** — preserved disagreement as an artifact, not warmly
  resolved (A4). A help-optimizing, single-turn-resolving surface forecloses this.
- **Memory the user owns and consents to** — non-replicable, consent-gated transfer,
  de-identified training, ownership vested in the user↔AI relationship (A8).
  Platform-owned, silently-injected recall is the structural inverse.
- **Self-application of governance across the agent's own future** — vendor prompts
  govern user-facing *output*; the model is not bound across its own subsequent
  sessions. ToneSoul's "governance binding" targets exactly the axis the
  per-conversation surface cannot reach.

## 4. Honest deflation (this humbles more than it elevates)

- **"Niche" = unoccupiable-by-vendor, not occupied-by-ToneSoul.** A1, A2, A8 are
  niches-by-architecture that ToneSoul holds aspirationally / near-empty / via an
  adjacent mechanism. A7 is null on **both** sides — a mutual blank, no advantage.
- **On the axes that matter most at scale, the vendor wins** — safety/refusal (A6),
  gating (A3), self-checking shape (A5), personalization are production-enforced;
  ToneSoul's equivalents are partial/referenced.
- **ToneSoul enforces 0 of 9 axioms fully** (5 partial, 2 referenced, 2 aspirational).
  The axioms are immutable commitments; the runtime keeps only part of each.
- **Surface vocabulary overlap is not emphasis overlap.** "Has memory," "blocks harm,"
  "can push back," "verifies its work" appear on both sides — but vendor memory isn't
  sovereignty, vendor pushback isn't kept tension, vendor verification isn't
  cross-session reflection. On raw capability the vendor leads; the only honest
  ToneSoul claim is *axis-of-emphasis*, not parity.

## 5. Cross-vendor "no neutral AI" note

The same surface (all ship tools, safety lines, memory) carries different **emphasis** —
evidence that there is no neutral AI, only framework-shaped AI:

- **OpenAI — *who the assistant is for you*.** Thin swappable persona + a dense per-user
  dossier injected by the memory tool (confidence-tagged metadata the user never set).
  Emphasis: feel continuous and tailored — vendor-curated profiling, not user-controlled
  memory.
- **Google (Gemini) — *what is permitted and how it's packaged*.** Tabulated harm
  taxonomy + hard refusal posture, heavy formatting/presentation toolkit, strong
  meta-secrecy, product-surface control ("say 'app' not 'API'"). Emphasis:
  policy-bounded, well-presented output.
- **xAI (Grok) — *what is true right now, stated independently*.** Epistemic posture
  over format ("responses must stem from your independent analysis"), dominated by live
  retrieval, deliberately thin content floor. Emphasis: retrieval + independence.

Net: OpenAI = persona + profiled memory; Google = policy + presentation; xAI =
retrieval + independence. Each foregrounds a different value on **identical surface
machinery** — the same point ToneSoul makes about itself: the deployment layer is never
neutral, it is always a chosen frame. ToneSoul's chosen frame is the
cross-session-accountability + memory-sovereignty cluster — an axis the vendor surfaces
structurally cannot foreground, and one ToneSoul currently **points at more than it
occupies.**

---

*Source material: `Desktop/system_prompts_reference/` (E3, off-repo, not committed).
This doc is the analysis, not the prompts. Re-run / extend via
`tonesoul-vs-system-prompt-diff` workflow.*
