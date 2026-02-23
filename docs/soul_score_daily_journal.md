# Soul Score Daily Journal Spec

## 1. 目標

- 每日只保留一筆 `Soul Score` 聚合紀錄，避免事件洪流造成資料爆炸。
- 同日事件採 `upsert + accumulate`，確保可追蹤且可防注入。
- 緊急事件可即時更新當日紀錄，供 governance 與監控即時讀取。

## 2. 資料模型

`daily_key = YYYY-MM-DD`（UTC）

建議欄位：

- `daily_key`: `TEXT PRIMARY KEY`
- `total_events`: `INTEGER`
- `tension_sum`: `REAL`
- `integrity_sum`: `REAL`
- `risk_sum`: `REAL`
- `soul_score`: `REAL`
- `high_risk_events`: `INTEGER`
- `emergency_updates`: `INTEGER`
- `last_event_at`: `TEXT` (ISO-8601 UTC)
- `updated_at`: `TEXT` (ISO-8601 UTC)

可選欄位（稽核）：

- `source_breakdown`: `JSON`
- `band_counts`: `JSON`（low/medium/high）

## 3. 寫入規則（Upsert）

輸入事件：

- `event_timestamp`
- `tension_delta`
- `integrity_delta`
- `risk_delta`
- `quality_band`
- `is_emergency`

流程：

1. 由 `event_timestamp` 正規化出 `daily_key`（UTC）。
2. 用 `daily_key` 做 `UPSERT`：
   - 不存在：建立新列。
   - 已存在：累加 sum/count 欄位，不新增第二列。
3. 更新 `last_event_at` 與 `updated_at`。
4. 重新計算 `soul_score`（同一套公式，不可在不同寫入路徑分叉）。

## 4. 防注入與限流

- **單日單列**：從結構上阻斷「大量 insert」攻擊。
- **單事件權重上限**：對 `tension_delta / risk_delta` 做 clamp。
- **來源配額**：同一 source 在短時間內超量時降權或丟棄。
- **異常熔斷**：若單分鐘事件暴增，進入 `degraded mode`（僅計數、不提升分數）。

## 5. 緊急事件即時更新

- `is_emergency = true` 時，必須立即觸發當日 `upsert`，不可等待批次。
- 緊急寫入額外累加：
  - `high_risk_events += 1`
  - `emergency_updates += 1`
- 即時刷新當日 `soul_score`，供 UI / gate 即刻讀取。

## 6. 讀取介面（建議）

- `get_daily(daily_key)`：讀單日聚合。
- `get_range(from_key, to_key)`：讀區間趨勢。
- `get_latest()`：讀最近一天（或最近有資料的一天）。

## 7. 回溯與修補

- 原始事件流保留在獨立 append-only log。
- 若公式升級，允許用 raw log 對特定日期做重算回填。
- 重算需記錄 `rebuild_reason`, `rebuild_at`, `rebuild_by`。

## 8. 非目標（本階段不做）

- 不做跨日多版本公式並存。
- 不做自動修正歷史資料的背景任務。
- 不做 UI 視覺化改版（只提供資料契約）。
