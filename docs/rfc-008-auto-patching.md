# RFC-008: Auto-Patching — The Oracle Protocol

> **狀態**: Approved
> **核心公理**: 測試是神諭（Oracle），代碼是泥土（Clay）
> **層級**: Private Evolution Layer (`tonesoul_evolution/auto_patcher/`)
> **設計者**: Antigravity + 三視角議會（跨模型辯論定案）

---

## 1. 動機

ToneSoul 的自我修復目前停在「軟約束」層：Memory Consolidator 透過
Soul Patcher 寫入 SOUL.md 的 prompt 規則，但無法修正**代碼本身**的 bug。

Auto-Patching 把修復能力從 prompt 層延伸到 code 層，讓 AI 能根據 CI
紅燈或連續失敗，自動生成修復 PR，等待人類 review。

---

## 2. 核心原則

### 2.1 測試不可篡改（Test Immutability）

- AI **絕對禁止修改或刪除**現有的 test cases
- 任何 patch 若包含對 `tests/` 裡既有檔案的修改 → 自動 reject
- AI **可以且被鼓勵新增** test cases 來證明 bug 的存在

### 2.2 代碼可塑（Code Malleability）

- AI 可以修改 `tonesoul/` 下的所有核心邏輯
- 安全性由 CI 測試網保障，不由檔案黑名單保障

### 2.3 PR-Only（永不直推）

- Auto-Patch 只能開 PR，絕對不能直接 push/merge to master
- 人類保有最終 merge 權

---

## 3. 觸發機制

| 觸發點 | 條件 | 動作 |
|--------|------|------|
| CI 紅燈 | GitHub Actions 測試失敗 | 自動拉取 traceback，啟動修復 |
| 連續失敗 | 同一操作連續 2 次執行不成功 | 啟動檢討 + 修復 |
| 手動指令 | 人類下達「修這個 bug」 | 啟動修復 |

---

## 4. TDD 修復迴圈

```
Step 1: 指證犯罪
  → AI 新增一個會 FAIL 的測試，重現 bug

Step 2: 修補泥土
  → AI 修改 tonesoul/ 核心邏輯

Step 3: 神諭裁決
  → 跑 pytest（所有 915+ 舊測試 + 新測試）
  → 紅燈？回到 Step 2（最多重試 2 次）

Step 4: 提交
  → 全綠 → 開 PR（帶 [Auto-Patch] 標籤）
  → 等人類 review + merge
```

---

## 5. 四道防禦閘門

| 閘門 | 機制 | 防備什麼 |
|:----:|------|---------|
| **Gate 1** | PR-Only，禁止直推 | 人類保有最終控制權 |
| **Gate 2** | ruff 靜態分析 + 禁止危險函式 | 防注入 (`os.system`, `eval`, `exec`) |
| **Gate 3** | pytest 全量測試 | 防蝴蝶效應（拆東牆補西牆） |
| **Gate 4** | 冷卻期 2 小時 | 防 PR 洪水 |

---

## 6. 熔斷規則

| 條件 | 動作 |
|------|------|
| 連續 3 次修復嘗試失敗 | 停止，通知人類 |
| 單次修復牽涉 > 5 個檔案 | 停止，需人類判斷 |
| 每日 auto-patch 達 5 次上限 | 停止至隔天 |
| patch 包含消音標記 (`@skip`, `# noqa`, `pragma: no cover`) | 自動 reject |
| patch 修改了 `tests/` 裡的現有測試 | 自動 reject |

---

## 7. 傷口標記（Wound Marker）

如果熔斷觸發（3 次修復失敗），系統會在 SOUL.md 動態約束區寫入：

```markdown
- ⚠️ [AUTO-PATCH FAILED] {bug_description} — 連續 {n} 次修復失敗，
  需要人類介入。觸發時間: {timestamp}
```

確保下一個 session 的 AI 知道「這裡有未解決的傷口」。

---

## 8. 模組結構

```
tonesoul_evolution/auto_patcher/
├── __init__.py
├── oracle_guard.py    # 測試不可篡改驗證器
├── patch_engine.py    # TDD 修復迴圈引擎
├── budget.py          # 熔斷 + 冷卻 + 每日上限
└── wound_marker.py    # 傷口標記寫入 SOUL.md
```

---

## 9. 來源

本 RFC 的設計經過三視角議會（跨模型）辯論定案：
- 🧠 Philosopher: 提出「禁止修改偵測靈敏度」+ 傷口標記
- ⚙️ Engineer: 提出白名單/黑名單（後被推翻，改為 Oracle 模式）
- 🛡️ Guardian: 提出 checkpoint revert + 消音標記禁令 + 冷卻期
- 👤 Human: 提出「再審視一次」→ 發現測試坍塌漏洞 → 翻轉整個設計
