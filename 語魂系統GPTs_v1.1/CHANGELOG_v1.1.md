# CHANGELOG v1.1

日期：2026-02-11  
範圍：`語魂系統GPTs_v1.1/`

## Added

- 新增整合目錄 `語魂系統GPTs_v1.1/` 作為單一定稿來源。
- 新增 `00_差異矩陣.md`，明確列出原版與 Codex 版衝突與整合策略。
- 新增口語與簡報輸出檔：
  - `14_簡報一頁圖_文字版.md`
  - `15_口語講稿_3分鐘.md`
  - `16_口語講稿_10分鐘.md`
- 新增本檔 `CHANGELOG_v1.1.md` 與 `MIGRATION_NOTE_v1.1.md`。

## Changed

- 術語統一：
  - `ΔS` 固定為 Direction（`[-1,1]`）
  - `ΔΣ` 固定為 Semantic Divergence（`[0,1]`）
- 門檻統一：`PASS / REWRITE / BLOCK` 與 `POAV` 門檻改為單一版本。
- Prompt 與治理文件全面對齊 `01_術語與門檻單一規格.md`。
- 多份文件補上實際 repo 可追溯路徑，避免宣稱無法回放。

## Fixed

- 修復 legacy 文字中導致路徑掃描誤判的表述（避免被當成失效檔案引用）。
- 清理原版 `body/*` 等不存在路徑的引用風險（改為現行可定位路徑）。

## Removed / Deprecated

- 棄用雙重 POAV 詞義並淘汰歧義寫法。
- 棄用將「語義漂移」標成 `ΔS` 的舊寫法（改為 `ΔΣ`）。
- 棄用「字數越短越精確」作為唯一精確度判定依據。

## Compatibility Notes

- 程式層若仍見 `delta_s`（legacy 變數名）代表 divergence，文件層一律標為 `ΔΣ`。
- `poav_gate()` 在 `enforce=false` 場景可 `record_only`；是否阻擋由上層策略決定。

## Verification Snapshot

- `語魂系統GPTs_v1.1` 目錄已補齊 `00~16` + `CHANGELOG` + `MIGRATION_NOTE`。
- 路徑引用一致性掃描：需維持 `Test-Path == True`（以當次掃描結果為準）。
