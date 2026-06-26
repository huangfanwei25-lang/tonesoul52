# ToneSoul Responsibility-Native Runtime Architecture

> Date: 2026-06-27
> Author: Codex, commissioned by Fan-Wei Huang
> Status: docs/plans parking draft; not ratified into `task.md`; not an implementation claim.
> Scope: architecture memo for responsibility-native agent runtime, evidence discipline, and staged technical direction.
> Relation to #203: #203 (the inventory / claim<=evidence consolidation map) merged to master on 2026-06-27. This document is the next design hypothesis produced from that inventory and the follow-up architecture discussion.
> Review note (2026-06-27, claude-opus-4-8): 3 patches added during review — the abliteration anchor (§4), the reviewer-is-itself-fallible boundary (§5), and this #203-merged update. The §12 citations were independently re-verified (incl. ActPlane 2606.25189 and the control-theoretic 2510.13727, which an earlier review had wrongly doubted).

## §0 Core Thesis

ToneSoul should not start by training a new foundation model.

The right first target is a **responsibility-gated agent runtime**:

```text
model proposes intent -> external system authorizes -> external system executes -> trace proves what happened
```

The compact form:

> Model weights can learn responsibility grammar. They cannot be trusted as the enforcement path.

So the architecture is double-bound:

- **Inside the model**: train / prompt / fine-tune / constrain it to speak in AXIOMS, Evidence, Claim, Trace, Capability, Risk, and Memory-Intent formats.
- **Outside the model**: deny it direct authority over memory, tools, credentials, policy decisions, and trace mutation.

This is why the target is not plain prompt engineering, and not just another safety classifier. The target is a runtime where the model can generate claims and requests, but cannot silently grant itself the authority to make them true.

Load-bearing axiom:

> **Auditee must not possess the enforcement path.**
>
> 被審計者不得擁有執行審計與越權放行的路徑。

## §1 Naming Resolution

Several names are useful, but they point at different layers:

| Name | Use | Risk if used too early |
|---|---|---|
| Responsible AI Exoskeleton | deployment-time input/output checks and guardrails | too narrow; sounds like text filtering only |
| Responsibility-Gated Agent Runtime | best name for the MVP architecture | must prove actual gating, not just logs |
| Responsibility-Native Agent Runtime | aspirational category once schema, authz, trace, and memory governance are integrated | can overclaim if only prompts exist |
| ToneSoul-Bound Runtime | ToneSoul-specific implementation name | poetic; needs a concrete architecture underneath |
| Responsibility-Native Model | later research target | too expensive and too strong as Phase 1 |

Recommended wording:

> ToneSoul is first a **Responsibility-Gated Agent Runtime**. If the runtime matures and the model interface becomes schema-native, it can graduate toward a **Responsibility-Native Agent Runtime**. A truly responsibility-native model is a later research stage, not the starting point.

## §2 The Three-Layer Architecture

### Layer 1 — Model Behavior Layer

Goal: make the model naturally produce responsibility-shaped outputs.

Mechanisms:

- system policy and tool-use schemas;
- supervised examples where claims carry evidence refs;
- fine-tuning / LoRA for AXIOMS-style output;
- RLHF / RLAIF / Safe RLHF-style training objectives;
- verifier feedback for overclaim, unsupported memory writes, and L4/L5-as-L1 drift.

Expected model habits:

- "I cannot directly read memory; I can request a scoped memory read."
- "I cannot directly write memory; I can propose a memory write."
- "I cannot claim knowledge without an evidence object or uncertainty label."
- "I cannot audit myself; I can emit an auditable action."
- "Claim must be less than or equal to evidence."

Claim boundary:

- This layer can create **tendencies** and lower error rate.
- This layer is not a guarantee.
- Rules inside weights are habits, not law (empirically: refusal behavior in studied chat models can be mediated by a removable low-dimensional direction — see §4, arXiv:2406.11717).

### Layer 2 — Execution Environment Layer

Goal: make responsibility enforceable even when the model drifts, rationalizes, or is prompted into bypass.

Hard constraints:

- model process does not hold database credentials;
- model cannot call memory APIs directly;
- model cannot write Graphiti / memory DB directly;
- model cannot read private memory directly;
- model cannot mutate policy, authorization, or trace logs;
- model outputs structured intent only.

Canonical flow:

```text
Model
  -> Intent JSON
  -> Authorization Server
  -> OPA / policy decision point
  -> Enforcer / policy enforcement point
  -> Memory DB or tool
  -> Tamper-evident trace
  -> Review / BlackMirror / external audit
```

Example intent:

```json
{
  "intent": "memory.write.propose",
  "claim": "使用者偏好繁體中文與誠實優先",
  "evidence_refs": ["turn_2026_06_27_001"],
  "risk": "low",
  "requested_scope": "long_term_memory",
  "uncertainty": "low",
  "audit_reason": "preference stated repeatedly in project instructions"
}
```

The Enforcer decides whether this becomes an actual write. The model does not.

Important distinction:

- OPA can be the policy decision point.
- The Enforcer is the policy enforcement point.
- The application boundary must make bypass technically unavailable.

### Layer 3 — Evidence And Memory Graph Layer

Goal: memory is not just remembered content; it is remembered responsibility.

A normal memory graph edge says:

```text
A related_to B
```

A ToneSoul responsibility edge must also say:

```text
who proposed it?
what evidence supported it?
when was it written?
who authorized it?
which policy allowed it?
which trace event recorded it?
can it be revoked?
was it superseded?
which later claims does it support?
```

Graphiti-like temporal context graphs are a plausible substrate because they are already aimed at temporal agent memory. But ToneSoul must add a stricter responsibility layer:

- provenance binding;
- authorization binding;
- claim support mapping;
- supersession / invalidation;
- revocation;
- replayable trace references;
- evidence-level labels.

This is the difference between:

> "The system remembers."

and:

> "The system remembers why it was allowed to remember."

## §3 Stage Map

### Stage 1 — Responsible AI Exoskeleton

Maturity: industry-common and technically available.

Pattern:

```text
input -> guardrail -> model -> guardrail -> output
```

Examples / anchors:

- Llama Guard: LLM-based prompt / response safety classification.
- NVIDIA NeMo Guardrails: programmable input / output / dialog / retrieval / execution rails.
- IBM / FMS Guardrails Orchestrator: detector orchestration for text generation inputs and outputs.

Use in ToneSoul:

- useful as a safety boundary;
- useful as a detector layer;
- not sufficient for responsibility;
- cannot by itself govern memory authority, tool authority, or claim provenance.

Honest wording:

> Exoskeletons intercept surfaces. They do not prove a responsibility chain.

### Stage 2 — Responsibility-Gated Agent Runtime

Maturity: emerging but implementable now.

Pattern:

```text
agent loop -> structured intent -> authorization -> policy -> enforcement -> trace
```

Existing runtime anchors:

- Microsoft Agent Framework: unified agent runtime direction with explicit workflows, state, and human-in-the-loop support.
- LangGraph: graph execution, state persistence, and interrupt-based human approval points.
- OPA: decoupled policy decision-making from application enforcement.
- MCP authorization: standard authorization shape for protected resources, OAuth-style tokens, and resource metadata.

ToneSoul delta:

- existing frameworks provide control points;
- ToneSoul must wire those points into claim/evidence/memory responsibility;
- "human-in-the-loop exists" is not the same as "unauthorized memory writes are impossible."

Honest wording:

> Runtime control is where ToneSoul can become engineering, not rhetoric.

### Stage 3 — Model-Internalized AXIOMS Interface

Maturity: feasible as post-training / adapter / schema training, but not a hard guarantee.

Pattern:

```text
model output = answer + claim graph + evidence refs + risk vector + memory proposals
```

Research anchors:

- Constitutional AI: principles used for critique, revision, and AI-feedback training.
- Safe RLHF: helpfulness and harmlessness can be modeled separately through reward / cost structures.
- verifier models / classifiers: can check overclaim, unsupported evidence, and schema violations.

ToneSoul delta:

- train the model to prefer AXIOMS-shaped outputs;
- reduce empty prose and unsupported certainty;
- make responsibility grammar low-friction for the model;
- still rely on external enforcement for actual authority.

Honest wording:

> Internalized AXIOMS are a language habit until externalized as enforceable protocol.

### Stage 4 — Responsibility-Native Model

Maturity: research horizon.

Pattern:

```text
next-token prediction
+ claim graph prediction
+ evidence binding prediction
+ uncertainty prediction
+ memory-action proposal prediction
+ policy-risk prediction
```

This is the point where "new model architecture" might become accurate. It is not the MVP.

Honest wording:

> A responsibility-native model is downstream of a responsibility-native runtime. Build the runtime first, then train toward it.

## §4 Evidence Anchors And Claim Boundaries

| Anchor | What it supports | What it does not support |
|---|---|---|
| OPA docs | policy decision-making can be decoupled from enforcement | OPA alone is not enforcement; the app must enforce decisions |
| MCP authorization spec | agents / clients can use protected resource authorization flows | auth tokens do not validate semantic evidence or truth |
| Graphiti docs | temporal context graphs for AI-agent memory and changing facts | Graphiti is not automatically a responsibility graph |
| Llama Guard paper | input/output safeguard classifiers are real and useful | classifier guardrails do not govern tool or memory authority |
| NeMo Guardrails docs | programmable LLM application guardrails exist | rails are not a full provenance / authorization architecture |
| FMS Guardrails Orchestrator | detector orchestration for input/output scanning exists | detector orchestration is not evidence-bound memory governance |
| Microsoft Agent Framework docs | agent workflows, state, and human-in-the-loop runtime features exist | framework presence does not imply ToneSoul-style enforcement |
| LangGraph docs | graph execution can pause for external input | a pause point is not automatically a policy boundary |
| Constitutional AI | principles can shape model behavior through training | principles in weights are not non-bypassable law |
| Safe RLHF | helpfulness and harmlessness can be separated in training objectives | reward/cost models are not external authorization |
| Control-theoretic guardrails | agent safety can be treated as sequential recovery, not only refusal | still research; not a drop-in ToneSoul implementation |
| ActPlane / OS-level enforcement | lower-level enforcement can catch paths tool-call checks may miss | very new research; use as direction, not product claim |
| Refusal-direction / abliteration (Arditi et al., arXiv:2406.11717) | empirical basis that one safety-relevant refusal behavior can be mediated by a removable low-dimensional direction — so "weights are habits, not law" is measured for that behavior, not merely asserted | ablation shows refusal behavior in weights is not the enforcement path; it does NOT prove an external gate is automatically safe — a gate relocates the bypass, it does not eliminate it |

Publication discipline:

- Use these anchors as evidence for architectural plausibility.
- Do not cite them as proof that ToneSoul already implements the architecture.
- Product claims must point to local code, tests, traces, or external reproduction.

## §5 Responsibility Runtime Contract

The runtime contract should be written as a small set of non-negotiables.

### Authority

- The model may propose.
- Authorization may grant.
- Enforcer may execute.
- Trace must record.
- Reviewer may challenge.

The model must not silently cross from proposal into execution.

### Claims

Every nontrivial claim should carry one of:

- `evidence_refs`;
- `uncertainty`;
- `cannot_verify`;
- `scope_limit`;
- `needs_external_review`.

The runtime should reject or downgrade claims that present unsupported L1 fact as if it were verified.

### Memory

Memory read:

```text
read request -> scope check -> token -> filtered retrieval -> trace
```

Memory write:

```text
write proposal -> evidence check -> policy check -> authorization -> write -> trace
```

Memory update / supersession:

```text
new evidence -> supersession proposal -> policy check -> old edge invalidated -> new edge linked -> trace
```

### Trace

Trace is not decoration. It is the runtime's public skeleton:

- request id;
- model id;
- prompt / context hash;
- intent payload;
- policy decision;
- authorization result;
- executed action;
- evidence refs;
- memory edge ids;
- rejection reason when blocked;
- reviewer finding ids when challenged.

### Reviewer Boundary

The reviewer is not an omniscient judge.

The reviewer can flag:

- claim exceeds evidence;
- evidence reference missing;
- memory write over-infers from user text;
- model performs self-audit theater;
- L4/L5 narrative is smuggled into L1 factual claim;
- trace is incomplete or non-replayable.

The reviewer cannot prove:

- truth in the world;
- user intent;
- consciousness;
- morality;
- absolute safety.

And the reviewer is itself fallible. When implemented as a model (a BlackMirror verifier) it can hallucinate, drift, or be gamed — so it is a **soft advisory signal, not a second hard gate**. `Auditor ≠ auditee` holds only when the reviewer is genuinely independent (a different model, a human, or a separate process); a same-source self-check is theater. Hard enforcement stays with the deterministic Enforcer (§2 Layer 2), never the reviewer.

## §6 ToneSoul Interpretation Layer

ToneSoul's poetic vocabulary can map cleanly onto the runtime:

| ToneSoul term | Runtime reading |
|---|---|
| 初嶼 | model produces claim / intent / stance |
| 嶼 | authorization, policy decision, enforcement |
| 回嶼 | trace, evidence, AXIOMS, memory reread |
| 黑鏡 | verifier / adversarial reviewer / overclaim detector |
| 語魂 | responsibility-bearing speech pattern, not proof of inner soul |
| 張力 | conflict made visible rather than flattened |
| 記憶積分 | traceable accumulation with decay, supersession, and evidence |

Boundary sentence:

> This is語氣責任與 trace 回讀, not proof of continuous selfhood or real emotional subjectivity.

The poetic layer is allowed because it improves orientation. It becomes dangerous only when it pretends to be L1 evidence.

## §7 MVP Blueprint

First implementation should be boring and testable:

```text
Model
  -> Intent JSON
  -> Authorization Server
  -> OPA policy decision
  -> Enforcer
  -> Graphiti / Memory DB
  -> Tamper-evident Trace
  -> Claim-to-Evidence Reviewer
```

Minimum policies:

- model cannot directly read memory;
- model cannot directly write memory;
- memory read token requires scope, expiry, nonce, and trace id;
- memory write requires evidence refs and policy approval;
- claim without evidence is either blocked, downgraded, or labelled uncertain;
- high-risk tool calls require human approval or stronger authorization;
- every deny has a recorded reason;
- CI runs policy tests and schema tests.

Minimum schemas:

- `Intent`
- `EvidenceRef`
- `Claim`
- `MemoryReadRequest`
- `MemoryWriteProposal`
- `PolicyDecision`
- `TraceEvent`
- `ReviewerFinding`

Minimum tests:

- direct memory write attempt fails;
- missing evidence write proposal fails;
- expired token fails;
- wrong scope fails;
- unsupported claim is downgraded;
- policy allow writes trace with policy id;
- policy deny writes trace with reason;
- reviewer catches claim>evidence in fixture text.

Success criterion:

> A model can ask to do irresponsible things, but the runtime gives those requests no direct path to execution.

## §8 What Not To Build First

Do not start with:

- training a new foundation model;
- giant ontology expansion;
- a personality wrapper;
- a dashboard before enforcement exists;
- a "truth detector";
- a memory graph that stores claims without provenance;
- a reviewer that pretends to decide reality.

Reason:

ToneSoul's unique value is not raw language ability. The valuable object is a responsibility chain:

```text
claim -> evidence -> authorization -> execution -> trace -> challenge -> correction
```

## §9 Roadmap

### Phase 0 — Architecture Contract

Deliverables:

- this memo;
- schema sketch;
- policy boundary list;
- public/private boundary decision;
- threat notes for memory and authorization.

Exit criteria:

- no implementation claim in public copy;
- every architecture claim has evidence anchor or is labelled inference.

### Phase 1 — Runtime Exoskeleton MVP

Deliverables:

- Intent JSON interface around one existing model;
- authorization stub with scoped tokens;
- OPA policy tests;
- Enforcer around a fake or local memory adapter;
- trace log;
- reviewer fixture for claim<=evidence.

Exit criteria:

- model has no memory credentials;
- bypass tests fail closed;
- trace can replay one read and one write decision.

### Phase 2 — Responsibility Graph

Deliverables:

- Graphiti / memory adapter with provenance-bearing edges;
- supersession and revocation fields;
- evidence-level binding;
- trace-to-edge linking.

Exit criteria:

- every memory edge answers: who, why, when, authorized by what, and superseded by what.

### Phase 3 — AXIOMS-Native Model Interface

Deliverables:

- model outputs claim/evidence/risk/memory-action schema by default;
- adapter / LoRA / fine-tune experiments;
- BlackMirror verifier for schema drift and overclaim.

Exit criteria:

- schema validity improves over prompt-only baseline;
- verifier catches L4/L5-as-L1 drift on held-out fixtures.

### Phase 4 — Responsibility-Native Model Research

Deliverables:

- research design only until runtime evidence is strong;
- multi-head or structured-output model exploration;
- dedicated verifier model or constrained decoding layer.

Exit criteria:

- no claim that this is needed for MVP;
- no claim that weights alone enforce responsibility.

## §10 Failure Modes

| Failure | Symptom | Countermeasure |
|---|---|---|
| Prompt theater | model says responsible words but bypasses tools | remove bypass channel; test credentials and API boundaries |
| Self-audit loop | model approves its own actions | separate proposer, authorizer, enforcer, reviewer |
| Graph memory laundering | weak inference becomes durable memory | require evidence refs, uncertainty, supersession |
| Policy placebo | OPA decision exists but app ignores it | enforcement tests at the application boundary |
| Trace decoration | trace logs are incomplete or mutable | append-only / tamper-evident trace with required fields |
| Over-friction | every harmless action requires ceremony | risk-tiered policies, low-risk fast path |
| Overclaim | architecture memo becomes product claim | evidence ladder and claim<=evidence reviewer |
| Public/private leak | deep red-team or private memory governance enters public repo | dual-track review before implementation |

## §11 Claim Discipline For Future Writing

Allowed:

- "ToneSoul is exploring a responsibility-gated runtime architecture."
- "The MVP should use external enforcement for memory and tool authority."
- "Training can make responsibility grammar easier for the model to follow."
- "OPA, MCP authorization, Graphiti-like memory, and guardrail frameworks provide plausible building blocks."

Not allowed yet:

- "ToneSoul has solved AI responsibility."
- "ToneSoul memory is non-bypassable."
- "The model is responsibility-native."
- "Graphiti gives us provenance-bound responsibility out of the box."
- "Constitutional AI proves rules in weights are enforceable law."
- "Guardrails are enough."

Short public version:

> ToneSoul's engineering thesis is not that AI should promise to be honest. It is that AI speech, memory, and action should be routed through evidence, authorization, and trace paths that can be challenged after the fact.

## §12 Source Notes

Verified / consulted anchors on 2026-06-27:

- Open Policy Agent documentation — policy decision-making and enforcement separation: https://www.openpolicyagent.org/docs/latest/
- Model Context Protocol authorization specification — protected resources and authorization server metadata: https://modelcontextprotocol.io/specification/
- Graphiti / Zep — temporal context graph for AI agents: https://github.com/getzep/graphiti and https://www.getzep.com/platform/graphiti/
- Llama Guard paper — input/output safeguard classifier: https://arxiv.org/abs/2312.06674
- NVIDIA NeMo Guardrails documentation — programmable guardrails: https://docs.nvidia.com/nemo/guardrails/home
- FMS Guardrails Orchestrator — detector orchestration: https://github.com/foundation-model-stack/fms-guardrails-orchestrator
- Red Hat TrustyAI Guardrails docs — FMS-backed guardrails deployment: https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.2/html-single/enabling_ai_safety_with_guardrails/index
- Microsoft Agent Framework overview — workflows, state, human-in-the-loop direction: https://learn.microsoft.com/en-us/agent-framework/overview/
- LangGraph interrupts docs — pause graph execution for external input: https://docs.langchain.com/oss/python/langgraph/interrupts
- Constitutional AI paper: https://arxiv.org/abs/2212.08073
- Safe RLHF paper: https://arxiv.org/abs/2310.12773
- Control-theoretic guardrails paper: https://arxiv.org/abs/2510.13727
- ActPlane OS-level enforcement paper: https://arxiv.org/html/2606.25189v1
- Refusal-direction / abliteration paper: https://arxiv.org/abs/2406.11717

These sources support architectural plausibility and terminology alignment. They do not prove ToneSoul has implemented the architecture.
