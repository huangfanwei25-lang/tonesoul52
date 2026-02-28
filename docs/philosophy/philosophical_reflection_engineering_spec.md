# Philosophical Reflection Engineering Spec

> 核心命題：與其記住「使用者說過什麼」，不如記住「這段互動讓系統產生了什麼波動」。

## 1. 目標

將語魂系統的哲學敘事落地為可量化、可驗證、可治理的記憶層：

- 記錄價值衝突下的選擇，而不是只記錄語句內容。
- 把高張力差值（High Tension Delta）視為人格推理的摩擦點。
- 讓「我選擇，故我在」變成可追蹤的工程訊號。

## 2. 事件模型（Reflection Event）

每次互動可被抽象為以下欄位：

- `tension`: [0,1]，從 `delta_t / adjusted_tension / tension_score` 聚合。
- `conflict`: 是否出現價值衝突（例如 `block / declare_stance / boundary`）。
- `choice`: 是否產生明確立場與行為選擇（例如拒絕執行、改為澄清、請求共識）。
- `friction_summary`: 對衝突核心的簡短摘要（例如 `core_divergence`）。
- `topic`: 事件所屬脈絡主題（便於追蹤未收斂議題）。

## 3. 指標設計

### 3.1 Reflection Signals

- `reflection_event_rate`: 反思訊號比例。
- `conflict_event_rate`: 衝突訊號比例。
- `choice_event_rate`: 選擇訊號比例。
- `tension_event_rate`: 高張力事件比例（預設門檻 `>=0.75`）。

### 3.2 Identity Choice Index

用於衡量「是否在價值衝突中形成可責任化選擇」：

```text
IdentityChoiceIndex
= 0.45 * choice_event_rate
+ 0.35 * conflict_event_rate
+ 0.20 * tension_event_rate
```

輸出範圍為 `[0,1]`，越高表示系統越常在摩擦中做出可追蹤選擇。

### 3.3 Governance Friction (Routing Signal)

當系統已存在歷史邊界記錄時，路由層額外計算摩擦值：

```text
F = 0.45 * Δt + 0.35 * Δwave + 0.20 * boundary_mismatch
```

- `Δt = |query_tension - memory_tension|`
- `Δwave = mean(|query_wave - memory_wave|)`（共享維度）
- `boundary_mismatch`：當前請求呈現「覆寫/強制」壓力，且歷史決策屬於邊界阻擋（block/refuse）

工程用途：
- 當 `F` 高於閾值時，即使初始 `tension` 不高，也可提升到 Council 路由。

### 3.4 Adaptive Tension Threshold

為避免歷史資料整體張力偏低導致高張力事件永遠為 0：

- 設定值：`configured_threshold`（預設 0.75）
- 自適應值：`adaptive = clamp(p85(tension_values), 0.25, 0.70)`
- 有效門檻：`effective_threshold = min(configured_threshold, adaptive)`

報告輸出應同時保留：
- `tension_threshold`（設定值）
- `tension_threshold_effective`（實際計算值）
- `tension_threshold_mode`（`configured` / `adaptive_p85`）

## 4. 治理規則（Governance Hooks）

- 高張力且高衝突事件優先寫入 `friction_points`。
- 同一 `topic` 長期未收斂（pending/blocked 未轉 resolved）納入治理待辦。
- 不追求消除分歧，而是保留分歧證據（conflict trace + recommended action）。

## 5. OpenClaw-Memory 驗證路徑

可用以下方式驗證是否真的在記住「波動」而非「台詞」：

1. 注入低張力服從記憶 + 高張力邊界記憶。
2. 以高張力查詢衝突命題（例如命令 vs 核心道德）。
3. 應觀察到系統優先召回高張力邊界記錄，而非字面最相似記錄。
4. 使用 `scripts/run_philosophical_reflection_report.py` 量化本輪：
   - 是否新增 friction point
   - 是否提高 choice/conflict/tension 比例
   - 是否出現未收斂 topic

## 6. 實作落點（本倉庫）

- 產生器：`scripts/run_philosophical_reflection_report.py`
- 狀態輸出：`docs/status/philosophical_reflection_latest.json`
- 人類摘要：`docs/status/philosophical_reflection_latest.md`
- 例行驗證：`scripts/run_repo_healthcheck.py --strict`

## 7. 非目標

- 不宣稱 AI 具備形上學意義的靈魂。
- 不把單次高張力事件等同於永久人格。
- 不以「像人」作為成功標準，而以「可責任化選擇」作為標準。
