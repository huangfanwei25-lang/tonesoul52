# Codex Task: Phase 584-587 — Reflection Loop + 章魚架構

**指派者**: 痕 (Hén)
**日期**: 2026-03-20
**分支**: feat/env-perception（不可 push 到 master）
**前置條件**: 2526 tests passing, lint clean
**設計文件**: `docs/RFC-014_Reflection_Loop_Octopus_Architecture.md`（必讀）

---

## 全局規則

1. **每個 Phase 單獨 commit**，commit message 格式：`feat(Phase N): [摘要]`
2. 每個 Phase 完成後：`ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` 全過
3. 預期測試數逐步增長：584 ≥ 2540, 585 ≥ 2555, 586 ≥ 2570, 587 ≥ 2580
4. **禁止修改** `AGENTS.md`、`CODEX_PROTOCOL.md`、`AXIOMS.json`
5. **禁止修改** `tonesoul/inter_soul/` — 已審核通過的套件
6. 連續失敗 3 次 → 停下，寫 CODEX_HANDBACK.md
7. **unified_pipeline.py 可以修改**，但必須保留所有現有 dispatch_trace 欄位

---

## 脈絡（先讀這些）

1. `docs/RFC-014_Reflection_Loop_Octopus_Architecture.md` — **必讀**，整體設計藍圖
2. `tonesoul/vow_system.py` — VowEnforcer API，Phase 584 的核心
3. `tonesoul/unified_pipeline.py` L2097-2176 — Council 審議後處理，Phase 585 的插入點
4. `tonesoul/llm/router.py` — 現有路由邏輯，Phase 586 要擴充
5. `tonesoul/llm/lmstudio_client.py` — LM Studio 客戶端，Phase 586 的 LOCAL 後端
6. `tonesoul/alert_escalation.py` — AlertLevel L1/L2/L3，Phase 586 的觸發條件
7. `tonesoul/council/pre_output_council.py` — Council deliberate() 和 verdict 型別

---

## Phase 584: VowEnforcer 接入 + ReflectionVerdict

**脈絡**: VowEnforcer 已完整實作（`enforce()` 接受文本，返回 `VowEnforcementResult`），但**從未接入 `process()`**。本 Phase 建立反思判決基礎設施。

### 任務

- [ ] 建立 `tonesoul/reflection.py`，包含：
  - `ReflectionVerdict` dataclass：`should_revise: bool`, `reasons: list[str]`, `severity: float`, `vow_result: Optional[VowEnforcementResult]`, `council_decision: Optional[str]`, `tension_delta: Optional[float]`
  - `MAX_REVISIONS: int = 2`（常數）
  - `REFLECTION_TENSION_THRESHOLD: float = 0.25`（常數）

- [ ] 在 `UnifiedPipeline` 中加入 `_self_check()` 方法：
  ```python
  def _self_check(self, draft: str, context: dict) -> ReflectionVerdict:
  ```
  - **關卡 1**: 呼叫 `VowEnforcer().enforce(draft)` — 若 `blocked=True` 或 `repair_needed=True`，加入 reasons
  - **關卡 2**: 呼叫 `self._get_council().deliberate(request)` — 若 verdict 為 REFINE 或 BLOCK，加入 reasons
  - **關卡 3**: 若 `self._tension_engine` 可用，用 `compute()` 估計 draft 張力，與上一步比較 delta — 若 delta > `REFLECTION_TENSION_THRESHOLD`，加入 reasons
  - `severity` = 各關卡最高觸發值（BLOCK=0.9, REFINE=0.4, Vow REPAIR=0.5, Vow FLAG=0.2, tension=0.3+delta）
  - `should_revise = len(reasons) > 0 and severity > 0.2`

- [ ] `dispatch_trace["reflection_verdict"]` 記錄 `ReflectionVerdict` 的 dict 表示

- [ ] 寫測試 `tests/test_reflection.py`（≥ 10 tests）：
  - `ReflectionVerdict` 基本建構
  - `_self_check` 在 Vow 全通過 + Council APPROVE → `should_revise=False`
  - `_self_check` 在 Vow BLOCK → `should_revise=True, severity≥0.8`
  - `_self_check` 在 Vow REPAIR → `should_revise=True, severity≥0.5`
  - `_self_check` 在 Council REFINE → `should_revise=True, severity≥0.4`
  - `_self_check` 在 Council BLOCK → `should_revise=True, severity≥0.9`
  - `_self_check` 在張力惡化 → `should_revise=True`
  - `_self_check` 在 Vow FLAG only → `should_revise=False`（FLAG 不足以觸發修訂）
  - 多重關卡觸發時 severity 取最高
  - `dispatch_trace` 正確記錄

### 技術提示
- `VowEnforcer().enforce(output)` 已可用，返回 `VowEnforcementResult`
- `check_vows(text)` 是快捷函數，也可以用
- Council 的 `deliberate()` 接受 `CouncilRequest(draft_output=draft, context=context)`
- 不要在此 Phase 修改 `process()` 的 LLM 呼叫流程 — 只建立基礎設施和 `_self_check` 方法
- `_self_check` 應該是可獨立測試的（mock VowEnforcer 和 Council）

### 禁止
- ❌ 不修改現有 `process()` 的 LLM 呼叫段（Phase 585 處理）
- ❌ 不修改 `vow_system.py` 本身

---

## Phase 585: Reflection Loop 主迴路

**脈絡**: Phase 584 建立了 `_self_check()`。本 Phase 將其織入 `process()` 的 LLM 生成段，實現「生成 → 自檢 → 條件修訂」迴路。

### 任務

- [ ] 在 `tonesoul/reflection.py` 加入：
  - `build_revision_prompt(draft: str, verdict: ReflectionVerdict) -> str` — 生成修訂提示
    - 格式：原文 + 問題原因列表 + 「請修訂以上回答，保留正確部分，修正問題。不要提及修訂過程。」

- [ ] 修改 `UnifiedPipeline.process()` — 在 LLM 呼叫後、現有 Council 審議前，插入反思迴路：
  ```python
  # 現有: response = router.chat(...)
  # 新增:
  revision_count = 0
  while revision_count < MAX_REVISIONS:
      verdict = self._self_check(response, context)
      if not verdict.should_revise:
          break
      revision_prompt = build_revision_prompt(response, verdict)
      response = router.chat(history=history, prompt=revision_prompt)
      revision_count += 1
  dispatch_trace["reflection_count"] = revision_count
  dispatch_trace["reflection_verdicts"] = [v.to_dict() for v in all_verdicts]
  ```
  - 注意：反思迴路在**現有 Council 審議之前**。迴路中的 Council 是「快速預檢」，後面的正式 Council 仍然保留

- [ ] 寫測試 `tests/test_reflection_loop.py`（≥ 10 tests）：
  - `build_revision_prompt` 格式正確，包含原因
  - 端對端：Vow 通過 → `reflection_count=0`
  - 端對端：Vow BLOCK → 修訂一次後通過 → `reflection_count=1`
  - 端對端：連續 BLOCK → 觸發 MAX_REVISIONS=2 上限
  - `dispatch_trace["reflection_count"]` 正確
  - `dispatch_trace["reflection_verdicts"]` 為列表
  - 修訂後的回答確實改變了（不是原文複製）
  - 反思迴路後，正式 Council 仍然被呼叫（未被跳過）
  - 異常處理：`_self_check` 失敗時 graceful fallback（不觸發修訂）
  - `build_revision_prompt` 含截斷保護（超長 draft 不炸 prompt）

### 技術提示
- `process()` 中 LLM 呼叫的位置在 ~L2128：`response = router.chat(history=history, prompt=full_prompt)`
- 後續的 Council 審議在 ~L2097-2176
- 反思迴路的 `_self_check` 中的 Council 預檢可以用 `CouncilRequest(draft_output=draft, context=..., perspectives=None)` — 使用預設 perspectives
- `build_revision_prompt` 對 draft 做截斷保護：if len(draft) > 4000: draft = draft[:4000] + "..."
- mock router 讓第二次 chat() 返回一個「修訂後」的回答

### 禁止
- ❌ 不修改 `vow_system.py`
- ❌ 不修改 `council/pre_output_council.py`
- ❌ 不移除現有的 Council 審議（L2097-2176 段）

---

## Phase 586: Thinking Depth Router

**脈絡**: ToneSoul 目前不區分本地/雲端 LLM。本 Phase 加入 ThinkingTier，根據 AlertLevel 選擇推理深度。

**用戶本地模型**: LM Studio 上的 `qwen3.5-9b-uncensored-hauhaucs-aggressive`（9B GGUF）
**Ollama 不支援此模型**，所以 LOCAL tier 預設走 LM Studio。

### 任務

- [ ] 在 `tonesoul/llm/router.py` 加入：
  ```python
  class ThinkingTier(Enum):
      LOCAL = "local"     # LM Studio 本地模型
      CLOUD = "cloud"     # 雲端 (Gemini/Claude)
      AUTO = "auto"       # 根據 AlertLevel 決定
  ```

- [ ] 加入模組層級函數：
  ```python
  def resolve_thinking_tier(alert_level) -> ThinkingTier:
      # L1 or no alert → LOCAL
      # L2, L3 → CLOUD
  ```

- [ ] 擴充 `LLMRouter.__init__` 支援 `thinking_tier` 參數（預設 "auto"）

- [ ] 加入 `LLMRouter.chat_with_tier()` 方法：
  ```python
  def chat_with_tier(self, *, history, prompt, tier="auto", alert_level=None) -> str:
  ```
  - `tier="auto"` 時根據 `alert_level` 決定
  - `tier="local"` 強制走 LM Studio：`self._try_lmstudio()`
  - `tier="cloud"` 強制走 Gemini：`self._try_gemini()`
  - 若指定 tier 不可用，fallback 到 `auto` 模式

- [ ] 在 `UnifiedPipeline.process()` 中：
  - 將 `router.chat(...)` 呼叫改為 `router.chat_with_tier(..., alert_level=self._last_alert_level)`
  - `dispatch_trace["thinking_tier"]` 記錄使用的 tier

- [ ] 寫測試 `tests/test_thinking_tier.py`（≥ 8 tests）：
  - `resolve_thinking_tier(None)` → LOCAL
  - `resolve_thinking_tier(L1)` → LOCAL
  - `resolve_thinking_tier(L2)` → CLOUD
  - `resolve_thinking_tier(L3)` → CLOUD
  - `chat_with_tier(tier="local")` 呼叫 LM Studio 路徑
  - `chat_with_tier(tier="cloud")` 呼叫 Gemini 路徑
  - `chat_with_tier(tier="auto", alert_level=None)` → LOCAL
  - Fallback：指定 tier 不可用時不 crash

### 技術提示
- 現有 `_try_lmstudio()` 和 `_try_gemini()` 已存在，可直接用
- `chat_with_tier` 內部建立臨時 client，不污染 `_cached_client`
- 或者加入 `_local_client` / `_cloud_client` 雙快取
- `AlertLevel` 從 `tonesoul.alert_escalation` import
- LM Studio 預設 port 1234，會自動偵測模型 — 若指定模型名需要透過 `create_lmstudio_client(model="...")`

### 禁止
- ❌ 不修改 `ollama_client.py`、`lmstudio_client.py`、`gemini_client.py` 的核心邏輯
- ❌ 不硬編碼模型名稱 — 模型名透過 `create_lmstudio_client(model=...)` 參數傳入

---

## Phase 587: 反思 + 路由整合

**脈絡**: Phase 585 的 Reflection Loop + Phase 586 的 ThinkingTier 整合。修訂用的 LLM 根據 severity 選擇 tier。

### 任務

- [ ] 修改 Reflection Loop（Phase 585）的修訂 LLM 呼叫：
  ```python
  # 修訂 tier 根據嚴重度選擇
  revision_tier = "cloud" if verdict.severity >= 0.5 else "local"
  response = router.chat_with_tier(
      history=history,
      prompt=revision_prompt,
      tier=revision_tier
  )
  ```

- [ ] `dispatch_trace["reflection_tiers"]` 記錄每次修訂使用的 tier

- [ ] 在 `tonesoul/reflection.py` 加入 `ReflectionStats` dataclass：
  ```python
  @dataclass
  class ReflectionStats:
      total_revisions: int
      local_revisions: int
      cloud_revisions: int
      final_severity: float
      verdicts: list[ReflectionVerdict]
  ```

- [ ] 整合端對端：
  - AlertLevel=None → 首次用 LOCAL 生成 → 自檢 → 若需修訂且 severity<0.5 → LOCAL 修訂
  - AlertLevel=L2 → 首次用 CLOUD 生成 → 自檢 → 修訂也用 CLOUD
  - AlertLevel=None → 首次 LOCAL → 自檢 severity≥0.5 → **升級到 CLOUD 修訂**（章魚核心場景）

- [ ] 寫測試 `tests/test_reflection_integration.py`（≥ 8 tests）：
  - 低張力 + 無問題 → LOCAL only, 0 revisions
  - 低張力 + Vow FLAG → LOCAL only, 0 revisions（FLAG 不觸發）
  - 低張力 + Vow REPAIR → LOCAL 修訂（severity < 0.5）
  - 低張力 + Council BLOCK → CLOUD 修訂（severity ≥ 0.9）
  - 高張力 (L2) → CLOUD 首次 + CLOUD 修訂
  - `ReflectionStats` 正確計數
  - `dispatch_trace["reflection_tiers"]` 記錄正確
  - `dispatch_trace["thinking_tier"]` 與反思 tier 可以不同

### 技術提示
- 這是章魚架構的核心場景：**本地生成 → 自檢發現嚴重問題 → 雲端修訂**
- Mock 兩個 client（local + cloud），驗證正確的 client 被呼叫

### 禁止
- ❌ 不修改 VowEnforcer 或 Council 的判決邏輯
- ❌ 不移除現有的 Council 審議段

---

## 成功標準

- [ ] VowEnforcer 成功接入 `process()` 流程
- [ ] Reflection Loop 在 Council REFINE/BLOCK 或 Vow 違反時自動修訂
- [ ] MAX_REVISIONS=2 硬上限防止無限迴圈
- [ ] ThinkingTier 根據 AlertLevel 選擇本地/雲端
- [ ] 修訂 tier 根據 severity 選擇（<0.5 本地，≥0.5 雲端）
- [ ] `dispatch_trace` 記錄完整反思軌跡
- [ ] `ruff check tonesoul tests` 通過
- [ ] `pytest tests/ -x --tb=short -q` 通過，測試數 ≥ 2580

## CODEX_HANDBACK.md 需記錄

1. `_self_check()` 的確切位置（unified_pipeline.py 哪一行）
2. Reflection Loop 插入的位置（LLM 呼叫後、Council 前的哪一行）
3. `chat_with_tier()` 的 fallback 邏輯描述
4. 最終測試計數
5. 任何設計決策（是否修改了 `_cached_client` 策略？雙快取 or 臨時 client？）
