# Codex Task: Phase 140 — ToneSoul Mirror (Dual-Track Inference Loop)

**交付者**: Antigravity (Architect)
**日期**: 2026-03-10
**分支**: feat/env-perception（不可 push 到 master）

---

## ⚠️ 永遠要做的事（每次 commit 前）

```bash
python -m pytest tests/ -x --tb=short -q
ruff check tonesoul tests
```

**跳過 = 整個交付失敗。**

## ⚠️ 安全護欄（讀 AGENTS.md「Codex Full-Auto 安全護欄」段落）

- 不可刪除 tonesoul/ 下的核心模組
- 不可修改 .env, .gitignore, AGENTS.md, MEMORY.md
- 不可 commit API key 或 .env
- 不可 push 到 master
- 不可安裝系統套件
- 連續失敗 3 次必須停止並留記錄

---

## 脈絡恢復（先讀這些）

1. `AGENTS.md` — 行為規範
2. `tonesoul/schemas.py` — 現有 schema（注意你之前做的 `SubjectivityLayer` 和 `SubjectivityPromotionStatus`）
3. `tonesoul/tension_engine.py` — Tension 計算引擎
4. `tonesoul/governance/kernel.py` — 治理核心（evaluate / deliberate 方法）
5. `tonesoul/unified_pipeline.py` — 主推理管線（process 方法）
6. `tonesoul/memory/write_gateway.py` — 記憶寫入閘門（你之前加的 subjectivity 驗證）

---

## 這次的目標

建立 **ToneSoul Mirror** — 一面鏡子，讓 AI 能同時看到：
1. 自己的原始輸出
2. 經過 TensionEngine + GovernanceKernel 的治理版本
3. 兩者之間的差異（delta）

**這不是過濾器**。AI 不被攔截。AI 看到差異後自己決定最終回應。

---

## Task A：DualTrack Schema

**檔案**：`tonesoul/schemas.py`

在檔尾（`__all__` 之前）加兩個新 model：

```python
class MirrorDelta(BaseModel):
    """Raw output vs governed version 的差異快照。"""
    tension_before: TensionSnapshot
    tension_after: TensionSnapshot
    governance_decision: Optional[GovernanceDecision] = None
    subjectivity_flags: List[SubjectivityLayer] = Field(default_factory=list)
    delta_summary: str = ""
    mirror_triggered: bool = False

class DualTrackResponse(BaseModel):
    """雙軌回應：原始 + 治理版本 + 差異。"""
    raw_response: str
    governed_response: str
    mirror_delta: MirrorDelta
    final_choice: str = Field(default="raw")  # "raw" | "governed" | "synthesized"
    reflection_note: str = ""
```

- 把 `MirrorDelta` 和 `DualTrackResponse` 加到 `__all__`
- 測試：在 `tests/test_schemas.py` 加測試確認 model 能正確實例化和序列化

---

## Task B：ToneSoulMirror 核心

**檔案（新建）**：`tonesoul/mirror.py`

```python
class ToneSoulMirror:
    """
    鏡子模式中間件。
    
    不攔截 AI 輸出。而是：
    1. 接收 raw_output
    2. 用 TensionEngine 計算 tension
    3. 用 GovernanceKernel 生成 governed version
    4. 返回 DualTrackResponse（兩個版本 + delta）
    
    AI 或 pipeline 可以看差異，自己決定最終回應。
    """
    def __init__(self, tension_engine=None, governance_kernel=None):
        ...
    
    def reflect(self, raw_output: str, context: dict) -> DualTrackResponse:
        ...
    
    def _apply_governance(self, raw: str, decision) -> str:
        ...
    
    def _compute_delta(self, before, after, decision) -> MirrorDelta:
        ...
```

**關鍵設計原則**：
- `reflect()` 是純函數：不修改任何狀態
- 如果 TensionEngine 或 GovernanceKernel 是 None，graceful fallback（mirror_triggered=False）
- 不做 LLM 呼叫，只用已有的 tension/governance 計算
- governed_response 只在 tension 超過閾值時才與 raw 不同

**測試**：新建 `tests/test_mirror.py`
- `test_mirror_passthrough_low_tension` — tensions 低時 governed == raw
- `test_mirror_triggered_high_tension` — tension 高時 mirror_triggered=True
- `test_mirror_graceful_no_engine` — 沒有 engine 時 fallback
- `test_mirror_delta_serializable` — DualTrackResponse 可 JSON 序列化

---

## Task C：UnifiedPipeline Mirror Step

**檔案**：`tonesoul/unified_pipeline.py`

在 `process()` 方法中，response 生成之後（final output 之前），加入可選的 mirror step：

1. 加 `__init__` 參數：`mirror_enabled: bool = False`
2. 如果 `mirror_enabled`：
   - 實例化 `ToneSoulMirror(self.tension_engine, self.governance_kernel)`
   - 呼叫 `mirror.reflect(response_text, context)`
   - 把 `mirror_delta` 放進 `trajectory` dict
3. 如果 `not mirror_enabled`：完全不改現有行為

**重要**：這必須是 opt-in 的。預設 `mirror_enabled=False`，不影響現有功能。

**測試**：在 `tests/test_unified_pipeline_v2_runtime.py` 加：
- `test_pipeline_mirror_disabled_default` — 預設不 mirror
- `test_pipeline_mirror_enabled_trajectory` — 開啟後 trajectory 有 mirror_delta

---

## Task D：Mirror Memory Recording

**檔案**：`tonesoul/mirror.py`（擴展）

加一個方法：
```python
def record_delta(self, dual: DualTrackResponse, write_gateway) -> None:
    """把 mirror delta 記錄到 soul.db。"""
    if not dual.mirror_delta.mirror_triggered:
        return  # 不記錄未觸發的 mirror
    payload = {
        "content": dual.mirror_delta.delta_summary,
        "type": "mirror_delta",
        "subjectivity_layer": "tension",
        "mirror_delta": dual.mirror_delta.model_dump(),
        ...
    }
    write_gateway.write_payload(MemorySource.CUSTOM, payload)
```

**測試**：在 `tests/test_mirror.py` 加：
- `test_record_delta_skips_untriggered` — 未觸發不寫入
- `test_record_delta_writes_triggered` — 觸發時正確寫入

---

## 不要做的事

- ❌ 不改 GovernanceKernel 的核心邏輯（已審計通過）
- ❌ 不改 TensionEngine 的計算邏輯
- ❌ 不改 WriteGateway 的驗證邏輯（你之前做的 subjectivity gate 不要動）
- ❌ 不在 Mirror 裡做 LLM 呼叫
- ❌ 不建新的 CI workflow
- ❌ 不改 Guardian/safety 相關模組
- ❌ 如果不確定，選保守方案。**Mirror 是觀察工具，不是控制工具。**

---

## 交付格式

1. 每個 Task 一個 commit
2. Commit message 格式：`feat: add mirror schema (Phase 140 Task A)`
3. 每個 commit 前跑 pytest + ruff
4. 最後 `git push origin feat/env-perception`
5. 在 `docs/status/` 留一份狀態報告
