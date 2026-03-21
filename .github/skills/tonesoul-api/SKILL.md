---
name: tonesoul-api
description: "**LIBRARY & API REFERENCE** — ToneSoul 內部模組 API 參考。USE WHEN: 使用 UnifiedPipeline、DreamEngine、MemoryCrystallizer、GovernanceKernel、DeliberationEngine、TensionEngine、PersonaTrackRecord、StaleRuleVerifier 等核心模組時。DO NOT USE FOR: 前端 UI 元件、第三方函式庫。INVOKES: file system tools for code lookup."
---

# ToneSoul API Reference

> 快速查用法、避免踩坑、找到規範寫法。

## 模組索引

| 模組 | 檔案 | 核心類別 | 一句話用途 |
|------|------|---------|-----------|
| Pipeline | `tonesoul/unified_pipeline.py` | `UnifiedPipeline` | 端到端處理：感知→審議→回應 |
| Dream Engine | `tonesoul/dream_engine.py` | `DreamEngine` | 離線自主碰撞引擎 |
| Crystallizer | `tonesoul/memory/crystallizer.py` | `MemoryCrystallizer` | 記憶淬鍊與決策規則管理 |
| Governance | `tonesoul/governance/kernel.py` | `GovernanceKernel` | 治理摩擦力與斷路器 |
| Deliberation | `tonesoul/deliberation/engine.py` | `InternalDeliberation` | Muse/Logos/Aegis 三方審議 |
| Gravity | `tonesoul/deliberation/gravity.py` | `SemanticGravity` | 審議權重計算 (Pareto) |
| Track Record | `tonesoul/deliberation/persona_track_record.py` | `PersonaTrackRecord` | 審議者歷史績效追蹤 |
| Tension | `tonesoul/tension_engine.py` | `TensionEngine` | 張力張量 T = W × E × D |
| Stale Verifier | `tonesoul/stale_rule_verifier.py` | `StaleRuleVerificationTaskBatch` | 老化規則自動驗證任務 |
| Write Gateway | `tonesoul/memory/write_gateway.py` | `MemoryWriteGateway` | 記憶寫入閘門（去重 + 簽名） |
| Vow System | `tonesoul/vow_system.py` | `VowSystem` | SelfCommit 承諾系統 |
| Scenario Envelope | `tonesoul/tonebridge/scenario_envelope.py` | `ScenarioEnvelopeBuilder` | Bull/Base/Bear 情境框架 |

## 常用模式

### 1. UnifiedPipeline — 最小調用

```python
from tonesoul.unified_pipeline import UnifiedPipeline

pipeline = UnifiedPipeline()
result = await pipeline.run("使用者輸入", context={})
# result.response — 最終回應
# result.trace — 完整審議軌跡
```

### 2. DreamEngine — 離線碰撞循環

```python
from tonesoul.dream_engine import DreamEngine

engine = DreamEngine()
cycle = engine.run_cycle(
    limit=3,                          # 最多處理 3 個刺激
    min_priority=0.35,                # 優先度門檻
    generate_verification_tasks=True, # Phase 542: 自動產生驗證任務
    max_verification_tasks=5,
)
# cycle.collisions — 碰撞結果
# cycle.stale_rule_tasks_generated — 產生的驗證任務數
```

### 3. MemoryCrystallizer — 晶體管理

```python
from tonesoul.memory.crystallizer import MemoryCrystallizer

cryst = MemoryCrystallizer(freshness_half_life_days=21)
crystals = cryst.load_crystals()        # 載入全部（含 freshness 刷新）
top = cryst.top_crystals(n=5)           # 取前 N（按 weight × freshness）
cryst.mark_support("rule text")         # 重新確認規則（刷新 freshness）
summary = cryst.freshness_summary()     # 治理用摘要
```

### 4. PersonaTrackRecord — 績效追蹤

```python
from tonesoul.deliberation.persona_track_record import PersonaTrackRecord

record = PersonaTrackRecord()
mult = record.get_multiplier("muse", resonance_state="drift", loop_detected=False)
# mult 範圍: 0.85 ~ 1.15
record.record_outcome("muse", "approve", resonance_state="drift", loop_detected=False)
```

### 5. StaleRuleVerificationTaskBatch — 驗證任務

```python
from tonesoul.stale_rule_verifier import StaleRuleVerificationTaskBatch

batch = StaleRuleVerificationTaskBatch()
tasks = batch.generate_from_crystals(crystals, max_tasks=10)
batch.persist_tasks(tasks)
pending = batch.get_pending_tasks()
```

## ⚠️ 注意事項

- **觸發**：直接實例化 `DreamEngine()` 而不傳入 mock 依賴
  **風險**：會連接真實 SoulDB 和 LLM Router，產生實際 API 呼叫和費用
  **快速檢查**：建構子參數是否全部為 `None`（會用預設值）
  **正確做法**：測試中用 `MagicMock()` 注入所有依賴

- **觸發**：對 `MemoryCrystallizer` 呼叫 `mark_support()` 用錯 rule text
  **風險**：不會報錯，但也不會刷新任何晶體的 freshness
  **快速檢查**：比對 `crystals.jsonl` 中的 `rule` 欄位是否完全匹配
  **正確做法**：先 `load_crystals()` 取出完整 rule 字串再傳入

- **觸發**：`PersonaTrackRecord` 的 JSON 檔案被多個 process 同時寫入
  **風險**：JSON 格式損壞，所有歷史績效遺失
  **快速檢查**：檔案大小突然變 0 或無法 parse
  **正確做法**：單一 process 寫入，或加檔案鎖

- **觸發**：`top_crystals()` 回傳結果排序改變（Phase 540 後）
  **風險**：依賴固定排序的邏輯會壞掉
  **快速檢查**：排序現在是 `weight × freshness_score` 而非純 `weight`
  **正確做法**：不要假設排序不變，用語意比對而非位置比對

- **觸發**：`freshness_half_life_days` 設太短（例如 3 天）
  **風險**：所有晶體快速老化，審議喪失歷史記憶
  **快速檢查**：`freshness_summary()` 的 `stale_count` 接近 `total_crystals`
  **正確做法**：預設 21 天，最短不低於 7 天

## 禁止事項

❌ 禁止直接修改 `crystals.jsonl` — 用 `MemoryCrystallizer` API  
❌ 禁止在測試中連接真實 LLMRouter — 用 mock  
❌ 禁止假設 `DreamCycleResult.collisions` 順序固定  
❌ 禁止在公開倉庫提交 `memory/*.jsonl` 資料檔案  
