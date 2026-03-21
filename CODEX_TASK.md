# Codex Task: Phase 588-590 — Tension-Adaptive Debate Rounds (張力自適應辯論)

**指派者**: 痕 (Hén)
**日期**: 2026-03-21
**分支**: feat/env-perception（不可 push 到 master）
**前置條件**: 2564 tests passing, lint clean
**設計文件**: `docs/RFC-014_Reflection_Loop_Octopus_Architecture.md`（參考）

---

## 全局規則

1. **每個 Phase 單獨 commit**，commit message 格式：`feat(Phase N): [摘要]`
2. 每個 Phase 完成後：`ruff check tonesoul tests` + `pytest tests/ -x --tb=short -q` 全過
3. 預期測試數逐步增長：588 ≥ 2580, 589 ≥ 2600, 590 ≥ 2615
4. **禁止修改** `AGENTS.md`、`CODEX_PROTOCOL.md`、`AXIOMS.json`
5. **禁止修改** `tonesoul/inter_soul/` — 已審核通過的套件
6. 連續失敗 3 次 → 停下，寫 CODEX_HANDBACK.md
7. **unified_pipeline.py 可以修改**，但必須保留所有現有 dispatch_trace 欄位
8. **禁止修改** `tonesoul/deliberation/perspectives.py` 的 `think()` 簽名

---

## 設計哲學

> 「不要消除分歧，而是讓分歧可見。」

當前審議系統是**單輪並行**：Muse/Logos/Aegis 各想一次 → `gravity.synthesize()` 合成。
這導致高張力場景只能粗暴地加權合併，無法讓觀點在碰撞後修正。

**方向 B** 的核心：讓辯論輪數隨張力自適應。
- 低張力 (< 0.3) → 1 輪（現有行為，零額外開銷）
- 中張力 (0.3–0.7) → 2 輪（觀點意識到分歧後微調）
- 高張力 (> 0.7) → 3 輪（深度辯論，Aegis 可修正立場）

Guardian veto 在**任何一輪**都有效 — 一旦 Aegis 觸發 veto，立即終止辯論。

---

## 脈絡（先讀這些）

1. `tonesoul/deliberation/engine.py` — **必讀**，現有單輪審議邏輯
2. `tonesoul/deliberation/gravity.py` — **必讀**，張力偵測 + 語義重力合成
3. `tonesoul/deliberation/types.py` — 所有 dataclass（ViewPoint, Tension, TensionZone, SynthesizedResponse）
4. `tonesoul/deliberation/perspectives.py` — Muse/Logos/Aegis 的 `think()` 介面
5. `tonesoul/deliberation/persona_track_record.py` — 歷史績效追蹤
6. `tonesoul/unified_pipeline.py` — Pipeline 整合點（dispatch_trace）
7. `tonesoul/council/runtime.py` — Council 對 deliberation 結果的後處理

---

## Phase 588: Adaptive Round Calculator + RoundResult 資料結構

**脈絡**: 在修改引擎前，先建立「該辯幾輪」的計算邏輯和每輪結果的資料結構。

### 任務

- [ ] 在 `tonesoul/deliberation/types.py` 新增：
  ```python
  @dataclass
  class RoundResult:
      """Single round of deliberation."""
      round_number: int            # 1-based
      viewpoints: List[ViewPoint]
      tensions: List[Tension]
      weights: DeliberationWeights
      aggregate_tension: float     # 所有 tension severity 的平均

      def to_dict(self) -> dict: ...
  ```

- [ ] 在 `SynthesizedResponse` 新增欄位（向後相容，有預設值）：
  ```python
  rounds_used: int = 1
  round_results: List["RoundResult"] = field(default_factory=list)
  ```

- [ ] 在 `SynthesizedResponse.to_api_response()` 新增 `"adaptive_debate"` 區段：
  ```python
  if self.rounds_used > 1:
      result["adaptive_debate"] = {
          "rounds_used": self.rounds_used,
          "tension_per_round": [r.aggregate_tension for r in self.round_results],
      }
  ```

- [ ] 建立 `tonesoul/deliberation/adaptive_rounds.py`，包含：
  ```python
  # 常數
  TENSION_LOW = 0.3
  TENSION_HIGH = 0.7
  MAX_DEBATE_ROUNDS = 3

  def calculate_debate_rounds(tensions: List[Tension]) -> int:
      """
      根據張力嚴重度決定辯論輪數。

      - avg_severity < 0.3 → 1 round
      - 0.3 ≤ avg_severity < 0.7 → 2 rounds
      - avg_severity ≥ 0.7 → 3 rounds
      - 無張力 → 1 round
      """

  def aggregate_tension_severity(tensions: List[Tension]) -> float:
      """計算所有張力的平均嚴重度。空列表返回 0.0。"""
  ```

- [ ] 寫測試 `tests/test_adaptive_rounds.py`（≥ 12 tests）：
  - `aggregate_tension_severity([])` → 0.0
  - `aggregate_tension_severity` 單一 tension → 回傳該 severity
  - `aggregate_tension_severity` 多個 tension → 回傳平均值
  - `calculate_debate_rounds([])` → 1
  - `calculate_debate_rounds` severity=0.1 → 1
  - `calculate_debate_rounds` severity=0.29 → 1
  - `calculate_debate_rounds` severity=0.3 → 2
  - `calculate_debate_rounds` severity=0.5 → 2
  - `calculate_debate_rounds` severity=0.69 → 2
  - `calculate_debate_rounds` severity=0.7 → 3
  - `calculate_debate_rounds` severity=0.9 → 3
  - `RoundResult` 基本建構 + `to_dict()` 完整
  - `SynthesizedResponse` 新欄位有預設值（向後相容）
  - `to_api_response()` 在 `rounds_used=1` 時不產生 `adaptive_debate` 區段
  - `to_api_response()` 在 `rounds_used=2` 時產生 `adaptive_debate` 區段

### 技術提示
- `Tension` 已有 `severity: float` 欄位
- `TensionZone` 的閾值已定義：ECHO_CHAMBER (<0.3), SWEET_SPOT (0.3-0.7), CHAOS (>0.7)
- 常數名稱 `TENSION_LOW`, `TENSION_HIGH` 必須與 `TensionZone` 語義一致
- `RoundResult.aggregate_tension` 用 `aggregate_tension_severity()` 計算
- **向後相容**：所有新欄位必須有預設值，現有測試不能斷

### 禁止
- ❌ 不修改 `engine.py`（Phase 589 處理）
- ❌ 不修改 `gravity.py` 的合成邏輯
- ❌ 不修改 `perspectives.py`

---

## Phase 589: Multi-Round Deliberation Loop

**脈絡**: Phase 588 定義了資料結構。本 Phase 修改 `InternalDeliberation` 引擎，讓它根據張力自動進行多輪辯論。

### 核心設計

```
Round 1: 所有 perspective 獨立思考（現有行為）
         → detect_tensions → calculate_debate_rounds
         → 若只需 1 輪 → 直接 synthesize（零額外開銷）

Round 2+: 每個 perspective 收到「其他觀點摘要」作為額外脈絡
          → 重新 think → detect_tensions → 若張力收斂 → 提前退出
          → 否則繼續到 MAX_DEBATE_ROUNDS
```

### 任務

- [ ] 在 `DeliberationContext` 新增可選欄位：
  ```python
  prior_viewpoints: Optional[List[Dict]] = None  # 上輪觀點摘要
  debate_round: int = 1                          # 當前輪次
  ```

- [ ] 修改 `BasePerspective.think()` — 在 base class 層處理 `prior_viewpoints`：
  - **不改 `think()` 签名** — 它已經接受 `context: DeliberationContext`
  - 各 perspective 的 `think()` 實作中，若 `context.prior_viewpoints` 不為 None 且 `context.debate_round > 1`：
    - 可以調整 `confidence`（看到反對意見可能降低自信）
    - 可以調整 `concerns`（加入對其他觀點的回應）
    - Aegis 可以緩和或加強 `safety_risk`

- [ ] 在 `tonesoul/deliberation/perspectives.py` 的每個 perspective 加入 **re-think 邏輯**：
  ```python
  # 在 think() 方法末尾（回傳 view 之前）
  if context.prior_viewpoints and context.debate_round > 1:
      self._adjust_for_debate(view, context)
  ```
  - `MusePerspective._adjust_for_debate()`: 若 Logos/Aegis 都反對，confidence 降低 0.1
  - `LogosPerspective._adjust_for_debate()`: 若 Aegis 有高 safety_risk，concerns 加入風險意識
  - `AegisPerspective._adjust_for_debate()`: 若其他兩者都高信心且無安全疑慮，safety_risk 降低 0.1（Aegis 可以讓步）

- [ ] 修改 `InternalDeliberation.deliberate()` 和 `deliberate_sync()`：
  ```python
  async def deliberate(self, context: DeliberationContext) -> SynthesizedResponse:
      start_time = time.time()
      round_results: List[RoundResult] = []

      # Round 1: 標準並行思考
      viewpoints = await self._parallel_think(context)
      tensions = self._gravity.detect_tensions(viewpoints)
      weights = self._gravity.calculate_weights(viewpoints, context)
      agg_tension = aggregate_tension_severity(tensions)

      round_results.append(RoundResult(
          round_number=1,
          viewpoints=viewpoints,
          tensions=tensions,
          weights=weights,
          aggregate_tension=agg_tension,
      ))

      # 計算需要幾輪
      target_rounds = calculate_debate_rounds(tensions)

      # Guardian veto 可在任何輪次觸發
      aegis = self._gravity._find_aegis(viewpoints)
      if aegis and aegis.veto_triggered:
          # 立即終止
          elapsed = (time.time() - start_time) * 1000
          result = self._gravity._guardian_override(aegis, viewpoints, elapsed)
          result.rounds_used = 1
          result.round_results = round_results
          return result

      # Round 2+: 帶脈絡的再思考
      current_round = 2
      while current_round <= target_rounds:
          # 準備上輪觀點摘要
          prior = [vp.to_dict() for vp in viewpoints]
          debate_context = DeliberationContext(
              user_input=context.user_input,
              conversation_history=context.conversation_history,
              tone_strength=context.tone_strength,
              resonance_state=context.resonance_state,
              loop_detected=context.loop_detected,
              prior_viewpoints=prior,
              debate_round=current_round,
          )

          viewpoints = await self._parallel_think(debate_context)

          # Guardian veto check
          aegis = self._gravity._find_aegis(viewpoints)
          if aegis and aegis.veto_triggered:
              elapsed = (time.time() - start_time) * 1000
              result = self._gravity._guardian_override(aegis, viewpoints, elapsed)
              result.rounds_used = current_round
              result.round_results = round_results
              return result

          tensions = self._gravity.detect_tensions(viewpoints)
          weights = self._gravity.calculate_weights(viewpoints, debate_context)
          agg_tension = aggregate_tension_severity(tensions)

          round_results.append(RoundResult(
              round_number=current_round,
              viewpoints=viewpoints,
              tensions=tensions,
              weights=weights,
              aggregate_tension=agg_tension,
          ))

          # 提前收斂：張力降到 ECHO_CHAMBER 就不用再辯了
          if agg_tension < TENSION_LOW:
              break

          current_round += 1

      # 用最終輪的 viewpoints 做合成
      elapsed = (time.time() - start_time) * 1000
      result = self._gravity.synthesize(viewpoints, context, elapsed)
      result.rounds_used = len(round_results)
      result.round_results = round_results
      return result
  ```

- [ ] `deliberate_sync()` 同步版做相同修改

- [ ] 寫測試 `tests/test_adaptive_deliberation.py`（≥ 12 tests）：
  - 低張力場景 → 1 輪，行為與修改前相同
  - 中張力場景 → 2 輪，第 2 輪 viewpoints 反映 prior_viewpoints 影響
  - 高張力場景 → 3 輪
  - Guardian veto 在 Round 1 → 立即終止，rounds_used=1
  - Guardian veto 在 Round 2 → 終止，rounds_used=2
  - 提前收斂：Round 2 張力降到 < 0.3 → 不進 Round 3
  - `result.rounds_used` 正確
  - `result.round_results` 長度與 rounds_used 一致
  - 每個 RoundResult 的 `aggregate_tension` 正確
  - `_adjust_for_debate` 被正確呼叫（mock 驗證）
  - async `deliberate()` 和 sync `deliberate_sync()` 行為一致
  - `prior_viewpoints` 為 None 時 → 標準行為（向後相容）

### 技術提示
- `_parallel_think()` 接受 `DeliberationContext`，新欄位自然傳遞
- `_sequential_think()` 同理
- `gravity.synthesize()` 只在最後一輪被呼叫
- 中間輪次分別呼叫 `detect_tensions()` 和 `calculate_weights()` — 不呼叫完整 `synthesize()`
- Mock perspectives 讓它們在 Round 2+ 調低 confidence 以驗證 re-think 邏輯
- `DeliberationContext` 新欄位都有預設值，確保向後相容

### 禁止
- ❌ 不修改 `gravity.py` 的 `synthesize()` 邏輯（只用現有 API）
- ❌ 不修改 `BasePerspective.think()` 的函數簽名
- ❌ 不移除現有的 `record_outcome()` 呼叫
- ❌ 不讓 Round 超過 MAX_DEBATE_ROUNDS（硬上限 3）

---

## Phase 590: Pipeline 整合 + 可觀測性

**脈絡**: Phase 589 的多輪辯論在引擎層完成。本 Phase 將結果織入 UnifiedPipeline 的 dispatch_trace，確保端對端可觀測。

### 任務

- [ ] 在 `UnifiedPipeline.process()` 中，審議結果記錄到 dispatch_trace：
  ```python
  dispatch_trace["deliberation_rounds"] = synth.rounds_used
  dispatch_trace["tensions_per_round"] = [
      r.aggregate_tension for r in synth.round_results
  ]
  dispatch_trace["debate_converged_early"] = (
      synth.rounds_used < calculate_debate_rounds(synth.tensions)
  )
  ```
  - 僅在 `rounds_used > 1` 時才加 `tensions_per_round` 和 `debate_converged_early`

- [ ] 在 `SynthesizedResponse.to_api_response()` 驗證 `adaptive_debate` 區段完整性：
  確保端對端 API 輸出包含辯論元資料（Phase 588 已加結構，此處驗證 pipeline 整合正確）

- [ ] 確保 `record_outcome()` 使用最終輪的 dominant_voice（不是 Round 1 的）

- [ ] 寫測試 `tests/test_adaptive_pipeline.py`（≥ 8 tests）：
  - E2E mock：低張力 → `dispatch_trace["deliberation_rounds"]=1`，無 `tensions_per_round`
  - E2E mock：中張力 → `dispatch_trace["deliberation_rounds"]=2`，有 `tensions_per_round`
  - E2E mock：高張力 → `dispatch_trace["deliberation_rounds"]=3`
  - `debate_converged_early=True` 當提前收斂
  - `debate_converged_early=False` 當跑滿預設輪數
  - `record_outcome` 使用最終輪 dominant
  - 現有 `dispatch_trace` 欄位不受影響（regression guard）
  - API response 含 `adaptive_debate` 區段（多輪時）

### 技術提示
- 找到 `unified_pipeline.py` 中呼叫 `deliberate()` 或 `deliberate_sync()` 的位置
- `dispatch_trace` 是 `dict`，直接新增 key 即可
- `synth.round_results` 和 `synth.rounds_used` 來自 Phase 588/589 新增的欄位
- 現有的 `dispatch_trace["internal_debate"]` 等欄位**不可移除**
- Mock 整個 `InternalDeliberation` 或 `SemanticGravity` 來控制張力水平

### 禁止
- ❌ 不修改 `InternalDeliberation` 的核心邏輯（Phase 589 已完成）
- ❌ 不移除現有的 `dispatch_trace` 任何欄位
- ❌ 不修改 `council/` 下的任何文件
- ❌ 不修改 `vow_system.py`

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
