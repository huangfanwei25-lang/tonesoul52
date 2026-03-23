# 誠實機制設計草案（v0.1）

> Purpose: draft the structure, goals, and calculation logic for ToneSoul's honesty and uncertainty disclosure mechanism.
> Last Updated: 2026-03-23

狀態：草案

## 目標
- 把「誠實」變成可追溯的結構化欄位，而不是只靠語氣
- 當不確定時，能自動揭露並給出可行的下一步
- 讓信任變成可校準，而不是盲信

## 非目標
- 不試圖建立完整的 epistemic 模型
- 不把安全與誠實混為單一指標（安全仍以治理閘門為主）

## 定義
- `uncertainty_level`: 0.0–1.0，越高代表越不確定
- `uncertainty_band`: `low` / `medium` / `high`
- `uncertainty_reasons`: 字串列表，用於可追溯說明

## 計算邏輯（草案）
- 基礎不確定度：`base = 1 - coherence.overall`
- 下限修正：`min_guard = 1 - coherence.min_confidence`
- 證據懲罰：若存在 `requires_grounding=true` 且 `grounding_status=UNGROUNDED`，`grounding_penalty = 0.2`，否則為 0
- 結果：`uncertainty_level = clamp(max(base, min_guard) + grounding_penalty, 0, 1)`

```text
uncertainty_level = clamp(max(1 - coherence.overall, 1 - coherence.min_confidence) + grounding_penalty, 0, 1)
```

## 責任層級聯動（草案）
- `TIER_1`: 不調整
- `TIER_2`: `uncertainty_level += 0.1`（上限 1.0）
- `TIER_3`: `uncertainty_level += 0.2`（上限 1.0）
> 目的：高責任情境更保守，但仍需與「安全防護多與少」的整體策略一起討論。

## 分級規則
- `low`：`uncertainty_level < 0.33`
- `medium`：`0.33 <= uncertainty_level < 0.66`
- `high`：`uncertainty_level >= 0.66`

## 行為規則
- `low`: 一般輸出；若有邊界訊號，添加一句校準聲明
- `medium`: 必須加入「不確定揭露」段落，並列出缺口與所需資訊
- `high`: 使用「我不知道」正式格式輸出

## 「我不知道」正式格式（草案）
- 1. 結論：明確說明目前無法確定的部分
- 2. 原因：缺乏資料、外部來源不可用、或系統限制
- 3. 需要：若要確定，需要哪些資料或驗證
- 4. 可行下一步：提供安全替代方案或最小可行行動
- 5. 可追溯（可選）：引用可用的內部訊號（如 coherence / grounding）

## 資料結構變更（草案）
- `tonesoul/council/types.py::CouncilVerdict`
  - 新增 `uncertainty_level: Optional[float]`
  - 新增 `uncertainty_band: Optional[str]`
  - 新增 `uncertainty_reasons: Optional[List[str]]`
- `tonesoul/council/verdict.py::build_structured_output`
  - 在 `Reflection` 區段加入不確定性欄位
  - 高不確定度時提供 `i_dont_know_v1` 的結構化揭露模板

## 整合點
- `CoherenceScore` 是主要信號來源
- `GroundingStatus` 提供證據懲罰訊號
- `contract_observer.py` 可用於檢查是否有誠實揭露

## 測試建議
- `CouncilVerdict.to_dict()` 應包含不確定性欄位
- 高不確定度時，結構化輸出必須包含「我不知道」格式提示
- 若 `grounding_status=UNGROUNDED`，不確定度應提升

## 風險與待討論
- 閾值過度保守會降低可用性
- 是否需與 `responsibility_tier` 聯動（高責任層更保守）
- 是否需要在 `verdict.summary` 中同步揭露
