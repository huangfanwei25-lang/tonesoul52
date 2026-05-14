# Independent Verifier — Spec v1

> Status: Phase A (spec) + Phase B (scaffold with Mock) — adopted 2026-05-14
> Authority: defines Council vs Verifier role boundary; Phase D actual LLM call deferred to API-budget return
> Origin: Kuan-Yu Hsieh framework (Implementer ≠ Verifier principle, ECC v2 Homunculus / Hermes Curator pattern)
> Related: `docs/research/integration_with_kuan_yu_hsieh_frameworks_2026-05-14.md` §3.3 + Gap C

---

## 0 ─ 為什麼存在

ToneSoul Council 目前是 **5 perspectives, same LLM, same session** — Guardian / Analyst / Critic / Advocate / Axiomatic 跑 multi-perspective synthesis。

朋友 Kuan-Yu Hsieh framework §3.3 explicit 警告：這個 pattern 是「**self-evaluation**」、failure mode known（ECC v2 對應分析）。朋友 framework 用 **Implementer ≠ Verifier** 原則、Verifier 必須是**不同 LLM / 不同 session / 不同 prompt cache**。

整合 doc §3.3 已 articulate ToneSoul 跟朋友 framework 對 Council 角色 framing 不同：

| Framing | 視角 |
|---|---|
| 朋友視角 | Council = 多 perspective 的 self-evaluation = fail mode |
| ToneSoul 視角 | Council = **pre-output synthesis**（多 perspective form one verdict）= 不是 evaluator |

**兩者都對**——但**前提是 ToneSoul 必須 explicit 把 Council 定位成 synthesis、另外加 independent verifier 來補 self-evaluation 風險**。Council 跟 verifier **不該 conflate**。

本 spec 定義那個「independent verifier」的 contract、scaffold、phasing。

---

## 1 ─ Council vs Verifier 角色區分

### 1.1 Role table

| 維度 | Council（既有）| Independent Verifier（本 spec）|
|---|---|---|
| **目的** | Pre-output synthesis | Post-verdict audit |
| **時序** | Verdict generation 之前（input → verdict）| Verdict generation 之後（verdict → report）|
| **input** | Draft + context | CouncilVerdict + context |
| **output** | CouncilVerdict | VerifierReport |
| **執行 substrate** | Same LLM as Implementer、same session | **Different LLM / different session / different prompt cache** |
| **如何分離** | Logical（多 perspective、單 LLM call）| Structural（不同 substrate stack instance）|
| **可否 override** | Council verdict 是最終 synthesis（Phase 864c trace 記決策路徑）| Verifier 預設**只 flag、不 override**（Phase A）；override 模式 gated（Phase E）|
| **fail-stop** | Guardian OBJECT + confidence > 0.7 → BLOCK | Verifier 自身錯誤不該 block 主流程（fail-open by default）|

### 1.2 為什麼這條 separation 結構性重要

per `docs/philosophy/substrate_stack_theory_2026-05-14.md`：ToneSoul Council 是 Layer 5 (prompt-level)、跟 Implementer 同 substrate stack instance。Verifier 該住在**不同 Layer 4 tool wrapper instance**（不同 LLM call、cache 隔離）。

對應 substrate theory §6.1：
> 真正的 hard enforcement 在 Layer 4 — Claude Code 工具集可以 wrap、refuse stale data、enforce checklist。這是 ToneSoul thesis 在 tool layer 的延伸。

Verifier 是 Layer 4 enforcement 在 verdict-audit 軸的 instance。Council 自己無法 audit 自己（同 substrate）、需要外加 Layer 4 機制。

---

## 2 ─ Protocol contract

### 2.1 Input

```python
VerifierInput = {
    "verdict": CouncilVerdict,     # the verdict to audit
    "context": dict,                # optional: draft text, request metadata
    "config": VerifierConfig,       # cost budget, timeout, etc.
}
```

### 2.2 Output

```python
@dataclass
class VerifierReport:
    status: VerifierStatus              # pass | flag | override
    reasoning: str                       # why this status
    flagged_perspectives: list[str]      # which Council voices look weak (optional)
    cost_estimate: dict                  # tokens / time / dollar (when LLM call)
    verifier_id: str                     # which verifier impl ran
    audited_at: str                      # UTC ISO8601
    fail_open_reason: str | None         # if verifier itself failed, why
```

### 2.3 VerifierStatus enum

```python
class VerifierStatus(Enum):
    PASS = "pass"           # verdict looks coherent
    FLAG = "flag"           # verdict looks suspect, but not blocking
    OVERRIDE = "override"   # verdict should be replaced (Phase E gated)
    SKIPPED = "skipped"     # verifier didn't run (disabled / over-budget)
    ERROR = "error"         # verifier itself crashed (fail-open)
```

### 2.4 Timing + invocation rules

- **When**：only after CouncilVerdict is fully generated (post-`generate_verdict()`)
- **Synchronous default**：blocks until report or timeout
- **Async option（Phase D+）**：background submission, report attached later via callback
- **Timeout default**：5 seconds; verifier exceeding → SKIPPED status with reason
- **Cost cap default**：1 LLM call per verdict in Phase D; configurable

### 2.5 Fail-open semantics

**Verifier failure must not block the main verdict flow.** If verifier crashes / times out / over-budget:
- Report status = `SKIPPED` or `ERROR`
- `fail_open_reason` populated
- CouncilVerdict proceeds unchanged
- Log + telemetry for follow-up

理由：Verifier 是 audit layer、不是 gating layer（Phase A）。Gating semantics 留到 Phase E 跟 governance 一起決定。

---

## 3 ─ Failure modes

| Failure mode | 發生時的處理 |
|---|---|
| Verifier LLM call timeout | SKIPPED, fail_open_reason="timeout after Ns" |
| Verifier LLM call rate-limited | SKIPPED, fail_open_reason="rate-limit at provider" |
| Verifier LLM call returned malformed JSON | ERROR, fail_open_reason="parse failure: <excerpt>" |
| Verifier LLM call exceeded cost budget | SKIPPED, fail_open_reason="cost budget exceeded: $X.YY" |
| Verifier flagged but Council had Guardian-OBJECT-block already | FLAG attached but no action (Council already blocked) |
| Verifier flagged AND requested override | OVERRIDE attempt **gated on Phase E config**; defaults to FLAG-only in Phase A-D |
| Concurrent Verifier instances on same verdict | First report wins; later ones logged + discarded |

---

## 4 ─ Override semantics（Phase E gated）

Phase A-D：Verifier **never overrides**, only flags. Council verdict stands.

Phase E (deferred)：introduce `VerifierConfig.override_enabled: bool`. When True + status == OVERRIDE:
- Verdict modified: verdict.verdict → BLOCK
- DeliberationTrace.deciding_factors appended with verifier reason (mirror strategy_mirror enforce-mode pattern, per Phase 864c)
- Strategic crystal auto-generated recording the override event
- Requires Fan-Wei explicit `OVERRIDE_ENABLED=true` env flag to activate

**Reason for staging**：override = giving non-Council substrate veto power over Council synthesis. This is governance-significant. Should NOT default-on. Same precedent as strategy_mirror enforce mode (scan-first, enforce-second, multi-week gating window).

---

## 5 ─ Cost model

### Phase A-C (no LLM)
- Mock verifier: zero cost (always returns PASS)
- Used for: unit tests, integration smoke, contract validation

### Phase D (Haiku LLM call)
- Estimated per call: ~200-500 input tokens (verdict + context summary) + ~100-300 output tokens
- At Anthropic Haiku 4.5 pricing: ~$0.001-0.003 per verdict
- Recommended budget: hard cap at $0.01/verdict default; configurable
- Telemetry: cumulative spend tracked in `memory/runtime/verifier_cost.jsonl` (gitignored)

### Phase D constraint (current)
**2026-05 起 Fan-Wei API budget 可能 0**（per `project_budget_constraint_2026-04` memory）. Phase D code lands disabled-by-default; runtime activation gated on budget return + Fan-Wei explicit opt-in. Scaffold + tests + mock can ship now without budget cost.

---

## 6 ─ Phasing

| Phase | 內容 | Cost | Reversibility |
|---|---|---|---|
| **A — spec** (this PR) | This doc | None | trivially reversible (revert PR) |
| **B — scaffold** (this PR) | `IndependentVerifier` abstract class + `MockIndependentVerifier` + `VerifierReport` dataclass + unit tests | None | reversible (delete module) |
| C — integration | Hook into `pre_output_council.py` with optional flag (default OFF). Verifier attaches report to verdict via new optional field | None (still mock) | reversible (remove flag) |
| **D — Haiku impl** | `HaikuVerifier(IndependentVerifier)` with Anthropic SDK call, timeout, retry, cost tracking | API budget | deferred until budget returns |
| E — opt-in trial + override | CLI flag + telemetry + override mode (Fan-Wei explicit) | API budget + governance review | gated |

Phase A+B ship together — they form one complete contract (spec + minimal impl) that downstream phases can build on.

---

## 7 ─ Open questions

1. **Verifier 應該看 Council 的 internal vote breakdown 還是只看 final verdict?** Phase A 預設兩者都看（CouncilVerdict 完整 dataclass）。但「只看 final verdict」更強 separation（Verifier 不知道 Guardian 投什麼 → 更接近 cold-eye reviewer）。trade-off：weak separation vs less context。
2. **多 Verifier instance（Haiku + Gemini）並聯時、reports 該怎麼 reconcile?** Phase A scope 不處理；Phase D 預設只一個 verifier instance；Phase E+ 才考慮 ensemble。
3. **Verifier 自身的 self-bias 怎麼處理?** Haiku 自己也有 RLHF bias、Verifier vs Council 同源（Anthropic family）的話 separation 仍 partial。Phase D 仍 valuable（不同 model / different cache）、但 acknowledge limitation。
4. **Verifier 報告是否該成為 public-facing audit trail?** 若是、需要 cryptographic chain（Aegis-style）。Phase A 預設報告 local-only、Phase E+ 才考慮。

這些都該 emerge through use、本 spec 不 freeze。

---

## 8 ─ References

- 朋友 framework Article 1（〈超有紀律的記憶管理〉）第 5 條 "Verifier 分離"
- 整合分析：`docs/research/integration_with_kuan_yu_hsieh_frameworks_2026-05-14.md` §1.4 第 5 條 + Gap C + §3.3
- Substrate stack theory：`docs/philosophy/substrate_stack_theory_2026-05-14.md` §6.1（Layer 4 enforcement）+ §3.2
- Direction doc Tier 2 第 1 條：`docs/architecture/direction_going_forward_2026-05-14.md` §3
- Phase 864c trace pattern（reference for override 設計）：`tonesoul/council/deliberation_trace.py` + `tonesoul/council/pre_output_council.py` strategy_mirror enforce-mode handling
- Strategic Crystal Format（reference for override event recording）：`docs/memory/STRATEGIC_CRYSTAL_FORMAT.md`

---

## 9 ─ Honest scope on this spec

- **Phase A+B 是 contract、不是 production system** — 真實 verification 在 Phase D
- **Mock impl 永遠 PASS** — 不代表 Council verdict 都 OK、只代表 contract works
- **separation 強度**：Phase D Haiku 是 Anthropic family、跟 Claude 同 RLHF lineage、separation 是 partial 不是 absolute
- **本 spec 借朋友 framework 的 Implementer/Verifier 原則** — 但 ToneSoul 對 Council 角色 framing 跟朋友不同（synthesis vs evaluator）、本 spec 把兩個 framing 合起來
- **Cost model 估算基於 2026-05 Anthropic pricing** — 會變、Phase D 實作時 reverify
- **不解的失敗類別**：Council 跟 Verifier 都被同一條 systematic bias 影響（e.g. Anthropic family-wide pattern）的時候、本 spec 無能為力。需要 third-party verifier（Gemini / GPT-4）才補、Phase E+ 候選。

---

## 後記

本 spec + scaffold 是 Phase A+B 一 PR ship、close loop with mock test。Phase C 整合進 council、Phase D 真實 Haiku call、Phase E 加 override — 都該後續 PR 單獨評估、不該預先 commit 整個路徑。

Strategic crystal 紀錄本 spec 從寫到實作的演化 — 預期會在 Phase D+ 後寫第一個 verifier-related crystal（covering "Did the Verifier actually catch failure modes that Council missed?"）。
