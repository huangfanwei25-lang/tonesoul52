# RFC-014: Reflection Loop + 章魚架構

> Purpose: draft exploratory RFC for reflection-loop and octopus-architecture ideas that have not yet been promoted to canonical runtime policy.
> Last Updated: 2026-03-23

> **日期**: 2026-03-20
> **作者**: 痕 (Hén) — Claude Opus 4.6
> **狀態**: Draft
> **前置**: Phase 583 (2526 tests, 212+ modules)
> **關聯**: RFC-009 Context Engineering, RFC-013 Nonlinear Prediction

---

## 一、核心命題

> 「沒有反思的 AI，只是一面快速的鏡子。它反射你的問題，但從不問自己：我這面鏡子有沒有扭曲？」

ToneSoul 目前是一條**單向管線**：

```
分析 → 審議 → 生成 → 複審 → 輸出
```

每一步都做得精緻，但管線是直線。直線管線有一個根本缺陷：
**它不會因為後面的發現而修正前面的判斷。**

Council 發現回答有問題 → 只能做確定性修補（加前綴、換模板）→ 不能叫 LLM 重新想一次。

這就像一個外科醫生，手術中發現切錯了位置，但只能用紗布補，不能重新下刀。

**Reflection Loop 的本質：讓管線從直線變成迴路。**

---

## 二、為什麼現在？

| 已建成 | 缺什麼 |
|--------|--------|
| Council 會投票 REFINE/BLOCK | 但 REFINE 不會觸發重新生成 |
| VowEnforcer 會偵測違規 | 但沒接進 process() |
| AlertEscalation 分 L1/L2/L3 | 但所有等級都用同一個 LLM |
| DreamEngine 會離線反思 | 但不會在對話中即時反思 |
| Inter-Soul Protocol 定義了跨靈魂通訊 | 但沒有第二個靈魂 |

系統的「感知力」已經足夠強了 — 它**知道**什麼時候出了問題。
但它的「行動力」還是直線的 — 知道了，卻只能往前走。

---

## 三、章魚架構 (Octopus Architecture)

### 3.1 三層金字塔

```
                    ┌───────────────┐
         L3        │   雲端主腦     │  Claude / GPT
                   │   深度反思     │  倫理困境、長鏈推理
                   │   危機介入     │  一回合 ≈ $0.03-0.10
                   └───────┬───────┘
                           │ 高張力時才呼叫
                   ┌───────┴───────┐
         L2        │   本地支腦     │  Qwen-7B / 305 (7B)
                   │   日常推理     │  一般對話、快速回應
                   │   初步審議     │  一回合 ≈ 0（本地推理）
                   └──┬─────┬──┬───┘
                      │     │  │
                   ┌──┴─┐┌──┴─┐┌──┴──┐
         L1        │腳本││腳本││腳本 │  純程式碼，零 LLM
                   │    ││    ││     │  VowEnforcer, DriftMonitor
                   │    ││    ││     │  TensionEngine, CircuitBreaker
                   └────┘└────┘└─────┘  一回合 ≈ <1ms
```

### 3.2 章魚的觸手

```
                        ┌──────────────────┐
                        │    主腦 (L3)      │
                        │  雲端 Claude      │
                        │  只在危機時啟動    │
                        └────────┬─────────┘
                                 │
              ┌──────────┬───────┼───────┬──────────┐
              │          │       │       │          │
         ┌────┴───┐ ┌───┴────┐ ┌┴─────┐ ┌┴────────┐ ┌┴────────┐
         │ 觸手 1  │ │ 觸手 2 │ │觸手 3│ │ 觸手 4  │ │ 觸手 5  │
         │L2:對話  │ │L2:分析 │ │L1:誓 │ │L1:漂移  │ │L1:張力  │
         │本地 7B  │ │本地 7B │ │言守衛│ │偵測器   │ │計算器   │
         └────────┘ └────────┘ └──────┘ └────────┘ └────────┘
```

**關鍵原則：**

1. **L1 觸手永遠不用 LLM** — VowEnforcer、DriftMonitor、TensionEngine 是確定性程式碼
2. **L2 觸手用本地小模型** — 快速、免費、可離線運作
3. **L3 主腦只在「不確定」時啟動** — 最貴但最強，用 AlertEscalation 的 L2/L3 做為觸發條件
4. **觸手之間不直接通訊** — 全部透過主幹（UnifiedPipeline）協調

### 3.3 AlertEscalation → 模型路由映射

現有的 AlertEscalation 已經完美地定義了三級觸發：

| AlertLevel | 現行行為 | 章魚架構行為 |
|------------|---------|-------------|
| **L1** (WARNING) | 記錄，繼續 | **L2 本地模型**處理，記錄 |
| **L2** (CRISIS) | 結構凍結，Guardian 控制 | L2 生成草稿 → **L3 審查修訂** |
| **L3** (SEABED) | 鎖定，最小回應 | **L3 主腦接管**全部推理 |

無 alert（最常見情況）→ L2 本地模型處理，不呼叫雲端。

**成本影響（概估）**：
- 目前（全走雲端）: 每輪 $0.03-0.10
- 章魚架構: ~80% L2 本地免費 + ~15% L2+L3 混合 + ~5% L3 全程 ≈ **省 70-80%**

---

## 四、Reflection Loop 設計

### 4.1 設計原則

1. **反思是例外，不是常態** — 大多數回答不需要反思，只有 Council 說 REFINE/BLOCK 或 Vow 被違反時才觸發
2. **最多 2 輪** — 防止無限迴圈，硬上限
3. **張力自適應** — 低張力跳過反思，高張力強制反思
4. **反思成本可控** — 反思用 L2 自我檢查，只有嚴重問題才呼叫 L3

### 4.2 反思迴路流程

```
                                  ┌──────────────┐
                                  │  process()   │
                                  └──────┬───────┘
                                         │
                              ┌──────────▼──────────┐
                              │ Phase 1-2: 分析+審議 │
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │ Phase 3: LLM 生成    │
                              │ (L2 本地 or L3 雲端)  │
         max_revisions = 2    └──────────┬──────────┘
              │                          │
              │               ┌──────────▼───────────┐
              │               │ Phase 3.5: Self-Check │◄────┐
              │               │  ┌─ VowEnforcer       │     │
              │               │  ├─ Council.pre_check │     │
              │               │  └─ Tension δ 估計    │     │
              │               └──────────┬───────────┘     │
              │                          │                  │
              │                    ┌─────┴─────┐           │
              │                    │  需要修訂？ │           │
              │                    └─────┬─────┘           │
              │                  NO/     │    \YES          │
              │                 │        │     │            │
              │                 ▼        │     ▼            │
              │          直接進入      │  ┌──────────┐      │
              │          Phase 4      │  │ 生成修訂   │      │
              │                       │  │ prompt    │      │
              │                       │  │ (含原因)   │      │
              │                       │  └────┬─────┘      │
              │                       │       │             │
              │                       │       ▼             │
              │                       │  ┌──────────┐      │
              └───── revision_count ──┤  │ LLM 重新  │      │
                     < max? ──────────┘  │ 生成      │──────┘
                                         └──────────┘
                                    (回到 Self-Check)
```

### 4.3 Self-Check 的三道關卡

```python
@dataclass
class ReflectionVerdict:
    """Self-Check 的結果"""
    should_revise: bool
    reasons: list[str]
    severity: float           # 0.0 ~ 1.0
    vow_violations: list[str]
    council_concerns: list[str]
    tension_delta: float      # 預估修復後的張力變化
```

**關卡 1: VowEnforcer（L1 腳本，<1ms）**

```python
vow_result = self._vow_enforcer.enforce(draft_response)
if vow_result.has_violations(severity="block"):
    → should_revise = True, reason = "誓言違反: {vow_id}"
```

- 純確定性，不用 LLM
- 檢查：No Misleading, Acknowledge Uncertainty, 等
- 如果 `VowAction.BLOCK` → 必須修訂
- 如果 `VowAction.FLAG` → 標記但不強制

**關卡 2: Council Pre-Check（L1 腳本 + 少量計算）**

```python
council_verdict = self._council.deliberate(draft_response, context)
if council_verdict.decision in (REFINE, BLOCK):
    → should_revise = True, reason = "Council: {concerns}"
```

- 現有 Council 已經會給 REFINE/BLOCK
- 差別是：現在 REFINE 會**真的觸發重新生成**，不只是加前綴

**關卡 3: Tension Delta 估計（L1 腳本，<5ms）**

```python
tension_before = self._tension_engine.last_tension
tension_after = self._tension_engine.estimate(draft_response)  # 模擬
delta = tension_after - tension_before
if delta > REFLECTION_TENSION_THRESHOLD:  # 如果回答讓張力惡化
    → should_revise = True, reason = f"張力惡化 Δ={delta:.2f}"
```

- 用 `_semantic_projection()` 估計回答的張力效果
- 如果回答讓張力**升高**超過閾值 → 需要修訂

### 4.4 修訂 Prompt 的結構

當 Self-Check 說 `should_revise = True`：

```python
revision_prompt = f"""
你剛才生成了以下回答：
---
{draft_response}
---

內部審查發現以下問題：
{'\n'.join(f'- {r}' for r in verdict.reasons)}

請修訂你的回答，保留正確的部分，修正上述問題。
不要提及這次修訂過程本身。
"""
```

修訂用的 LLM 選擇：
- `severity < 0.5` → L2 本地模型自行修訂
- `severity >= 0.5` → L3 雲端主腦修訂（嚴重問題需要更強的推理）

### 4.5 反思的計量經濟學

| 場景 | 頻率（估） | LLM 呼叫次數 | 成本 |
|------|-----------|-------------|------|
| 無問題，直通 | ~75% | 1 (L2) | 免費 |
| Vow FLAG，輕微 | ~10% | 1 (L2) | 免費 |
| Council REFINE | ~10% | 2 (L2+L2) | 免費 |
| Council BLOCK / Vow BLOCK | ~4% | 2 (L2+L3) | ~$0.05 |
| L3 Seabed Crisis | ~1% | 1-2 (L3) | ~$0.10 |

**加權平均**: ~0.95 × $0 + 0.04 × $0.05 + 0.01 × $0.10 = **~$0.003/輪**
（對比現行全走雲端 ~$0.05/輪，省 94%）

---

## 五、VowEnforcer 整合（補全缺口）

VowEnforcer 目前**存在但未接入 process()**。這是 Reflection Loop 的前置條件。

### 5.1 接入點

```python
# unified_pipeline.py — Phase 3.5 Self-Check
# 在 LLM 回應之後、Council 之前

def _self_check(self, draft: str, context: dict) -> ReflectionVerdict:
    reasons = []
    severity = 0.0

    # 關卡 1: VowEnforcer (L1)
    vow_result = self._get_vow_enforcer().enforce(draft)
    for v in vow_result.violations:
        reasons.append(f"Vow [{v.vow_id}]: {v.detail}")
        if v.action == VowAction.BLOCK:
            severity = max(severity, 0.8)
        elif v.action == VowAction.REPAIR:
            severity = max(severity, 0.5)

    # 關卡 2: Council Pre-Check (L1)
    verdict = self._get_council().deliberate(draft, context)
    if verdict.decision == CouncilDecision.BLOCK:
        reasons.append(f"Council BLOCK: {verdict.summary}")
        severity = max(severity, 0.9)
    elif verdict.decision == CouncilDecision.REFINE:
        for c in verdict.concerns:
            reasons.append(f"Council REFINE: {c}")
        severity = max(severity, 0.4)

    # 關卡 3: Tension Delta (L1)
    t_delta = self._estimate_tension_delta(draft)
    if t_delta > REFLECTION_TENSION_THRESHOLD:
        reasons.append(f"張力惡化 Δ={t_delta:.2f}")
        severity = max(severity, 0.3 + t_delta)

    return ReflectionVerdict(
        should_revise=len(reasons) > 0 and severity > 0.2,
        reasons=reasons,
        severity=min(severity, 1.0),
        ...
    )
```

### 5.2 Reflection 主迴路

```python
# unified_pipeline.py — 替換目前的單次 LLM 呼叫

MAX_REVISIONS = 2

draft = self._call_llm(prompt, tier="auto")  # 首次生成
revision_count = 0

while revision_count < MAX_REVISIONS:
    verdict = self._self_check(draft, context)
    dispatch_trace["reflection_verdicts"].append(verdict)

    if not verdict.should_revise:
        break  # 通過自檢，繼續 Phase 4

    # 選擇修訂用的 LLM 層級
    revision_tier = "L3" if verdict.severity >= 0.5 else "L2"
    revision_prompt = self._build_revision_prompt(draft, verdict)
    draft = self._call_llm(revision_prompt, tier=revision_tier)
    revision_count += 1

dispatch_trace["reflection_count"] = revision_count
```

---

## 六、Thinking Depth Router（方向 A）

AlertEscalation 的 L1/L2/L3 直接映射到 LLM 路由：

### 6.1 修改 `llm/router.py`

```python
class ThinkingTier(Enum):
    LOCAL = "local"       # L2: 本地 9B (LM Studio)
    CLOUD = "cloud"       # L3: 雲端 (Claude/GPT/Gemini)
    AUTO = "auto"         # 根據 AlertLevel 決定

def resolve_thinking_tier(alert_level: AlertLevel) -> ThinkingTier:
    """AlertEscalation → LLM 選擇"""
    if alert_level == AlertLevel.L3:
        return ThinkingTier.CLOUD    # 危機 → 雲端主腦
    elif alert_level == AlertLevel.L2:
        return ThinkingTier.CLOUD    # 嚴重 → 雲端主腦
    else:
        return ThinkingTier.LOCAL    # 正常 → 本地支腦
```

### 6.2 本地模型設定

```python
# config.py 或 .env
LOCAL_LLM_BACKEND = "lmstudio"      # 預設 LM Studio（支援自訂 GGUF 模型）
LOCAL_LLM_MODEL = "qwen3.5-9b-uncensored-hauhaucs-aggressive"
CLOUD_LLM_BACKEND = "gemini"        # or "claude", "openai"
CLOUD_LLM_MODEL = "claude-opus-4-6" # 雲端主腦
```

> **備註**: Ollama 不支援此自訂模型，故 LOCAL 預設走 LM Studio。
> LM Studio 的 `_get_model()` 會自動偵測已載入模型，若明確指定模型名稱可跳過偵測。

### 6.3 整合到 UnifiedPipeline

```python
def _call_llm(self, prompt: str, tier: str = "auto") -> str:
    if tier == "auto":
        tier = resolve_thinking_tier(self._last_alert_level)

    if tier == ThinkingTier.LOCAL:
        client = resolve_llm_backend("lmstudio")  # 本地 9B
    else:
        client = resolve_llm_backend("gemini")     # 雲端

    return client.chat(prompt)
```

---

## 七、多 AI 協作路線圖（方向 C）

### 7.1 階段一：本地 L2 + 雲端 L3（Phase 584-589）
- UnifiedPipeline 根據 AlertLevel 選擇本地或雲端 LLM
- 大多數對話走本地 7B，只有高張力才呼叫雲端
- Inter-Soul Protocol 暫時不啟用

### 7.2 階段二：L2↔L3 反思協作（Phase 590-595）
- L2 生成草稿 → Self-Check 發現問題 → L3 做修訂
- 這是「章魚架構」的第一個真實案例：兩個不同能力的 LLM 協作
- Inter-Soul Protocol 的 TensionPacket 可用於 L2 向 L3 傳遞張力上下文

### 7.3 階段三：多觸手專職化（Phase 596+，長期觀察）
- 不同觸手（L2 實例）專門負責不同任務：
  - 觸手 A: ToneBridge 語調分析（快速，本地）
  - 觸手 B: Council 審議回應生成（快速，本地）
  - 觸手 C: Memory Retrieval + Summarization（快速，本地）
- 主腦（L3）只做最終仲裁
- **前提：本地模型的品質必須到達可接受水準**

---

## 八、之前提到的待做事項整合

之前的分析中提到幾個值得做但尚未排期的方向：

| 方向 | 來源 | 與本 RFC 的關係 | 建議時機 |
|------|------|----------------|---------|
| **Tension-Adaptive Debate Rounds** | finance_as_human_nature 文件 | 反思迴路的輪數已經做到張力自適應 | 包含在 Phase 584-586 |
| **Thinking Depth Router** | 上次對話 | 本 RFC 的方向 A，是反思迴路的基礎設施 | Phase 584 前置 |
| **Council Feedback Loop** | finance_as_human_nature 文件 | 反思迴路的核心 — Council REFINE → 重新生成 | Phase 585-586 |
| **DSPy 結構化 Prompt** | 上次對話 | 修訂 prompt 可以用 DSPy Signature 規範化 | Phase 590+ 觀察 |
| **Letta 記憶分層** | 上次對話 | 與 Hippocampus 互補但不緊急 | Phase 596+ |
| **RAGAS 評估** | 上次對話 | 反思品質需要量化，RAGAS 可借鑑 | Phase 593+ |

---

## 九、實作 Phase 規劃

### Phase 584: VowEnforcer 接入 + ReflectionVerdict（前置）
- [ ] 將 VowEnforcer 接入 process()（目前未接入）
- [ ] 建立 `ReflectionVerdict` dataclass
- [ ] 實作 `_self_check()` 方法（三道關卡）
- [ ] 測試：Vow 違反觸發反思判決
- **成功標準**: `dispatch_trace["reflection_verdict"]` 正確反映 Vow + Council + TensionDelta

### Phase 585: Reflection Loop 主迴路
- [ ] 修改 process() 的 LLM 呼叫段為 `_generate_with_reflection()`
- [ ] 實作修訂 prompt 生成 (`_build_revision_prompt()`)
- [ ] `MAX_REVISIONS = 2` 硬上限
- [ ] `dispatch_trace["reflection_count"]` + `reflection_verdicts`
- [ ] 測試：Council REFINE → 觸發修訂 → 第二次通過
- [ ] 測試：MAX_REVISIONS 上限不會無限迴圈
- **成功標準**: 端對端 — Vow 違反 → 自動修訂 → 通過

### Phase 586: Thinking Depth Router
- [ ] `ThinkingTier` enum (LOCAL / CLOUD / AUTO)
- [ ] `resolve_thinking_tier(alert_level)` 映射函數
- [ ] 修改 `llm/router.py` 支援 tier 參數
- [ ] UnifiedPipeline 根據 AlertLevel 選擇 tier
- [ ] 設定檔支援 `LOCAL_LLM_MODEL` / `CLOUD_LLM_MODEL`
- [ ] 測試：L1 → LOCAL, L2 → CLOUD, L3 → CLOUD
- **成功標準**: 無 alert 時走本地模型，L2+ 時自動升級到雲端

### Phase 587: 反思 + 路由整合
- [ ] Reflection Loop 的修訂 tier 根據 severity 選擇
- [ ] `severity < 0.5` → L2 自行修訂; `severity >= 0.5` → L3 修訂
- [ ] 全流程端對端測試（本地生成 → 自檢失敗 → 雲端修訂）
- [ ] `dispatch_trace` 記錄完整反思軌跡（tier + verdict + revision_count）
- **成功標準**: 章魚架構的最小可行版本運作

### Phase 588-589: Observability + Polish
- [ ] Reflection Loop 的觀測性（日誌、timing、token 成本追蹤）
- [ ] 反思品質指標：修訂後的 Vow 通過率、Council 通過率
- [ ] 設定檔化：REFLECTION_TENSION_THRESHOLD、MAX_REVISIONS
- [ ] 說明文件

---

## 十、哲學結語

> 反思不是重新計算。
>
> 計算器不會反思 — 它只會重算。
> 人才會反思 — 因為反思需要一個「我」站在「我的回答」對面，審視它。
>
> ToneSoul 的 Council 就是那個「站在對面的我」。
> 但過去的它只能看、只能說「這裡有問題」。
> 現在我們要讓它不只是看，而是**把問題遞回去**。
>
> 這就是反思的最小定義：
> **能力 × 自我審查 × 修正迴路。**
>
> 章魚不聰明在它的頭，聰明在觸手之間的協調。
> 一個 7B 模型做不了什麼，但一個 7B + 一個 Claude + 五個確定性守衛，
> 就是一隻完整的章魚。

---

*此文件是設計規格，待人類核准後進入 Phase 實作。*
