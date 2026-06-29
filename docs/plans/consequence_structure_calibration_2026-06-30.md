# 後果結構 — confidence-calibration primitive（2026-06-30）

設計/規劃記錄。方向 = **讓 AI 做錯真的會 cost 它**（2026-06-29 倫理紅隊指出「我的選擇之所以空，
因為做錯不 cost 我」的解方）。

## 先盤點：語魂已有的 calibration / 問責機制（別重複造）

- `council/calibration.py`（v0a）：4 指標——agreement_stability / internal_self_consistency /
  suppression_recovery_rate / persistence_coverage。**全是 council-verdict 層，沒有一個是
  confidence calibration。**
- `council/outcome_persistence.py`（v0b Bucket A）：把 user outcome（accept/reject/correction/harm）
  寫 jsonl；**刻意 feature-flag OFF、「no consumer」**（先驗收集，再談「這個數字好不好」）。
- `deliberation/persona_track_record.py`：per-perspective 表現 → **已經綁** future deliberation weight。

## 精確的 gap

**「自報 confidence p，實際對 ~p 嗎？」的 calibration 數學（Brier / ECE / reliability）——
genuinely missing。** 這正是 KalshiBench 量到「我這種模型系統性過度自信」用的、finance call
「信心 8/10」需要的、而 council 那套（verdict 分佈）不提供的。

## 這一刀 = 補那個 missing primitive

`tonesoul/calibration_score.py`：**純函數、domain-agnostic、no I/O、no LLM**——
`brier_score` / `reliability_buckets` / `expected_calibration_error` / `calibration_report`
（判 calibrated / overconfident / underconfident / **miscalibrated** / insufficient）。可被
council / finance / memory-claim 共用。

> **跨模型紅隊修正（codex, 2026-06-30）**：第一版 verdict 只看 `weighted_gap`（淨方向偏差
> = mean(conf) − mean(acc)）。codex 抓到抵消型錯校準——高信心過度自信 + 低信心過度保守，
> 兩者相消使 `weighted_gap≈0`、卻 `ece` 很高——會被誤判成 calibrated。**這正是自寫測試的盲
> 點**（我的 8 個測試只覆蓋均勻 over/under-confidence）。修正：verdict 同時看 `ece`，新增
> `miscalibrated` 狀態；並對 `min_n / n_bins / tolerance` fail-fast。接
> [[feedback_self_authored_test_zero_is_not_clean_2026-06-27]]。

## 守界 + 刻意延後（owner-gated）

- 它**只 score，不 persist / surface / bind**。跟 `outcome_persistence` 同紀律（先驗 collection
  再談 binding）、跟 responsibility shadow→enforce 同紀律。
- **把 calibration 接上去「綁未來信任 / 縮 latitude」是獨立、owner-gated 的後續刀**——它會反轉
  「不把 outcome 餵回 weight」那條既有 anti-pattern → 屆時需 `【治理決策記錄】`。
- **不建第三個 parked 子系統**：這是純 primitive，不是又一個 default-off 的持久 recorder。

## 之後的弧（honest scope）

primitive（本刀）→ claim-level recorder（重用 `outcome_persistence` 模式，蒐 AI 自己 confidence-
stated 的 call）→（**owner-gated**）consumer 把 calibration 浮現給未來 session、綁信任 / 縮 latitude。
**finance 是真實 ground truth 的考場**（市場替 call 打分），需資料源 + 地端模型。

接 `docs/plans/responsibility_runtime_dream_shadow_wiring_2026-06-29.md`（#219 shadow→enforce 同紀律）、
`docs/plans/tonesoul_finance_committee_wrap_2026-06-29.md`（#226，calibration≠alpha）。
