# ToneSoul Skills 索引

> 基於 Anthropic 內部 Skill 九類分類框架，適配 ToneSoul 專案。

## 九大分類

| # | 分類 | 用途 | 觸發時機 | 狀態 |
|---|------|------|----------|------|
| 1 | **Library & API Reference** | 內部模組用法、陷阱、規範寫法 | 使用 ToneSoul 子系統時 | ✅ |
| 2 | **Workflow & Process** | Phase 流程、審議流程、提交門檻 | 執行多步驟開發任務時 | ✅ |
| 3 | **Architecture & Design** | 架構決策、模式選擇、取捨框架 | 設計新模組或重構時 | 📋 |
| 4 | **Testing & Quality** | 測試策略、覆蓋率門檻、斷言模式 | 寫測試或驗證品質時 | 📋 |
| 5 | **Debugging & Diagnostics** | 錯誤定位、日誌分析、快速排查 | 遇到失敗或異常行為時 | 📋 |
| 6 | **Security & Safety** | 安全檢查、權限驗證、敏感操作 | 碰觸生產環境或敏感資料時 | ✅ |
| 7 | **Documentation & Knowledge** | 文件撰寫規範、知識沉澱格式 | 寫文件或更新規範時 | 📋 |
| 8 | **Deployment & Operations** | 部署流程、環境切換、監控 | 部署或操作基礎設施時 | 📋 |
| 9 | **Domain-Specific** | 金融分析、張力計算、審議引擎 | 碰觸領域核心邏輯時 | 📋 |

## Skill 寫作規範

### 高訊號注意事項區塊格式

```md
## ⚠️ 注意事項

- **觸發**：[什麼條件下會出事]
  **風險**：[會造成什麼後果]
  **快速檢查**：[一行指令或觀測欄位]
  **正確做法**：[該怎麼做]
```

### 品質門檻

1. 不重述平台預設行為
2. 每條注意事項必須有觸發條件
3. 優先寫不可逆錯誤
4. 只保留可驗證的規則
5. 要有失敗指紋（錯誤訊息、回應碼）
6. 最多 7 條核心警示
7. 用禁止句提高訊號密度

### On-Demand Hook 設計原則

- 啟用條件明確（使用者主動觸發）
- 作用範圍是會話級
- 規則分三級：`hard-block` / `confirm` / `log-only`
- 要有可審計的逃生機制
- 攔截訊息要給替代路徑

## 目錄結構

```
.github/skills/
├── README.md                          ← 本檔案
├── tonesoul-api/SKILL.md              ← 分類 1: ToneSoul API 參考
├── phase-workflow/SKILL.md            ← 分類 2: Phase 工作流程
├── careful/SKILL.md                   ← 分類 6: 安全護欄 On-Demand Hook
└── ...
```
