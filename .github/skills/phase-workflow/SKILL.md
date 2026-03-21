---
name: phase-workflow
description: "**WORKFLOW & PROCESS** — ToneSoul Phase 開發流程。USE WHEN: 開始新 Phase、執行多步驟開發任務、需要更新 task.md、提交程式碼。DO NOT USE FOR: 單一檔案小修改、純閱讀操作。INVOKES: terminal (pytest, ruff), file system tools."
---

# Phase 開發工作流程

> 每個 Phase 都是一次可追溯的系統進化。

## Phase 生命週期

```
規劃 → 紅燈測試 → 綠燈實作 → Lint/Test → 記錄 → 提交
```

## 啟動 Phase 檢查表

開始新 Phase 前，依序確認：

1. **讀 `task.md` 最新狀態** — 確認前一 Phase 已完成
2. **確認無回歸** — `pytest tests/ -x` 全過
3. **寫 Phase 規格** — 在 task.md 頂部寫入：
   ```md
   ## Phase N: [名稱] (日期)
   - [ ] 任務 1
   - [ ] 任務 2
   **成功標準**: [可測試的結果]
   ```
4. **探索依賴** — 讀相關模組原始碼，不要猜

## 實作規範

### 測試先行

```python
# 1. 先寫會失敗的測試
def test_new_feature():
    result = new_function(input)
    assert result == expected  # 紅燈

# 2. 寫最小程式碼讓測試通過
def new_function(input):
    return expected  # 綠燈

# 3. 重構（測試仍通過）
```

### 驗證門檻

每個 Phase 結束前必須通過：

```bash
# Lint 檢查
python -m ruff check [修改的檔案]

# 測試（至少包含修改涉及的測試檔案）
python -m pytest tests/[相關測試] -q

# 無回歸（若修改了核心模組）
python -m pytest tests/ -x --tb=short
```

### task.md 記錄格式

Phase 完成後，更新 task.md：

```md
## Phase N: [名稱] (日期)
- [x] 任務 1
- [x] 任務 2
**成功標準**: [可測試的結果]
**Validation**:
- `python -m ruff check [檔案列表]` -> passed
- `python -m pytest [測試列表] -q` -> N passed
```

## ⚠️ 注意事項

- **觸發**：跳過「讀現有程式碼」直接寫新功能
  **風險**：重複實作已存在的功能，或破壞隱含的不變式
  **快速檢查**：`grep -r "關鍵字" tonesoul/` 確認沒有相似實作
  **正確做法**：先用 Explore subagent 搜尋相關模組

- **觸發**：一個 Phase 包含超過 7 個任務
  **風險**：無法在單次對話中完成，中途斷線會導致不一致狀態
  **快速檢查**：計算任務數
  **正確做法**：拆分成多個 Phase，每個 3-5 個任務

- **觸發**：修改了核心模組但只跑新測試
  **風險**：破壞了其他模組依賴的行為
  **快速檢查**：`pytest tests/ -x` 跑全套
  **正確做法**：修改核心模組時一律跑完整測試

- **觸發**：忘記更新 task.md
  **風險**：下次對話（或其他 AI）無法知道目前進度
  **快速檢查**：task.md 頂部是否有最新 Phase 記錄
  **正確做法**：Phase 驗證通過後立即更新

## 禁止事項

❌ 禁止提交無法通過 `ruff check` 的程式碼  
❌ 禁止提交無對應測試的新功能  
❌ 禁止用 `--no-verify` 繞過 commit hooks  
❌ 禁止在一個 Phase 中同時重構 + 加新功能（分開做）  
❌ 禁止 Phase 標記為完成但測試未通過

## 三次失敗規則

卡住超過 3 次嘗試後：
1. 停止嘗試
2. 記錄：嘗試了什麼、錯誤訊息、為什麼失敗
3. 質疑基本假設
4. 找 2-3 個替代方案
5. 換個角度重試
